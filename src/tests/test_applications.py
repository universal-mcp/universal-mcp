from collections.abc import Callable

import pytest
from loguru import logger

from universal_mcp.applications import app_from_slug


@pytest.mark.parametrize(
    "app_name",
    [
        "github",
        "zenquotes",
        "tavily",
        "google-calendar",
        "google-mail",
        "resend",
        "reddit",
        "markitdown",
        "e2b",
        "firecrawl",
        "serp",
    ],
)
def test_application(app_name):
    app = app_from_slug(app_name)(integration=None)
    assert app is not None
    tools = app.list_tools()
    logger.info(f"Tools for {app_name}: {tools}")
    assert len(tools) > 0
    assert isinstance(tools[0], Callable)
    for tool in tools:
        assert tool.__name__ is not None
        assert tool.__doc__ is not None
