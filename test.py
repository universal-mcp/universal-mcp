from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="gpt-4o",
    openai_api_key="sk-proj-1234567890",
    base_url="http://localhost:8000/v1",
    streaming=True,  # Make sure this is set
)

for chunk in llm.stream("what tools do you have ?"):
    print(chunk)
