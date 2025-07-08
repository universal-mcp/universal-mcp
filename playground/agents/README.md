# Playground Agents

This directory contains different agent implementations for the playground.

## React Agent (`react.py`)

The traditional MCP-based agent that connects to MCP servers and uses tools via the Model Control Protocol.

## Auto Agent (`auto_agent.py`)

An intelligent agent that can:
- Decompose complex tasks into individual steps
- Automatically determine whether each task requires an external app or can be handled through general reasoning
- Search for and select relevant apps for tasks that need them
- Choose appropriate actions from those apps
- Execute tasks in sequence with context passing between steps

### Features

- **Task Decomposition**: Breaks down complex requests into manageable subtasks
- **Task Type Analysis**: Automatically determines whether tasks require external apps or can be handled through general reasoning
- **App Discovery**: Uses API search to find relevant applications for tasks that need them
- **Action Selection**: Intelligently chooses the best actions from available apps
- **Interactive Mode**: Allows user choice when multiple apps are available
- **Context Passing**: Results from previous tasks are passed to subsequent tasks
- **General Reasoning**: Handles tasks that don't require external apps using built-in knowledge and reasoning

### Configuration

The AutoAgent is configured via environment variables:

- `AUTO_AGENT_API_KEY`: Your AgentR API key (required)
- `AUTO_AGENT_API_BASE_URL`: Base URL for the backend API (default: http://localhost:8000)

Example:
```bash
export AUTO_AGENT_API_KEY="your_agentr_api_key_here"
export AUTO_AGENT_API_BASE_URL="http://localhost:8000"
```

### Usage

In the playground, select "Auto Agent" from the agent type dropdown. You can configure:

- **App Limit**: Maximum number of apps to consider (1-20)
- **Action Limit**: Maximum number of actions to consider per app (1-50)
- **Interactive Mode**: Allow user to choose between multiple apps

### Example Tasks

**Tasks requiring external apps:**
- "Search for the best places to eat in bangalore, covering important cuisines"
- "Find the latest news about AI and summarize the key points"
- "Search for Python tutorials and create a learning plan"

**Tasks that don't require external apps:**
- "Analyze the benefits and drawbacks of remote work"
- "Explain the concept of machine learning in simple terms"
- "Create a summary of effective communication principles"

**Mixed tasks:**
- "Analyze current AI trends and then search for the latest ChatGPT news"
- "Compare different programming paradigms and find tutorials for the best one"

The AutoAgent will automatically:
1. Decompose the task into subtasks
2. Analyze each subtask to determine if it requires an external app
3. For app-required tasks: Find relevant apps and select appropriate actions
4. For general reasoning tasks: Use built-in knowledge and analysis
5. Execute all tasks in sequence with context passing
6. Provide a comprehensive result 