# Time Agent with Google ADK and Gradio

![Python Version](https://img.shields.io/badge/python-3.12-blue.svg)
![uv](https://img.shields.io/badge/uv-managed-430f8e.svg?style=flat&logo=python&logoColor=white)
![Gradio Version](https://img.shields.io/badge/gradio-6.1.0-orange.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

A simple but comprehensive example demonstrating how to build an AI agent using Google's Agent Development Kit (ADK) with a Gradio web interface. The agent can tell the current time by using custom tools.

## What You'll Learn

- **Agent Development**: Introduction to building AI agents with Google's ADK framework
- **Tool Usage**: How agents can use tools (custom functions) to perform tasks
- **LLM Integration**: Combining Large Language Model capabilities with custom functions
- **Async Programming**: Working with `async/await` for efficient API communication
- **Web UI**: Creating interactive interfaces with Gradio

## Project Structure

```
gradio-adk-intro/
├── time_agent/         # Agent package (works with both ADK web and Gradio)
│   ├── __init__.py     # Package initialization
│   ├── agent.py        # Main agent code and configuration
│   ├── tools.py        # Custom tool definitions
│   └── .env            # API key configuration (create this)
├── app.py              # Gradio UI application
├── .env                # API key configuration (root level)
└── README.md           # This file
```

## Prerequisites

- [uv](https://github.com/astral-sh/uv) installed (manages dependencies and virtual environment)
- A Google API key from [Google AI Studio](https://aistudio.google.com/api-keys)

## Setup

1. **Clone or download the repository**

   ```bash
   git clone https://github.com/kirenz/gradio-adk-intro
   ```

   Navigate into the project directory:

  ```bash
  cd gradio-adk-intro
  ```

2. **Install dependencies** (also creates the virtual environment)

   ```bash
   uv sync
   ```

3. **Get your API key** (free) from [Google AI Studio](https://aistudio.google.com/api-keys)


4. **Configure your API key**

   Rename the `.env.example` file to `.env` in both the project root and the `time_agent/` folder, and add your Google API key:

   ```bash
   GOOGLE_API_KEY=YourApiKeyHere
   ```

**Important**: The `.env` file is already listed in `.gitignore` and will **not** be committed to the repository, keeping your key private.


## Running the Application

### Option 1: Run with Gradio (Web UI)

Start the Time Agent application with Gradio interface:

```bash
uv run app.py
```

> **Note**: You may see a warning about "App name mismatch detected" - this can be safely ignored.

### Option 2: Run with ADK Web

Navigate to the `time_agent/` directory and run with ADK web:

```bash
cd time_agent
adk web
```

This will start the ADK web interface where you can interact with the agent. 

## How It Works

### The Agent

The agent is powered by Google's Gemini 2.0 Flash model and has been configured with:

- **Instructions**: Behavioral guidelines for how to respond to users
- **Tools**: Custom functions it can call (like `get_current_time`)
- **Session Management**: Maintains conversation context across messages

### The Tool

The `get_current_time()` function in `tools.py` demonstrates:

- How to create a tool that the agent can use
- Why agents need tools (LLMs don't know the current time)
- Proper return format (dictionary) for agent processing

### The Flow

1. User asks: "What time is it?"
2. Agent recognizes it needs the time
3. Agent calls `get_current_time()` tool
4. Tool returns current system time
5. Agent formulates a natural language response

### Expected Warning

When the agent uses a tool, you may see:

```
Warning: there are non-text parts in the response: ['function_call']
```

This is **normal and expected**! It just means the agent called a tool. The warning is informational and doesn't indicate a problem.

## Troubleshooting

### Port Already in Use

**Problem**: `OSError: [Errno 48] Address already in use`

**Solution**:
- Another Gradio app is still running. Stop it with `Ctrl + C`
- Or use a different port in `app.py`:
  ```python
  demo.launch(server_port=7861)
  ```

### API Authentication Error

**Problem**: `AuthenticationError` or `API key not found`

**Solution**:
- Check that `.env` file exists in the project root
- Ensure API key is entered correctly (without quotes)
- Verify the API key is active in Google AI Studio

### Module Not Found

**Problem**: `ModuleNotFoundError`

**Solution**:
```bash
uv sync
```

### Python Version Issues

**Problem**: Wrong Python version

**Solution**:
- `uv` automatically manages the correct Python version (3.11)
- If issues persist: run `uv sync` again

## Extending the Project

Want to add more capabilities? Try:

1. **Add New Tools**: Create functions in `tools.py` for weather, calculations, etc.
2. **Multi-Agent Systems**: Create multiple agents with different specializations
3. **Persistent Storage**: Switch from `InMemoryRunner` to a database-backed runner
4. **Enhanced UI**: Customize the Gradio interface with additional components

## Resources

- [Gradio Documentation](https://www.gradio.app/docs/)
- [Google ADK Documentation](https://ai.google.dev/adk)
- [Google Gemini API](https://ai.google.dev/docs)
- [uv Package Manager](https://github.com/astral-sh/uv)


