import uvicorn
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from langchain_vercel_adapters import VercelTypes as V
from langchain_vercel_adapters import serialize_to_data_stream_protocol

from universal_mcp.client.agents import SimpleAgent

app = FastAPI()
agent = SimpleAgent(
    name="simple",
    instructions="hello",
    model="gpt-4o-mini",
)


@app.post("/api/chat")
async def handle_chat_data(request: V.ChatMessages):
    messages = request.messages
    stream = agent.stream(thread_id=request.id, user_input=messages[-1].content)
    stream = serialize_to_data_stream_protocol(stream)
    response = StreamingResponse(stream, media_type="text/event-stream")
    response.headers["x-vercel-ai-data-stream"] = "v1"
    return response


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
