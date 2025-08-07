from langchain_openai import AzureChatOpenAI


def get_llm(model: str, tags: list[str] | None = None):
    return AzureChatOpenAI(model=model, api_version="2024-12-01-preview", azure_deployment=model, tags=tags)


if __name__ == "__main__":
    llm = get_llm("gpt-4.1")
    print(llm.invoke("Hello, world!"))
