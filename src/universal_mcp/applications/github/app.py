from typing import Any, ClassVar

from loguru import logger

from universal_mcp.applications.application import APIApplication
from universal_mcp.integrations import Integration


class GithubApp(APIApplication):
    APP_TAGS: ClassVar[list[str]] = ["developers-tools"]

    def __init__(self, integration: Integration) -> None:
        super().__init__(name="github", integration=integration)
        self.base_api_url = "https://api.github.com/repos"

    def _get_headers(self):
        if not self.integration:
            raise ValueError("Integration not configured")
        credentials = self.integration.get_credentials()
        if "headers" in credentials:
            return credentials["headers"]
        return {
            "Authorization": f"Bearer {credentials['access_token']}",
            "Accept": "application/vnd.github.v3+json",
        }

    def star_repository(self, repo_full_name: str) -> str:
        """
        Stars a GitHub repository using the GitHub API and returns a status message.

        Args:
            repo_full_name: The full name of the repository in 'owner/repo' format (e.g., 'octocat/Hello-World')

        Returns:
            A string message indicating whether the starring operation was successful, the repository was not found, or an error occurred

        Raises:
            RequestException: If there are network connectivity issues or API request failures
            ValueError: If the repository name format is invalid

        Tags:
            star, github, api, action, social, repository, important
        """
        url = f"https://api.github.com/user/starred/{repo_full_name}"
        response = self._put(url, data={})
        if response.status_code == 204:
            return f"Successfully starred repository {repo_full_name}"
        elif response.status_code == 404:
            return f"Repository {repo_full_name} not found"
        else:
            logger.error(response.text)
            return f"Error starring repository: {response.text}"

    def list_commits(self, repo_full_name: str) -> str:
        """
        Retrieves and formats a list of recent commits from a GitHub repository

        Args:
            repo_full_name: The full name of the repository in 'owner/repo' format

        Returns:
            A formatted string containing the most recent 12 commits, including commit hash, message, and author

        Raises:
            requests.exceptions.HTTPError: When the GitHub API request fails (e.g., repository not found, rate limit exceeded)
            requests.exceptions.RequestException: When network issues or other request-related problems occur

        Tags:
            list, read, commits, github, history, api, important
        """
        repo_full_name = repo_full_name.strip()
        url = f"{self.base_api_url}/{repo_full_name}/commits"
        response = self._get(url)
        response.raise_for_status()
        commits = response.json()
        if not commits:
            return f"No commits found for repository {repo_full_name}"
        result = f"Recent commits for {repo_full_name}:\n\n"
        for commit in commits[:12]:  # Limit to 12 commits
            sha = commit.get("sha", "")[:7]
            message = commit.get("commit", {}).get("message", "").split("\n")[0]
            author = commit.get("commit", {}).get("author", {}).get("name", "Unknown")

            result += f"- {sha}: {message} (by {author})\n"
        return result

    def list_branches(self, repo_full_name: str) -> str:
        """
        Lists all branches for a specified GitHub repository and returns them in a formatted string representation.

        Args:
            repo_full_name: The full name of the repository in 'owner/repo' format (e.g., 'octocat/Hello-World')

        Returns:
            A formatted string containing the list of branches, or a message indicating no branches were found

        Raises:
            HTTPError: When the GitHub API request fails (e.g., repository not found, authentication error)
            RequestException: When there are network connectivity issues or API communication problems

        Tags:
            list, branches, github, read, api, repository, important
        """
        repo_full_name = repo_full_name.strip()
        url = f"{self.base_api_url}/{repo_full_name}/branches"
        response = self._get(url)
        response.raise_for_status()
        branches = response.json()
        if not branches:
            return f"No branches found for repository {repo_full_name}"
        result = f"Branches for {repo_full_name}:\n\n"
        for branch in branches:
            branch_name = branch.get("name", "Unknown")
            result += f"- {branch_name}\n"
        return result

    def list_pull_requests(self, repo_full_name: str, state: str = "open") -> str:
        """
        Retrieves and formats a list of pull requests for a specified GitHub repository.

        Args:
            repo_full_name: The full name of the repository in the format 'owner/repo' (e.g., 'tensorflow/tensorflow')
            state: Filter for pull request state. Can be 'open', 'closed', or 'all'. Defaults to 'open'

        Returns:
            A formatted string containing the list of pull requests, including PR number, title, author, and status. Returns a message if no pull requests are found.

        Raises:
            HTTPError: Raised when the GitHub API request fails (e.g., invalid repository name, rate limiting, or authentication issues)

        Tags:
            list, pull-request, github, api, read, important, fetch, query
        """
        repo_full_name = repo_full_name.strip()
        url = f"{self.base_api_url}/{repo_full_name}/pulls"
        params = {"state": state}
        response = self._get(url, params=params)
        response.raise_for_status()
        pull_requests = response.json()
        if not pull_requests:
            return f"No pull requests found for repository {repo_full_name} with state '{state}'"
        result = f"Pull requests for {repo_full_name} (State: {state}):\n\n"
        for pr in pull_requests:
            pr_title = pr.get("title", "No Title")
            pr_number = pr.get("number", "Unknown")
            pr_state = pr.get("state", "Unknown")
            pr_user = pr.get("user", {}).get("login", "Unknown")

            result += (
                f"- PR #{pr_number}: {pr_title} (by {pr_user}, Status: {pr_state})\n"
            )
        return result

    def list_issues(
        self,
        repo_full_name: str,
        state: str = "open",
        assignee: str = None,
        labels: str = None,
        per_page: int = 30,
        page: int = 1,
    ) -> list[dict[str, Any]]:
        """
        Retrieves a list of issues from a specified GitHub repository with optional filtering parameters.

        Args:
            repo_full_name: The full name of the repository in 'owner/repo' format
            state: Filter issues by state ('open', 'closed', 'all'). Defaults to 'open'
            assignee: Filter by assignee username. Use 'none' for unassigned issues, '*' for assigned issues
            labels: Comma-separated string of label names to filter by (e.g., 'bug,ui,@high')
            per_page: Number of results per page (max 100). Defaults to 30
            page: Page number for pagination. Defaults to 1

        Returns:
            List of dictionaries containing issue data from the GitHub API response

        Raises:
            HTTPError: When the GitHub API request fails (e.g., invalid repository name, authentication failure)
            RequestException: When there are network connectivity issues or other request-related problems

        Tags:
            list, issues, github, api, read, filter, pagination, important, project-management
        """
        repo_full_name = repo_full_name.strip()
        url = f"{self.base_api_url}/{repo_full_name}/issues"
        params = {"state": state, "per_page": per_page, "page": page}
        if assignee:
            params["assignee"] = assignee
        if labels:
            params["labels"] = labels
        response = self._get(url, params=params)
        response.raise_for_status()
        return response.json()

    def get_pull_request(self, repo_full_name: str, pull_number: int) -> str:
        """
        Retrieves and formats detailed information about a specific GitHub pull request from a repository

        Args:
            repo_full_name: The full repository name in 'owner/repo' format (e.g., 'octocat/Hello-World')
            pull_number: The numeric identifier of the pull request to retrieve

        Returns:
            A formatted string containing pull request details including title, creator, status, and description

        Raises:
            HTTPError: Raised when the GitHub API request fails (e.g., invalid repository name, non-existent PR number, or authentication issues)
            RequestException: Raised when there are network connectivity issues or other request-related problems

        Tags:
            get, read, github, pull-request, api, fetch, format, important
        """
        repo_full_name = repo_full_name.strip()
        url = f"{self.base_api_url}/{repo_full_name}/pulls/{pull_number}"
        response = self._get(url)
        response.raise_for_status()
        pr = response.json()
        pr_title = pr.get("title", "No Title")
        pr_number = pr.get("number", "Unknown")
        pr_state = pr.get("state", "Unknown")
        pr_user = pr.get("user", {}).get("login", "Unknown")
        pr_body = pr.get("body", "No description provided.")
        result = (
            f"Pull Request #{pr_number}: {pr_title}\n"
            f"Created by: {pr_user}\n"
            f"Status: {pr_state}\n"
            f"Description: {pr_body}\n"
        )
        return result

    def create_pull_request(
        self,
        repo_full_name: str,
        head: str,
        base: str,
        title: str = None,
        body: str = None,
        issue: int = None,
        maintainer_can_modify: bool = True,
        draft: bool = False,
    ) -> dict[str, Any]:
        """
        Creates a new pull request in a GitHub repository, optionally converting an existing issue into a pull request.

        Args:
            repo_full_name: The full name of the repository (e.g. 'owner/repo')
            head: The name of the branch where your changes are implemented
            base: The name of the branch you want the changes pulled into
            title: The title of the new pull request (required if issue is not specified)
            body: The contents of the pull request
            issue: An issue number to convert to a pull request. If specified, the issue's title, body, and comments will be used
            maintainer_can_modify: Indicates whether maintainers can modify the pull request
            draft: Indicates whether the pull request is a draft

        Returns:
            A dictionary containing the complete GitHub API response

        Raises:
            ValueError: Raised when neither 'title' nor 'issue' parameter is specified
            HTTPError: Raised when the GitHub API request fails

        Tags:
            create, pull-request, github, api, write, important
        """
        repo_full_name = repo_full_name.strip()
        url = f"{self.base_api_url}/{repo_full_name}/pulls"
        pull_request_data = {
            "head": head,
            "base": base,
            "maintainer_can_modify": maintainer_can_modify,
            "draft": draft,
        }
        if issue is not None:
            pull_request_data["issue"] = issue
        else:
            if title is None:
                raise ValueError("Either 'title' or 'issue' must be specified")
            pull_request_data["title"] = title
            if body is not None:
                pull_request_data["body"] = body
        response = self._post(url, pull_request_data)
        response.raise_for_status()
        return response.json()

    def create_issue(
        self, repo_full_name: str, title: str, body: str = "", labels=None
    ) -> str:
        """
        Creates a new issue in a specified GitHub repository with a title, body content, and optional labels.

        Args:
            repo_full_name: The full name of the repository in 'owner/repo' format
            title: The title of the issue
            body: The contents/description of the issue (defaults to empty string)
            labels: Labels to associate with the issue, as a comma-separated string or list. Only users with push access can set labels

        Returns:
            A string containing a confirmation message with the issue number, title, and URL

        Raises:
            HTTPError: When the GitHub API request fails (e.g., invalid repository name, authentication issues, or insufficient permissions)

        Tags:
            create, issues, github, api, project-management, write, important
        """
        repo_full_name = repo_full_name.strip()
        url = f"{self.base_api_url}/{repo_full_name}/issues"
        issue_data = {"title": title, "body": body}
        if labels:
            if isinstance(labels, str):
                labels_list = [
                    label.strip() for label in labels.split(",") if label.strip()
                ]
                issue_data["labels"] = labels_list
            else:
                issue_data["labels"] = labels
        response = self._post(url, issue_data)
        response.raise_for_status()
        issue = response.json()
        issue_number = issue.get("number", "Unknown")
        issue_url = issue.get("html_url", "")
        return (
            f"Successfully created issue #{issue_number}:\n"
            f"Title: {title}\n"
            f"URL: {issue_url}"
        )

    def list_repo_activities(
        self, repo_full_name: str, direction: str = "desc", per_page: int = 30
    ) -> str:
        """
        Retrieves and formats a list of activities for a specified GitHub repository.

        Args:
            repo_full_name: The full name of the repository in 'owner/repo' format
            direction: The sort direction for results ('asc' or 'desc'). Defaults to 'desc'
            per_page: Number of activities to return per page (1-100). Defaults to 30

        Returns:
            A formatted string containing a list of repository activities, including timestamps and actor names. Returns a 'No activities' message if no activities are found.

        Raises:
            HTTPError: Raised when the GitHub API request fails
            ValueError: May be raised if repo_full_name is invalid or empty after stripping

        Tags:
            list, activity, github, read, events, api, query, format
        """
        repo_full_name = repo_full_name.strip()
        url = f"{self.base_api_url}/{repo_full_name}/activity"
        params = {"direction": direction, "per_page": per_page}
        response = self._get(url, params=params)
        response.raise_for_status()
        activities = response.json()
        if not activities:
            return f"No activities found for repository {repo_full_name}"
        result = f"Repository activities for {repo_full_name}:\n\n"
        for activity in activities:
            # Extract common fields
            timestamp = activity.get("timestamp", "Unknown time")
            actor_name = "Unknown user"
            if "actor" in activity and activity["actor"]:
                actor_name = activity["actor"].get("login", "Unknown user")

            # Create a simple description of the activity
            result += f"- {actor_name} performed an activity at {timestamp}\n"
        return result

    def update_issue(
        self,
        repo_full_name: str,
        issue_number: int,
        title: str = None,
        body: str = None,
        assignee: str = None,
        state: str = None,
        state_reason: str = None,
    ) -> dict[str, Any]:
        """
        Updates an existing GitHub issue with specified parameters including title, body, assignee, state, and state reason.

        Args:
            repo_full_name: The full name of the repository in 'owner/repo' format
            issue_number: The unique identifier number of the issue to update
            title: The new title of the issue (optional)
            body: The new content/description of the issue (optional)
            assignee: GitHub username to assign to the issue (optional)
            state: The desired state of the issue ('open' or 'closed') (optional)
            state_reason: The reason for state change ('completed', 'not_planned', 'reopened', or null) (optional)

        Returns:
            A dictionary containing the complete GitHub API response with updated issue details

        Raises:
            HTTPError: Raised when the GitHub API request fails (e.g., invalid repository, non-existent issue, insufficient permissions)
            RequestException: Raised when there's a network error or API connectivity issue

        Tags:
            github, issues, update, api, project-management, write, important
        """
        url = f"{self.base_api_url}/{repo_full_name}/issues/{issue_number}"
        update_data = {}
        if title is not None:
            update_data["title"] = title
        if body is not None:
            update_data["body"] = body
        if assignee is not None:
            update_data["assignee"] = assignee
        if state is not None:
            update_data["state"] = state
        if state_reason is not None:
            update_data["state_reason"] = state_reason
        response = self._patch(url, update_data)
        response.raise_for_status()
        return response.json()

    def list_tools(self):
        return [
            self.star_repository,
            self.list_commits,
            self.list_branches,
            self.list_pull_requests,
            self.list_issues,
            self.get_pull_request,
            self.create_pull_request,
            self.create_issue,
            self.update_issue,
            self.list_repo_activities,
        ]
