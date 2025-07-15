import asyncio
import datetime
from typing import Annotated, Any, List, Optional

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import create_react_agent
from loguru import logger
from pydantic import BaseModel
from typing_extensions import TypedDict

from universal_mcp.applications import app_from_slug
from universal_mcp.client.agents.base import BaseAgent
from universal_mcp.client.agents.llm import get_llm
from universal_mcp.integrations import AgentRIntegration
from universal_mcp.tools import ToolManager
from universal_mcp.tools.adapters import ToolFormat
from universal_mcp.utils.agentr import AgentrClient


class State(TypedDict):
    messages: Annotated[list, add_messages]
    loaded_apps: list[str]
    needs_choice: bool


class TaskAnalysis(BaseModel):
    """Combined analysis of task type and app requirements"""
    requires_app: bool
    reasoning: str
    app_sets: List[List[str]] = []  # Multiple sets of app choices
    choice: List[bool] = []  # Whether user choice is needed for each app set


class UserChoices(BaseModel):
    """Structured output for parsing user choice responses"""
    user_choices: List[str] = []


class AutoAgent(BaseAgent):
    def __init__(
        self, 
        name: str, 
        instructions: str, 
        model: str, 
        api_key: str
    ):
        super().__init__(name, instructions, model)
        self.api_key = api_key
        self.client = AgentrClient(api_key=self.api_key)
        self.llm = get_llm(model)
        self.tool_manager = ToolManager()

        self._agent: Optional[Any] = None
        self._last_choice_data: Optional[dict] = None

        self.task_analysis_prompt = """You are a task analysis expert. Given a task description and available apps, determine:

        1. Whether the task requires an external application or can be handled through general reasoning
        2. If it requires an app, which apps are most relevant
        3. If the task requires multiple different types of functionality, organize apps into logical sets

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

        For complex tasks that require multiple types of functionality, organize apps into logical sets.
        For example, if a task requires both email and search functionality, you might create:
        - app_sets: [["outlook", "google-mail"], ["serpapi", "tavily"]]
        - choice: [True, False] (user chooses email app, all search apps are loaded)
        
        The choice field should be an array of booleans with the same length as app_sets.
        Set choice[i] to True if the user should choose from app_sets[i].
        Set choice[i] to False if all apps in app_sets[i] should be automatically loaded.

        Analyze the given task and determine if it requires an external app or can be completed through general reasoning.
        If it requires an app, select the most relevant apps from the available list.
        If the task requires multiple different types of functionality, organize apps into logical sets.
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
                choice_message = f"I need to load some apps to help with your request. Please provide your choices for the following app sets:\n\n"
                
                for i, app_set in enumerate(response.get("app_sets", []), 1):
                    choice_message += f"Set {i}:\n"
                    for app in app_set.get("apps", []):
                        choice_message += f"  - {app.get('name', app.get('id'))}: {app.get('description', 'No description')}\n"
                    choice_message += "\n"
                
                # Store the choice data for the choice node to use
                self._last_choice_data = response
                
                # Update loaded_apps with any auto-selected apps from the choice data
                if "auto_selected_apps" in response:
                    current_loaded_apps.extend(response["auto_selected_apps"])
                
                # Return the choice message and signal to go to choice node
                return {"messages": [AIMessage(content=choice_message)], "loaded_apps": current_loaded_apps, "needs_choice": True}
            else:
                # This is a direct response
                return {"messages": [AIMessage(content=str(response))], "loaded_apps": current_loaded_apps, "needs_choice": False}

        async def choice_handler(state: State):
            """Handle user choice input and execute with selected apps"""
            user_input = state["messages"][-1].content
            
            # Get current loaded_apps from state, defaulting to empty list if not present
            current_loaded_apps = state.get("loaded_apps", [])
            
            if not self._last_choice_data:
                return {"messages": [AIMessage(content="No choice data available. Please try again.")], "loaded_apps": current_loaded_apps, "needs_choice": False}
            
            # Parse user choices using LLM
            user_choices = await self.parse_user_choices_with_llm(user_input, self._last_choice_data)
            
            # Execute with the parsed choices
            result = await self.run(state["messages"], user_choices=user_choices)
            
            # Update loaded_apps with the user-selected apps
            current_loaded_apps.extend(user_choices)
            
            # Clear the stored choice data
            self._last_choice_data = None
            
            return {"messages": [AIMessage(content=str(result))], "loaded_apps": current_loaded_apps, "needs_choice": False}

        graph_builder.add_node("task_analyzer", task_analyzer)
        graph_builder.add_node("choice_handler", choice_handler)
        
        # Add conditional edge from START to task_analyzer or choice_handler
        def route_from_start(state: State):
            # Check if we have stored choice data (indicating we need to handle choices)
            if self._last_choice_data is not None:
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

    async def get_app_details(self, app_ids: List[str]) -> List[dict]:
        """Get detailed information about apps for better choice presentation"""
        app_details = []
        
        for app_id in app_ids:
            try:
                # Try to get app info from AgentR client
                app_info = self.client.fetch_app(app_id)
                app_details.append({
                    "id": app_info.get("id"),
                    "name": app_info.get("name"),
                    "description": app_info.get("description"),
                    "category": app_info.get("category"),
                    "available": app_info.get("available", True)
                })
            except Exception as e:
                logger.error(f"Error getting details for app {app_id}: {e}")
                app_details.append({
                    "id": app_id,
                    "name": app_id,
                    "description": "Error loading details",
                    "category": "Unknown",
                    "available": True
                })
        
        return app_details

    async def get_app_choice_data(self, app_sets: List[List[str]], choice_flags: List[bool], messages: List[BaseMessage]) -> dict:
        """Get app choice data for frontend display"""
        task = messages[-1].content
        logger.info(f"Preparing app choice data for task: {task}")
        
        choice_data = {
            "task": task,
            "app_sets": []
        }
        
        # Load auto-selected apps immediately
        auto_selected_apps = []
        
        for set_index, (app_set, needs_choice) in enumerate(zip(app_sets, choice_flags), 1):
            # Get detailed information about the apps in this set
            app_details = await self.get_app_details(app_set)
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
            
            if not needs_choice:
                # Automatically load all apps in this set
                selected_apps = [app["id"] for app in available_apps]
                selected_names = [app["name"] for app in available_apps]
                logger.info(f"Automatically loading all apps in set {set_index}: {', '.join(selected_names)}")
                auto_selected_apps.extend(selected_apps)
                continue
            
            # Add this set to choice data for frontend
            set_data = {
                "set_index": set_index,
                "apps": available_apps,
                "needs_choice": needs_choice
            }
            choice_data["app_sets"].append(set_data)
        
        # Load auto-selected apps immediately
        if auto_selected_apps:
            logger.info(f"Loading auto-selected apps: {', '.join(auto_selected_apps)}")
            await self._load_actions_for_apps(auto_selected_apps)
        
        logger.info(f"Prepared choice data with {len(choice_data['app_sets'])} sets and {len(auto_selected_apps)} auto-selected apps")
        
        # Add auto-selected apps to the choice data for state tracking
        choice_data["auto_selected_apps"] = auto_selected_apps
        
        return choice_data


    async def parse_user_choices_with_llm(self, user_input: str, choice_data: dict) -> List[str]:
        """Use LLM to parse user choice input and return a list of selected app IDs"""
        logger.info(f"Using LLM to parse user choices: {user_input}")
        
        # Create a prompt for the LLM to parse the user's choice
        available_apps = []
        for i, app_set in enumerate(choice_data.get("app_sets", []), 1):
            for app in app_set.get("apps", []):
                available_apps.append(f"Set {i}: {app.get('name', app.get('id'))} ({app.get('description', 'No description')})")
        
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
            structured_llm = self.llm.with_structured_output(UserChoices)
            parsed_choices = await structured_llm.ainvoke(prompt)
            
            logger.info(f"LLM parsed choices: {parsed_choices}")
            return parsed_choices.user_choices
            
        except Exception as e:
            logger.error(f"Failed to parse user choices with LLM: {e}")
            # Fallback to empty list
            return []

    async def load_action_for_app(self, app_name):
        logger.info(f"Loading all actions for app: {app_name}")
         
        # Get all actions for the app
        app_actions = self.client.list_actions(app_name)
        
        if not app_actions:
            logger.warning(f"No actions available for app: {app_name}")
            return
        
        logger.debug(f"Found {len(app_actions)} actions for {app_name}")
        
        # Register all actions as tools
        app = app_from_slug(app_name)
        integration = AgentRIntegration(name=app_name, api_key=self.api_key, base_url="https://api.agentr.dev")
        app_instance = app(integration=integration)
        logger.debug(f"Registering all tools for app: {app_name}")
        self.tool_manager.register_tools_from_app(app_instance)
        
        logger.info(f"Successfully loaded all {len(app_actions)} actions for app: {app_name}")

    async def analyze_task_and_select_apps(self, task: str, available_apps: List[dict], messages: List[BaseMessage] = None) -> TaskAnalysis:
        """Combined task analysis and app selection to reduce LLM calls"""
        logger.info(f"Analyzing task and selecting apps: {task}")
        
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
        If the task requires multiple different types of functionality, organize apps into logical sets using the app_sets field.
        
        Consider the conversation context when making your decision. For example:
        - If the user previously mentioned specific apps or tools, prefer those
        - If the conversation is about a specific topic, choose apps relevant to that topic
        - If the user is continuing a previous task, maintain consistency in app selection. Include previous app selection if it is still relevant.
        """
        
        # Use structured output with Pydantic model
        structured_llm = self.llm.with_structured_output(TaskAnalysis)
        response = await structured_llm.ainvoke(prompt)
        logger.debug(f"Task analysis response: {response}")
        
        logger.info(f"Task requires app: {response.requires_app}")
        logger.info(f"Reasoning: {response.reasoning}")
        if response.requires_app:
            logger.info(f"App sets: {response.app_sets}")
            logger.info(f"Choice flags: {response.choice}")
        
        return response
        
    async def _load_actions_for_apps(self, selected_apps: List[str]) -> None:
        """Load actions for a list of apps"""
        for app_name in selected_apps:
            logger.info(f"Loading actions for app: {app_name}")
            try:
                await self.load_action_for_app(app_name)
                logger.info(f"Successfully loaded actions for app: {app_name}")
            except Exception as e:
                logger.error(f"Failed to load actions for app {app_name}: {e}")
                continue

    async def _execute_with_selected_apps(self, selected_apps: List[str], messages: List[BaseMessage] = None) -> str:
        """Load selected apps and execute the task, falling back to general reasoning if needed"""
        if not selected_apps:
            logger.warning("No apps selected, using general reasoning")
            return await self._execute_task_with_agent(messages or [])
        
        await self._load_actions_for_apps(selected_apps)
        
        logger.info(f"Successfully loaded actions for {len(selected_apps)} apps: {', '.join(selected_apps)}")
        return await self._execute_task_with_agent(messages or [])

    async def _execute_task_with_agent(self, messages: List[BaseMessage]) -> str:
        """Execute a task using the current agent with provided messages"""
        agent = self.get_agent()
        results = await agent.ainvoke({"messages": messages})
        ai_message = results["messages"][-1]
        return ai_message.content

    def get_agent(self, force_recreate: bool = True):
        """Get or create an agent with tools."""
        # Always create a new agent when requested or if no agent exists
        if force_recreate or self._agent is None:
            logger.info("Creating new agent with tools")
            tools = self.tool_manager.list_tools(format=ToolFormat.LANGCHAIN)
            logger.debug(f"Created agent with {len(tools)} tools")
            
            # Get current datetime and timezone information
            current_time = datetime.datetime.now()
            utc_time = datetime.datetime.now(datetime.UTC)
            timezone_info = f"Current local time: {current_time.strftime('%Y-%m-%d %H:%M:%S')} | UTC time: {utc_time.strftime('%Y-%m-%d %H:%M:%S')}"
            
            self._agent = create_react_agent(
                self.llm, 
                tools=tools, 
                prompt=f"You are a helpful assistant that is given a list of actions for an app. You are also given a task. Use the tools to complete the task. Current time information: {timezone_info}"
            )
            logger.info("Agent created successfully")
        else:
            logger.debug("Reusing existing agent")
        
        return self._agent
    


    async def run(self, messages: List[BaseMessage], user_choices: List[str] = None):
        # Extract task from the last message
        if not messages or len(messages) == 0:
            raise ValueError("No messages provided")
        
        task = messages[-1].content
        logger.info(f"Starting task execution: {task}")
        
        # If user_choices are provided, skip task analysis and execute directly
        if user_choices:
            logger.info("User choices provided, skipping task analysis")
            logger.info(f"User selected apps: {', '.join(user_choices)}")
            result = await self._execute_with_selected_apps(user_choices, messages)
            return result
        
        # Get all available apps
        all_apps = self.client.list_all_apps()
        available_apps = [
            {"id": app["id"], "name": app["name"], "description": app["description"]} 
            for app in all_apps 
            if app.get("available", False)
        ]
        
        logger.info(f"Found {len(available_apps)} available apps")
        
        # Analyze task and select apps
        task_analysis = await self.analyze_task_and_select_apps(task, available_apps, messages)
        
        if not task_analysis.requires_app:
            logger.info(f"Task does not require an app, using general reasoning")
            return await self._execute_task_with_agent(messages or [])
        
        if not task_analysis.app_sets:
            logger.warning(f"No suitable app found for task: {task}")
            logger.info(f"Falling back to general reasoning for this task")
            return await self._execute_task_with_agent(messages or [])
        
        # Check if choices are required
        choice_data = await self.get_app_choice_data(task_analysis.app_sets, task_analysis.choice, messages)
        choice_data["requires_app"] = True
        choice_data["reasoning"] = task_analysis.reasoning
        
        # If no choices are needed (all apps auto-selected), execute directly
        if not choice_data["app_sets"]:
            logger.info("No user choices required, auto-selected apps already loaded")
            return await self._execute_task_with_agent(messages)
        
        logger.info("User choices required, providing choice data")
        return choice_data


if __name__ == "__main__":
    # Test the AutoAgent
    import os
    
    # Get API key from environment or use a placeholder
    api_key = os.getenv("AUTO_AGENT_API_KEY", "test_api_key")
    if api_key == "test_api_key":
        api_key = input("Enter your API key: ")
    
    agent = AutoAgent(
        "Auto Agent", 
        "You are a helpful assistant", 
        "gpt-4.1",
        api_key=api_key
    )
    
    print("AutoAgent created successfully!")
    print(f"Agent name: {agent.name}")
    print(f"Agent instructions: {agent.instructions}")
    print(f"Agent model: {agent.model}")
    
    asyncio.run(agent.run_interactive())
