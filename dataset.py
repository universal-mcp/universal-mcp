import asyncio

from dotenv import load_dotenv
from langsmith import Client


load_dotenv()

client = Client()

async def create_examples(user_input: str):
    """Run the agent and create a LangSmith dataset example"""
    
    # Create/get dataset
    dataset_name = "metaagent-actual-runs"
    try:
        dataset = client.create_dataset(
            dataset_name, 
            description="AutoAgent dataset with actual execution results"
        )
    except Exception:
        dataset = client.read_dataset(dataset_name=dataset_name)
    

    # Define the input
    # user_input = "Send an email to Manoj from my google mail account, manoj@agentr.dev, with the subject 'Hello from auto agent' and the body 'testing'"
    
    # Capture initial state
    initial_state = {
        "messages": [{"role": "user", "content": user_input}],
        "selected_tool_ids": [],
        "token_usage": {"input": 0, "output": 0, "total": 0},
        "user_input": user_input
    }
    
    # Execute the agent
    #result = await agent.invoke(user_input=user_input)
    result = None
    
    # Extract the final state from the result
    # Note: Adjust these based on your actual result structure
    
    # Create the dataset example with actual results
    example = client.create_example(
        inputs=initial_state,
        dataset_id=dataset.id
    )
    
    print(f"✅ Created dataset example with ID: {example.id}")
    print(f"Dataset: {dataset_name}")
    print(f"Input: {user_input}")
    print(f"Result: {result}")
    
    return example

if __name__ == "__main__":
    example_prompts = [
        "Create a Google Doc summarizing the last 5 merged pull requests in my GitHub repo- universal-mcp/universal-mcp, including links and commit highlights.",
        "Summarize the key insights from all marketing emails received this week and add a section in a Google Doc with action points.",
        "Create a sheet of the best cafes and restaurants near IIT Bombay",
        "Track the top posts in r/startups over the past 7 days and create a trend report on what's being discussed most (e.g., hiring, funding, MVPs).",
        "Find the best restaurants in Goa",
        "List the unread emails from the last 24 hours, sorted by sender.",
        "Tell me how many meetings I have tomorrow and when they start.",
        "Create a meeting with aditakarsh@example.com on the topic of the latest trends in AI at 8PM today.",
        "What are the topics of my meetings today and who are the attendees? Give a 1-line context for each attendee using LinkedIn or web search.",
        "Fetch my last inbox mail from outlook",
        "Fetch unsubscribe links from my inbox for promo emails I have received in the last 7 days",
        "Fetch all unread emails and new tickets from Clickup for me from last night",
        "Give me a report on the earnings of Oklo, and projections for the company revenue, stock price",
        "Create a weekly expense report from my credit card transactions and categorize spending by type (food, transport, entertainment, etc.)",
        "Generate a comparison table of SaaS tools for project management, including pricing, features, and user ratings",
        "Research the top 10 Y Combinator startups from the latest batch and create a report on their industries and funding status in Google Docs",
        "Find and summarize the key takeaways from the latest earnings calls of FAANG companies",
        "Draft personalized LinkedIn outreach messages for 10 potential collaborators in the fintech space based on their recent posts in a Google Sheet",
        "Monitor my Twitter mentions and DMs from the past 48 hours and create a response priority list in Google Sheets",
        "Create a content calendar for next month with trending AI/ML topics and optimal posting times based on my audience analytics"
    ]
    for prompt in example_prompts:
        asyncio.run(create_examples(prompt))