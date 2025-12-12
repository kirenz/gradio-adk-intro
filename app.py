"""
Simple Time Agent with Google ADK and Gradio.

A single-file example that demonstrates how to create an agent with tools
that can tell the current time in different cities.

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

import asyncio  # For asynchronous programming (async/await)
import gradio as gr  # Gradio framework for the web interface
from dotenv import load_dotenv  # Loads environment variables from .env file
from google.genai import types  # Data types for Google GenAI (Content, Part)
from google.adk.agents.llm_agent import Agent  # The Agent class from ADK
from google.adk.runners import InMemoryRunner  # Runner for executing agents

from tools import get_current_time  # Import the tool function

# Load environment variables (e.g., GOOGLE_API_KEY from .env file)
# This is necessary for the agent to authenticate with Google
load_dotenv()


# ============================================================================
# Agent and Runner Setup
# ============================================================================
# The agent is the "brain" - it understands requests and decides what to do.
# The runner is the "manager" - it executes the agent and manages sessions.
# ============================================================================

# --- Create Agent ---
# The agent is an instance that connects the LLM (Gemini) with tools.
# It's like a virtual assistant with special capabilities.
root_agent = Agent(
    # The AI model used (Gemini 2.0 Flash is fast and efficient)
    model='gemini-2.0-flash',

    # Internal name of the agent (for logging and referencing)
    name='root_agent',

    # Brief description of what the agent can do (helps in multi-agent systems)
    description="A helpful assistant that can tell the current time.",

    # The "personality" and behavioral instructions for the agent.
    # These instructions influence HOW the agent responds.
    instruction="""
    You are a helpful assistant.
    When the user asks for the time, use the 'get_current_time' tool.
    You yourself do NOT know what time it is - you MUST use the tool!
    Respond in the same language as the user's question.
    Be friendly and precise in your answer.
    """,

    # List of available tools (functions) that the agent can call.
    # The agent automatically analyzes the function signature and docstring
    # to understand when and how to use the tool.
    tools=[get_current_time],
)

# --- Create Runner ---
# The InMemoryRunner is the "execution manager" for the agent.
# It handles:
# 1. Session management: Stores conversation histories (in memory)
# 2. Message processing: Forwards messages to the agent
# 3. Event handling: Returns responses and intermediate results
#
# "InMemory" means all data is stored in RAM.
# On restart, all conversations are lost.
# For "real" applications, there are also persistent runners (e.g., with database).
runner = InMemoryRunner(
    agent=root_agent,  # The agent to be executed
    app_name='root_agent'  # Application name (for session grouping)
)

# --- Global Session ID ---
# A session is like a "conversation thread". It stores the history
# of all messages between user and agent.
# We store the ID globally so it persists across multiple function calls
# and the conversation can be continued.
SESSION_ID = None


# ============================================================================
# Chat Processing Function (Asynchronous)
# ============================================================================
# This function is the core of agent communication.
# It's "async" because communication with the Gemini API takes time
# and we don't want to block (other requests could run in parallel).
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
    global SESSION_ID  # Access the global session ID

    # --- Session Management ---
    # A session only needs to be created ONCE.
    # After that, we use the same session ID for all further messages,
    # so the agent can "remember" previous messages.
    if SESSION_ID is None:
        # Create new session via the runner's session service
        session = await runner.session_service.create_session(
            user_id='gradio_user',  # Unique user ID
            app_name='root_agent'  # App name for grouping
        )
        SESSION_ID = session.id  # Store session ID for later use

    # --- Format Message ---
    # ADK expects messages in Google GenAI's "Content" format.
    # - role='user': Marks the message as user input
    # - parts: List of message parts (here only one text part)
    content = types.Content(
        role='user',
        parts=[types.Part(text=message)]
    )

    # --- Execute Agent ---
    # run_async() starts processing and returns an AsyncGenerator.
    # The agent can produce multiple "events":
    # - Tool calls (e.g., get_current_time is called)
    # - Intermediate responses
    # - Final response (is_final_response() == True)
    response_text = ""
    events_async = runner.run_async(
        user_id='gradio_user',  # Must match the session
        session_id=SESSION_ID,  # Our stored session ID
        new_message=content  # The formatted user message
    )

    # --- Iterate Through Events ---
    # We iterate over all events until we find the final response.
    # "async for" is like a for loop, but for asynchronous generators.
    async for event in events_async:
        # Check if this is the final response (not just an intermediate step)
        if event.is_final_response() and event.content and event.content.parts:
            # Extract text from the first part
            response_text = event.content.parts[0].text
            break  # We have the response, exit the loop

    return response_text


# ============================================================================
# Synchronous Wrapper for Gradio
# ============================================================================
# Gradio components normally expect synchronous functions.
# Since our agent function is asynchronous (async), we need a "wrapper"
# that calls the asynchronous function from a synchronous one.
# ============================================================================

def chat_with_agent(message: str, history: list) -> str:
    """
    Synchronous wrapper for asynchronous agent communication.

    Gradio calls this function when the user sends a message.
    It uses asyncio.run() to execute the asynchronous function.

    Args:
        message: The user's text message
        history: The previous chat history (managed by Gradio, not used here)

    Returns:
        The agent's text response, or an error message
    """
    try:
        # asyncio.run() executes an async function and waits for the result
        response = asyncio.run(chat_with_agent_async(message))
        return response
    except Exception as e:
        # On errors (e.g., API errors) return a readable message
        return f"Error: {str(e)}"


def reset_session():
    """
    Resets the session to start a new conversation.

    Called when the user clicks "Clear Chat".
    By resetting the SESSION_ID, a completely new session will be created
    on the next call - the agent "forgets" everything.

    Returns:
        Empty list to clear the chat history in the UI
    """
    global SESSION_ID
    SESSION_ID = None  # Reset session ID
    return []  # Empty list = empty chat in Gradio


# ============================================================================
# Gradio User Interface
# ============================================================================
# Gradio offers two main approaches:
# 1. gr.Interface() - Simple, but less flexible
# 2. gr.Blocks() - Flexible, full control over layout and interactions
#
# Here we use gr.Blocks() because we:
# - Have a chatbot with multiple components
# - Want to define custom event handlers
# - Want to add examples and a reset button
# ============================================================================

# gr.Blocks() creates a context for UI definition
# Everything within the "with" block belongs to this UI
with gr.Blocks(title="Google ADK Time Agent") as demo:

    # --- Headings (Markdown Components) ---
    # gr.Markdown() renders Markdown text as HTML
    gr.Markdown("# Time Agent with Google ADK")
    gr.Markdown("Ask the agent for the current time! The agent itself doesn't know what time it is – it must use its tool.")

    # --- Chatbot Component ---
    # gr.Chatbot() displays the conversation history (user and bot messages)
    # The format is a list of dictionaries: {"role": "user/assistant", "content": "..."}
    chatbot = gr.Chatbot(
        label="Chat",  # Label above the component
        height=400  # Height in pixels
    )

    # --- Text Input ---
    # gr.Textbox() is an input field for text
    msg = gr.Textbox(
        label="Your Message",  # Label
        placeholder="e.g., 'What time is it?' or 'How late is it?'",
        lines=1  # Single-line input
    )

    # --- Reset Button ---
    # gr.Button() creates a clickable button
    clear = gr.Button("Clear Chat")

    # --- Examples ---
    # gr.Examples() displays clickable example inputs
    # When the user clicks on them, the text is inserted into the input field
    gr.Examples(
        examples=[
            ["What time is it?"],
            ["Can you tell me the time?"],
            ["What's the current time?"],
            ["Hello, do you know what time it is right now?"],
        ],
        inputs=msg  # The component into which the example is inserted
    )

    # --- Event Handler Function ---
    # This function is called when the user submits a message
    def respond(message: str, chat_history: list):
        """
        Processes the user message and updates the chat.

        Flow:
        1. Send message to the agent and receive response
        2. Add user message to chat history
        3. Add bot response to chat history
        4. Clear text field and return updated chat

        Args:
            message: The user's entered message
            chat_history: The previous chat history (list of dicts)

        Returns:
            Tuple of:
            - "" (empty string to clear the text field)
            - chat_history (updated chat history)
        """
        # Get response from the agent
        bot_response = chat_with_agent(message, chat_history)

        # Add messages to history (Gradio chat format)
        chat_history.append({"role": "user", "content": message})
        chat_history.append({"role": "assistant", "content": bot_response})

        # Return: Empty text field + updated chat
        return "", chat_history

    # --- Connect Events ---
    # .submit() is triggered when Enter is pressed
    # Parameters: (function, [input components], [output components])
    msg.submit(
        fn=respond,  # The function to call
        inputs=[msg, chatbot],  # Values passed to the function
        outputs=[msg, chatbot]  # Components updated with the return values
    )

    # .click() is triggered when the button is clicked
    clear.click(
        fn=reset_session,  # Function to reset
        inputs=None,  # No inputs needed
        outputs=chatbot  # Updates the chatbot (with empty list)
    )


# ============================================================================
# Program Start
# ============================================================================
# This block is only executed when the script is run directly
# (not when it's imported as a module)
# ============================================================================

if __name__ == "__main__":
    # demo.launch() starts the Gradio web server
    # By default at http://127.0.0.1:7860
    # Optional parameters:
    # - share=True: Creates a public link (for demos)
    # - server_port=8080: Different port
    # - debug=True: More error output
    demo.launch()
