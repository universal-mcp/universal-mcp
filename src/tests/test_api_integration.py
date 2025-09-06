import pytest

from universal_mcp.applications.utils import app_from_slug
from universal_mcp.exceptions import NotAuthorizedError
from universal_mcp.integrations import ApiKeyIntegration
from universal_mcp.stores import MemoryStore


def test_perplexity_api_no_key():
    store = MemoryStore()

    integration = ApiKeyIntegration("PERPLEXITY", store=store)
    PerplexityApp = app_from_slug("perplexity")

    app = PerplexityApp(integration=integration)

    with pytest.raises(NotAuthorizedError) as exc_info:
        app.chat("Hello, how are you?")

    assert "Please ask the user for api key" in str(exc_info.value)
    assert "PERPLEXITY_API_KEY" in str(exc_info.value)
