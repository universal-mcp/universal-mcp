from typing import Any

from loguru import logger

from universal_mcp.applications.application import APIApplication
from universal_mcp.integrations import Integration


class GithubApp(APIApplication):
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
        """Star a GitHub repository

        Args:
            repo_full_name: The full name of the repository (e.g. 'owner/repo')

        Returns:

            A confirmation message
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
        """List recent commits for a GitHub repository

        Args:
            repo_full_name: The full name of the repository (e.g. 'owner/repo')

        Returns:
            A formatted list of recent commits
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
        """List branches for a GitHub repository

        Args:
            repo_full_name: The full name of the repository (e.g. 'owner/repo')

        Returns:
            A formatted list of branches
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
        """List pull requests for a GitHub repository

        Args:
            repo_full_name: The full name of the repository (e.g. 'owner/repo')
            state: The state of the pull requests to filter by (open, closed, or all)

        Returns:
            A formatted list of pull requests
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
        """List issues for a GitHub repository

        Args:
            repo_full_name: The full name of the repository (e.g. 'owner/repo')
            state: State of issues to return (open, closed, all). Default: open
            assignee: Filter by assignee. Use 'none' for no assignee, '*' for any assignee
            labels: Comma-separated list of label names (e.g. "bug,ui,@high")
            per_page: The number of results per page (max 100)
            page: The page number of the results to fetch

        Returns:
             The complete GitHub API response
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
        """Get a specific pull request for a GitHub repository

        Args:
            repo_full_name: The full name of the repository (e.g. 'owner/repo')
            pull_number: The number of the pull request to retrieve

        Returns:
            A formatted string with pull request details
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
        """Create a new pull request for a GitHub repository

        Args:
            repo_full_name: The full name of the repository (e.g. 'owner/repo')
            head: The name of the branch where your changes are implemented
            base: The name of the branch you want the changes pulled into
            title: The title of the new pull request (required if issue is not specified)
            body: The contents of the pull request
            issue: An issue number to convert to a pull request. If specified, the issue's
                   title, body, and comments will be used for the pull request
            maintainer_can_modify: Indicates whether maintainers can modify the pull request
            draft: Indicates whether the pull request is a draft

        Returns:
            The complete GitHub API response
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
        """Create a new issue in a GitHub repository

        Args:
            repo_full_name: The full name of the repository (e.g. 'owner/repo')
            title: The title of the issue
            body: The contents of the issue
            labels: Labels to associate with this issue. Enter as a comma-separated string
                   (e.g. "bug,enhancement,documentation").
                   NOTE: Only users with push access can set labels for new issues.
                   Labels are silently dropped otherwise.

        Returns:
            A confirmation message with the new issue details
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
        """List activities for a GitHub repository

        Args:
            repo_full_name: The full name of the repository (e.g. 'owner/repo')
            direction: The direction to sort the results by (asc or desc). Default: desc
            per_page: The number of results per page (max 100). Default: 30

        Returns:
            A formatted list of repository activities
        """
        repo_full_name = repo_full_name.strip()
        url = f"{self.base_api_url}/{repo_full_name}/activity"

        # Build query parameters
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
        """Update an issue in a GitHub repository

        Args:
            repo_full_name: The full name of the repository (e.g. 'owner/repo')
            issue_number: The number that identifies the issue
            title: The title of the issue
            body: The contents of the issue
            assignee: Username to assign to this issue
            state: State of the issue (open or closed)
            state_reason: Reason for state change (completed, not_planned, reopened, null)

        Returns:
             The complete GitHub API response
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
