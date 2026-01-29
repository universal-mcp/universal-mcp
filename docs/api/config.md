# Configuration API

Pydantic models for server and application configuration.

## ServerConfig

::: universal_mcp.config.ServerConfig
    options:
      show_source: false

## AppConfig

::: universal_mcp.config.AppConfig
    options:
      show_source: false

## IntegrationConfig

::: universal_mcp.config.IntegrationConfig
    options:
      show_source: false

## StoreConfig

::: universal_mcp.config.StoreConfig
    options:
      show_source: false

## Usage Examples

### Complete YAML Configuration

```yaml
# Server-level settings
server:
  name: "My MCP Server"
  version: "1.0.0"
  debug: false

# Store configuration
store:
  type: keyring
  service_name: universal-mcp-prod

# Application definitions
applications:
  # OAuth application
  - name: github
    module: universal_mcp.applications.github
    class_name: GitHubApp
    init_kwargs:
      timeout: 30
    integration:
      type: oauth
      client_id: ${GITHUB_CLIENT_ID}
      client_secret: ${GITHUB_CLIENT_SECRET}
      auth_url: https://github.com/login/oauth/authorize
      token_url: https://github.com/login/oauth/access_token
      scopes:
        - repo
        - user
      callback_port: 8080

  # API Key application
  - name: slack
    module: my_apps.slack
    class_name: SlackApp
    integration:
      type: api_key
      api_key_name: SLACK_BOT_TOKEN
      headers:
        Authorization: "Bearer {api_key}"

  # No authentication
  - name: public_api
    module: my_apps.public
    class_name: PublicAPIApp
    # No integration needed

# Global timeout settings
timeouts:
  default: 30
  max: 300
```

### Loading Configuration

```python
from universal_mcp.config import ServerConfig

# From YAML file
config = ServerConfig.from_yaml("config.yaml")

# From dict
config = ServerConfig.from_dict({
    "store": {"type": "memory"},
    "applications": [...]
})

# Access fields
print(config.server.name)
print(config.store.type)
for app in config.applications:
    print(f"App: {app.name}")
```

### Environment Variable Substitution

Variables in format `${VAR_NAME}` are automatically replaced:

```yaml
integration:
  client_id: ${GITHUB_CLIENT_ID}  # Replaced with os.environ["GITHUB_CLIENT_ID"]
  client_secret: ${GITHUB_CLIENT_SECRET}
```

```python
import os
os.environ["GITHUB_CLIENT_ID"] = "abc123"
os.environ["GITHUB_CLIENT_SECRET"] = "secret"

config = ServerConfig.from_yaml("config.yaml")
print(config.applications[0].integration.client_id)  # "abc123"
```

### Validation

Pydantic validates configuration:

```python
from universal_mcp.config import ServerConfig
from pydantic import ValidationError

try:
    config = ServerConfig.from_yaml("invalid.yaml")
except ValidationError as e:
    print("Configuration errors:")
    for error in e.errors():
        print(f"  {error['loc']}: {error['msg']}")
```

Example validation errors:
```
Configuration errors:
  store.type: value is not a valid enumeration member
  applications.0.module: field required
  applications.1.integration.client_id: field required
```

## Configuration Examples

### Minimal Configuration

```yaml
store:
  type: memory

applications:
  - name: simple_app
    module: my_module
    class_name: MyApp
```

### Multi-Environment Configuration

```yaml
# config.prod.yaml
store:
  type: keyring
  service_name: myapp-prod

applications:
  - name: github
    module: apps.github
    class_name: GitHubApp
    integration:
      type: oauth
      client_id: ${GITHUB_CLIENT_ID}
      client_secret: ${GITHUB_CLIENT_SECRET}
      # ... production settings
```

```yaml
# config.dev.yaml
store:
  type: memory

applications:
  - name: github
    module: apps.github
    class_name: GitHubApp
    integration:
      type: api_key
      api_key_name: DEV_GITHUB_TOKEN
```

### Application-Specific Configuration

```yaml
applications:
  - name: weather_api
    module: apps.weather
    class_name: WeatherApp

    # Custom kwargs passed to __init__
    init_kwargs:
      api_version: "2.5"
      units: "metric"
      timeout: 10
      cache_ttl: 3600

    integration:
      type: api_key
      api_key_name: WEATHER_API_KEY
```

Application receives kwargs:
```python
class WeatherApp(APIApplication):
    def __init__(
        self,
        name: str,
        integration: Integration,
        api_version: str = "2.5",
        units: str = "metric",
        **kwargs
    ):
        super().__init__(name, integration, **kwargs)
        self.api_version = api_version
        self.units = units
```

## Programmatic Configuration

### Building Config in Code

```python
from universal_mcp.config import (
    ServerConfig,
    AppConfig,
    IntegrationConfig,
    StoreConfig
)

config = ServerConfig(
    store=StoreConfig(type="keyring", service_name="my-app"),
    applications=[
        AppConfig(
            name="github",
            module="apps.github",
            class_name="GitHubApp",
            integration=IntegrationConfig(
                type="oauth",
                client_id="...",
                client_secret="...",
                auth_url="https://github.com/login/oauth/authorize",
                token_url="https://github.com/login/oauth/access_token",
                scopes=["repo"]
            )
        )
    ]
)

# Use config
from universal_mcp.servers import LocalServer
server = LocalServer.from_config_object(config)
```

### Merging Configurations

```python
def merge_configs(base_config, override_config):
    """Merge two configurations, override takes precedence."""
    base_dict = base_config.model_dump()
    override_dict = override_config.model_dump()

    # Deep merge logic
    merged = {**base_dict, **override_dict}

    return ServerConfig.from_dict(merged)

base = ServerConfig.from_yaml("base.yaml")
override = ServerConfig.from_yaml("override.yaml")
final = merge_configs(base, override)
```

## Integration Configuration Types

### API Key Integration

```yaml
integration:
  type: api_key
  api_key_name: MY_API_KEY

  # Optional: custom headers
  headers:
    Authorization: "Bearer {api_key}"
    X-API-Version: "2024-01"

  # Optional: query parameter instead
  query_param: "api_key"
```

### OAuth Integration

```yaml
integration:
  type: oauth
  client_id: ${CLIENT_ID}
  client_secret: ${CLIENT_SECRET}
  auth_url: https://provider.com/oauth/authorize
  token_url: https://provider.com/oauth/token

  # Required scopes
  scopes:
    - read
    - write

  # Optional settings
  callback_port: 8080
  callback_path: "/oauth/callback"
```

### AgentR Integration

```yaml
integration:
  type: agentr
  integration_id: github_integration_123
  agentr_api_key: ${AGENTR_API_KEY}
  agentr_url: https://api.agentr.io  # Optional
```

## Store Configuration Types

### Keyring Store

```yaml
store:
  type: keyring
  service_name: my-app-name  # Required
```

### Environment Store

```yaml
store:
  type: environment
  # No additional config needed
```

### Memory Store

```yaml
store:
  type: memory
  # No additional config needed
```

## Validation Rules

### Required Fields

```python
# ServerConfig requires:
# - store (StoreConfig)
# - applications (list of AppConfig)

# AppConfig requires:
# - name (str)
# - module (str)
# - class_name (str)

# IntegrationConfig requires (varies by type):
# - type (str)
# - type="api_key" requires: api_key_name
# - type="oauth" requires: client_id, client_secret, auth_url, token_url, scopes
# - type="agentr" requires: integration_id, agentr_api_key
```

### Type Validation

```python
# Enums
store.type in ["keyring", "environment", "memory"]
integration.type in ["api_key", "oauth", "agentr"]

# URLs
auth_url: must be valid URL
token_url: must be valid URL

# Ports
callback_port: must be 1-65535

# Lists
scopes: must be list of strings
applications: must be list of AppConfig
```

## Configuration Best Practices

### 1. Use Environment Variables for Secrets

```yaml
# Good
integration:
  client_secret: ${CLIENT_SECRET}

# Bad - secret in version control
integration:
  client_secret: "actual_secret_here"
```

### 2. Separate Dev/Prod Configs

```bash
config/
  base.yaml          # Common settings
  dev.yaml           # Development overrides
  prod.yaml          # Production overrides
  test.yaml          # Test settings
```

### 3. Validate Before Deployment

```python
def validate_config(config_path):
    try:
        config = ServerConfig.from_yaml(config_path)
        print("✓ Configuration valid")
        return True
    except Exception as e:
        print(f"✗ Configuration invalid: {e}")
        return False

# In CI/CD pipeline
if not validate_config("config.prod.yaml"):
    exit(1)
```

### 4. Document Required Environment Variables

```yaml
# config.yaml
# Required environment variables:
#   - GITHUB_CLIENT_ID: OAuth client ID from GitHub
#   - GITHUB_CLIENT_SECRET: OAuth client secret
#   - SLACK_BOT_TOKEN: Slack bot token from App settings

applications:
  - name: github
    integration:
      client_id: ${GITHUB_CLIENT_ID}
      client_secret: ${GITHUB_CLIENT_SECRET}
```

## Related Documentation

- [Servers API](servers.md) - Using configuration with servers
- [Architecture: Server Initialization](../architecture/server-init.md) - How config is loaded
