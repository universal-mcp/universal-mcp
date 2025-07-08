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
    app_ids: List[str] = []
    choice: bool = False


class ActionSelection(BaseModel):
    action_ids: List[str]


class TaskDecomposition(BaseModel):
    tasks: List[str]


class AutoAgent:
    def __init__(self, api_key: str, api_base_url: str = "http://localhost:8000"):
        logger.info("Initializing AutoAgent")
        self.api_key = api_key
        self.client = AgentrClient(api_key=self.api_key)
        self.llm = ChatOpenAI(model="gpt-4.1")
        self.tool_manager = ToolManager()
        self.app_selection_prompt = """You are a task planning agent that helps identify relevant apps for user requests. Consider app IDs and their descriptions when making selections.
        Return the app IDs that are most relevant to completing the given task. If multiple apps seem relevant, ask the user to choose by setting the choice flag to True.
        """
        self.action_selection_prompt = """You are a helpful assistant that is given a list of actions for an app.
        You are also given a task.
        You need to determine the best actions to take to complete the task.
        Return the action IDs that are most relevant to completing the given task.
        """
        self.task_decomposition_prompt = """You are a task decomposition expert. Given a complex task that requires multiple steps, break it down into individual tasks that can be executed in sequence.

        For each task, provide a clear, specific task description that can be executed independently.

        Example:
        Task: "Search for best ramen place in bangalore and email the result to aditakarsh27@gmail.com"
        Decomposition:
        - "Search for best ramen place in bangalore"
        - "Email the search results to aditakarsh27@gmail.com"

        Another example:
        Task: "Analyze the benefits of remote work and create a summary"
        Decomposition:
        - "Analyze the benefits of remote work"
        - "Create a summary of the analysis"

        Each task should be specific and self-contained. Some tasks may require external apps (like search or email), while others can be completed through general reasoning and knowledge.
        """
        self.task_analysis_prompt = """You are a task analysis expert. Given a task description and available apps, determine:

        1. Whether the task requires an external application or can be handled through general reasoning
        2. If it requires an app, which apps are most relevant

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

        Analyze the given task and determine if it requires an external app or can be completed through general reasoning.
        If it requires an app, select the most relevant apps from the available list.
        """
        self.api_base_url = api_base_url
        logger.debug("AutoAgent initialized successfully")

    async def search_apps_via_api(self, query: str, limit: int = 5) -> List[dict]:
        """Search for apps using the backend API"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.api_base_url}/apps/search/"
                params = {"query": query, "top_k": limit}
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        apps = await response.json()
                        logger.debug(f"Found {len(apps)} apps via API search (limited to {limit})")
                        return apps
                    else:
                        logger.error(f"API search failed with status {response.status}")
                        return []
        except Exception as e:
            logger.error(f"Error searching apps via API: {e}")
            return []

    async def search_actions_via_api(self, app_name: str, query: str, limit: int = 10) -> List[dict]:
        """Search for actions using the backend API"""
        try:
            async with aiohttp.ClientSession() as session:
                # First try app-specific action search
                url = f"{self.api_base_url}/apps/{app_name}/actions/search/"
                params = {"query": query, "top_k": limit}
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        actions = await response.json()
                        logger.debug(f"Found {len(actions)} actions for {app_name} via API search (limited to {limit})")
                        return actions
                    else:
                        logger.warning(f"App-specific action search failed for {app_name}, trying global search")
                        
                        # Fallback to global action search
                        url = f"{self.api_base_url}/apps/actions/search/"
                        async with session.get(url, params=params) as response:
                            if response.status == 200:
                                all_actions = await response.json()
                                # Filter actions for the specific app
                                app_actions = [action for action in all_actions if action.get("app_id") == app_name]
                                logger.debug(f"Found {len(app_actions)} actions for {app_name} via global search (limited to {limit})")
                                return app_actions
                            else:
                                logger.error(f"Global action search failed with status {response.status}")
                                return []
        except Exception as e:
            logger.error(f"Error searching actions via API: {e}")
            return []

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

    async def handle_app_choice(self, choice_apps: List[str], task: str) -> List[str]:
        """Handle user choice when multiple apps are available"""
        logger.info(f"Multiple apps available for task: {task}")
        logger.info(f"Available choices: {choice_apps}")
        
        # Get detailed information about the apps
        app_details = await self.get_app_details(choice_apps)
        
        # Filter to only available apps
        available_apps = [app for app in app_details if app.get("available", False)]
        
        if not available_apps:
            logger.warning("No available apps found in choices")
            return []
        
        if len(available_apps) == 1:
            # Only one available app, use it
            selected = available_apps[0]["id"]
            logger.info(f"Only one available app: {selected}")
            return [selected]
        
        # Present choices to user (in a real implementation)
        logger.info("Available apps for your task:")
        for i, app in enumerate(available_apps, 1):
            logger.info(f"{i}. {app['name']} ({app['category']})")
            logger.info(f"   {app['description'][:100]}...")

        # Ask the user to choose
        while True:
            try:
                user_choice = input("Enter the number of the app you want to use: ")
                choice_index = int(user_choice) - 1
                if 0 <= choice_index < len(available_apps):
                    selected = available_apps[choice_index]["id"]
                    selected_name = available_apps[choice_index]["name"]
                    logger.info(f"User chose app: {selected} ({selected_name})")
                    return [selected]
                else:
                    print(f"Please enter a number between 1 and {len(available_apps)}")
            except ValueError:
                print("Please enter a valid number")
            except KeyboardInterrupt:
                logger.info("User cancelled app selection")
                return []



    async def load_action_for_app(self, app_name, task, action_limit: int = 10):
        logger.info(f"Loading actions for app: {app_name}")
        
        # Use the search API to find relevant actions
        app_actions = await self.search_actions_via_api(app_name, task, limit=action_limit)
        
        if not app_actions:
            logger.warning(f"No actions found via search for {app_name}, falling back to all actions")
            # Fallback to getting all actions if search returns nothing
            app_actions = self.client.list_actions(app_name)
        
        logger.debug(f"Found {len(app_actions)} actions for {app_name}")
        
        # If we have actions, select the most relevant ones
        if app_actions:
            llm_prompt = self.action_selection_prompt
            llm_prompt += f"\nHere are the actions for the app {app_name}: {app_actions}"
            llm_prompt += f"\nHere is the task: {task}"

            # Use structured output with Pydantic model
            structured_llm = self.llm.with_structured_output(ActionSelection)
            response = await structured_llm.ainvoke(llm_prompt)
            logger.debug(f"Response: {response}")
            selected_actions = response.action_ids
            logger.info(f"Selected actions: {selected_actions}")
        else:
            selected_actions = []
            logger.warning(f"No actions available for app: {app_name}")
        
        # Register the selected actions as tools
        app = app_from_slug(app_name)
        integration = AgentRIntegration(name=app_name, api_key=self.api_key, base_url="https://api.agentr.dev")
        app_instance = app(integration=integration)
        logger.debug(f"Registering tools for app: {app_name}")
        self.tool_manager.register_tools_from_app(app_instance, tool_names=selected_actions)
        logger.info(f"Successfully loaded actions for app: {app_name}")

    async def decompose_task(self, task: str) -> List[dict]:
        """Decompose a complex task into individual tasks"""
        logger.info(f"Decomposing task: {task}")
        
        prompt = f"""
        {self.task_decomposition_prompt}
        
        Complex task: {task}
        
        Break this down into individual tasks. Each task should be specific and can be executed independently.
        """
        
        # Use structured output with Pydantic model
        structured_llm = self.llm.with_structured_output(TaskDecomposition)
        response = await structured_llm.ainvoke(prompt)
        logger.debug(f"Decomposition response: {response}")
        
        # Create task objects
        tasks = []
        for i, task_desc in enumerate(response.tasks):
            tasks.append({
                "id": i + 1,
                "description": task_desc,
                "original_task": task
            })
        
        logger.info(f"Decomposed into {len(tasks)} tasks:")
        for task_info in tasks:
            logger.info(f"  {task_info['id']}. {task_info['description']}")
        
        return tasks

    async def analyze_task_and_select_apps(self, task: str, available_apps: List[dict], interactive: bool = False) -> TaskAnalysis:
        """Combined task analysis and app selection to reduce LLM calls"""
        logger.info(f"Analyzing task and selecting apps: {task}")
        
        prompt = f"""
        {self.task_analysis_prompt}
        
        Task: {task}
        Available apps: {available_apps}
        
        Determine if this task requires an external application or can be completed through general reasoning and knowledge.
        If it requires an app, select the most relevant apps from the available list.
        """
        
        # Use structured output with Pydantic model
        structured_llm = self.llm.with_structured_output(TaskAnalysis)
        response = await structured_llm.ainvoke(prompt)
        logger.debug(f"Task analysis response: {response}")
        
        logger.info(f"Task requires app: {response.requires_app}")
        logger.info(f"Reasoning: {response.reasoning}")
        if response.requires_app:
            logger.info(f"Selected apps: {response.app_ids}")
            logger.info(f"Choice needed: {response.choice}")
        
        # Handle interactive choice if needed
        if response.requires_app and response.choice and len(response.app_ids) > 1 and interactive:
            logger.info("Interactive mode: handling user choice")
            selected_apps = await self.handle_app_choice(response.app_ids, task)
            response.app_ids = selected_apps
            response.choice = False
        
        return response

    async def execute_task_without_app(self, task_info: dict) -> dict:
        """Execute a task that doesn't require an external app using general reasoning"""
        logger.info(f"Executing task without app: {task_info['description']}")
        
        # Create a simple agent without any tools for general reasoning
        agent = create_react_agent(
            self.llm, 
            tools=[], 
            prompt="You are a helpful assistant that can handle general reasoning, analysis, and knowledge-based tasks. Provide thoughtful, accurate, and helpful responses."
        )
        
        # Execute the task
        logger.info(f"Invoking general reasoning agent for task: {task_info['description']}")
        results = await agent.ainvoke({"messages": [HumanMessage(content=task_info['description'])]})
        ai_message = results["messages"][-1]
        
        logger.info(f"Task {task_info['id']} completed with general reasoning")
        return {
            "app": "general_reasoning",
            "result": ai_message.content,
            "success": True
        }

    async def execute_single_task(self, task_info: dict, action_limit: int = 10, interactive: bool = False) -> dict:
        """Execute a single task with optimized LLM calls"""
        logger.info(f"Executing task {task_info['id']}: {task_info['description']}")
        
        # Use the original task description for analysis (without previous context)
        original_task_description = task_info.get('original_description', task_info['description'])
        
        # Get available apps for this task
        search_results = await self.search_apps_via_api(original_task_description, limit=5)
        available_apps = [
            {"id": app["id"], "name": app["name"], "description": app["description"]} 
            for app in search_results 
            if app.get("available", False)
        ]
        
        if not available_apps:
            logger.warning("No apps found via search, falling back to all apps")
            all_apps = self.client.list_all_apps()
            available_apps = [{"id": app["id"], "name": app["name"], "description": app["description"]} for app in all_apps if app["available"] == True]
        
        # Combined task analysis and app selection (reduces LLM calls)
        task_analysis = await self.analyze_task_and_select_apps(original_task_description, available_apps, interactive)
        
        if not task_analysis.requires_app:
            logger.info(f"Task does not require an app, using general reasoning")
            return await self.execute_task_without_app(task_info)
        
        if not task_analysis.app_ids:
            logger.warning(f"No suitable app found for task: {task_info['description']}")
            logger.info(f"Falling back to general reasoning for this task")
            return await self.execute_task_without_app(task_info)
        
        # Use the selected app(s)
        if len(task_analysis.app_ids) > 1:
            logger.warning(f"Multiple apps returned ({len(task_analysis.app_ids)}), using first: {task_analysis.app_ids}")
        app_name = task_analysis.app_ids[0]
        logger.info(f"Using app for task: {app_name}")
        
        # Load actions for this specific app and task
        await self.load_action_for_app(app_name, task_info['description'], action_limit)
        
        # Create agent with the loaded tools
        agent = self.get_agent()
        
        # Execute the task
        logger.info(f"Invoking agent for task: {task_info['description']}")
        results = await agent.ainvoke({"messages": [HumanMessage(content=task_info['description'])]})
        ai_message = results["messages"][-1]
        
        logger.info(f"Task {task_info['id']} completed")
        return {
            "app": app_name,
            "result": ai_message.content,
            "success": True
        }

    def get_agent(self):
        logger.info("Creating agent with tools")
        tools = self.tool_manager.list_tools(format=ToolFormat.LANGCHAIN)
        logger.debug(f"Created agent with {len(tools)} tools")
        agent = create_react_agent(self.llm, tools=tools, prompt="You are a helpful assistant that is given a list of actions for an app. You are also given a task. Use the tools to complete the task. ")
        return agent

    async def run(self, task, app_limit: int = 5, action_limit: int = 10, interactive: bool = False):
        logger.info(f"Starting task execution: {task}")
        
        # First, decompose the task into individual tasks
        decomposed_tasks = await self.decompose_task(task)
        
        if not decomposed_tasks:
            logger.warning("No tasks could be decomposed from the original task")
            return "No tasks could be decomposed from the original task"
        
        # Execute tasks in series, passing results between them
        results = []
        context = ""
        
        for i, task_info in enumerate(decomposed_tasks):
            logger.info(f"=== Executing Task {i+1}/{len(decomposed_tasks)} ===")
            
            # Store the original task description for app selection
            original_description = task_info['description']
            
            # Add context from previous tasks if available (for task execution only)
            if context:
                enhanced_task = f"{task_info['description']}\n\nContext from previous tasks: {context}"
                task_info['description'] = enhanced_task
                task_info['original_description'] = original_description
            
            # Execute the single task
            execution_result = await self.execute_single_task(task_info, action_limit, interactive)
            results.append({
                "task_id": task_info['id'],
                "app": execution_result["app"],
                "description": task_info['description'],
                "result": execution_result["result"],
                "success": execution_result["success"]
            })
            
            # Update context for next task
            app_name = execution_result['app']
            if app_name == "general_reasoning":
                app_display = "General Reasoning"
            else:
                app_display = app_name
            context += f"\nTask {i+1} ({app_display}): {execution_result['result']}\n"
            
            logger.info(f"Task {i+1} completed with result: {execution_result['result'][:200]}...")
        
        # Compile final result
        final_result = f"All tasks completed successfully!\n\n"
        for result in results:
            status = "✓" if result["success"] else "✗"
            app_name = result['app']
            if app_name == "general_reasoning":
                app_display = "General Reasoning"
            else:
                app_display = app_name
            final_result += f"{status} Task {result['task_id']} ({app_display}): {result['result']}\n\n"
        
        logger.info("All tasks completed")
        return final_result


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