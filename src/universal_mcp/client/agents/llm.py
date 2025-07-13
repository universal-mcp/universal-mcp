from langchain_openai import AzureChatOpenAI


def get_llm(model: str):
    return AzureChatOpenAI(
        model="gpt-4o",
        api_version="2024-12-01-preview",
        azure_deployment="gpt-4o",
    )


if __name__ == "__main__":
    llm = get_llm("gpt-4o")
    print(llm.invoke("Hello, world!"))
