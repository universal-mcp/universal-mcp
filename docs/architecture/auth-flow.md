# Authentication Flow

This page details the three authentication patterns supported by universal-mcp: API Key, OAuth 2.0, and AgentR platform integration.

## Overview

Universal-mcp supports multiple authentication strategies through the Integration abstraction:

1. **API Key Authentication** - Simple token-based auth
2. **OAuth 2.0 Authentication** - Full OAuth flow with token refresh
3. **AgentR Integration** - Platform-managed credentials

## API Key Authentication

The simplest authentication method: store an API key and inject it into requests.

### Setup Flow

```mermaid
sequenceDiagram
    participant User
    participant CLI as universal-mcp CLI
    participant Int as ApiKeyIntegration
    participant Store as Store

    User->>CLI: Set API key
    CLI->>Int: create ApiKeyIntegration(name, store)
    User->>Int: authorize()
    Note over Int: Returns instructions:<br/>"Please set GITHUB_API_KEY<br/>in your environment"

    User->>Store: set("GITHUB_API_KEY", "ghp_...")
    Note over Store: Key stored securely
```

### Request Flow

```mermaid
sequenceDiagram
    participant App as Application
    participant Int as ApiKeyIntegration
    participant Store as Store
    participant API as External API

    App->>Int: get_credentials()
    Int->>Store: get("GITHUB_API_KEY")

    alt Key exists
        Store-->>Int: "ghp_..."
        Int-->>App: {"api_key": "ghp_..."}

        App->>App: _get_headers()
        Note over App: headers = {<br/>  "Authorization": "Bearer ghp_..."<br/>}

        App->>API: HTTP Request with auth header
        API-->>App: 200 OK
    else Key not found
        Store-->>Int: KeyNotFoundError
        Int-->>App: NotAuthorizedError
        Note over App: Prompt user to authorize
    end
```

### Configuration Example

```yaml
applications:
  - name: github
    module: github_app
    integration:
      type: api_key
      api_key_name: GITHUB_API_KEY
      headers:
        Authorization: "Bearer {api_key}"
```

### Key Storage Options

| Store Type | Usage | Security |
|------------|-------|----------|
| EnvironmentStore | Environment variable | Low - visible in process list |
| KeyringStore | System keyring | High - encrypted by OS |
| MemoryStore | In-process only | Medium - lost on restart |

## OAuth 2.0 Authentication

Full OAuth 2.0 authorization code flow with automatic token refresh.

### Initial Authorization Flow

```mermaid
sequenceDiagram
    participant User
    participant App as Application
    participant Int as OAuthIntegration
    participant Local as CallbackServer
    participant Browser
    participant OAuth as OAuth Provider
    participant Store as Store

    User->>App: Trigger authorization
    App->>Int: authorize()

    Note over Int: Build auth URL with<br/>client_id, scopes, redirect_uri

    Int->>Local: Start callback server on localhost:8080
    Int-->>User: Authorization URL
    Int->>Browser: Open URL in browser

    Browser->>OAuth: Authorization request
    Note over OAuth: User logs in and<br/>grants permissions

    OAuth->>Local: Redirect with code
    Local->>Int: Receive authorization code

    Int->>OAuth: Exchange code for tokens<br/>POST /oauth/token
    OAuth-->>Int: {<br/>  access_token: "...",<br/>  refresh_token: "...",<br/>  expires_in: 3600<br/>}

    Int->>Store: set("oauth_tokens", {...})
    Note over Store: Tokens stored securely

    Int->>Local: Stop callback server
    Int-->>User: "Authorization successful!"
```

### Token Usage Flow

```mermaid
sequenceDiagram
    participant App as Application
    participant Int as OAuthIntegration
    participant Store as Store
    participant API as External API

    App->>Int: get_credentials()
    Int->>Store: get("oauth_tokens")
    Store-->>Int: {access_token, refresh_token, expires_at}

    alt Token is valid (not expired)
        Int-->>App: {access_token}
        App->>API: HTTP Request with Bearer token
        API-->>App: 200 OK
    else Token expired
        Int->>Int: refresh_token()
        Note over Int: Use refresh_token to get new access_token
        Int-->>App: {new_access_token}
        App->>API: HTTP Request with new token
        API-->>App: 200 OK
    end
```

### Token Refresh Flow

```mermaid
sequenceDiagram
    participant Int as OAuthIntegration
    participant OAuth as OAuth Provider
    participant Store as Store

    Note over Int: Access token expired

    Int->>Store: get("oauth_tokens")
    Store-->>Int: {refresh_token}

    Int->>OAuth: POST /oauth/token<br/>{<br/>  grant_type: "refresh_token",<br/>  refresh_token: "...",<br/>  client_id: "...",<br/>  client_secret: "..."<br/>}

    alt Refresh successful
        OAuth-->>Int: {<br/>  access_token: "new_token",<br/>  refresh_token: "new_refresh",<br/>  expires_in: 3600<br/>}

        Int->>Store: set("oauth_tokens", {...})
        Note over Store: Updated tokens stored
    else Refresh failed (token revoked)
        OAuth-->>Int: 401 Unauthorized
        Int->>Store: delete("oauth_tokens")
        Note over Int: User must re-authorize
    end
```

### Configuration Example

```yaml
applications:
  - name: slack
    module: slack_app
    integration:
      type: oauth
      client_id: ${SLACK_CLIENT_ID}
      client_secret: ${SLACK_CLIENT_SECRET}
      auth_url: https://slack.com/oauth/authorize
      token_url: https://slack.com/api/oauth.access
      scopes:
        - chat:write
        - channels:read
      callback_port: 8080
```

### OAuth Components

**OAuthIntegration** manages:
- Authorization URL generation
- Callback server (receives OAuth code)
- Token exchange (code → access_token)
- Token refresh (refresh_token → new access_token)
- Token storage

**CallbackServer** (internal):
- Temporary HTTP server on localhost
- Receives OAuth redirect
- Extracts authorization code
- Shuts down after successful callback

## AgentR Platform Integration

Delegates credential management to the AgentR platform.

### Authorization Flow

```mermaid
sequenceDiagram
    participant User
    participant App as Application
    participant Int as AgentRIntegration
    participant AgentR as AgentR Platform

    User->>App: Trigger authorization
    App->>Int: authorize()

    Int->>AgentR: Request auth details
    AgentR-->>Int: {<br/>  message: "Visit AgentR dashboard",<br/>  auth_url: "https://agentr.io/auth",<br/>  integration_id: "..."<br/>}

    Int-->>User: Display auth instructions

    Note over User: User authorizes on<br/>AgentR platform

    Note over AgentR: Credentials managed<br/>by platform
```

### Credential Retrieval Flow

```mermaid
sequenceDiagram
    participant App as Application
    participant Int as AgentRIntegration
    participant AgentR as AgentR Platform

    App->>Int: get_credentials()

    Int->>AgentR: GET /api/credentials/{integration_id}
    Note over Int: Uses AgentR API key

    alt Credentials available
        AgentR-->>Int: {<br/>  access_token: "...",<br/>  credentials: {...}<br/>}
        Int-->>App: credentials
    else Not authorized
        AgentR-->>Int: 403 Forbidden
        Int-->>App: NotAuthorizedError
    end
```

### Configuration Example

```yaml
applications:
  - name: gmail
    module: gmail_app
    integration:
      type: agentr
      integration_id: gmail_integration_123
      agentr_api_key: ${AGENTR_API_KEY}
```

### Benefits of AgentR

1. **Centralized Management**: All credentials in one platform
2. **Security**: Credentials never stored locally
3. **Sharing**: Team members share access without sharing credentials
4. **Audit**: Platform tracks credential usage
5. **Rotation**: Automatic credential rotation

## Comparison Matrix

| Feature | API Key | OAuth 2.0 | AgentR |
|---------|---------|-----------|---------|
| **Setup Complexity** | Low | Medium | Low |
| **Security** | Medium | High | High |
| **Token Refresh** | Manual | Automatic | Automatic |
| **User Experience** | Copy/paste key | Browser flow | Browser flow |
| **Revocation** | Manual | Automatic | Platform-managed |
| **Sharing** | Share key (insecure) | Each user authorizes | Platform sharing |
| **Best For** | Development, personal tools | Production OAuth apps | Enterprise, teams |

## Store Selection Guide

Different stores are appropriate for different scenarios:

### MemoryStore
- **Use for**: Testing, development
- **Pros**: Fast, no setup
- **Cons**: Lost on restart
- **Security**: Low (in-process memory)

### EnvironmentStore
- **Use for**: CI/CD, containerized deployments
- **Pros**: Standard 12-factor approach
- **Cons**: Visible in process environment
- **Security**: Medium (process isolation)

### KeyringStore
- **Use for**: Production, local development
- **Pros**: Secure, persistent, encrypted by OS
- **Cons**: Requires system keyring
- **Security**: High (OS-level encryption)

## Error Handling

Common authentication errors and how they're handled:

```mermaid
graph TD
    A[get_credentials] --> B{Credentials exist?}
    B -->|No| C[NotAuthorizedError]
    C --> D[Prompt user to authorize]

    B -->|Yes| E{Token valid?}
    E -->|No| F{Has refresh token?}
    F -->|Yes| G[Refresh token]
    G --> H{Refresh success?}
    H -->|Yes| I[Return new token]
    H -->|No| C

    F -->|No| C
    E -->|Yes| I
```

### Exception Hierarchy

- `NotAuthorizedError`: No credentials found
- `KeyNotFoundError`: Specific key missing from store
- `TokenExpiredError`: Token expired and no refresh available
- `OAuthError`: OAuth flow error (user denied, invalid client, etc.)

## Related Documentation

- [Request Flow](request-flow.md) - How auth fits into the request lifecycle
- [Integrations API](../api/integrations.md) - Integration class reference
- [Stores API](../api/stores.md) - Store class reference
