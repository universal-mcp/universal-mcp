import pytest

from universal_mcp.applications import app_from_slug
from universal_mcp.exceptions import NotAuthorizedError
from universal_mcp.integrations import ApiKeyIntegration
from universal_mcp.stores import MemoryStore


def test_perplexity_api_no_key():
    # Create a memory store
    store = MemoryStore()

    # Create API key integration with the store
    integration = ApiKeyIntegration("PERPLEXITY", store=store)

    # Create Perplexity app with the integration
    app = app_from_slug("perplexity")(integration=integration)

    # Try to make a chat request without setting API key
    with pytest.raises(NotAuthorizedError) as exc_info:
        app.chat("Hello, how are you?")

    # Verify the error message suggests setting up API key
    assert "Please ask the user for api key" in str(exc_info.value)
    assert "PERPLEXITY_API_KEY" in str(exc_info.value)
