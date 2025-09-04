from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage
from loguru import logger


def get_message_text(msg: BaseMessage) -> str:
    """Get the text content of a message."""
    content = msg.content
    if isinstance(content, str):
        return content
    elif isinstance(content, dict):
        return content.get("text", "")
    else:
        txts = [c if isinstance(c, str) else (c.get("text") or "") for c in content]
        return "".join(txts).strip()

def load_chat_model(fully_specified_name: str) -> BaseChatModel:
    """Load a chat model from a fully specified name.

    Args:
        fully_specified_name (str): String in the format 'provider/model'.
    """
    logger.info(f"Loading chat model: {fully_specified_name}")
    try:
        provider, model = fully_specified_name.split("/", maxsplit=1)
        if provider == "google_anthropic_vertex":
            from langchain_google_vertexai.model_garden import ChatAnthropicVertex
            return ChatAnthropicVertex(model=model, temperature=0.2, location="asia-east1")
        elif provider == "anthropic":
            from langchain_anthropic import ChatAnthropic
            return ChatAnthropic(model=model, temperature=1, thinking={"type": "enabled", "budget_tokens": 2048}, max_tokens=4096) # pyright: ignore[reportCallIssue]
        elif provider == "gemini":
            from langchain_google_genai import ChatGoogleGenerativeAI
            return ChatGoogleGenerativeAI(model=model, temperature=1.0, max_retries=2)
        elif provider == "azure":
            from langchain_openai import AzureChatOpenAI
            return AzureChatOpenAI(model=model, api_version="2024-12-01-preview", azure_deployment=model)
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    except Exception as e:
        logger.error(f"Failed to load chat model '{fully_specified_name}': {e}")
        raise