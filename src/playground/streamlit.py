import asyncio
import os
import uuid
from collections.abc import AsyncGenerator
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from pydantic import ValidationError
from streamlit.runtime.scriptrunner import get_script_run_ctx

from playground.client import AgentClient, AgentClientError
from playground.schema import ChatHistory, ChatMessage, TaskData, TaskDataStatus
from playground.settings import settings

# A Streamlit app for interacting with the langgraph agent via a simple chat interface.
# The app has three main functions which are all run async:

# - main() - sets up the streamlit app and high level structure
# - draw_messages() - draws a set of chat messages - either replaying existing messages
#   or streaming new ones.

# The app heavily uses AgentClient to interact with the agent's FastAPI endpoints.


APP_TITLE = "Agent Service Toolkit"
APP_ICON = "🧰"
use_streaming = True


# --- Function to handle unique filename generation ---
def get_unique_filepath(upload_dir: Path, filename: str) -> Path:
    """Checks if a file exists and returns a unique path if needed."""
    filepath = upload_dir / filename
    if not filepath.exists():
        return filepath

    # Handle collision
    base, ext = os.path.splitext(filename)
    counter = 1
    while True:
        new_filename = f"{base}_{counter}{ext}"
        new_filepath = upload_dir / new_filename
        if not new_filepath.exists():
            return new_filepath
        counter += 1


async def main() -> None:
    st.set_page_config(
        page_title=APP_TITLE,
        page_icon=APP_ICON,
        menu_items={},
    )

    # Hide the streamlit upper-right chrome
    st.html(
        """
        <style>
        [data-testid="stStatusWidget"] {
                visibility: hidden;
                height: 0%;
                position: fixed;
            }
        </style>
        """,
    )
    if st.get_option("client.toolbarMode") != "minimal":
        st.set_option("client.toolbarMode", "minimal")
        await asyncio.sleep(0.1)
        st.rerun()

    if "agent_client" not in st.session_state:
        load_dotenv()
        agent_url = os.getenv("AGENT_URL")
        if not agent_url:
            host = os.getenv("HOST", "0.0.0.0")
            port = os.getenv("PORT", 8000)
            agent_url = f"http://{host}:{port}"
        try:
            with st.spinner("Connecting to agent service..."):
                st.session_state.agent_client = AgentClient(base_url=agent_url)
        except AgentClientError as e:
            st.error(f"Error connecting to agent service at {agent_url}: {e}")
            st.markdown("The service might be booting up. Try again in a few seconds.")
            st.stop()
    agent_client: AgentClient = st.session_state.agent_client

    # --- Ensure Upload Directory Exists ---
    uploads_dir = settings.DATA_DIR / "uploads"
    try:
        uploads_dir.mkdir(parents=True, exist_ok=True)
        # Simple permission check (might not be foolproof on all OS/filesystems)
        # Try creating and deleting a dummy file
        dummy_path = uploads_dir / f".streamlit_write_test_{uuid.uuid4()}"
        dummy_path.touch()
        dummy_path.unlink()
    except OSError as e:
        st.error(
            f"Error creating or accessing upload directory ({uploads_dir}): {e}\n"
            "Please ensure the application has write permissions to this directory."
        )
        st.stop()
    # --- End Directory Check ---

    # Initialize state variables if not present
    if "thread_id" not in st.session_state:
        thread_id = st.query_params.get("thread_id")
        if not thread_id:
            thread_id = get_script_run_ctx().session_id
            messages = []
        else:
            try:
                messages: ChatHistory = agent_client.get_history(
                    thread_id=thread_id
                ).messages
            except AgentClientError:
                st.error("No message history found for this Thread ID.")
                messages = []
        st.session_state.messages = messages
        st.session_state.thread_id = thread_id
        st.session_state.uploaded_file_obj = None
        st.session_state.file_processed = False

    # Place it before the chat input for better flow
    uploaded_file = st.file_uploader(
        "Upload a file (optional)", type=None, key="file_uploader"
    )

    # Check if a new file has been uploaded or if the uploader was cleared
    if uploaded_file is not None:
        # Check if this is a new file or a different file than the last processed one
        if (
            "last_processed_file" not in st.session_state
            or st.session_state.get("last_processed_file") != uploaded_file.name
        ):
            # Reset the processed state for the new file
            st.session_state.file_processed = False
            st.session_state.uploaded_file_obj = uploaded_file
            st.info(
                f"File '{uploaded_file.name}' ready for processing with your next message.",
                icon="📄",
            )
    elif (
        uploaded_file is None and st.session_state.get("uploaded_file_obj") is not None
    ):
        # User cleared the file uploader, so reset the state
        st.session_state.uploaded_file_obj = None
        st.session_state.file_processed = False
        if "last_processed_file" in st.session_state:
            del st.session_state["last_processed_file"]

    # Draw existing messages
    messages: list[ChatMessage] = st.session_state.messages

    if len(messages) == 0:
        WELCOME = "Hello. I am your AI assistant with access to wide variety of tools. You can enable/disable desired tools at agentr.dev/apps."
        with st.chat_message("ai"):
            st.write(WELCOME)

    # draw_messages() expects an async iterator over messages
    async def amessage_iter() -> AsyncGenerator[ChatMessage, None]:
        for m in messages:
            yield m

    await draw_messages(amessage_iter())

    # Generate new message if the user provided new input
    if user_input := st.chat_input(
        "Enter message or upload a file and describe task..."
    ):
        final_message_content = user_input
        display_content = user_input

        # --- Handle File Upload Integration ---
        if st.session_state.uploaded_file_obj and not st.session_state.file_processed:
            uploaded_file_obj = st.session_state.uploaded_file_obj
            original_filename = uploaded_file_obj.name

            try:
                # Determine unique path and save the file
                save_filepath = get_unique_filepath(uploads_dir, original_filename)
                file_bytes = uploaded_file_obj.getvalue()
                save_filepath.write_bytes(file_bytes)

                # Get the absolute path as a string
                absolute_filepath_str = str(save_filepath.resolve())

                # Prepare metadata string
                # Use a clear prefix so the agent can easily parse it
                file_metadata_prefix = (
                    f"[User uploaded file named '{original_filename}'. "
                    f"It has been saved at the following absolute path: {absolute_filepath_str}]"
                    f"\n\n"
                )

                # Combine file metadata with user message
                final_message_content = file_metadata_prefix + user_input

                # Prepare display content for chat history
                display_content = (
                    f"[Using uploaded file: {original_filename}]\n\n{user_input}"
                )

                # Mark the file as processed to prevent reprocessing
                st.session_state.last_processed_file = original_filename
                st.session_state.file_processed = True

            except OSError as e:
                st.error(f"Error saving uploaded file '{original_filename}': {e}")
                # Don't proceed with sending message if file saving failed
                st.stop()  # Stop execution for this run
            except Exception as e:
                st.error(f"An unexpected error occurred during file handling: {e}")
                st.stop()

        # --- End File Upload Integration ---

        # Only proceed if we haven't stopped due to an error
        if final_message_content is not None:
            # Use final_message_content which might include the path metadata
            messages.append(ChatMessage(type="human", content=final_message_content))

            # Display the user-friendly content in the chat history
            st.chat_message("human").write(display_content)

            try:
                if use_streaming:
                    stream = agent_client.astream(
                        # Send the full content including path metadata to the agent
                        message=final_message_content,
                        thread_id=st.session_state.thread_id,
                    )
                    await draw_messages(stream, is_new=True)
                else:
                    response = await agent_client.ainvoke(
                        # Send the full content including path metadata to the agent
                        message=final_message_content,
                        thread_id=st.session_state.thread_id,
                    )
                    messages.append(response)
                    st.chat_message("ai").write(response.content)

                # Rerun to clear input box and update state cleanly
                st.rerun()
            except AgentClientError as e:
                st.error(f"Error generating response: {e}")
                # Don't stop necessarily, maybe the agent service is down, allow user to retry
            except Exception as e:
                st.error(
                    f"An unexpected error occurred during agent communication: {e}"
                )

    # If messages have been generated, show feedback widget
    if len(messages) > 0 and st.session_state.last_message:
        with st.session_state.last_message:
            await handle_feedback()


async def draw_messages(
    messages_agen: AsyncGenerator[ChatMessage | str, None],
    is_new: bool = False,
) -> None:
    """
    Draws a set of chat messages - either replaying existing messages
    or streaming new ones.

    This function has additional logic to handle streaming tokens and tool calls.
    - Use a placeholder container to render streaming tokens as they arrive.
    - Use a status container to render tool calls. Track the tool inputs and outputs
      and update the status container accordingly.

    The function also needs to track the last message container in session state
    since later messages can draw to the same container. This is also used for
    drawing the feedback widget in the latest chat message.

    Args:
        messages_aiter: An async iterator over messages to draw.
        is_new: Whether the messages are new or not.
    """

    # Keep track of the last message container
    last_message_type = None
    st.session_state.last_message = None

    # Placeholder for intermediate streaming tokens
    streaming_content = ""
    streaming_placeholder = None

    # Iterate over the messages and draw them
    while msg := await anext(messages_agen, None):
        # str message represents an intermediate token being streamed
        if isinstance(msg, str):
            # If placeholder is empty, this is the first token of a new message
            # being streamed. We need to do setup.
            if not streaming_placeholder:
                if last_message_type != "ai":
                    last_message_type = "ai"
                    st.session_state.last_message = st.chat_message("ai")
                with st.session_state.last_message:
                    streaming_placeholder = st.empty()

            streaming_content += msg
            streaming_placeholder.write(streaming_content)
            continue
        if not isinstance(msg, ChatMessage):
            st.error(f"Unexpected message type: {type(msg)}")
            st.write(msg)
            st.stop()
        match msg.type:
            # A message from the user, the easiest case
            case "human":
                last_message_type = "human"
                st.chat_message("human").write(msg.content)

            # A message from the agent is the most complex case, since we need to
            # handle streaming tokens and tool calls.
            case "ai":
                # If we're rendering new messages, store the message in session state
                if is_new:
                    st.session_state.messages.append(msg)

                # If the last message type was not AI, create a new chat message
                if last_message_type != "ai":
                    last_message_type = "ai"
                    st.session_state.last_message = st.chat_message("ai")

                with st.session_state.last_message:
                    # If the message has content, write it out.
                    # Reset the streaming variables to prepare for the next message.
                    if msg.content:
                        if streaming_placeholder:
                            streaming_placeholder.write(msg.content)
                            streaming_content = ""
                            streaming_placeholder = None
                        else:
                            st.write(msg.content)

                    if msg.tool_calls:
                        # Create a status container for each tool call and store the
                        # status container by ID to ensure results are mapped to the
                        # correct status container.
                        call_results = {}
                        for tool_call in msg.tool_calls:
                            status = st.status(
                                f"""Tool Call: {tool_call["name"]}""",
                                state="running" if is_new else "complete",
                            )
                            call_results[tool_call["id"]] = status
                            status.write("Input:")
                            status.write(tool_call["args"])

                        # Expect one ToolMessage for each tool call.
                        for _ in range(len(call_results)):
                            tool_result: ChatMessage = await anext(messages_agen)
                            if tool_result.type != "tool":
                                st.error(
                                    f"Unexpected ChatMessage type: {tool_result.type}"
                                )
                                st.write(tool_result)
                                st.stop()

                            # Record the message if it's new, and update the correct
                            # status container with the result
                            if is_new:
                                st.session_state.messages.append(tool_result)
                            status = call_results[tool_result.tool_call_id]
                            status.write("Output:")
                            status.write(tool_result.content)
                            status.update(state="complete")

            case "custom":
                # CustomData example used by the bg-task-agent
                # See:
                # - src/agents/utils.py CustomData
                # - src/agents/bg_task_agent/task.py
                try:
                    task_data: TaskData = TaskData.model_validate(msg.custom_data)
                except ValidationError:
                    st.error("Unexpected CustomData message received from agent")
                    st.write(msg.custom_data)
                    st.stop()

                if is_new:
                    st.session_state.messages.append(msg)

                if last_message_type != "task":
                    last_message_type = "task"
                    st.session_state.last_message = st.chat_message(
                        name="task", avatar=":material/manufacturing:"
                    )
                    with st.session_state.last_message:
                        status = TaskDataStatus()

                status.add_and_draw_task_data(task_data)

            # In case of an unexpected message type, log an error and stop
            case _:
                st.error(f"Unexpected ChatMessage type: {msg.type}")
                st.write(msg)
                st.stop()


async def handle_feedback() -> None:
    """Draws a feedback widget and records feedback from the user."""

    # Keep track of last feedback sent to avoid sending duplicates
    if "last_feedback" not in st.session_state:
        st.session_state.last_feedback = (None, None)

    latest_run_id = st.session_state.messages[-1].run_id
    feedback = st.feedback("stars", key=latest_run_id)

    # If the feedback value or run ID has changed, send a new feedback record
    if (
        feedback is not None
        and (latest_run_id, feedback) != st.session_state.last_feedback
    ):
        # Normalize the feedback value (an index) to a score between 0 and 1
        normalized_score = (feedback + 1) / 5.0

        agent_client: AgentClient = st.session_state.agent_client
        try:
            await agent_client.acreate_feedback(
                run_id=latest_run_id,
                key="human-feedback-stars",
                score=normalized_score,
                kwargs={"comment": "In-line human feedback"},
            )
        except AgentClientError as e:
            st.error(f"Error recording feedback: {e}")
            st.stop()
        st.session_state.last_feedback = (latest_run_id, feedback)
        st.toast("Feedback recorded", icon=":material/reviews:")


if __name__ == "__main__":
    asyncio.run(main())
