from typing import Any

from universal_mcp.applications import APIApplication
from universal_mcp.integrations import Integration


class RocketlaneApp(APIApplication):
    def __init__(self, integration: Integration = None, **kwargs) -> None:
        super().__init__(name="rocketlane", integration=integration, **kwargs)
        subdomain = self.integration.get_credentials().get("subdomain")
        self.base_url = f"https://{subdomain}.api.rocketlane.com/api/v1"

    def _get_headers(self) -> dict[str, Any]:
        api_key = self.integration.get_credentials().get("api_key")
        return {
            "api-key": f"{api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def get_subscription(
        self,
    ) -> Any:
        """
        Retrieves subscription details from the server.

        Args:
            None: This function does not take any parameters.

        Returns:
            A JSON response containing subscription details.

        Raises:
            requests.HTTPError: Raised if an HTTP error occurs during the request

        Tags:
            fetch, subscription, management, important
        """
        url = f"{self.base_url}/subscription"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_home(
        self,
    ) -> Any:
        """
        Retrieves the JSON response from the '/home' endpoint of the configured API.

        Returns:
            Any: Parsed JSON data returned by the '/home' endpoint.

        Raises:
            requests.HTTPError: If the HTTP request to the '/home' endpoint returns an unsuccessful status code.

        Tags:
            get, home, api, request, important
        """
        url = f"{self.base_url}/home"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_all_projects(
        self,
    ) -> dict[str, Any]:
        """
        Retrieves a list of all projects from the remote service.

        Args:
            None: This function takes no arguments

        Returns:
            A dictionary containing the JSON response data representing all available projects.

        Raises:
            HTTPError: If the HTTP request to retrieve the projects fails or returns an unsuccessful status code.

        Tags:
            list, projects, api, important
        """
        url = f"{self.base_url}/projects"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_projects_by_projectid(self, projectId) -> Any:
        """
        Retrieves project details for a given project ID from the server.

        Args:
            projectId: The unique identifier of the project to retrieve.

        Returns:
            A JSON-deserialized object containing the project's details as returned by the server.

        Raises:
            ValueError: Raised if 'projectId' is None.
            requests.HTTPError: Raised if the HTTP request to retrieve the project fails (e.g., 4xx or 5xx response).

        Tags:
            get, project, fetch, management, important
        """
        if projectId is None:
            raise ValueError("Missing required parameter 'projectId'")
        url = f"{self.base_url}/projects/{projectId}"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def get_projects_by_projectid_tasks(self, projectId) -> Any:
        """
        Retrieves a list of tasks associated with a given project ID.

        Args:
            projectId: str. The unique identifier of the project whose tasks are to be retrieved.

        Returns:
            dict. A JSON object containing the list of tasks for the specified project.

        Raises:
            ValueError: If the projectId parameter is None.
            requests.HTTPError: If the HTTP request to retrieve tasks fails (i.e., non-2xx response).

        Tags:
            get, list, project-tasks, management, important
        """
        if projectId is None:
            raise ValueError("Missing required parameter 'projectId'")
        url = f"{self.base_url}/projects/{projectId}/tasks"
        query_params = {}
        response = self._get(url, params=query_params)
        response.raise_for_status()
        return response.json()

    def create_task(
        self,
        projectId,
        taskDescription=None,
        taskName=None,
        assignee=None,
        startDate=None,
        dueDate=None,
    ) -> dict[str, Any]:
        """
        Creates a new task within the specified project, assigning optional details such as description, name, assignee, start date, and due date.

        Args:
            projectId: str. The unique identifier of the project in which to create the task. Required.
            taskDescription: Optional[str]. A description of the task to be created.
            taskName: Optional[str]. The name of the new task.
            assignee: Optional[str]. The user to whom the task is assigned.
            startDate: Optional[str]. The starting date for the task, formatted as an ISO 8601 string.
            dueDate: Optional[str]. The due date for task completion, formatted as an ISO 8601 string.

        Returns:
            dict[str, Any]: A dictionary containing the details of the created task as returned by the API.

        Raises:
            ValueError: If 'projectId' is not provided.
            requests.HTTPError: If the API request fails and returns a non-success HTTP status code.

        Tags:
            create, task, management, project, api, important
        """
        if projectId is None:
            raise ValueError("Missing required parameter 'projectId'")
        request_body = {
            "taskDescription": taskDescription,
            "taskName": taskName,
            "assignee": assignee,
            "startDate": startDate,
            "dueDate": dueDate,
        }
        request_body = {k: v for k, v in request_body.items() if v is not None}
        url = f"{self.base_url}/projects/{projectId}/tasks"
        query_params = {}
        response = self._post(url, data=request_body, params=query_params)
        response.raise_for_status()
        return response.json()

    def list_tools(self):
        return [
            self.get_subscription,
            self.get_home,
            self.get_all_projects,
            self.get_projects_by_projectid,
            self.get_projects_by_projectid_tasks,
            self.create_task,
        ]
