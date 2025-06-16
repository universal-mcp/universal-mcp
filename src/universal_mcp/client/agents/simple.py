from universal_mcp.client.agents.base import BaseAgent
from universal_mcp.client.agents.llm import LLMClient


class SimpleAgent(BaseAgent):
    def __init__(self, name: str, instructions: str, model: str):
        super().__init__(name, instructions, model)
        self.llm_client = LLMClient(model)

    async def execute(self, user_input: str):
        messages = [
            {"role": "system", "content": self.instructions},
            {"role": "user", "content": user_input},
        ]
        response = await self.llm_client.generate_response(messages)
        return response.content
