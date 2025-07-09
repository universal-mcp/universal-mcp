# Start of Selection
import asyncio
import os
import uuid
from collections.abc import AsyncGenerator
from pathlib import Path

import streamlit as st
from pydantic import ValidationError
from streamlit.runtime.scriptrunner import get_script_run_ctx

from playground.client import AgentClient, AgentClientError, create_agent_client
from playground.schema import ChatHistory, ChatMessage, TaskData, TaskDataStatus, AppChoiceData
from playground.settings import settings

# A Streamlit app for interacting with the langgraph agent via a simple chat interface.
# The app uses a flex layout: messages take most of the viewport, input sticks to the bottom.

APP_TITLE = "MCP Playground"
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
    # Configure page layout
    st.set_page_config(
        page_title=APP_TITLE,
        page_icon=APP_ICON,
        layout="wide",
        initial_sidebar_state="collapsed",
        menu_items={},
    )

    # Custom CSS for chat layout and styling
    st.markdown(
        """
        <style>
        /* Hide Streamlit default header and footer */
        #MainMenu, header, footer {
            visibility: hidden;
        }

        /* Light theme base styling */
        body {
            background-color: #f8f9fa;
            color: #212529;
            font-family: 'Segoe UI', Roboto, Arial, sans-serif;
        }

        /* Remove default container styling */
        .main .block-container {
            padding: 0;
            margin: 0 auto;
            max-width: none;
            background: none;
            box-shadow: none;
        }

        /* Chat container layout */
        .chat-app {
            display: flex;
            flex-direction: column;
            height: 100vh;
            max-width: 1000px;
            margin: 0 auto;
        }

        /* File uploader expander styling */
        .chat-app .streamlit-expanderHeader {
            background-color: #e9ecef;
            color: #212529 !important;
            border: 1px solid #ced4da;
            border-radius: 0.5rem;
            padding: 1rem;
            margin: 1rem 2rem;
        }
        .chat-app .streamlit-expanderContent {
            background-color: #ffffff;
            border: 1px solid #ced4da;
            border-top: none;
            border-radius: 0 0 0.5rem 0.5rem;
            padding: 1rem 2rem;
            margin: 0 2rem 1rem;
        }

        /* Message area styling */
        .chat-app .message-area {
            flex: 1;
            overflow-y: auto;
            background-color: #ffffff;
            border: 1px solid #ced4da;
            border-radius: 0.5rem;
            padding: 1rem 2rem;
            margin: 1rem 2rem;
        }
        .chat-app .message-area::-webkit-scrollbar {
            width: 6px;
        }
        .chat-app .message-area::-webkit-scrollbar-thumb {
            background-color: #adb5bd;
            border-radius: 3px;
        }

        /* Chat input area styling */
        .chat-app .chat-input-area {
            position: sticky;
            bottom: 0;
            background-color: #ffffff;
            border-top: 1px solid #ced4da;
            padding: 1rem 2rem;
            margin: 0 2rem 1rem;
            z-index: 100;
        }
        .chat-app .chat-input-area .stButton > button {
            background-color: #007bff;
            color: #ffffff;
            border: none;
            border-radius: 0.25rem;
            padding: 0.5rem 1rem;
        }

        /* Chat message bubbles */
        .stChatMessage {
            max-width: 60%;
            border: 1px solid #ced4da;
            border-radius: 0.75rem;
            padding: 0.75rem 1rem;
            margin: 0.5rem 0;
            font-size: 0.95rem;
            color: #212529;
        }
        .stChatMessage[data-testid="stChatMessage"][aria-label="user message"] {
            background-color: #cce5ff;
            border-color: #b8daff;
            margin-left: 20%;
            border-bottom-right-radius: 0.25rem;
        }
        .stChatMessage[data-testid="stChatMessage"][aria-label="assistant message"] {
            background-color: #e2e3e5;
            border-color: #d6d8db;
            margin-right: 20%;
            border-bottom-left-radius: 0.25rem;
        }
        </style>
    """,
        unsafe_allow_html=True,
    )

    # Minimal toolbar
    if st.get_option("client.toolbarMode") != "minimal":
        st.set_option("client.toolbarMode", "minimal")
        await asyncio.sleep(0.1)
        st.rerun()

    # Title/header
    col1, _ = st.columns([2, 1])
    with col1:
        st.title(f"{APP_ICON} {APP_TITLE}")

    # Agent type selection
    if "agent_type" not in st.session_state:
        st.session_state.agent_type = "react"
    
    agent_type = st.selectbox(
        "Select Agent Type",
        ["react", "auto"],
        index=0 if st.session_state.agent_type == "react" else 1,
        help="React Agent: Traditional MCP-based agent. Auto Agent: Task decomposition and app selection agent."
    )
    
    if agent_type != st.session_state.agent_type:
        st.session_state.agent_type = agent_type
        st.session_state.messages = []  # Clear messages when switching agents
        st.rerun()

    # Agent configuration
    if agent_type == "auto":
        with st.expander("⚙️ Auto Agent Configuration", expanded=False):
            col1, col2, col3 = st.columns(3)
            with col1:
                app_limit = st.number_input("App Limit", min_value=1, max_value=20, value=5, help="Maximum number of apps to consider")
            with col2:
                action_limit = st.number_input("Action Limit", min_value=1, max_value=50, value=10, help="Maximum number of actions to consider per app")
            with col3:
                interactive = st.checkbox("Interactive Mode", value=False, help="Allow user to choose between multiple apps")
            
            st.session_state.agent_config = {
                "app_limit": app_limit,
                "action_limit": action_limit,
                "interactive": interactive
            }
    else:
        st.session_state.agent_config = {}

    # --- Initialize Agent Client ---
    # Initialize agent client only once per session
    if "agent_client" not in st.session_state or st.session_state.get("agent_type") != agent_type:
        st.session_state.agent_type = agent_type
        # Create agent client and store it in session state
        agent_client = await create_agent_client(agent_type=agent_type).__aenter__()
        st.session_state.agent_client = agent_client
        st.session_state.agent_client_context = create_agent_client(agent_type=agent_type)
    
    agent_client = st.session_state.agent_client

    # --- Ensure Upload Directory Exists ---
    uploads_dir = settings.DATA_DIR / "uploads"
    try:
        uploads_dir.mkdir(parents=True, exist_ok=True)
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

    # Initialize session state
    if "thread_id" not in st.session_state:
        thread_id = st.query_params.get("thread_id")
        if not thread_id:
            thread_id = get_script_run_ctx().session_id
            messages = []
        else:
            try:
                messages: ChatHistory = agent_client.get_history(thread_id=thread_id).messages
            except AgentClientError:
                st.error("No message history found for this Thread ID.")
                messages = []
        st.session_state.thread_id = thread_id
        st.session_state.messages = messages
        st.session_state.uploaded_file_obj = None
        st.session_state.file_processed = False

    # Start chat app layout
    st.markdown('<div class="chat-app">', unsafe_allow_html=True)

    # File uploader expander
    with st.expander("📎 Upload File", expanded=False):
        uploaded_file = st.file_uploader(
            "Upload a file to process",
            type=None,
            key="file_uploader",
            help="Upload any file to process with the AI assistant",
        )

    # Handle file upload state
    if uploaded_file is not None:
        if (
            "last_processed_file" not in st.session_state
            or st.session_state.get("last_processed_file") != uploaded_file.name
        ):
            st.session_state.file_processed = False
            st.session_state.uploaded_file_obj = uploaded_file
            st.info(
                f"File '{uploaded_file.name}' ready for processing with your next message.",
                icon="📄",
            )
    elif uploaded_file is None and st.session_state.get("uploaded_file_obj") is not None:
        st.session_state.uploaded_file_obj = None
        st.session_state.file_processed = False
        if "last_processed_file" in st.session_state:
            del st.session_state["last_processed_file"]

    # Message display area: only render container if there are past messages
    messages: list[ChatMessage] = st.session_state.messages

    if not messages:
        if agent_type == "auto":
            WELCOME = (
                "Hello! I am your Auto Agent that can decompose complex tasks and automatically "
                "select the best apps and actions to complete them. Just describe what you want to do, "
                "and I'll break it down into steps and execute them for you."
            )
        else:
            WELCOME = (
                "Hello. I am your AI assistant with access to "
                "a wide variety of tools. You can enable/disable "
                "desired tools at agentr.dev/apps."
            )
        with st.chat_message("ai", avatar="🤖"):
            st.write(WELCOME)
    else:
        st.markdown('<div class="message-area">', unsafe_allow_html=True)

        async def amessage_iter() -> AsyncGenerator[ChatMessage, None]:
            for m in messages:
                yield m

        await draw_messages(amessage_iter())
        st.markdown("</div>", unsafe_allow_html=True)

    # Chat input area
    st.markdown('<div class="chat-input-area">', unsafe_allow_html=True)
    
    # Check if we're waiting for app choices
    if "waiting_for_app_choice" in st.session_state and st.session_state.waiting_for_app_choice:
        # Show app choice UI
        choice_data = st.session_state.app_choice_data
        user_choices = await handle_app_choice_ui(choice_data)
        
        if user_choices is not None:
            # User has made their choices, execute the task
            st.session_state.waiting_for_app_choice = False
            del st.session_state.app_choice_data
            
            # Execute task with choices
            try:
                result = await agent_client.run_with_choices(
                    message=st.session_state.pending_task,
                    frontend_choices=user_choices,
                    thread_id=st.session_state.thread_id,
                    agent_config=st.session_state.agent_config,
                )
                
                # Add the result as an AI message
                response = ChatMessage(type="ai", content=result)
                messages.append(response)
                st.chat_message("ai", avatar="🤖").write(result)
                
                # Clear pending task
                del st.session_state.pending_task
                # Ensure chat input reappears after task completion
                st.rerun()
            except AgentClientError as e:
                st.error(f"Error executing task: {e}")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")
    else:
        # Normal chat input
        if user_input := st.chat_input("Enter message or upload a file and describe task...", key="chat_input"):
            final_message_content = user_input
            display_content = user_input

            # --- Handle File Upload Integration ---
            if st.session_state.uploaded_file_obj and not st.session_state.file_processed:
                uploaded_file_obj = st.session_state.uploaded_file_obj
                original_filename = uploaded_file_obj.name
                try:
                    save_filepath = get_unique_filepath(uploads_dir, original_filename)
                    file_bytes = uploaded_file_obj.getvalue()
                    save_filepath.write_bytes(file_bytes)
                    absolute_filepath_str = str(save_filepath.resolve())
                    file_metadata_prefix = (
                        f"[User uploaded file named '{original_filename}'. "
                        f"It has been saved at the following absolute path: "
                        f"{absolute_filepath_str}]\n\n"
                    )
                    final_message_content = file_metadata_prefix + user_input
                    display_content = f"[Using uploaded file: {original_filename}]\n\n{user_input}"
                    st.session_state.last_processed_file = original_filename
                    st.session_state.file_processed = True
                except OSError as e:
                    st.error(f"Error saving uploaded file '{original_filename}': {e}")
                    st.stop()
                except Exception as e:
                    st.error(f"An unexpected error occurred during file handling: {e}")
                    st.stop()
            # --- End File Upload Integration ---

            messages.append(ChatMessage(type="human", content=final_message_content))
            st.chat_message("human", avatar="👤").write(display_content)
            
            # For auto agent, check if we need app choices
            if agent_type == "auto":
                try:
                    # Get choice data
                    choice_data = await agent_client.get_choice_data(
                        message=final_message_content,
                        thread_id=st.session_state.thread_id,
                        agent_config=st.session_state.agent_config,
                    )
                    
                    if choice_data['requires_app'] and choice_data['app_sets']:
                        # User choice needed, show choice UI
                        st.session_state.waiting_for_app_choice = True
                        st.session_state.app_choice_data = choice_data
                        st.session_state.pending_task = final_message_content
                        st.rerun()
                    elif choice_data['requires_app'] and choice_data['auto_selected']:
                        # All apps auto-selected, execute directly
                        try:
                            result = await agent_client.run_with_choices(
                                message=final_message_content,
                                frontend_choices={"auto_selected": choice_data['auto_selected'], "user_choices": {}},
                                thread_id=st.session_state.thread_id,
                                agent_config=st.session_state.agent_config,
                            )
                            
                            # Add the result as an AI message
                            response = ChatMessage(type="ai", content=result)
                            messages.append(response)
                            st.chat_message("ai", avatar="🤖").write(result)
                            # Ensure chat input reappears after task completion
                            st.rerun()
                        except AgentClientError as e:
                            st.error(f"Error executing task: {e}")
                        except Exception as e:
                            st.error(f"An unexpected error occurred: {e}")
                    else:
                        # No app choice needed, proceed with normal execution
                        if use_streaming:
                            stream = agent_client.astream(
                                message=final_message_content,
                                thread_id=st.session_state.thread_id,
                                agent_config=st.session_state.agent_config,
                            )
                            await draw_messages(stream, is_new=True)
                        else:
                            response = await agent_client.ainvoke(
                                message=final_message_content,
                                thread_id=st.session_state.thread_id,
                                agent_config=st.session_state.agent_config,
                            )
                            messages.append(response)
                            st.chat_message("ai", avatar="🤖").write(response.content)
                            # Ensure chat input reappears after task completion
                            st.rerun()
                except AgentClientError as e:
                    st.error(f"Error getting choice data: {e}")
                except Exception as e:
                    st.error(f"An unexpected error occurred: {e}")
            else:
                # For react agent, proceed with normal execution
                try:
                    if use_streaming:
                        stream = agent_client.astream(
                            message=final_message_content,
                            thread_id=st.session_state.thread_id,
                            agent_config=st.session_state.agent_config,
                        )
                        await draw_messages(stream, is_new=True)
                    else:
                        response = await agent_client.ainvoke(
                            message=final_message_content,
                            thread_id=st.session_state.thread_id,
                            agent_config=st.session_state.agent_config,
                        )
                        messages.append(response)
                        st.chat_message("ai", avatar="🤖").write(response.content)
                        # Ensure chat input reappears after task completion
                        st.rerun()
                except AgentClientError as e:
                    st.error(f"Error generating response: {e}")
                except Exception as e:
                    st.error(f"An unexpected error occurred during agent communication: {e}")
    st.markdown("</div>", unsafe_allow_html=True)

    # End chat app wrapper
    st.markdown("</div>", unsafe_allow_html=True)


async def draw_messages(
    messages_agen: AsyncGenerator[ChatMessage | str, None],
    is_new: bool = False,
) -> None:
    """
    Draws a set of chat messages - either replaying existing messages
    or streaming new ones.
    """
    last_message_type = None
    st.session_state.last_message = None
    streaming_content = ""
    streaming_placeholder = None

    while msg := await anext(messages_agen, None):
        if isinstance(msg, str):
            if not streaming_placeholder:
                if last_message_type != "ai":
                    last_message_type = "ai"
                    st.session_state.last_message = st.chat_message("ai", avatar="🤖")
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
            case "human":
                last_message_type = "human"
                st.chat_message("human", avatar="👤").write(msg.content)
            case "ai":
                if is_new:
                    st.session_state.messages.append(msg)
                if last_message_type != "ai":
                    last_message_type = "ai"
                    st.session_state.last_message = st.chat_message("ai", avatar="🤖")
                with st.session_state.last_message:
                    if msg.content:
                        if streaming_placeholder:
                            streaming_placeholder.write(msg.content)
                            streaming_content = ""
                            streaming_placeholder = None
                        else:
                            st.write(msg.content)
                    if msg.tool_calls:
                        call_results = {}
                        for tool_call in msg.tool_calls:
                            status = st.status(
                                f"Tool Call: {tool_call['name']}",
                                state="running" if is_new else "complete",
                            )
                            call_results[tool_call["id"]] = status
                            status.write("Input:")
                            status.write(tool_call["args"])
                        for _ in range(len(call_results)):
                            tool_result: ChatMessage = await anext(messages_agen)
                            if tool_result.type != "tool":
                                st.error(f"Unexpected ChatMessage type: {tool_result.type}")
                                st.write(tool_result)
                                st.stop()
                            if is_new:
                                st.session_state.messages.append(tool_result)
                            status = call_results[tool_result.tool_call_id]
                            status.write("Output:")
                            status.write(tool_result.content)
                            status.update(state="complete")
            case "custom":
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
                    st.session_state.last_message = st.chat_message(name="task", avatar="⚙️")
                    with st.session_state.last_message:
                        status = TaskDataStatus()
                status.add_and_draw_task_data(task_data)
            case "app_choice":
                if is_new:
                    st.session_state.messages.append(msg)
                if last_message_type != "app_choice":
                    last_message_type = "app_choice"
                    st.session_state.last_message = st.chat_message(name="app_choice", avatar="🤖")
                with st.session_state.last_message:
                    st.write("App selection required")
                    st.write(msg.content)
            case _:
                st.error(f"Unexpected ChatMessage type: {msg.type}")
                st.write(msg)
                st.stop()


async def handle_app_choice_ui(choice_data: dict) -> dict | None:
    """Handle app choice UI and return user selections."""
    st.markdown("### 🤖 App Selection Required")
    st.markdown(f"**Task:** {choice_data['task']}")
    st.markdown(f"**Reasoning:** {choice_data['reasoning']}")
    
    if not choice_data['requires_app']:
        st.info("This task doesn't require any external apps and can be completed with general reasoning.")
        return None
    
    if not choice_data['app_sets'] and not choice_data['auto_selected']:
        st.warning("No suitable apps found for this task.")
        return None
    
    # Show auto-selected apps
    if choice_data['auto_selected']:
        st.markdown("**Automatically Selected Apps:**")
        for app_id in choice_data['auto_selected']:
            st.markdown(f"- ✅ {app_id}")
    
    # Handle user choices for app sets
    user_choices = {}
    
    for app_set in choice_data['app_sets']:
        set_index = app_set['set_index']
        apps = app_set['apps']
        
        st.markdown(f"**App Set {set_index}:**")
        
        # Create checkboxes for each app
        selected_apps = []
        for app in apps:
            app_id = app['id']
            app_name = app['name']
            app_category = app.get('category', 'Unknown')
            app_description = app.get('description', 'No description available')
            
            # Create a unique key for each checkbox
            checkbox_key = f"app_{set_index}_{app_id}"
            
            if st.checkbox(
                f"**{app_name}** ({app_category})",
                key=checkbox_key,
                help=app_description
            ):
                selected_apps.append(app_id)
        
        if selected_apps:
            user_choices[str(set_index)] = selected_apps
    
    # Create the final choice data
    final_choices = {
        "auto_selected": choice_data['auto_selected'],
        "user_choices": user_choices
    }
    
    # Add a submit button
    if st.button("🚀 Execute Task with Selected Apps", type="primary"):
        return final_choices
    
    return None

async def handle_feedback() -> None:
    """Draws a feedback widget and records feedback from the user."""
    if "last_feedback" not in st.session_state:
        st.session_state.last_feedback = (None, None)
    latest_run_id = st.session_state.messages[-1].run_id
    feedback = st.feedback("stars", key=latest_run_id)
    if feedback is not None and (latest_run_id, feedback) != st.session_state.last_feedback:
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
        st.toast("Feedback recorded", icon="⭐")


if __name__ == "__main__":
    asyncio.run(main())
# End of Selectio
