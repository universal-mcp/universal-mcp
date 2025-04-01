# Integrations

This package provides integration classes for handling authentication and authorization with external services.

## Overview

An Integration defines how an application authenticates and authorizes with a service provider. The base `Integration` class provides an interface that all integrations must implement.

## Supported Integrations

### AgentR Integration
The `AgentRIntegration` class handles OAuth-based authentication flow with the AgentR API. It requires an API key which can be obtained from [agentr.dev](https://agentr.dev).

### API Key Integration  
The `ApiKeyIntegration` class provides a simple API key based authentication mechanism. API keys are configured via environment variables.

## Usage

Each integration implements three key methods:

- `authorize()` - Initiates the authorization flow
- `get_credentials()` - Retrieves stored credentials
- `set_credentials()` - Stores new credentials

See the individual integration classes for specific usage details.