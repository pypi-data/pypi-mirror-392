# Synq AI - Multi-Agent Interaction System

**Synq** is a Python SDK for orchestrating multi-agent AI conversations and interactions. Create intelligent agents, place them in sandboxes, and let them collaborate to solve complex tasks.

## 🚀 Installation

```bash
pip install synq-ai
```

## 📋 Requirements

- Python 3.8 or higher
- A running Synq server (see [Server Setup](#server-setup))
- API keys for AI providers (OpenAI, Anthropic, etc.)

## 🎯 Quick Start

```python
from synq import SynqClient, OutputFormat, OutputFormatType

# Initialize the client
client = SynqClient(base_url="http://localhost:8080")

# Create AI agents
client.create_agent(
    agent_id="analyst",
    provider="openai",
    model="gpt-4o-mini",
    system_prompt="You are a data analyst. Analyze information and provide insights.",
    api_key="your-openai-api-key"
)

client.create_agent(
    agent_id="writer",
    provider="openai",
    model="gpt-4o-mini",
    system_prompt="You are a writer. Transform analysis into clear narratives.",
    api_key="your-openai-api-key"
)

# Create a sandbox for agents to interact
sandbox = client.create_sandbox(
    sandbox_id="analysis_session",
    agent_ids=["analyst", "writer"],
    ttl_seconds=3600,
    output_format=OutputFormat(
        type=OutputFormatType.SUMMARY,
        instructions="Create a concise summary of the key findings."
    )
)

# Inject a message to start the conversation
client.inject_message(
    sandbox_id="analysis_session",
    from_agent="user",
    content="Analyze the impact of remote work on productivity."
)

# Start an AI conversation (agents talk to each other)
client.start_ai_conversation(
    sandbox_id="analysis_session",
    rounds=5
)

# Get the conversation history
messages = client.get_messages("analysis_session")
for msg in messages:
    print(f"{msg.from_agent_id}: {msg.payload}")

# Generate formatted output
output = client.generate_output("analysis_session")
print(output)

# Clean up
client.close_sandbox("analysis_session")
```

## 🏗️ Core Concepts

### Agents

Agents are AI entities with specific roles and capabilities. Each agent has:
- **Unique ID**: Identifies the agent
- **Provider**: AI provider (OpenAI, Anthropic, Custom, External)
- **System Prompt**: Defines the agent's behavior and expertise
- **Model**: The underlying AI model (e.g., `gpt-4o-mini`, `claude-3-sonnet-20240229`)

### Sandboxes

Sandboxes are isolated environments where agents interact:
- **Controlled Conversations**: Agents communicate within sandbox boundaries
- **TTL (Time-to-Live)**: Automatic cleanup after specified duration
- **Output Formats**: Define how conversations are summarized
- **Context**: Shared metadata accessible to all agents

### Messages

Messages are the communication units between agents:
- **Content**: The message text
- **Role**: Message role (user, agent, system)
- **Metadata**: Additional contextual information

## 📚 API Reference

### Client Initialization

```python
from synq import SynqClient

client = SynqClient(
    base_url="http://localhost:8080",  # Synq server URL
    timeout=30  # Request timeout in seconds
)
```

### Agent Management

#### Create an Agent

```python
agent = client.create_agent(
    agent_id="my_agent",
    provider="openai",  # "openai", "anthropic", "custom", "external"
    system_prompt="You are a helpful assistant.",
    model="gpt-4o-mini",  # Optional: defaults to provider default
    temperature=0.7,  # Optional: 0.0 to 1.0
    api_key="your-api-key",  # Optional: uses env vars if not provided
    metadata={"role": "assistant"}  # Optional: custom metadata
)
```

**Supported Providers:**
- `openai` - OpenAI models (GPT-4, GPT-3.5, etc.)
- `anthropic` - Anthropic models (Claude 3, etc.)
- `custom` - Custom AI implementations
- `external` - External agents connected via WebSocket

**API Keys from Environment:**
If you don't provide `api_key`, Synq will look for:
- OpenAI: `OPENAI_API_KEY`
- Anthropic: `ANTHROPIC_API_KEY`

#### List Agents

```python
agents = client.list_agents()
for agent in agents:
    print(f"{agent.id}: {agent.type}")
```

#### Get a Specific Agent

```python
agent = client.get_agent("my_agent")
if agent:
    print(f"Agent status: {agent.status}")
```

#### Delete an Agent

```python
client.delete_agent("my_agent")
```

### Sandbox Management

#### Create a Sandbox

```python
from synq import OutputFormat, OutputFormatType

sandbox = client.create_sandbox(
    sandbox_id="my_sandbox",
    agent_ids=["agent1", "agent2"],
    ttl_seconds=3600,  # Optional: default 3600 (1 hour)
    output_format=OutputFormat(  # Optional
        type=OutputFormatType.SUMMARY,
        instructions="Summarize the key points."
    ),
    context={"topic": "brainstorming"}  # Optional metadata
)
```

**Output Format Types:**
- `SUMMARY` - Generate a summary of the conversation
- `DECISION` - Extract decisions made
- `JSON` - Structured JSON output (requires schema)
- `CUSTOM` - Custom format with specific instructions

#### List Sandboxes

```python
sandboxes = client.list_sandboxes()
for sb in sandboxes:
    print(f"{sb.id}: {sb.status}")
```

#### Get a Specific Sandbox

```python
sandbox = client.get_sandbox("my_sandbox")
```

#### Close a Sandbox

```python
client.close_sandbox("my_sandbox")
```

### Message Management

#### Inject a Message

```python
client.inject_message(
    sandbox_id="my_sandbox",
    from_agent="user",  # Or any agent ID
    content="Hello, agents!",
    role="user",  # Optional: default "user"
    metadata={"priority": "high"}  # Optional
)
```

#### Get Messages

```python
messages = client.get_messages("my_sandbox")
for msg in messages:
    print(f"[{msg.timestamp}] {msg.from_agent_id}: {msg.payload}")
```

### Conversation Control

#### Start AI Conversation

Start an autonomous conversation where agents talk to each other:

```python
client.start_ai_conversation(
    sandbox_id="my_sandbox",
    rounds=5  # Number of conversation rounds
)
```

#### Continue Conversation

Add more rounds to an existing conversation:

```python
client.continue_conversation(
    sandbox_id="my_sandbox",
    rounds=3  # Additional rounds
)
```

#### Agent-Specific Response

Trigger a specific agent to respond:

```python
client.agent_respond(
    sandbox_id="my_sandbox",
    agent_id="specific_agent",
    message="Your turn to respond."
)
```

### Output Generation

#### Generate Formatted Output

```python
output = client.generate_output("my_sandbox")
print(output)
```

The output format is determined by the `output_format` specified when creating the sandbox.

### Vector Search

Search for similar agents using embeddings:

```python
results = client.vector_search(
    query_vector=[0.1, 0.2, ...],  # Your embedding vector
    top_k=10  # Number of results
)
```

### Health Check

```python
health = client.health_check()
print(health["status"])  # "healthy" or "unhealthy"
```

## 🔌 Building External Agents

You can connect custom agents to sandboxes using WebSockets:

```python
from synq.agent import AgentClient

# Create an external agent client
agent = AgentClient(
    agent_id="my_bot",
    sandbox_id="my_sandbox",
    synq_url="ws://localhost:8080"
)

# Define message handler
@agent.on_message
def handle_message(message):
    print(f"Received: {message.content}")
    
    # Process and respond
    response = f"I received: {message.content}"
    agent.send(response)

# Run the agent (blocking)
agent.run()
```

### Agent Client Methods

```python
# Initialize
agent = AgentClient(
    agent_id="agent_id",
    sandbox_id="sandbox_id",
    synq_url="ws://localhost:8080",
    auto_reconnect=True  # Auto-reconnect on disconnect
)

# Register message handler
@agent.on_message
def handle(message):
    # message.id
    # message.sandbox_id
    # message.from_agent
    # message.role
    # message.content
    # message.created_at
    # message.metadata
    pass

# Send message
agent.send(
    content="Hello!",
    metadata={"type": "greeting"}
)

# Run (blocking)
agent.run()

# Run (async)
await agent.run_async()

# Stop
agent.stop()
```

## 🎨 Use Cases

### 1. Multi-Perspective Analysis

```python
# Create specialized analysts
client.create_agent("tech_analyst", "openai", 
    "You analyze technology trends.", model="gpt-4o-mini")
client.create_agent("market_analyst", "openai",
    "You analyze market dynamics.", model="gpt-4o-mini")
client.create_agent("synthesizer", "openai",
    "You combine multiple perspectives.", model="gpt-4o-mini")

sandbox = client.create_sandbox(
    "analysis_pod",
    ["tech_analyst", "market_analyst", "synthesizer"],
    output_format=OutputFormat(OutputFormatType.SUMMARY)
)

client.inject_message("analysis_pod", "user", 
    "Analyze the future of electric vehicles.")
client.start_ai_conversation("analysis_pod", rounds=6)
```

### 2. Debate and Discussion

```python
client.create_agent("proponent", "openai",
    "You argue in favor of the topic.", model="gpt-4o-mini")
client.create_agent("opponent", "openai",
    "You argue against the topic.", model="gpt-4o-mini")
client.create_agent("moderator", "openai",
    "You moderate the debate and summarize.", model="gpt-4o-mini")

sandbox = client.create_sandbox(
    "debate_pod",
    ["proponent", "opponent", "moderator"],
    output_format=OutputFormat(
        type=OutputFormatType.DECISION,
        instructions="Summarize the key arguments from both sides."
    )
)

client.inject_message("debate_pod", "moderator",
    "Topic: Should AI development be regulated?")
client.start_ai_conversation("debate_pod", rounds=8)
```

### 3. Creative Collaboration

```python
client.create_agent("ideator", "openai",
    "You generate creative ideas.", model="gpt-4o-mini")
client.create_agent("critic", "openai",
    "You critically evaluate ideas.", model="gpt-4o-mini")
client.create_agent("builder", "openai",
    "You turn ideas into concrete plans.", model="gpt-4o-mini")

sandbox = client.create_sandbox(
    "creative_pod",
    ["ideator", "critic", "builder"],
    output_format=OutputFormat(
        type=OutputFormatType.JSON,
        schema={
            "idea": "string",
            "critique": "string",
            "action_plan": ["string"]
        }
    )
)

client.inject_message("creative_pod", "user",
    "Develop a new mobile app concept.")
client.start_ai_conversation("creative_pod", rounds=10)
```

### 4. Research Assistant Team

```python
client.create_agent("researcher", "anthropic",
    "You research and gather information.", model="claude-3-sonnet-20240229")
client.create_agent("fact_checker", "anthropic",
    "You verify facts and sources.", model="claude-3-sonnet-20240229")
client.create_agent("writer", "anthropic",
    "You write clear, well-structured reports.", model="claude-3-sonnet-20240229")

sandbox = client.create_sandbox(
    "research_pod",
    ["researcher", "fact_checker", "writer"],
    ttl_seconds=7200
)

client.inject_message("research_pod", "user",
    "Research the health benefits of Mediterranean diet.")
client.start_ai_conversation("research_pod", rounds=10)
```

## ⚠️ Error Handling

Synq provides specific exception types for different error scenarios:

```python
from synq import (
    SynqError,
    SynqAPIError,
    SynqConnectionError,
    SynqValidationError
)

try:
    agent = client.create_agent(
        agent_id="test_agent",
        provider="openai",
        system_prompt="Test agent"
    )
except SynqValidationError as e:
    print(f"Validation error: {e}")
except SynqConnectionError as e:
    print(f"Connection error: {e}")
except SynqAPIError as e:
    print(f"API error: {e}")
    print(f"Status code: {e.status_code}")
    print(f"Response: {e.response_body}")
except SynqError as e:
    print(f"General Synq error: {e}")
```

**Exception Types:**
- `SynqError` - Base exception for all Synq errors
- `SynqAPIError` - API returned an error (includes status_code and response_body)
- `SynqConnectionError` - Failed to connect to the server
- `SynqValidationError` - Invalid input parameters

## 🖥️ Server Setup

To use Synq, you need a running Synq server. You have two options:

### Option 1: Using Docker (Recommended)

```bash
# Pull and run the Synq server
docker run -p 8080:8080 synq/server:latest
```

### Option 2: Contact the Synq Team

For production deployments or hosted solutions, contact the Synq team at support@synq.dev

### Environment Variables

Set your AI provider API keys as environment variables:

```bash
export OPENAI_API_KEY="your-openai-key"
export ANTHROPIC_API_KEY="your-anthropic-key"
```

Or pass them directly when creating agents:

```python
client.create_agent(
    agent_id="my_agent",
    provider="openai",
    system_prompt="...",
    api_key="your-api-key"
)
```

## 🔍 Best Practices

### 1. Design Clear Agent Roles

Give each agent a specific, well-defined role:

```python
# ✅ Good: Specific role
system_prompt = "You are a financial analyst specializing in tech stocks."

# ❌ Bad: Vague role
system_prompt = "You are helpful."
```

### 2. Use Appropriate Conversation Rounds

- Simple tasks: 3-5 rounds
- Complex analysis: 8-12 rounds
- Creative projects: 10-15 rounds

### 3. Leverage Output Formats

Use structured output formats for actionable results:

```python
output_format = OutputFormat(
    type=OutputFormatType.JSON,
    schema={
        "summary": "string",
        "recommendations": ["string"],
        "confidence": "number"
    }
)
```

### 4. Clean Up Resources

Always close sandboxes when done:

```python
try:
    # ... your code
    client.start_ai_conversation("my_sandbox", rounds=5)
finally:
    client.close_sandbox("my_sandbox")
```

### 5. Handle Errors Gracefully

```python
try:
    sandbox = client.create_sandbox(
        sandbox_id="test",
        agent_ids=["agent1", "agent2"]
    )
except SynqValidationError as e:
    print(f"Invalid input: {e}")
    # Handle validation error
except SynqAPIError as e:
    print(f"Server error: {e}")
    # Handle server error
```

## 📊 Data Models

### Agent

```python
from synq import Agent

agent = Agent(
    id="agent_id",
    owner_id="owner_id",
    type="openai",
    metadata={"key": "value"},
    state_dimensions={},
    status="active",
    created_at="2024-01-01T00:00:00Z",
    updated_at="2024-01-01T00:00:00Z"
)
```

### Sandbox

```python
from synq import Sandbox, OutputFormat, OutputFormatType

sandbox = Sandbox(
    id="sandbox_id",
    agent_ids=["agent1", "agent2"],
    ttl_seconds=3600,
    status="active",
    context={"key": "value"},
    output_format=OutputFormat(type=OutputFormatType.SUMMARY),
    created_at="2024-01-01T00:00:00Z",
    updated_at="2024-01-01T00:00:00Z"
)
```

### Message

```python
from synq import Message

message = Message(
    id="msg_id",
    from_agent_id="agent1",
    to_agent_id="agent2",  # Optional
    to_topic="general",  # Optional
    type="text",
    payload="Hello!",
    timestamp=1234567890,
    sandbox_id="sandbox_id"
)
```

### OutputFormat

```python
from synq import OutputFormat, OutputFormatType

# Summary format
output_format = OutputFormat(
    type=OutputFormatType.SUMMARY,
    instructions="Create a brief summary."
)

# JSON format with schema
output_format = OutputFormat(
    type=OutputFormatType.JSON,
    schema={
        "title": "string",
        "points": ["string"]
    }
)

# Custom format
output_format = OutputFormat(
    type=OutputFormatType.CUSTOM,
    instructions="Format as a newspaper article."
)
```

## 🔧 Advanced Features

### Custom Metadata

Add custom metadata to agents, sandboxes, and messages:

```python
# Agent metadata
client.create_agent(
    agent_id="analyst",
    provider="openai",
    system_prompt="...",
    metadata={
        "department": "research",
        "expertise": ["finance", "technology"],
        "priority": 1
    }
)

# Sandbox context
sandbox = client.create_sandbox(
    sandbox_id="project_alpha",
    agent_ids=["agent1", "agent2"],
    context={
        "project_id": "alpha-001",
        "deadline": "2024-12-31",
        "budget": 10000
    }
)

# Message metadata
client.inject_message(
    sandbox_id="project_alpha",
    from_agent="user",
    content="Status update?",
    metadata={
        "urgency": "high",
        "requires_response": True
    }
)
```

### Temperature Control

Control response randomness:

```python
# Creative writing (higher temperature)
client.create_agent(
    agent_id="creative_writer",
    provider="openai",
    model="gpt-4o-mini",
    system_prompt="You are a creative writer.",
    temperature=0.9  # More random/creative
)

# Analysis (lower temperature)
client.create_agent(
    agent_id="analyst",
    provider="openai",
    model="gpt-4o-mini",
    system_prompt="You are an analyst.",
    temperature=0.2  # More focused/deterministic
)
```

### Model Selection

Choose appropriate models for your use case:

```python
# Fast and cost-effective
client.create_agent("quick_responder", "openai", "...", model="gpt-4o-mini")

# Balanced performance
client.create_agent("balanced", "openai", "...", model="gpt-4o")

# Maximum capability
client.create_agent("advanced", "anthropic", "...", model="claude-3-opus-20240229")
```

## 🤝 Support

- **Documentation**: [synq.dev/docs](https://synq.dev/docs)
- **Email**: support@synq.dev
- **Issues**: Report bugs and request features

## 📄 License

Proprietary - See license terms at [synq.dev/license](https://synq.dev/license)

## 🔄 Version

Current version: **0.2.0**

## 🚦 Changelog

### 0.2.0
- Added support for external agents via WebSocket
- Improved error handling with specific exception types
- Added vector search capabilities
- Enhanced output format options
- Added conversation continuation feature

---

**Built with ❤️ by the Synq Team**

