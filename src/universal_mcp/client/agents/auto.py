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
    apps_loaded: list[str]
    needs_choice: bool


class TaskAnalysis(BaseModel):
    """Combined analysis of task type and app requirements"""
    requires_app: bool
    reasoning: str
    app_sets: List[List[str]] = []  # Multiple sets of app choices
    choice: List[bool] = []  # Whether user choice is needed for each app set


class UserChoices(BaseModel):
    """Structured output for parsing user choice responses"""
    auto_selected: List[str] = []  # Apps that were auto-selected
    user_choices: dict[str, List[str]] = {}  # User choices by set number


class AutoAgent(BaseAgent):
    def __init__(
        self, 
        name: str, 
        instructions: str, 
        model: str, 
        api_key: str, 
        app_limit: int = 20, 
        action_limit: int = 10,
        conversation_history: List[BaseMessage] = [],
        loaded_apps: List[str] = []
    ):
        super().__init__(name, instructions, model)
        self.api_key = api_key
        self.client = AgentrClient(api_key=self.api_key)
        self.llm = get_llm(model)
        self.tool_manager = ToolManager()
        
        # Configuration limits
        self.app_limit = app_limit
        self.action_limit = action_limit

        self._conversation_history = conversation_history
        self._loaded_apps = loaded_apps

        self._agent: Optional[Any] = None
        self._current_tools_hash: Optional[str] = None
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

        async def chatbot(state: State):
            response = await self.run(state["messages"][-1].content)
            loaded_apps = self.get_loaded_apps()
            
            # Check if the response is choice data (dict) or a direct response (str)
            if isinstance(response, dict) and "requires_app" in response:
                # This is choice data - store it and ask for user input
                choice_message = f"I need to load some apps to help with your request. Please provide your choices for the following app sets:\n\n"
                
                for i, app_set in enumerate(response.get("app_sets", []), 1):
                    choice_message += f"Set {i}:\n"
                    for app in app_set.get("apps", []):
                        choice_message += f"  - {app.get('name', app.get('id'))}: {app.get('description', 'No description')}\n"
                    choice_message += "\n"
                
                if response.get("auto_selected"):
                    choice_message += f"Auto-selected apps: {', '.join(response['auto_selected'])}\n\n"
                                
                # Store the choice data for the choice node to use
                self._last_choice_data = response
                
                # Return the choice message and signal to go to choice node
                return {"messages": [AIMessage(content=choice_message)], "apps_loaded": loaded_apps, "needs_choice": True}
            else:
                # This is a direct response
                return {"messages": [AIMessage(content=str(response))], "apps_loaded": loaded_apps, "needs_choice": False}

        async def choice_handler(state: State):
            """Handle user choice input and execute with selected apps"""
            user_input = state["messages"][-1].content
            
            if not self._last_choice_data:
                return {"messages": [AIMessage(content="No choice data available. Please try again.")], "apps_loaded": self.get_loaded_apps(), "needs_choice": False}
            
            # Parse user choices using LLM
            frontend_choices = await self.parse_user_choices_with_llm(user_input, self._last_choice_data)
            
            # Execute with the parsed choices
            result = await self.run(user_input, frontend_choices)
            
            # Clear the stored choice data
            self._last_choice_data = None
            
            return {"messages": [AIMessage(content=str(result))], "apps_loaded": self.get_loaded_apps(), "needs_choice": False}

           

        graph_builder.add_node("chatbot", chatbot)
        graph_builder.add_node("choice_handler", choice_handler)
        
        # Add edges
        graph_builder.add_edge(START, "chatbot")
        
        # Add conditional edge from chatbot to choice_handler or END
        def route_after_chatbot(state: State):
            if state.get("needs_choice", False):
                return "choice_handler"
            else:
                return END
        
        graph_builder.add_conditional_edges("chatbot", route_after_chatbot)
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

    async def get_app_choice_data(self, app_sets: List[List[str]], choice_flags: List[bool], task: str) -> dict:
        """Get app choice data for frontend display"""
        logger.info(f"Preparing app choice data for task: {task}")
        
        choice_data = {
            "task": task,
            "app_sets": [],
            "auto_selected": []
        }
        
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
                choice_data["auto_selected"].append(selected)
                continue
            
            if not needs_choice:
                # Automatically load all apps in this set
                selected_apps = [app["id"] for app in available_apps]
                selected_names = [app["name"] for app in available_apps]
                logger.info(f"Automatically loading all apps in set {set_index}: {', '.join(selected_names)}")
                choice_data["auto_selected"].extend(selected_apps)
                continue
            
            # Add this set to choice data for frontend
            set_data = {
                "set_index": set_index,
                "apps": available_apps,
                "needs_choice": needs_choice
            }
            choice_data["app_sets"].append(set_data)
        
        logger.info(f"Prepared choice data with {len(choice_data['app_sets'])} sets and {len(choice_data['auto_selected'])} auto-selected apps")
        return choice_data

    async def process_frontend_choices(self, frontend_choices: dict, task: str) -> List[str]:
        """Process app choices from frontend"""
        logger.info(f"Processing frontend choices for task: {task}")
        
        all_selected_apps = []
        
        # Add auto-selected apps
        if "auto_selected" in frontend_choices:
            all_selected_apps.extend(frontend_choices["auto_selected"])
            logger.info(f"Auto-selected apps: {frontend_choices['auto_selected']}")
        
        # Process user choices from frontend
        if "user_choices" in frontend_choices:
            for set_index, selected_apps in frontend_choices["user_choices"].items():
                logger.info(f"User selected for set {set_index}: {selected_apps}")
                all_selected_apps.extend(selected_apps)
        
        logger.info(f"Total selected apps from frontend: {', '.join(all_selected_apps)}")
        return all_selected_apps

    async def parse_user_choices_with_llm(self, user_input: str, choice_data: dict) -> dict:
        """Use LLM to parse user choice input and convert to frontend_choices format"""
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

        Auto-selected apps: {', '.join(choice_data.get('auto_selected', []))}

        The user responded with: "{user_input}"

        Please parse their response and extract their choices.

        Rules:
        1. Include all auto-selected apps in the auto_selected array
        2. For each set the user chose from, add an entry to user_choices with the set number as key
        3. If the user says "all" or "everything", include all apps from that set
        4. If the user says "none" or "skip", don't include that set
        5. Match app names as closely as possible to the available apps
        6. If the user's response is unclear, make your best guess based on context
        """
        
        try:
            # Use structured output with Pydantic model
            structured_llm = self.llm.with_structured_output(UserChoices)
            parsed_choices = await structured_llm.ainvoke(prompt)
            
            logger.info(f"LLM parsed choices: {parsed_choices}")
            return parsed_choices.model_dump()
            
        except Exception as e:
            logger.error(f"Failed to parse user choices with LLM: {e}")
            # Fallback to auto-selected apps only
            return {
                "auto_selected": choice_data.get("auto_selected", []),
                "user_choices": {}
            }

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
        
        # Track the loaded app
        self._loaded_apps.append(app_name)
        logger.info(f"Successfully loaded all {len(app_actions)} actions for app: {app_name}")

    async def analyze_task_and_select_apps(self, task: str, available_apps: List[dict]) -> TaskAnalysis:
        """Combined task analysis and app selection to reduce LLM calls"""
        logger.info(f"Analyzing task and selecting apps: {task}")
        
        # Get conversation context
        conversation_history = self.get_conversation_history()
        context_summary = ""
        
        if len(conversation_history) > 1:  # More than just the current task
            # Create a summary of previous conversation context
            previous_messages = conversation_history[:-1]  # Exclude current task
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
        
    async def _load_actions_for_apps(self, selected_apps: List[str]) -> List[str]:
        """Load actions for a list of apps and return successfully loaded app names"""
        loaded_apps = []
        for app_name in selected_apps:
            logger.info(f"Loading actions for app: {app_name}")
            try:
                await self.load_action_for_app(app_name)
                loaded_apps.append(app_name)
                logger.info(f"Successfully loaded actions for app: {app_name}")
            except Exception as e:
                logger.error(f"Failed to load actions for app {app_name}: {e}")
                continue
        return loaded_apps

    async def _execute_with_selected_apps(self, selected_apps: List[str]) -> str:
        """Load selected apps and execute the task, falling back to general reasoning if needed"""
        if not selected_apps:
            logger.warning("No apps selected, using general reasoning")
            return await self._execute_task_with_agent()
        
        loaded_apps = await self._load_actions_for_apps(selected_apps)
        
        if not loaded_apps:
            logger.warning("Failed to load actions for any app, using general reasoning")
            return await self._execute_task_with_agent()
        
        logger.info(f"Successfully loaded actions for {len(loaded_apps)} apps: {', '.join(loaded_apps)}")
        return await self._execute_task_with_agent()

    async def _execute_task_with_agent(self) -> str:
        """Execute a task using the current agent with conversation history"""
        agent = self.get_agent()
        messages = self.get_conversation_history()
        results = await agent.ainvoke({"messages": messages})
        ai_message = results["messages"][-1]
        self.add_to_conversation_history(ai_message)
        return ai_message.content

    def _get_tools_hash(self) -> str:
        """Generate a hash of the current tools to detect changes"""
        tools = self.tool_manager.list_tools(format=ToolFormat.LANGCHAIN)
        tools_info = [(tool.name, tool.description) for tool in tools]
        return str(hash(str(tools_info)))
    
    def get_agent(self, force_recreate: bool = True):
        """Get or create an agent with tools. Reuses existing agent if tools haven't changed."""
        current_tools_hash = self._get_tools_hash()
        
        # Check if we need to recreate the agent
        if (force_recreate or 
            self._agent is None or 
            self._current_tools_hash != current_tools_hash):
            
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
            self._current_tools_hash = current_tools_hash
            logger.info("Agent created successfully")
        else:
            logger.debug("Reusing existing agent")
        
        return self._agent
    
    def add_to_conversation_history(self, message: BaseMessage):
        """Add a message to the conversation history"""
        self._conversation_history.append(message)
        logger.debug(f"Added message to history. Total messages: {len(self._conversation_history)}")
    
    def get_conversation_history(self) -> List[BaseMessage]:
        """Get the current conversation history"""
        return self._conversation_history.copy()
    
    def clear_conversation_history(self):
        """Clear the conversation history"""
        self._conversation_history.clear()
        logger.info("Conversation history cleared")
    
    def reset_agent(self):
        """Reset the agent and clear conversation history"""
        self._agent = None
        self._current_tools_hash = None
        self._loaded_apps.clear()
        self._last_choice_data = None
        self.clear_conversation_history()
        logger.info("Agent reset successfully")
    
    def get_loaded_apps(self) -> List[str]:
        """Get the list of currently loaded apps"""
        return self._loaded_apps.copy()
    
    def get_conversation_stats(self) -> dict:
        """Get statistics about the current conversation"""
        human_messages = [msg for msg in self._conversation_history if isinstance(msg, HumanMessage)]
        ai_messages = [msg for msg in self._conversation_history if isinstance(msg, AIMessage)]
        
        return {
            "total_messages": len(self._conversation_history),
            "human_messages": len(human_messages),
            "ai_messages": len(ai_messages),
            "loaded_apps": len(self._loaded_apps),
            "loaded_app_names": self._loaded_apps.copy(),
            "has_agent": self._agent is not None
        }
    
    def is_conversation_empty(self) -> bool:
        """Check if the conversation history is empty"""
        return len(self._conversation_history) == 0

    async def run(self, task, frontend_choices: dict = None):
        logger.info(f"Starting task execution: {task}")
        
        # Add the new task to conversation history
        if not frontend_choices:
            human_message = HumanMessage(content=task)
            self.add_to_conversation_history(human_message)
        
        # If frontend_choices are provided, skip task analysis and execute directly
        if frontend_choices:
            logger.info("Frontend choices provided, skipping task analysis")
            selected_apps = await self.process_frontend_choices(frontend_choices, task)
            return await self._execute_with_selected_apps(selected_apps)
        
        # Get all available apps
        all_apps = self.client.list_all_apps()
        available_apps = [
            {"id": app["id"], "name": app["name"], "description": app["description"]} 
            for app in all_apps 
            if app.get("available", False)
        ]
        
        logger.info(f"Found {len(available_apps)} available apps")
        
        # Analyze task and select apps
        task_analysis = await self.analyze_task_and_select_apps(task, available_apps)
        
        if not task_analysis.requires_app:
            logger.info(f"Task does not require an app, using general reasoning")
            return await self._execute_task_with_agent()
        
        if not task_analysis.app_sets:
            logger.warning(f"No suitable app found for task: {task}")
            logger.info(f"Falling back to general reasoning for this task")
            return await self._execute_task_with_agent()
        
        # Check if choices are required
        choice_data = await self.get_app_choice_data(task_analysis.app_sets, task_analysis.choice, task)
        choice_data["requires_app"] = True
        choice_data["reasoning"] = task_analysis.reasoning
        
        # If no choices are needed (all apps auto-selected), execute directly
        if not choice_data["app_sets"] and choice_data["auto_selected"]:
            logger.info("No user choices required, executing with auto-selected apps")
            selected_apps = choice_data["auto_selected"]
            
            return await self._execute_with_selected_apps(selected_apps)
        
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
        "openrouter/auto",
        api_key=api_key
    )
    
    print("AutoAgent created successfully!")
    print(f"Agent name: {agent.name}")
    print(f"Agent instructions: {agent.instructions}")
    print(f"Agent model: {agent.model}")
    print(f"App limit: {agent.app_limit}")
    print(f"Action limit: {agent.action_limit}")
    print(f"Loaded apps: {agent.get_loaded_apps()}")
    print(f"Conversation empty: {agent.is_conversation_empty()}")
    
    # Test conversation stats
    stats = agent.get_conversation_stats()
    print(f"Conversation stats: {stats}")
    
    asyncio.run(agent.run_interactive())
