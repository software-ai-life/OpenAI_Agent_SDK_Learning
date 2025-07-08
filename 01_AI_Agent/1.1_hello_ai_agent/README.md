# Hello AI Agent

A simple AI assistant application built with the OpenAI Agents framework, demonstrating how to create a custom AI agent that responds only in haikus.

## Features

- Uses OpenRouter API with Qwen 3 30B model
- Custom AI agent with specific instructions (haiku responses)
- SSL certificate bypass for connection issues
- Asynchronous execution with asyncio

## Prerequisites

- Python 3.8+
- Required packages: `agents`, `openai`, `httpx`, `requests`

## Installation

Install the required dependencies:

```bash
pip install agents openai httpx requests
```

Or if using uv:

```bash
uv add agents openai httpx requests
```

## Configuration

The application uses the following configuration:

- **API Key**: OpenRouter API key (currently hardcoded)
- **Base URL**: `https://openrouter.ai/api/v1`
- **Model**: `qwen/qwen3-30b-a3b:free`

## Usage

Run the application:

```bash
python hello_world.py
```

Or using uv:

```bash
uv run python hello_world.py
```

## How It Works

1. **SSL Bypass**: The application creates an `httpx.AsyncClient` with SSL verification disabled to handle certificate issues
2. **Agent Creation**: Creates an AI agent with specific instructions to respond only in haikus
3. **Query Processing**: Sends a query about "recursion in programming" to the agent
4. **Response**: The agent responds in haiku format as instructed

## Code Structure

```python
# Create HTTP client with SSL bypass
http_client = httpx.AsyncClient(verify=False)

# Initialize OpenAI client
client = AsyncOpenAI(
    base_url=BASE_URL, 
    api_key=OPENROUTER_API_KEY,
    http_client=http_client
)

# Create agent with specific instructions
agent = Agent(
    name="Assistant",
    instructions="You only respond in haikus.",
    model=OpenAIChatCompletionsModel(model=MODEL_NAME, openai_client=client),
)

# Run the agent
result = await Runner.run(agent, "Tell me about recursion in programming.")
```

## Troubleshooting

### SSL Certificate Issues

If you encounter SSL certificate verification errors:

```
[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: self-signed certificate in certificate chain
```

The application handles this by setting `verify=False` in the HTTP client configuration.

### API Connection Errors

If you get `openai.APIConnectionError: Connection error`, ensure:

1. Your internet connection is stable
2. The OpenRouter API is accessible
3. The API key is valid and has sufficient credits

## Environment Variables

For production use, consider setting these as environment variables instead of hardcoding:

```bash
export OPENROUTER_API_KEY="your-api-key-here"
export BASE_URL="https://openrouter.ai/api/v1"
export MODEL_NAME="qwen/qwen3-30b-a3b:free"
```

## Example Output

The agent will respond to the query about recursion in haiku format, such as:

```
Function calls itself,
Smaller problems, same pattern—
Base case ends the loop.
```

## Security Note

⚠️ **Warning**: The API key is currently hardcoded in the source code. For production applications, always use environment variables or secure configuration management to store sensitive credentials.

## Dependencies

- `agents`: OpenAI Agents framework
- `openai`: OpenAI Python client
- `httpx`: HTTP client for async requests
- `requests`: HTTP library for Python
- `asyncio`: Asynchronous I/O support 