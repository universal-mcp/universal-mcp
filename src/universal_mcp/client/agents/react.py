from loguru import logger

from universal_mcp.tools.manager import ToolManager

from .base import BaseAgent
from .llm import LLMClient


class ReActAgent(BaseAgent):
    def __init__(self, name: str, instructions: str, model: str):
        super().__init__(name, instructions, model)
        self.llm_client = LLMClient(model)
        self.max_iterations = 10
        logger.debug(f"Initialized ReActAgent: name={name}, model={model}")

    def _build_system_message(self) -> str:
        system_message = f"""You are {self.name}. {self.instructions}

You have access to various tools that can help you answer questions and complete tasks. When you need to use a tool:

1. Think about what information you need
2. Call the appropriate tool with the right parameters
3. Use the tool results to provide a comprehensive answer

Always explain your reasoning and be thorough in your responses. If you need to use multiple tools to answer a question completely, do so."""
        logger.debug(f"System message built: {system_message}")
        return system_message

    def _build_messages(self, user_input: str) -> list[dict[str, str]]:
        """Build message history for the conversation"""
        messages = [{"role": "system", "content": self._build_system_message()}]

        # Add conversation history
        for entry in self.conversation_history:
            messages.append({"role": "user", "content": entry["human"]})
            messages.append({"role": "assistant", "content": entry["assistant"]})

        # Add current user input
        messages.append({"role": "user", "content": user_input})

        logger.debug(f"Built messages for user_input='{user_input}': {messages}")
        return messages

    async def process_step(self, user_input: str, tool_manager: ToolManager) -> str:
        """Process user input using native tool calling"""

        logger.info(f"Processing user input: {user_input}")

        # Build conversation messages
        messages = self._build_messages(user_input)

        # Use native tool calling with conversation loop
        try:
            response = await self.llm_client.generate_response_with_tool_results(
                messages, tool_manager, self.max_iterations
            )
            final_answer = response.content
            logger.info(f"LLM response received: {final_answer}")
        except Exception as e:
            logger.error(f"Error during LLM response generation: {e}")
            raise

        # Store in conversation history
        self.conversation_history.append({"human": user_input, "assistant": final_answer})
        logger.debug(f"Updated conversation history: {self.conversation_history[-1]}")

        return final_answer
