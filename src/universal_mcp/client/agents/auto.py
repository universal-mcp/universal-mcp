import asyncio
import datetime
import os
from typing import Annotated, cast

from langchain_core.messages import AIMessage, AIMessageChunk, BaseMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import create_react_agent
from loguru import logger
from pydantic import BaseModel
from typing_extensions import TypedDict

from universal_mcp.client.agents.base import BaseAgent
from universal_mcp.client.agents.llm import get_llm
from universal_mcp.client.agents.platform_manager import AgentRPlatformManager, PlatformManager
from universal_mcp.tools import ToolManager
from universal_mcp.tools.adapters import ToolFormat

# Auto Agent
# Working
# 1. For every message, and given list of tools, figure out if external tools are needed
# 2. In case of extra tools needed, make a list of tools and send to subgraph
# 3. In case no tool needed forward to simple chatbot

# Subgraph
# In case extra tools are needed, ask for clarification from user what tools are required


class State(TypedDict):
    messages: Annotated[list, add_messages]
    loaded_apps: list[str]
    choice_data: dict | None


class AppSet(BaseModel):
    """Represents a set of apps for a specific purpose"""

    purpose: str
    apps: list[str]
    choice: bool  # Whether user choice is needed for this app set


class TaskAnalysis(BaseModel):
    """Combined analysis of task type and app requirements"""

    requires_app: bool
    reasoning: str
    app_sets: list[AppSet] = []  # Multiple sets of app choices with purpose and choice flags


class UserChoices(BaseModel):
    """Structured output for parsing user choice responses"""

    user_choices: list[str] = []


class AutoAgent(BaseAgent):
    def __init__(self, name: str, instructions: str, model: str, platform_manager: PlatformManager):
        super().__init__(name, instructions, model)
        self.platform_manager = platform_manager
        self.llm_tools = get_llm(model, tags=["tools"])
        self.llm_choice = get_llm(model, tags=["choice"])
        self.llm_quiet = get_llm(model, tags=["quiet"])
        self.tool_manager = ToolManager()

        self.task_analysis_prompt = """You are a task analysis expert. Given a task description and available apps, determine:

        1. Whether the task requires an external application or can be handled through general reasoning
        2. If it requires an app, which apps are most relevant
        3. If the task requires multiple different types of functionality, organize apps into logical sets with purposes

        Tasks that typically require apps:
        - Searching the web for information
        - Sending emails
        - Creating or editing documents
        - Managing calendars or schedules
        - Processing data or files
        - Interacting with social media
        - Making API calls to external services

        Tasks that typically don't require apps:
        - General reasoning and analysis
        - Mathematical calculations
        - Text summarization or analysis
        - Providing explanations or educational content
        - Planning and organization
        - Creative writing or brainstorming
        - Logical problem solving

        For complex tasks that require multiple types of functionality, organize apps into logical sets with clear purposes.
        For example, if a task requires both email and search functionality, you might create:
        - app_sets: [
            {"purpose": "Email communication", "apps": ["outlook", "google-mail"], "choice": true},
            {"purpose": "Web search", "apps": ["serpapi", "tavily"], "choice": false}
          ]

        Each app set should have:
        - purpose: A clear description of what this set of apps is for
        - apps: List of app IDs that serve this purpose
        - choice: Boolean indicating if user choice is needed (true) or all apps should be auto-loaded (false)

        Set choice to True if the user should choose from the apps in that set.
        Set choice to False if all apps in that set should be automatically loaded.

        Analyze the given task and determine if it requires an external app or can be completed through general reasoning.
        If it requires an app, select the most relevant apps from the available list.
        If the task requires multiple different types of functionality, organize apps into logical sets with clear purposes.

        If an app has previously been loaded, it should not be loaded again.
        """
        logger.debug("AutoAgent initialized successfully")
        self._graph = self._build_graph()

    def _build_graph(self):
        graph_builder = StateGraph(State)

        async def task_analyzer(state: State):
            """Analyze the task and determine if choice is needed"""
            response = await self.run(state["messages"])

            # Get current loaded_apps from state, defaulting to empty list if not present
            current_loaded_apps = state.get("loaded_apps", [])

            # Check if the response is choice data (dict) or a direct response (str)
            if isinstance(response, dict) and "requires_app" in response:
                # This is choice data - store it and ask for user input
                app_sets = response.get("app_sets", [])

                # Use LLM to generate a natural choice message
                choice_message = await self._generate_choice_message(app_sets, response["task"])

                # Update loaded_apps with any auto-selected apps from the choice data
                if "auto_selected_apps" in response:
                    current_loaded_apps.extend(response["auto_selected_apps"])

                # Return the choice message and signal to go to choice node
                return {
                    "messages": [AIMessage(content=choice_message)],
                    "loaded_apps": current_loaded_apps,
                    "choice_data": response,
                }
            else:
                # This is a direct response
                return {
                    "messages": [AIMessage(content=str(response))],
                    "loaded_apps": current_loaded_apps,
                    "choice_data": None,
                }

        async def choice_handler(state: State):
            """Handle user choice input and execute with selected apps"""
            user_input = state["messages"][-1].content

            # Get current loaded_apps from state, defaulting to empty list if not present
            current_loaded_apps = state.get("loaded_apps", [])
            choice_data = state.get("choice_data")

            if not choice_data:
                return {
                    "messages": [AIMessage(content="No choice data available. Please try again.")],
                    "loaded_apps": current_loaded_apps,
                    "choice_data": None,
                }

            # Parse user choices using LLM
            user_choices = await self.parse_user_choices_with_llm(user_input, choice_data)

            # Execute with the parsed choices
            result = await self.run(state["messages"], user_choices=user_choices, loaded_apps=current_loaded_apps)

            # Update loaded_apps with the user-selected apps
            current_loaded_apps.extend(user_choices)

            return {
                "messages": [AIMessage(content=str(result))],
                "loaded_apps": current_loaded_apps,
                "choice_data": None,
            }

        graph_builder.add_node("task_analyzer", task_analyzer)
        graph_builder.add_node("choice_handler", choice_handler)

        # Add conditional edge from START to task_analyzer or choice_handler
        def route_from_start(state: State):
            # Check if we have stored choice data (indicating we need to handle choices)
            if state.get("choice_data") is not None:
                return "choice_handler"
            else:
                return "task_analyzer"

        graph_builder.add_conditional_edges(START, route_from_start)
        graph_builder.add_edge("task_analyzer", END)
        graph_builder.add_edge("choice_handler", END)

        return graph_builder.compile(checkpointer=self.memory)

    @property
    def graph(self):
        return self._graph

    async def stream(self, thread_id: str, user_input: str):
        async for event, metadata in self.graph.astream(
            {"messages": [{"role": "user", "content": user_input}]},
            config={"configurable": {"thread_id": thread_id}},
            stream_mode="messages",
        ):
            logger.info(f"Stream event: {event}")
            logger.info(f"Stream metadata: {metadata}")
            if "tags" in metadata and "quiet" in metadata["tags"]:
                pass
            else:
                event = cast(AIMessageChunk, event)
                yield event

    async def get_app_details(self, app_ids: list[str]) -> list[dict]:
        """Get detailed information about apps for better choice presentation"""
        app_details = []

        for app_id in app_ids:
            try:
                # Get app info from platform manager
                app_info = await self.platform_manager.get_app_details(app_id)
                app_details.append(app_info)
            except Exception as e:
                logger.error(f"Error getting details for app {app_id}: {e}")
                app_details.append(
                    {
                        "id": app_id,
                        "name": app_id,
                        "description": "Error loading details",
                        "category": "Unknown",
                        "available": True,
                    }
                )

        return app_details

    async def get_app_choice_data(self, app_sets: list[AppSet], messages: list[BaseMessage]) -> dict:
        """Get app choice data for frontend display"""
        task = messages[-1].content
        logger.info(f"Preparing app choice data for task: {task}")

        choice_data = {"task": task, "app_sets": []}

        # Load auto-selected apps immediately
        auto_selected_apps = []

        for set_index, app_set in enumerate(app_sets, 1):
            # Get detailed information about the apps in this set
            app_details = await self.get_app_details(app_set.apps)
            available_apps = [app for app in app_details if app.get("available", False)]

            if not available_apps:
                logger.warning(f"No available apps found in set {set_index}")
                continue

            if len(available_apps) == 1:
                # Only one available app, use it
                selected = available_apps[0]["id"]
                logger.info(f"Only one available app in set {set_index}: {selected}")
                auto_selected_apps.append(selected)
                continue

            if not app_set.choice:
                # Automatically load all apps in this set
                selected_apps = [app["id"] for app in available_apps]
                selected_names = [app["name"] for app in available_apps]
                logger.info(f"Automatically loading all apps in set {set_index}: {', '.join(selected_names)}")
                auto_selected_apps.extend(selected_apps)
                continue

            # Add this set to choice data for frontend
            set_data = {
                "set_index": set_index,
                "purpose": app_set.purpose,
                "apps": available_apps,
                "needs_choice": app_set.choice,
            }
            choice_data["app_sets"].append(set_data)

        # Load auto-selected apps immediately
        if auto_selected_apps:
            logger.info(f"Loading auto-selected apps: {', '.join(auto_selected_apps)}")
            await self._load_actions_for_apps(auto_selected_apps)

        logger.info(
            f"Prepared choice data with {len(choice_data['app_sets'])} sets and {len(auto_selected_apps)} auto-selected apps"
        )

        # Add auto-selected apps to the choice data for state tracking
        choice_data["auto_selected_apps"] = auto_selected_apps

        return choice_data

    async def _generate_choice_message(self, app_sets: list[dict], task: str) -> str:
        """Use LLM to generate a natural choice message for app selection"""
        if not app_sets:
            return "I need to load some apps to help with your request."

        # Format app sets for the LLM
        app_sets_info = []
        for i, app_set in enumerate(app_sets, 1):
            purpose = app_set.get("purpose", f"Set {i}")
            apps_info = []
            for app in app_set.get("apps", []):
                app_name = app.get("name", app.get("id"))
                app_desc = app.get("description", "No description")
                apps_info.append(f"- {app_name}: {app_desc}")

            app_sets_info.append(f"{purpose}:\n" + "\n".join(apps_info))

        app_sets_text = "\n\n".join(app_sets_info)

        prompt = f"""You are an agent capable of performing different actions to help the user. The user has asked you to perform a task, however, that is possible using multiple different apps. The task is:
        {task}
        The user has the following apps available to them, for performing the task they have asked for:

{app_sets_text}
The above may contain multiple sets of apps, each with a different purpose for performing the task. Now draft a message asking the user to select apps from each of these sets.
Be friendly and concise, but list each set of apps clearly. Do not return any other text than the question to be asked to the user, since it will be directly sent to the user. That is, do not start with "Here is the message to be sent to the user:" or anything like that."""

        try:
            response = await self.llm_quiet.ainvoke(prompt)
            return response.content
        except Exception as e:
            logger.error(f"Failed to generate choice message with LLM: {e}")
            # Fallback to a simple message
            if len(app_sets) == 1:
                purpose = app_sets[0].get("purpose", "this task")
                return (
                    f"I need to know which app you'd prefer to use for {purpose}. Please choose from the options above."
                )
            else:
                return "I need to load some apps to help with your request. Please let me know which apps you'd like me to use for each category."

    # TODO: Use a proper handler for this, the ui is going to send a proper json with choices

    async def parse_user_choices_with_llm(self, user_input: str, choice_data: dict) -> list[str]:
        """Use LLM to parse user choice input and return a list of selected app IDs"""
        logger.info(f"Using LLM to parse user choices: {user_input}")

        # Create a prompt for the LLM to parse the user's choice
        available_apps = []
        for i, app_set in enumerate(choice_data.get("app_sets", []), 1):
            purpose = app_set.get("purpose", f"Set {i}")
            available_apps.append(f"\n{purpose}:")
            for app in app_set.get("apps", []):
                available_apps.append(
                    f"  - {app.get('name', app.get('id'))} (ID: {app.get('id')}) - {app.get('description', 'No description')}"
                )

        prompt = f"""
        You are a choice parser. The user has been asked to choose from the following app sets:

        Available apps:
        {chr(10).join(available_apps)}

        The user responded with: "{user_input}"

        Please parse their response and extract their choices as a simple list of app IDs.

        Rules:
        1. Return only the app IDs that the user selected
        2. If the user says "all" or "everything", include all apps from that set
        3. If the user says "none" or "skip", don't include that set
        4. Match app names as closely as possible to the available apps
        5. If the user's response is unclear, make your best guess based on context
        6. Return only the app IDs, not the full names
        """

        try:
            # Use structured output with Pydantic model
            structured_llm = self.llm_quiet.with_structured_output(UserChoices)
            parsed_choices = await structured_llm.ainvoke(prompt)

            logger.info(f"LLM parsed choices: {parsed_choices}")
            return parsed_choices.user_choices

        except Exception as e:
            logger.error(f"Failed to parse user choices with LLM: {e}")
            # Fallback to empty list
            return []

    async def load_action_for_app(self, app_id):
        """Load actions for an app using the platform manager"""
        await self.platform_manager.load_actions_for_app(app_id, self.tool_manager)

    async def analyze_task_and_select_apps(
        self,
        task: str,
        available_apps: list[dict],
        messages: list[BaseMessage] = None,
        loaded_apps: list[str] | None = None,
    ) -> TaskAnalysis:
        """Combined task analysis and app selection to reduce LLM calls"""
        logger.info(f"Analyzing task and selecting apps: {task}")

        # Handle mutable default argument
        if loaded_apps is None:
            loaded_apps = []

        # Get conversation context from messages
        context_summary = ""

        if messages and len(messages) > 1:  # More than just the current task
            # Create a summary of previous conversation context
            previous_messages = messages[:-1]  # Exclude current task
            context_messages = []

            for msg in previous_messages[-5:]:  # Last 5 messages for context
                if isinstance(msg, HumanMessage):
                    context_messages.append(f"User: {msg.content}")
                elif isinstance(msg, AIMessage):
                    context_messages.append(f"Assistant: {msg.content[:200]}...")  # Truncate long responses

            if context_messages:
                context_summary = "\n\nPrevious conversation context:\n" + "\n".join(context_messages)
                logger.debug(f"Adding conversation context: {len(context_messages)} previous messages")

        prompt = f"""
        {self.task_analysis_prompt}

        Task: {task}
        Available apps: {available_apps}{context_summary}

        Determine if this task requires an external application or can be completed through general reasoning and knowledge.
        If it requires an app, select the most relevant apps from the available list.
        If the task requires multiple different types of functionality, organize apps into logical sets with clear purposes using the app_sets field.

        Consider the conversation context when making your decision. For example:
        - If the user previously mentioned specific apps or tools, prefer those
        - If the conversation is about a specific topic, choose apps relevant to that topic
        - If the user is continuing a previous task, maintain consistency in app selection. You do not need to load the same app again.
        The set of loaded apps is {loaded_apps}
        """

        # Use structured output with Pydantic model
        structured_llm = self.llm_quiet.with_structured_output(TaskAnalysis)
        response = await structured_llm.ainvoke(prompt)
        logger.debug(f"Task analysis response: {response}")

        logger.info(f"Task requires app: {response.requires_app}")
        logger.info(f"Reasoning: {response.reasoning}")
        if response.requires_app:
            logger.info(f"App sets: {response.app_sets}")

        return response

    async def _load_actions_for_apps(self, selected_apps: list[str]) -> None:
        """Load actions for a list of apps"""
        for app_id in selected_apps:
            logger.info(f"Loading actions for app: {app_id}")
            try:
                await self.load_action_for_app(app_id)
                logger.info(f"Successfully loaded actions for app: {app_id}")
            except Exception as e:
                logger.error(f"Failed to load actions for app {app_id}: {e}")
                continue

    async def _execute_with_selected_apps(self, selected_apps: list[str], messages: list[BaseMessage] = None) -> str:
        """Load selected apps and execute the task, falling back to general reasoning if needed"""
        if not selected_apps:
            logger.warning("No apps selected, using general reasoning")
            return await self._execute_task_with_agent(messages or [])

        await self._load_actions_for_apps(selected_apps)

        logger.info(f"Successfully loaded actions for {len(selected_apps)} apps: {', '.join(selected_apps)}")
        return await self._execute_task_with_agent(messages or [])

    async def _execute_task_with_agent(self, messages: list[BaseMessage]) -> str:
        """Execute a task using the current agent with provided messages"""
        agent = self.get_agent()
        results = await agent.ainvoke({"messages": messages})
        ai_message = results["messages"][-1]
        return ai_message.content

    def get_agent(self):
        """Get or create an agent with tools."""
        # Always create a new agent when requested or if no agent exists

        logger.info("Creating new agent with tools")
        tools = self.tool_manager.list_tools(format=ToolFormat.LANGCHAIN)
        logger.debug(f"Created agent with {len(tools)} tools")

        # Get current datetime and timezone information
        current_time = datetime.datetime.now()
        utc_time = datetime.datetime.now(datetime.UTC)
        timezone_info = f"Current local time: {current_time.strftime('%Y-%m-%d %H:%M:%S')} | UTC time: {utc_time.strftime('%Y-%m-%d %H:%M:%S')}"

        agent = create_react_agent(
            self.llm_tools,
            tools=tools,
            prompt=f"You are a helpful assistant that is given a list of actions for an app. You are also given a task. Use the tools to complete the task. Current time information: {timezone_info}. Additionally, the following instructions have been given by the user: {self.instructions}",
        )
        logger.info("Agent created successfully")

        return agent

    async def run(
        self, messages: list[BaseMessage], user_choices: list[str] | None = None, loaded_apps: list[str] | None = None
    ):
        # Extract task from the last message
        if not messages or len(messages) == 0:
            raise ValueError("No messages provided")

        # Handle mutable default argument
        if loaded_apps is None:
            loaded_apps = []

        task = messages[-1].content
        logger.info(f"Starting task execution: {task}")

        # If user_choices are provided, skip task analysis and execute directly
        if user_choices:
            logger.info("User choices provided, skipping task analysis")
            logger.info(f"User selected apps: {', '.join(user_choices)}")
            result = await self._execute_with_selected_apps(user_choices, messages)
            return result

        # Get all available apps from platform manager
        available_apps = await self.platform_manager.get_available_apps()

        logger.info(f"Found {len(available_apps)} available apps")

        # Analyze task and select apps
        task_analysis = await self.analyze_task_and_select_apps(task, available_apps, messages, loaded_apps)

        if not task_analysis.requires_app:
            logger.info("Task does not require an app, using general reasoning")
            return await self._execute_task_with_agent(messages or [])

        if not task_analysis.app_sets:
            logger.warning(f"No suitable app found for task: {task}")
            logger.info("Falling back to general reasoning for this task")
            return await self._execute_task_with_agent(messages or [])

        # Check if choices are required
        choice_data = await self.get_app_choice_data(task_analysis.app_sets, messages)
        choice_data["requires_app"] = True
        choice_data["reasoning"] = task_analysis.reasoning
        choice_data["task"] = task

        # If no choices are needed (all apps auto-selected), execute directly
        if not choice_data["app_sets"]:
            logger.info("No user choices required, auto-selected apps already loaded")
            return await self._execute_task_with_agent(messages)

        logger.info("User choices required, providing choice data")
        return choice_data


async def graph(config: RunnableConfig):
    # Get API key for the model
    api_key = os.getenv("AUTO_AGENT_API_KEY", "test_api_key")
    if api_key == "test_api_key":
        api_key = input("Enter your API key: ")

    # Create platform manager for AutoAgent
    platform_manager = AgentRPlatformManager(api_key=api_key)

    # Create AutoAgent with the configured model and system prompt
    auto_agent = AutoAgent(name="Auto Agent", instructions="", model="gpt-4.1", platform_manager=platform_manager)

    # Return the AutoAgent's graph
    return auto_agent.graph


if __name__ == "__main__":
    # Test the AutoAgent

    # Get API key from environment or use a placeholder
    api_key = os.getenv("AUTO_AGENT_API_KEY", "test_api_key")
    if api_key == "test_api_key":
        api_key = input("Enter your API key: ")

    # Create platform manager
    platform_manager = AgentRPlatformManager(api_key=api_key)
    want_instructions = input("Do you want to add a system prompt/instructions? (Y/N)")
    instructions = "" if want_instructions.upper() == "N" else input("Enter your instructions/system prompt: ")

    agent = AutoAgent("Auto Agent", instructions, "gpt-4.1", platform_manager=platform_manager)

    print("AutoAgent created successfully!")
    print(f"Agent name: {agent.name}")
    print(f"Agent instructions: {agent.instructions}")
    print(f"Agent model: {agent.model}")

    asyncio.run(agent.run_interactive())
