import os

from langchain_openai import AzureChatOpenAI, ChatOpenAI


def get_llm(model: str, tags: list[str] = None):
    return AzureChatOpenAI(model="gpt-4o", api_version="2024-12-01-preview", azure_deployment="gpt-4o", tags=tags)
    llm = ChatOpenAI(
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        openai_api_base="https://openrouter.ai/api/v1",
        model_name="gpt-4o",
        tags=tags,
        # model_kwargs={
        #     "headers": {
        #         "HTTP-Referer": "https://wingmen.app",
        #         "X-Title": "Wingmen",
        #     },
        # },
    )
    return llm


if __name__ == "__main__":
    llm = get_llm("gpt-4.1")
    print(llm.invoke("Hello, world!"))
