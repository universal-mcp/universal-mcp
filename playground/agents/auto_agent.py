import json
import asyncio
import aiohttp
from contextlib import asynccontextmanager
from typing import Any, List

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from loguru import logger
from pydantic import BaseModel

from universal_mcp.applications import app_from_slug
from universal_mcp.tools.adapters import ToolFormat
from universal_mcp.utils.agentr import AgentrClient
from universal_mcp.tools import ToolManager
from universal_mcp.integrations import AgentRIntegration



class TaskAnalysis(BaseModel):
    """Combined analysis of task type and app requirements"""
    requires_app: bool
    reasoning: str
    app_sets: List[List[str]] = []  # Multiple sets of app choices
    choice: List[bool] = []  # Whether user choice is needed for each app set








class AutoAgent:
    def __init__(self, api_key: str, api_base_url: str = "http://localhost:8000"):
        logger.info("Initializing AutoAgent")
        self.api_key = api_key
        self.client = AgentrClient(api_key=self.api_key)
        self.llm = ChatOpenAI(model="gpt-4.1")
        self.tool_manager = ToolManager()


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
        self.api_base_url = api_base_url
        logger.debug("AutoAgent initialized successfully")





    async def get_app_details(self, app_ids: List[str]) -> List[dict]:
        """Get detailed information about apps for better choice presentation"""
        app_details = []
        
        async with aiohttp.ClientSession() as session:
            for app_id in app_ids:
                try:
                    url = f"{self.api_base_url}/apps/{app_id}/"
                    async with session.get(url) as response:
                        if response.status == 200:
                            app_info = await response.json()
                            app_details.append({
                                "id": app_info.get("id"),
                                "name": app_info.get("name"),
                                "description": app_info.get("description"),
                                "category": app_info.get("category"),
                                "available": app_info.get("available", False)
                            })
                        else:
                            # Fallback to basic info
                            app_details.append({
                                "id": app_id,
                                "name": app_id,
                                "description": "No description available",
                                "category": "Unknown",
                                "available": True
                            })
                except Exception as e:
                    logger.error(f"Error getting details for app {app_id}: {e}")
                    app_details.append({
                        "id": app_id,
                        "name": app_id,
                        "description": "Error loading details",
                        "category": "Unknown",
                        "available": False
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

    async def handle_multiple_app_sets(self, app_sets: List[List[str]], choice_flags: List[bool], task: str) -> List[str]:
        """Handle user choice when multiple sets of apps are available"""
        logger.info(f"Multiple app sets available for task: {task}")
        
        all_selected_apps = []
        
        for set_index, (app_set, needs_choice) in enumerate(zip(app_sets, choice_flags), 1):
            logger.info(f"\n=== App Set {set_index} ===")
            
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
                all_selected_apps.append(selected)
                continue
            
            if not needs_choice:
                # Automatically load all apps in this set
                selected_apps = [app["id"] for app in available_apps]
                selected_names = [app["name"] for app in available_apps]
                logger.info(f"Automatically loading all apps in set {set_index}: {', '.join(selected_names)}")
                all_selected_apps.extend(selected_apps)
                continue
            
            # Present choices to user for this set
            logger.info(f"Available apps for set {set_index}:")
            for i, app in enumerate(available_apps, 1):
                logger.info(f"{i}. {app['name']} ({app['category']})")
                logger.info(f"   {app['description'][:100]}...")

            # Ask the user to choose for this set
            while True:
                try:
                    user_choice = input(f"Enter the numbers of the apps you want to use for set {set_index} (comma-separated, e.g., 1,3,5): ")
                    if user_choice.lower() == 'all':
                        selected_indices = list(range(len(available_apps)))
                    else:
                        # Parse comma-separated numbers
                        choice_indices = [int(x.strip()) - 1 for x in user_choice.split(',')]
                        selected_indices = choice_indices
                    
                    # Validate all selected indices
                    valid_selections = []
                    for idx in selected_indices:
                        if 0 <= idx < len(available_apps):
                            valid_selections.append(available_apps[idx]["id"])
                        else:
                            print(f"Invalid selection: {idx + 1}. Please enter numbers between 1 and {len(available_apps)}")
                            break
                    else:
                        # All selections are valid
                        selected_names = [available_apps[idx]["name"] for idx in selected_indices]
                        logger.info(f"User chose apps for set {set_index}: {', '.join(selected_names)}")
                        all_selected_apps.extend(valid_selections)
                        break
                        
                except ValueError:
                    print("Please enter valid numbers separated by commas (e.g., 1,3,5) or 'all' for all apps")
                except KeyboardInterrupt:
                    logger.info("User cancelled app selection")
                    return []
        
        logger.info(f"Total selected apps across all sets: {', '.join(all_selected_apps)}")
        return all_selected_apps

    async def process_frontend_choices(self, app_sets: List[List[str]], choice_flags: List[bool], frontend_choices: dict, task: str) -> List[str]:
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



    async def load_action_for_app(self, app_name, task, action_limit: int = 10):
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



    async def analyze_task_and_select_apps(self, task: str, available_apps: List[dict], interactive: bool = False) -> TaskAnalysis:
        """Combined task analysis and app selection to reduce LLM calls"""
        logger.info(f"Analyzing task and selecting apps: {task}")
        
        prompt = f"""
        {self.task_analysis_prompt}
        
        Task: {task}
        Available apps: {available_apps}
        
        Determine if this task requires an external application or can be completed through general reasoning and knowledge.
        If it requires an app, select the most relevant apps from the available list.
        If the task requires multiple different types of functionality, organize apps into logical sets using the app_sets field.
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
        
        return response

    async def execute_task_without_app(self, task: str) -> str:
        """Execute a task that doesn't require an external app using general reasoning"""
        logger.info(f"Executing task without app: {task}")
        
        # Create a simple agent without any tools for general reasoning
        agent = create_react_agent(
            self.llm, 
            tools=[], 
            prompt="You are a helpful assistant that can handle general reasoning, analysis, and knowledge-based tasks. Provide thoughtful, accurate, and helpful responses."
        )
        
        # Execute the task
        logger.info(f"Invoking general reasoning agent for task: {task}")
        results = await agent.ainvoke({"messages": [HumanMessage(content=task)]})
        ai_message = results["messages"][-1]
        
        logger.info("Task completed with general reasoning")
        return ai_message.content



    def get_agent(self):
        logger.info("Creating agent with tools")
        tools = self.tool_manager.list_tools(format=ToolFormat.LANGCHAIN)
        logger.debug(f"Created agent with {len(tools)} tools")
        agent = create_react_agent(self.llm, tools=tools, prompt="You are a helpful assistant that is given a list of actions for an app. You are also given a task. Use the tools to complete the task. ")
        return agent

    async def run(self, task, app_limit: int = 20, action_limit: int = 10, interactive: bool = False, frontend_choices: dict = None):
        logger.info(f"Starting task execution: {task}")
        
        # Get all available apps
        all_apps = self.client.list_all_apps()
        available_apps = [
            {"id": app["id"], "name": app["name"], "description": app["description"]} 
            for app in all_apps 
            if app.get("available", False)
        ]
        
        logger.info(f"Found {len(available_apps)} available apps")
        
        # Analyze task and select apps
        task_analysis = await self.analyze_task_and_select_apps(task, available_apps, interactive)
        
        if not task_analysis.requires_app:
            logger.info(f"Task does not require an app, using general reasoning")
            return await self.execute_task_without_app(task)
        
        if not task_analysis.app_sets:
            logger.warning(f"No suitable app found for task: {task}")
            logger.info(f"Falling back to general reasoning for this task")
            return await self.execute_task_without_app(task)
        
        # Handle app sets for user choice
        if frontend_choices:
            # Use frontend choices
            selected_apps = await self.process_frontend_choices(task_analysis.app_sets, task_analysis.choice, frontend_choices, task)
        else:
            # Use terminal-based choice
            selected_apps = await self.handle_multiple_app_sets(task_analysis.app_sets, task_analysis.choice, task)
        
        if not selected_apps:
            logger.warning("No apps selected, using general reasoning")
            return await self.execute_task_without_app(task)
        
        # Load actions for all selected apps
        loaded_apps = []
        for app_name in selected_apps:
            logger.info(f"Loading actions for app: {app_name}")
            try:
                await self.load_action_for_app(app_name, task, action_limit)
                loaded_apps.append(app_name)
                logger.info(f"Successfully loaded actions for app: {app_name}")
            except Exception as e:
                logger.error(f"Failed to load actions for app {app_name}: {e}")
                continue
        
        if not loaded_apps:
            logger.warning("Failed to load actions for any app, using general reasoning")
            return await self.execute_task_without_app(task)
        
        logger.info(f"Successfully loaded actions for {len(loaded_apps)} apps: {', '.join(loaded_apps)}")
        
        # Create agent with the loaded tools
        agent = self.get_agent()
        
        # Execute the task
        logger.info(f"Invoking agent for task: {task}")
        results = await agent.ainvoke({"messages": [HumanMessage(content=task)]})
        ai_message = results["messages"][-1]
        
        logger.info("Task completed successfully")
        return ai_message.content

    async def get_choice_data(self, task, app_limit: int = 20, interactive: bool = False) -> dict:
        """Get app choice data for frontend display"""
        logger.info(f"Getting choice data for task: {task}")
        
        # Get all available apps
        all_apps = self.client.list_all_apps()
        available_apps = [
            {"id": app["id"], "name": app["name"], "description": app["description"]} 
            for app in all_apps 
            if app.get("available", False)
        ]
        
        logger.info(f"Found {len(available_apps)} available apps")
        
        # Analyze task and select apps
        task_analysis = await self.analyze_task_and_select_apps(task, available_apps, interactive)
        
        if not task_analysis.requires_app:
            return {"requires_app": False, "reasoning": task_analysis.reasoning}
        
        if not task_analysis.app_sets:
            return {"requires_app": True, "app_sets": [], "auto_selected": []}
        
        # Get choice data for frontend
        choice_data = await self.get_app_choice_data(task_analysis.app_sets, task_analysis.choice, task)
        choice_data["requires_app"] = True
        choice_data["reasoning"] = task_analysis.reasoning
        
        return choice_data


@asynccontextmanager
async def create_auto_agent():
    """Create an AutoAgent instance with default configuration."""
    import os
    from playground.settings import settings
    
    # Read from environment variables with fallback to settings
    api_key = os.getenv("AUTO_AGENT_API_KEY", settings.AUTO_AGENT_API_KEY)
    api_base_url = os.getenv("AUTO_AGENT_API_BASE_URL", settings.AUTO_AGENT_API_BASE_URL)
    
    if not api_key:
        raise ValueError(
            "AUTO_AGENT_API_KEY environment variable is required. "
            "Please set it to your AgentR API key."
        )
    
    auto_agent = AutoAgent(
        api_key=api_key,
        api_base_url=api_base_url
    )
    yield auto_agent 