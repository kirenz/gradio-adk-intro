"""
Simple Time Agent with Google ADK and Gradio.

A single-file example that demonstrates how to create a Gradio interface
for an agent that can tell the current time.

=== What is Google ADK? ===
The Agent Development Kit (ADK) is a framework from Google for building
AI agents. An "Agent" is an LLM (Large Language Model) that:
1. Can follow instructions
2. Can call tools (functions) to perform tasks
3. Can conduct conversations and maintain context

=== What is Gradio? ===
Gradio is a Python framework that allows you to quickly create web interfaces
for AI applications. It converts Python functions into interactive web apps -
without requiring HTML/CSS/JavaScript knowledge.
"""

import asyncio
import gradio as gr
from google.genai import types

# Import the agent and runner from the time_agent package
from time_agent import runner


# ============================================================================
# Session Management
# ============================================================================

# Global Session ID
# A session is like a "conversation thread". It stores the history
# of all messages between user and agent.
# We store the ID globally so it persists across multiple function calls
# and the conversation can be continued.
SESSION_ID = None


# ============================================================================
# Chat Processing Function (Asynchronous)
# ============================================================================

async def chat_with_agent_async(message: str) -> str:
    """
    Sends a message to the agent and returns the response.

    Flow:
    1. Create/reuse session (for conversation context)
    2. Format message in the correct format (Content object)
    3. Send message to the agent
    4. Wait for events and extract final response

    Args:
        message: The user's text message

    Returns:
        The agent's text response
    """
    global SESSION_ID

    # --- Session Management ---
    if SESSION_ID is None:
        session = await runner.session_service.create_session(
            user_id='gradio_user',
            app_name='root_agent'
        )
        SESSION_ID = session.id

    # --- Format Message ---
    content = types.Content(
        role='user',
        parts=[types.Part(text=message)]
    )

    # --- Execute Agent ---
    response_text = ""
    events_async = runner.run_async(
        user_id='gradio_user',
        session_id=SESSION_ID,
        new_message=content
    )

    # --- Iterate Through Events ---
    async for event in events_async:
        if event.is_final_response() and event.content and event.content.parts:
            response_text = event.content.parts[0].text
            break

    return response_text


# ============================================================================
# Synchronous Wrapper for Gradio
# ============================================================================

def chat_with_agent(message: str, history: list) -> str:
    """
    Synchronous wrapper for asynchronous agent communication.

    Args:
        message: The user's text message
        history: The previous chat history (managed by Gradio, not used here)

    Returns:
        The agent's text response, or an error message
    """
    try:
        response = asyncio.run(chat_with_agent_async(message))
        return response
    except Exception as e:
        return f"Error: {str(e)}"


def reset_session():
    """
    Resets the session to start a new conversation.

    Returns:
        Empty list to clear the chat history in the UI
    """
    global SESSION_ID
    SESSION_ID = None
    return []


# ============================================================================
# Gradio User Interface
# ============================================================================

with gr.Blocks(title="Google ADK Time Agent") as demo:

    # --- Headings ---
    gr.Markdown("# Time Agent with Google ADK")
    gr.Markdown("Ask the agent for the current time! The agent itself doesn't know what time it is – it must use its tool.")

    # --- Chatbot Component ---
    chatbot = gr.Chatbot(
        label="Chat",
        height=400
    )

    # --- Text Input ---
    msg = gr.Textbox(
        label="Your Message",
        placeholder="e.g., 'What time is it?' or 'How late is it?'",
        lines=1
    )

    # --- Reset Button ---
    clear = gr.Button("Clear Chat")

    # --- Examples ---
    gr.Examples(
        examples=[
            ["What time is it?"],
            ["Can you tell me the time?"],
            ["What's the current time?"],
            ["Hello, do you know what time it is right now?"],
        ],
        inputs=msg
    )

    # --- Event Handler Function ---
    def respond(message: str, chat_history: list):
        """
        Processes the user message and updates the chat.

        Args:
            message: The user's entered message
            chat_history: The previous chat history (list of dicts)

        Returns:
            Tuple of:
            - "" (empty string to clear the text field)
            - chat_history (updated chat history)
        """
        bot_response = chat_with_agent(message, chat_history)

        chat_history.append({"role": "user", "content": message})
        chat_history.append({"role": "assistant", "content": bot_response})

        return "", chat_history

    # --- Connect Events ---
    msg.submit(
        fn=respond,
        inputs=[msg, chatbot],
        outputs=[msg, chatbot]
    )

    clear.click(
        fn=reset_session,
        inputs=None,
        outputs=chatbot
    )


# ============================================================================
# Program Start
# ============================================================================

if __name__ == "__main__":
    demo.launch()
