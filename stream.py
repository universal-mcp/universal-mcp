import json
import time
import uuid
from typing import Annotated

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from langchain_core.messages import (
    AIMessageChunk,
)
from langchain_openai import AzureChatOpenAI
from langgraph.graph.message import add_messages
from langgraph.prebuilt import create_react_agent
from loguru import logger
from pydantic import BaseModel
from typing_extensions import TypedDict
import uvicorn

from universal_mcp.config import ServerConfig
from universal_mcp.servers import server_from_config


class State(TypedDict):
    # Messages have the type "list". The `add_messages` function
    # in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list, rather than overwriting them)
    messages: Annotated[list, add_messages]


llm = AzureChatOpenAI(
    model="gpt-4o",
    api_version="2024-12-01-preview",
    streaming=True,
)


def chatbot(state: State):
    return {"messages": [llm.invoke(state["messages"])]}


def create_graph(config: ServerConfig | None = None):
    """Create a LangGraph with tools loaded from config.
    
    Args:
        config: Optional ServerConfig to load apps from. If not provided,
               creates a default config with GitHub app.
               
    Returns:
        Configured LangGraph instance
    """
    
    # Create a local server to handle tool loading
    server =  server_from_config(config)
    
    # Get the tools in LangChain format
    tools = server._tool_manager.list_tools(format="langchain")

    if not tools:
        print("Warning: No tools were registered for the agent.")

    # Create the agent with the collected tools
    graph = create_react_agent(
            model=llm,
            tools=tools,
            debug=False,
    )
    return graph


def format_sse(data: str, event: str = "content") -> str:
    return f"event: {event}\ndata: {data}\n\n"



async def openai_sse_stream_generator(messages: list[dict], config: ServerConfig | None = None):
    """
    Streams LangGraph results in OpenAI-compatible SSE format.
    """
    graph = create_graph(config)
    first_chunk = True

    try:
        # Use stream_mode="messages" to get AIMessageChunk objects
        async for event in graph.astream(
            {"messages": messages}, stream_mode="messages"
        ):
            # Standard LangGraph stream_mode="messages" yields AIMessageChunk directly
            # or sometimes tuples (chunk, metadata) - handle both for robustness
            chunk: AIMessageChunk | None = None
            if (
                isinstance(event, tuple)
                and len(event) > 0
                and isinstance(event[0], AIMessageChunk)
            ):
                chunk = event[0]
            elif isinstance(event, AIMessageChunk):
                chunk = event

            if chunk:
                chunk_id = f"chatcmpl-chunk-{uuid.uuid4()}"
                created_time = int(time.time())
                delta = {}
                finish_reason = None  # Typically null until the end

                # 1. Add role only for the very first chunk
                if first_chunk:
                    delta["role"] = "assistant"
                    first_chunk = False

                # 2. Add content if present
                if chunk.content:
                    delta["content"] = chunk.content

                # 3. Add tool calls if present (LangChain streams tool calls in chunks)
                # AIMessageChunk might have 'tool_call_chunks' attribute during streaming
                tool_call_deltas = []
                if hasattr(chunk, "tool_call_chunks") and chunk.tool_call_chunks:
                    for tool_call_chunk in chunk.tool_call_chunks:
                        # Map LangChain tool_call_chunk fields to OpenAI delta format
                        # Required: index. Optional but standard: id, type, function (name, arguments)
                        # Note: LangChain chunks might only contain *part* of the name or args
                        formatted_tc = {
                            "index": tool_call_chunk.get(
                                "index"
                            ),  # LangChain usually provides index
                            "id": tool_call_chunk.get("id"),
                            "type": "function",
                            "function": {},
                        }
                        if tool_call_chunk.get("name"):
                            formatted_tc["function"]["name"] = tool_call_chunk.get(
                                "name"
                            )
                        if tool_call_chunk.get("args"):
                            # OpenAI expects arguments as a string, LangChain often provides string chunks
                            formatted_tc["function"]["arguments"] = tool_call_chunk.get(
                                "args"
                            )

                        # Clean up empty fields if not present in this specific chunk delta
                        if not formatted_tc["function"]:
                            del formatted_tc["function"]
                        if formatted_tc["id"] is None:
                            del formatted_tc["id"]  # ID might appear later or in parts

                        # Only add if we have index and some data (id/function)
                        if formatted_tc["index"] is not None and (
                            formatted_tc.get("id") or formatted_tc.get("function")
                        ):
                            tool_call_deltas.append(formatted_tc)

                    if tool_call_deltas:
                        delta["tool_calls"] = tool_call_deltas
                        # If the *final* chunk signals tool use, set finish_reason
                        # This depends on how LangGraph signals the end state.
                        # A common pattern is that the *last* AIMessageChunk might have usage_metadata
                        # indicating 'tool_calls' as the reason. We'll add a basic final chunk later.

                # Only yield if delta has content or tool calls
                if delta.get("content") or delta.get("tool_calls") or delta.get("role"):
                    openai_chunk = {
                        "id": chunk_id,
                        "object": "chat.completion.chunk",
                        "created": created_time,
                        "model": "gpt-4o",
                        "choices": [
                            {
                                "index": 0,
                                "delta": delta,
                                "finish_reason": finish_reason,
                                # Add logprobs if available and needed: "logprobs": chunk.logprobs,
                            }
                        ],
                        # Add system_fingerprint and usage if available from LangGraph metadata
                        # "system_fingerprint": "...",
                        # "usage": chunk.usage_metadata # If available on the chunk
                    }
                    sse_data = f"data: {json.dumps(openai_chunk)}\n\n"
                    yield sse_data.encode("utf-8")

        # After the loop finishes, send a final chunk if needed to set finish_reason
        # This part is tricky as LangGraph's stream_mode="messages" might not explicitly
        # yield a final state chunk with the finish_reason easily accessible.
        # You might need to inspect the final state of the graph separately or
        # rely on conventions (e.g., if the last delta had tool_calls, reason is 'tool_calls')
        # For simplicity, we'll send a final chunk with finish_reason = "stop" as a default.
        # A more robust implementation would determine the correct reason ('stop', 'length', 'tool_calls').

        final_chunk_id = f"chatcmpl-chunk-{uuid.uuid4()}"
        final_created_time = int(time.time())
        final_openai_chunk = {
            "id": final_chunk_id,
            "object": "chat.completion.chunk",
            "created": final_created_time,
            "model": "gpt-4o",
            "choices": [
                {
                    "index": 0,
                    "delta": {},  # Empty delta in the final chunk
                    "finish_reason": "stop",  # Or "tool_calls" if that was the last action
                }
            ],
            # Potentially add final usage stats here if retrieved from graph state
            # "usage": { ... }
        }
        sse_data = f"data: {json.dumps(final_openai_chunk)}\n\n"
        yield sse_data.encode("utf-8")

    except Exception as e:
        # Handle exceptions and optionally stream an error message
        print(f"Error during streaming: {e}")
        error_message = {
            "error": {
                "message": f"An error occurred: {str(e)}",
                "type": "stream_error",
            }
        }
        logger.error(f"Error during streaming: {e}")
        # You could send this as SSE data, but [DONE] is often expected anyway
        # sse_data = f"data: {json.dumps(error_message)}\n\n"
        # yield sse_data.encode('utf-8')
        pass  # Fall through to send [DONE]

    finally:
        # Always send the [DONE] message at the very end
        yield b"data: [DONE]\n\n"


# while True:
#     try:
#         user_input = input("User: ")
#         if user_input.lower() in ["quit", "exit", "q"]:
#             print("Goodbye!")
#             break
#         stream_graph_updates(user_input)
#     except:
#         # fallback if input() is not available
#         user_input = "What do you know about LangGraph?"
#         print("User: " + user_input)
#         stream_graph_updates(user_input)
#         break


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,  # Allow credentials (cookies, authorization headers, etc)
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


class MessageRequest(BaseModel):
    messages: list[dict]
    config: ServerConfig | None = None


@app.post("/api/chat")
async def chat(request: MessageRequest):
    return StreamingResponse(
        langgraph_sse_stream_with_events(request.messages),
        media_type="text/event-stream",
    )


@app.post("/v1/chat/completions")  # Match OpenAI API path convention
async def stream_openai_compatible(request: MessageRequest):
    """
    Endpoint to stream LangGraph results in OpenAI-compatible SSE format.
    Accepts a list of messages similar to OpenAI API.
    """
    config = ServerConfig(
        name="Default Server",
        description="Default LangGraph Server",
        type="local",
        apps=[
            {
                "name": "zenquotes",
            }
        ],
    )
    return StreamingResponse(
        openai_sse_stream_generator(request.messages, config), 
        media_type="text/event-stream"
    )



async def test_agentr():
    config = ServerConfig(
        name="Default Server",
        description="Default LangGraph Server",
        type="local",
        apps=[
            {
                "name": "zenquotes",
                "description": "Zenquotes app"
            }
        ],
    )
    graph = create_graph(config)
    results = await graph.ainvoke({"messages": [{"role": "user", "content": "Using perplexity get the weather of bangalore?"}]})
    ai_message = results["messages"][-1]
    print(ai_message.content)


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_agentr())


