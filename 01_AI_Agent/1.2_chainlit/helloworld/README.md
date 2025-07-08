# Chainlit Hello World Chatbot

A simple chatbot application built with Chainlit, demonstrating the basic message handling functionality of the Chainlit UI framework.

## About Chainlit

**Chainlit** is a powerful open-source Python framework designed for building conversational AI applications with beautiful, interactive user interfaces. It provides developers with an easy way to create chat-based applications, AI assistants, and conversational interfaces.

### Key Features of Chainlit UI

🎨 **Beautiful Chat Interface**
- Modern, responsive chat UI out of the box
- Customizable themes and styling
- Support for rich media (images, files, audio)
- Real-time message streaming

🚀 **Developer-Friendly**
- Simple Python decorators for handling events
- Hot reload during development (`-w` flag)
- Built-in session management
- Easy integration with AI/ML models

💬 **Rich Conversational Features**
- Multi-turn conversations
- User input validation
- File uploads and downloads
- Typing indicators
- Message history

🔧 **Advanced Capabilities**
- Async/await support
- WebSocket connections
- Custom components
- Authentication systems
- Integration with LangChain, OpenAI, and other AI frameworks

## This Project

This is a minimal "Hello World" example that demonstrates the basic structure of a Chainlit application. The chatbot simply echoes back any message sent by the user with a "Received: " prefix.

## Prerequisites

- Python 3.8+
- Chainlit framework

## Installation

Install Chainlit using pip:

```bash
pip install chainlit
```

Or using uv:

```bash
uv add chainlit
```

## Usage

### Running the Application

Start the chatbot server:

```bash
chainlit run chatbot.py -w
```

The `-w` flag enables watch mode, which automatically reloads the application when you make changes to the code.

### Using uv

If you're using uv for package management:

```bash
uv run chainlit run chatbot.py -w
```

### Accessing the Chat Interface

Once the server starts, open your web browser and navigate to:
```
http://localhost:8000
```

You'll see a beautiful chat interface where you can:
- Type messages in the input field
- See the bot's responses in real-time
- View conversation history

## Code Structure

```python
import chainlit as cl

@cl.on_message
async def main(message: cl.Message):
    # Our custom logic goes here...
    # Send a fake response back to the user
    await cl.Message(
        content=f"Received: {message.content}",
    ).send()
```

### Code Explanation

1. **Import Chainlit**: `import chainlit as cl`
   - Imports the Chainlit framework

2. **Message Handler Decorator**: `@cl.on_message`
   - Decorates the function that will handle incoming user messages
   - This function is called every time a user sends a message

3. **Async Function**: `async def main(message: cl.Message):`
   - Defines an asynchronous function to handle messages
   - Receives a `cl.Message` object containing the user's input

4. **Response Logic**: The function processes the incoming message and sends a response
   - `message.content` contains the user's text
   - Creates a new `cl.Message` with the response content
   - `.send()` sends the message back to the user interface

## Example Interaction

**User Input:**
```
Hello, how are you?
```

**Bot Response:**
```
Received: Hello, how are you?
```

## Customization Ideas

You can extend this basic chatbot by:

1. **Adding AI Integration**:
   ```python
   # Integrate with OpenAI, Anthropic, or other AI services
   response = await openai_client.chat.completions.create(...)
   ```

2. **Adding Rich Media**:
   ```python
   # Send images, files, or other media
   await cl.Message(
       content="Here's an image:",
       elements=[cl.Image(path="image.jpg")]
   ).send()
   ```

3. **Session Management**:
   ```python
   # Store user data across conversations
   cl.user_session.set("user_name", name)
   ```

4. **File Uploads**:
   ```python
   @cl.on_file_upload
   async def handle_file(file):
       # Process uploaded files
   ```

## Troubleshooting

### Port Already in Use

If you get a port conflict error, specify a different port:

```bash
chainlit run chatbot.py -w --port 8001
```

### Installation Issues

If you encounter dependency issues:

```bash
pip install --upgrade chainlit
```

Or with uv:
```bash
uv sync
```

## Next Steps

This basic example provides the foundation for building more sophisticated chatbots. Consider exploring:

- Integration with AI models (OpenAI, Anthropic, local models)
- Adding conversation memory and context
- Implementing user authentication
- Creating custom UI components
- Adding file processing capabilities

## Resources

- [Chainlit Documentation](https://docs.chainlit.io/)
- [Chainlit GitHub Repository](https://github.com/Chainlit/chainlit)
- [Chainlit Examples](https://github.com/Chainlit/chainlit/tree/main/examples)

## License

This project is open source and available under the MIT License.
