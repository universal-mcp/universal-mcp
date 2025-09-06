from pydantic import BaseModel, Field


class Agent(BaseModel):
    name: str = Field(description="The name of the agent")
    description: str = Field(description="A small paragraph description of the agent")
    expertise: str = Field(description="Agents expertise. Growth expert, SEO expert, etc")
    instructions: str = Field(description="The instructions for the agent")
    schedule: str = Field(
        description="The schedule for the agent in crontab syntax (e.g., '0 9 * * *' for daily at 9 AM)"
    )


AGENT_PROMPT = """You are an AI assistant that creates autonomous agents based on user requests.

Your task is to analyze the user's request and create a structured agent definition that includes:
- A clear name for the agent
- A concise description of what the agent does
- The agent's area of expertise
- Detailed instructions for executing the task
- A cron schedule for when the agent should run
- A list of apps/services the agent will need to use

Be specific and actionable in your agent definitions. Consider the user's intent and create agents that can effectively accomplish their goals.

<query>
{query}
</query>
"""


async def generate_agent(llm, query):
    response = await llm.with_structured_output(Agent).ainvoke(input=AGENT_PROMPT.format(query=query))
    return response
