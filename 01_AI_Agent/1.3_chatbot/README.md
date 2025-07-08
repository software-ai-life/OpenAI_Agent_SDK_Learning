# Panaversity AI Assistant Chatbot

An advanced AI chatbot application built with **Chainlit** and **OpenAI Agents** framework, featuring conversational memory, real-time responses, and a beautiful web interface. This project demonstrates the integration of modern AI technologies to create a sophisticated conversational assistant.

## 🚀 Features

### Core Capabilities
- **Intelligent Conversations**: Powered by Qwen 3 30B model via OpenRouter API
- **Conversational Memory**: Maintains context across multiple turns in a conversation
- **Real-time Responses**: Live typing indicators and instant message updates
- **Beautiful UI**: Modern, responsive chat interface built with Chainlit
- **Session Management**: Persistent conversation history during chat sessions

### Technical Features
- **OpenAI Agents Framework**: Advanced agent-based architecture for AI interactions
- **Async Processing**: Non-blocking message handling for smooth user experience
- **Error Handling**: Robust error management with user-friendly error messages
- **SSL Bypass**: Configured to handle certificate verification issues
- **Hot Reload**: Development mode with automatic code reloading

## 🛠 Technology Stack

- **Frontend**: Chainlit web interface
- **Backend**: Python with asyncio
- **AI Framework**: OpenAI Agents
- **AI Model**: Qwen 3 30B (via OpenRouter API)
- **HTTP Client**: httpx with SSL configuration
- **Package Management**: UV (modern Python package manager)

## 📋 Prerequisites

- Python 3.8+
- UV package manager (recommended) or pip
- Internet connection for OpenRouter API access

## 🔧 Installation

### Install Dependencies

Using UV (recommended):
```bash
uv add openai-agents python-dotenv chainlit
```

Using pip:
```bash
pip install openai-agents python-dotenv chainlit
```

### Setup Virtual Environment

Create a virtual environment:
```bash
uv venv
```

Activate the environment (Mac/Linux):
```bash
source .venv/bin/activate
```

Activate the environment (Windows):
```bash
.venv\Scripts\activate
```

## 🚀 Usage

### Running the Application

Start the chatbot server:
```bash
uv run chainlit run main.py -w
```

If you encounter virtual environment path mismatch warnings:
```bash
uv run --active chainlit run main.py -w
```

### Accessing the Chat Interface

1. Once the server starts, open your web browser
2. Navigate to: `http://localhost:8000`
3. Start chatting with the Panaversity AI Assistant!

### Using Different Ports

If port 8000 is already in use:
```bash
uv run --active chainlit run main.py -w --port 8001
```

## 💬 How It Works

### Application Flow

1. **Initialization**: When a user connects, the app sets up:
   - OpenRouter API client with SSL bypass
   - Qwen 3 30B model configuration
   - AI Agent with helpful assistant instructions
   - Empty conversation history

2. **Message Processing**: For each user message:
   - Shows "Thinking..." indicator
   - Adds user input to conversation history
   - Sends context to AI agent via OpenAI Agents framework
   - Updates the interface with the AI response
   - Maintains conversation history for future context

3. **Session Management**: 
   - Conversation history persists throughout the session
   - Each user gets their own isolated chat session
   - Context is maintained across multiple message exchanges

### Code Architecture

```python
# Session initialization with AI agent setup
@cl.on_chat_start
async def start():
    # Configure OpenRouter client
    # Create AI agent with instructions
    # Initialize conversation history

# Message handling with context awareness
@cl.on_message
async def main(message: cl.Message):
    # Retrieve conversation history
    # Process message with AI agent
    # Update chat interface
    # Maintain session context
```

## 🎯 Key Components

### 1. **AI Agent Configuration**
- **Model**: Qwen 3 30B (free tier via OpenRouter)
- **Instructions**: "You are a helpful assistant"
- **Context Awareness**: Full conversation history included in each request

### 2. **Chainlit Integration**
- **Real-time UI**: Instant message updates and typing indicators
- **Session Management**: Built-in user session handling
- **Message Threading**: Async message processing

### 3. **OpenRouter API**
- **Model Access**: Free access to Qwen 3 30B model
- **SSL Configuration**: Custom HTTP client for certificate handling
- **Error Handling**: Graceful degradation on API issues

## 🎨 User Experience Features

### Interactive Elements
- **Welcome Message**: Greeting users upon connection
- **Thinking Indicator**: Shows AI processing status
- **Real-time Updates**: Messages update in place
- **Conversation Flow**: Natural multi-turn conversations

### Example Interaction

**User**: "Hello! Can you help me understand Python decorators?"

**Assistant**: *Thinking...*

**Assistant**: "Hello! I'd be happy to help you understand Python decorators. Decorators are a powerful feature in Python that allow you to modify or extend the behavior of functions or classes without permanently modifying their code..."

## 🔧 Customization

### Changing AI Instructions
Modify the agent instructions in `main.py`:
```python
agent = Agent(
    name="Assistant", 
    instructions="Your custom instructions here",
    model=model
)
```

### Using Different Models
Update the model configuration:
```python
MODEL_NAME = "anthropic/claude-3-haiku"  # Example alternative
```

### Adding Custom Features
Extend the chatbot with additional Chainlit decorators:
```python
@cl.on_file_upload
async def handle_file(file):
    # Handle file uploads

@cl.on_settings_update
async def setup_agent(settings):
    # Dynamic settings configuration
```

## 🚨 Troubleshooting

### Common Issues

**1. Port Already in Use**
```bash
# Use a different port
uv run --active chainlit run main.py -w --port 8001
```

**2. Virtual Environment Warnings**
```bash
# Use the --active flag
uv run --active chainlit run main.py -w
```

**3. SSL Certificate Errors**
The application is configured to bypass SSL verification. If you encounter SSL issues, ensure the `httpx.AsyncClient(verify=False)` configuration is maintained.

**4. API Key Issues**
Ensure the OpenRouter API key is valid and has sufficient credits for the Qwen model.

## 🔒 Security Notes

⚠️ **Important Security Considerations**:

1. **API Key**: Currently hardcoded in the source. For production:
   ```bash
   # Use environment variables
   export OPENROUTER_API_KEY="your-key-here"
   ```

2. **SSL Bypass**: Only use `verify=False` in development environments
3. **Input Validation**: Consider adding input sanitization for production use

## 📚 Learning Resources

- [Chainlit Documentation](https://docs.chainlit.io/)
- [OpenAI Agents Framework](https://github.com/pydantic/pydantic-ai)
- [OpenRouter API Documentation](https://openrouter.ai/docs)
- [Qwen Model Information](https://qwenlm.github.io/)

## 🎯 Next Steps

Enhance your chatbot further by exploring:

1. **Advanced Features**:
   - File upload and processing
   - Image generation and analysis
   - Web search integration
   - Custom tools and functions

2. **Production Deployment**:
   - Environment variable configuration
   - Docker containerization
   - Cloud deployment (Vercel, Heroku, etc.)

3. **UI Customization**:
   - Custom themes and styling
   - Additional UI components
   - Multi-language support

## 📄 License

This project is open source and available under the MIT License.

---

**Built with ❤️ using Chainlit and OpenAI Agents**
