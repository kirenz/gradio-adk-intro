"""
Time Agent - Main Agent Configuration

This module defines the agent that can tell the current time.
It can be used with both ADK web and Gradio interfaces.
"""

from dotenv import load_dotenv
from google.adk.agents.llm_agent import Agent
from google.adk.runners import InMemoryRunner

from .tools import get_current_time

# Load environment variables (e.g., GOOGLE_API_KEY from .env file)
load_dotenv()


# Create the Time Agent
root_agent = Agent(
    # The AI model used (Gemini 2.0 Flash is fast and efficient)
    model='gemini-2.0-flash',

    # Internal name of the agent (for logging and referencing)
    name='root_agent',

    # Brief description of what the agent can do
    description="A helpful assistant that can tell the current time.",

    # The "personality" and behavioral instructions for the agent
    instruction="""
    You are a helpful assistant.
    When the user asks for the time, use the 'get_current_time' tool.
    You yourself do NOT know what time it is - you MUST use the tool!
    Respond in the same language as the user's question.
    Be friendly and precise in your answer.
    """,

    # List of available tools that the agent can call
    tools=[get_current_time],
)


# Create the Runner
# The InMemoryRunner manages the agent execution and sessions
runner = InMemoryRunner(
    agent=root_agent,
    app_name='root_agent'
)
