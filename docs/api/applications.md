# Applications API

Applications are the core abstraction for wrapping external APIs and services. They expose tools (callable functions) that AI agents can invoke.

## BaseApplication

::: universal_mcp.applications.application.BaseApplication
    options:
      show_source: false
      members:
        - __init__
        - list_tools

## APIApplication

::: universal_mcp.applications.application.APIApplication
    options:
      show_source: false
      members:
        - __init__
        - get
        - post
        - put
        - delete
        - patch
        - _get_headers
        - _make_request

## GraphQLApplication

::: universal_mcp.applications.application.GraphQLApplication
    options:
      show_source: false
      members:
        - __init__
        - execute_query
        - execute_mutation
        - _get_client

## Usage Examples

### Creating a REST API Application

```python
from universal_mcp.applications import APIApplication
from universal_mcp.integrations import ApiKeyIntegration
from universal_mcp.stores import KeyringStore

class GitHubApp(APIApplication):
    def __init__(self):
        store = KeyringStore(service_name="github")
        integration = ApiKeyIntegration(
            name="github_api_key",
            store=store,
            api_key_name="GITHUB_TOKEN"
        )

        super().__init__(
            name="github",
            integration=integration
        )
        self.base_url = "https://api.github.com"

    def list_tools(self):
        return [
            self.create_issue,
            self.list_repositories,
        ]

    def create_issue(
        self,
        repo: str,
        title: str,
        body: str
    ) -> dict:
        """Create a GitHub issue.

        Args:
            repo: Repository in format "owner/repo"
            title: Issue title
            body: Issue description

        Returns:
            Created issue data including number and URL
        """
        return self.post(
            f"/repos/{repo}/issues",
            json={"title": title, "body": body}
        )

    def list_repositories(self, username: str) -> list[dict]:
        """List user's public repositories.

        Args:
            username: GitHub username

        Returns:
            List of repository objects
        """
        return self.get(f"/users/{username}/repos")
```

### Creating a GraphQL Application

```python
from universal_mcp.applications import GraphQLApplication
from universal_mcp.integrations import OAuthIntegration

class GitHubGraphQLApp(GraphQLApplication):
    def __init__(self):
        integration = OAuthIntegration(
            name="github_oauth",
            client_id="...",
            client_secret="...",
            auth_url="https://github.com/login/oauth/authorize",
            token_url="https://github.com/login/oauth/access_token",
            scopes=["repo"]
        )

        super().__init__(
            name="github_graphql",
            integration=integration
        )
        self.graphql_url = "https://api.github.com/graphql"

    def list_tools(self):
        return [self.get_user_info]

    def get_user_info(self, username: str) -> dict:
        """Get user information via GraphQL.

        Args:
            username: GitHub username

        Returns:
            User profile data
        """
        query = '''
        query($username: String!) {
            user(login: $username) {
                name
                bio
                company
                location
            }
        }
        '''
        return self.execute_query(
            query,
            variables={"username": username}
        )
```

### Application Without Authentication

For public APIs that don't require authentication:

```python
from universal_mcp.applications import APIApplication

class PublicAPIApp(APIApplication):
    def __init__(self):
        # No integration needed
        super().__init__(name="public_api")
        self.base_url = "https://api.publicapis.org"

    def list_tools(self):
        return [self.random_api]

    def random_api(self) -> dict:
        """Get a random API from the public APIs list.

        Returns:
            Random API entry
        """
        return self.get("/random")
```

## Best Practices

### 1. Set Base URL

Always set `base_url` in `__init__`:

```python
def __init__(self):
    super().__init__(name="myapp")
    self.base_url = "https://api.example.com"  # Set this!
```

### 2. Handle Errors

Use try/except for better error messages:

```python
def create_user(self, name: str) -> dict:
    """Create a user."""
    try:
        return self.post("/users", json={"name": name})
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 409:
            raise ValueError(f"User {name} already exists")
        raise
```

### 3. Document Return Types

Be specific about return types in docstrings:

```python
def get_user(self, user_id: int) -> dict:
    """Get user by ID.

    Returns:
        dict: User object containing:
            - id (int): User ID
            - name (str): Full name
            - email (str): Email address
    """
```

### 4. Use Type Hints

Always include type hints for better schema generation:

```python
from typing import Literal

def update_status(
    self,
    status: Literal["active", "inactive", "pending"]
) -> dict:
    """Update status."""
    # Type hint generates enum in schema
```

## Related Documentation

- [Architecture: Tool Registration](../architecture/tool-registration.md) - How tools are discovered
- [Integrations API](integrations.md) - Authentication setup
- [Tools API](tools.md) - Tool system details
