from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from loguru import logger

from universal_mcp.applications import app_from_slug
from universal_mcp.integrations import AgentRIntegration
from universal_mcp.tools import ToolManager


class PlatformManager(ABC):
    """Abstract base class for platform-specific functionality.
    
    This class abstracts away platform-specific operations like fetching apps,
    loading actions, and managing integrations. This allows the AutoAgent to
    work with different platforms without being tightly coupled to any specific one.
    """
    
    @abstractmethod
    async def get_available_apps(self) -> List[Dict[str, Any]]:
        """Get list of available apps from the platform.
        
        Returns:
            List of app dictionaries with at least 'id', 'name', 'description', and 'available' fields
        """
        pass
    
    @abstractmethod
    async def get_app_details(self, app_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific app.
        
        Args:
            app_id: The ID of the app to get details for
            
        Returns:
            Dictionary containing app details
        """
        pass
    
    @abstractmethod
    async def load_actions_for_app(self, app_name: str, tool_manager: ToolManager) -> None:
        """Load actions for a specific app and register them as tools.
        
        Args:
            app_name: The name/ID of the app to load actions for
            tool_manager: The tool manager to register tools with
        """
        pass


class AgentRPlatformManager(PlatformManager):
    """Platform manager implementation for AgentR platform."""
    
    def __init__(self, api_key: str, base_url: str = "https://api.agentr.dev"):
        """Initialize the AgentR platform manager.
        
        Args:
            api_key: The API key for AgentR
            base_url: The base URL for AgentR API
        """
        from universal_mcp.utils.agentr import AgentrClient
        
        self.api_key = api_key
        self.base_url = base_url
        self.client = AgentrClient(api_key=api_key, base_url=base_url)
        logger.debug("AgentRPlatformManager initialized successfully")
    
    async def get_available_apps(self) -> List[Dict[str, Any]]:
        """Get list of available apps from AgentR.
        
        Returns:
            List of app dictionaries with id, name, description, and available fields
        """
        try:
            all_apps = self.client.list_all_apps()
            available_apps = [
                {
                    "id": app["id"], 
                    "name": app["name"], 
                    "description": app.get("description", ""),
                    "available": app.get("available", False)
                }
                for app in all_apps 
                if app.get("available", False)
            ]
            logger.info(f"Found {len(available_apps)} available apps from AgentR")
            return available_apps
        except Exception as e:
            logger.error(f"Error fetching apps from AgentR: {e}")
            return []
    
    async def get_app_details(self, app_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific app from AgentR.
        
        Args:
            app_id: The ID of the app to get details for
            
        Returns:
            Dictionary containing app details
        """
        try:
            app_info = self.client.fetch_app(app_id)
            return {
                "id": app_info.get("id"),
                "name": app_info.get("name"),
                "description": app_info.get("description"),
                "category": app_info.get("category"),
                "available": app_info.get("available", True)
            }
        except Exception as e:
            logger.error(f"Error getting details for app {app_id}: {e}")
            return {
                "id": app_id,
                "name": app_id,
                "description": "Error loading details",
                "category": "Unknown",
                "available": True
            }
    
    async def load_actions_for_app(self, app_name: str, tool_manager: ToolManager) -> None:
        """Load actions for a specific app from AgentR and register them as tools.
        
        Args:
            app_name: The name/ID of the app to load actions for
            tool_manager: The tool manager to register tools with
        """
        logger.info(f"Loading all actions for app: {app_name}")
        
        try:
            # Get all actions for the app
            app_actions = self.client.list_actions(app_name)
            
            if not app_actions:
                logger.warning(f"No actions available for app: {app_name}")
                return
            
            logger.debug(f"Found {len(app_actions)} actions for {app_name}")
            
            # Register all actions as tools
            app = app_from_slug(app_name)
            integration = AgentRIntegration(
                name=app_name, 
                api_key=self.api_key, 
                base_url=self.base_url
            )
            app_instance = app(integration=integration)
            logger.debug(f"Registering all tools for app: {app_name}")
            tool_manager.register_tools_from_app(app_instance)
            
            logger.info(f"Successfully loaded all {len(app_actions)} actions for app: {app_name}")
            
        except Exception as e:
            logger.error(f"Failed to load actions for app {app_name}: {e}")
            raise
