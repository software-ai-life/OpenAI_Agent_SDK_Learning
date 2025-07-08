# OpenAI SDK Learning Projects

A comprehensive collection of AI agent projects demonstrating various OpenAI SDK features and frameworks, from basic concepts to advanced streaming implementations.

## 📁 Project Structure

```
01_AI_Agent/
├── 1.1_hello_ai_agent/     # Basic AI agent with OpenRouter API
├── 1.2_chainlit/           # Chainlit UI introduction  
├── 1.3_chatbot/            # Full-featured chatbot with memory
└── 1.4_streamimg/          # Advanced streaming story generator

...

keep learning...
```

## 🚀 Projects Overview

### 1.1 Hello AI Agent
**Basic AI Agent Implementation**
- Introduction to OpenAI Agents framework
- OpenRouter API integration
- Haiku-responding AI assistant

**Key Features:**
- Simple agent setup
- Custom instructions
- Basic async operations

### 1.2 Chainlit Hello World
**UI Framework Introduction**
- Basic Chainlit web interface
- Message handling
- Simple echo bot functionality

**Key Features:**
- Web-based chat interface
- Real-time messaging
- Simple interaction patterns

### 1.3 Chatbot with Memory
**Advanced Conversational AI**
- Full conversational memory
- Session management
- Beautiful web interface
- Error handling and recovery

**Key Features:**
- Multi-turn conversations
- Context preservation
- User session isolation
- Professional UI/UX

### 1.4 Streaming Story Generator
**Real-time Content Streaming**
- Token-by-token streaming
- Creative story generation
- Advanced UI interactions
- Multiple streaming modes

**Key Features:**
- Real-time text streaming
- Typewriter effects
- Specialized storytelling AI
- Performance optimization

## 🛠 Technology Stack

- **AI Framework**: OpenAI Agents SDK
- **UI Framework**: Chainlit
- **AI Provider**: OpenRouter API (Qwen 3 30B model)
- **Language**: Python 3.8+
- **Package Manager**: UV
- **HTTP Client**: httpx with SSL configuration

## 📋 Prerequisites

- Python 3.8 or higher
- UV package manager (recommended)
- OpenRouter API key
- Git (for version control)

## 🔧 Quick Start

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd OpenAISDK
```

### 2. Get OpenRouter API Key

1. Visit [OpenRouter](https://openrouter.ai/keys)
2. Create an account and generate an API key
3. Copy your API key for later use

### 3. Choose a Project

Each project is self-contained. Navigate to any project directory:

```bash
cd 01_AI_Agent/1.4_streamimg  # Example: Streaming project
```

### 4. Setup Environment

Create a `.env` file in the project directory:

```env
OPENROUTER_API_KEY=your-api-key-here
BASE_URL=https://openrouter.ai/api/v1
MODEL_NAME=qwen/qwen3-30b-a3b:free
```

### 5. Install Dependencies

```bash
uv add openai-agents python-dotenv chainlit httpx
```

### 6. Run the Project

```bash
uv run --active chainlit run main.py -w
```

### 7. Access the Interface

Open your browser to: `http://localhost:8000`

## 🎯 Key Learning Concepts

### AI Agent Development
- Agent configuration and instructions
- Model selection and optimization
- Error handling strategies
- Async programming patterns

### UI/UX Design
- Modern chat interfaces
- Real-time interactions
- User experience optimization
- Progressive content delivery

### Streaming Technologies
- Token-by-token streaming
- Chunk-based updates
- Performance considerations
- User engagement techniques

### Production Considerations
- Environment variable management
- Security best practices
- SSL configuration
- Deployment strategies

## 🔒 Security Notes

⚠️ **Important**: Never commit API keys to version control

- Use `.env` files for local development
- Set environment variables in production
- Follow principle of least privilege
- Implement proper input validation

## 🚨 Common Issues & Solutions

### Port Already in Use
```bash
uv run --active chainlit run main.py -w --port 8001
```

### Virtual Environment Warnings
```bash
uv run --active chainlit run main.py -w
```

### SSL Certificate Errors
Projects include SSL bypass configuration for development.

### API Connection Issues
- Verify API key validity
- Check internet connection
- Ensure OpenRouter API is accessible

## 📚 Additional Resources

- [Chainlit Documentation](https://docs.chainlit.io/)
- [OpenAI Agents SDK](https://github.com/pydantic/pydantic-ai)
- [OpenRouter API Docs](https://openrouter.ai/docs)
- [UV Package Manager](https://github.com/astral-sh/uv)

## 🤝 Contributing

Feel free to:
- Report issues
- Suggest improvements
- Add new projects
- Enhance documentation

## 📄 License

This project is open source and available under the MIT License.

---

**Happy Learning! 🎉**

Start your AI development journey with hands-on projects that teach real-world skills. 