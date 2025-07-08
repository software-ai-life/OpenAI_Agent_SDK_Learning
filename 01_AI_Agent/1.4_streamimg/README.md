# AI Story Generator with Real-time Streaming

A sophisticated AI-powered story generator built with **Chainlit** and **OpenAI Agents** framework, showcasing **real-time text streaming** capabilities. This project demonstrates how to implement token-by-token streaming responses for a seamless user experience.

## 🌊 Understanding Streaming in AI Applications

### What is Streaming?

**Streaming** in AI applications refers to the real-time delivery of generated content as it's being produced, rather than waiting for the complete response. Instead of seeing a blank screen followed by the entire response appearing at once, users see content appearing progressively, character by character or word by word.

### Why Streaming Matters

1. **Enhanced User Experience**: Users see immediate feedback and progress
2. **Perceived Performance**: Applications feel faster and more responsive
3. **Better Engagement**: Users stay engaged watching content appear
4. **Reduced Wait Time**: No long pauses before seeing any content
5. **Modern AI UX**: Matches expectations set by ChatGPT and similar tools

## 🔄 Streaming Modes Explained

This project demonstrates two distinct streaming approaches:

### 1. Token-by-Token Streaming (Real-time)

**What it is:**
- Each individual token (word, character, or subword) appears immediately upon generation
- Creates a "typewriter effect" where text flows naturally
- Provides the most responsive user experience

**Implementation:**
```python
# Process raw response events for immediate token display
if event.type == "raw_response_event":
    if hasattr(event.data, 'delta') and event.data.delta:
        token = event.data.delta
        await msg.stream_token(token)  # Display immediately
```

**User Experience:**
```
The cat slowly opened → The cat slowly opened the → The cat slowly opened the ancient...
```

### 2. Chunk-by-Chunk Streaming (Batch Updates)

**What it is:**
- Content appears in larger blocks or sentences
- Less granular but still provides progressive loading
- Useful when processing or formatting is needed between updates

**Implementation:**
```python
# Process complete message chunks
elif event.type == "run_item_stream_event":
    if event.item.type == "message_output_item":
        text_content = ItemHelpers.text_message_output(event.item)
        msg.content = text_content
        await msg.update()
```

**User Experience:**
```
The cat slowly opened the ancient book. → The cat slowly opened the ancient book. 
Dust particles danced in the moonlight...
```

### 3. Comparison Table

| Feature | Token-by-Token | Chunk-by-Chunk |
|---------|----------------|----------------|
| **Responsiveness** | Highest | Moderate |
| **Bandwidth Usage** | Higher | Lower |
| **User Engagement** | Maximum | Good |
| **Implementation Complexity** | Simple | Moderate |
| **Use Case** | Chat interfaces | Document generation |

## 🚀 Features

### Core Capabilities
- **Real-time Token Streaming**: Watch stories unfold word by word
- **Creative Story Generation**: AI-powered narrative creation
- **Interactive Prompting**: Guided story theme suggestions
- **Beautiful UI**: Modern, responsive Chainlit interface
- **Error Handling**: Graceful error management and recovery

### Technical Features
- **OpenAI Agents Framework**: Advanced agent-based AI architecture
- **Async Processing**: Non-blocking streaming for smooth performance
- **SSL Configuration**: Handles certificate verification issues
- **Environment Variables**: Secure API key management
- **Hot Reload**: Development mode with automatic reloading

## 🛠 Technology Stack

- **Frontend**: Chainlit web interface with streaming support
- **Backend**: Python asyncio with OpenAI Agents
- **AI Model**: Qwen 3 30B via OpenRouter API
- **HTTP Client**: httpx with SSL configuration
- **Package Management**: UV (modern Python package manager)

## 📋 Prerequisites

- Python 3.8+
- UV package manager (recommended) or pip
- OpenRouter API key
- Internet connection for API access

## 🔧 Installation

### 1. Clone and Setup

```bash
# Navigate to the project directory
cd 01_AI_Agent/1.4_streamimg
```

### 2. Install Dependencies

Using UV (recommended):
```bash
uv add openai-agents python-dotenv chainlit httpx
```

Using pip:
```bash
pip install openai-agents python-dotenv chainlit httpx
```

### 3. Environment Configuration

Create a `.env` file in the project root:

```env
OPENROUTER_API_KEY=your-openrouter-api-key-here
BASE_URL=https://openrouter.ai/api/v1
MODEL_NAME=qwen/qwen3-30b-a3b:free
```

**Get your OpenRouter API key**: [https://openrouter.ai/keys](https://openrouter.ai/keys)

## 🚀 Usage

### Starting the Application

```bash
uv run --active chainlit run main.py -w
```

**Flags explanation:**
- `--active`: Use the active virtual environment
- `-w`: Enable watch mode for development (auto-reload on changes)

### Accessing the Interface

1. Open your browser to: `http://localhost:8000`
2. You'll see a welcome message with example prompts
3. Enter a story theme and watch the magic happen!

### Example Story Prompts

Try these engaging prompts to see streaming in action:

- "A talking cat's adventure in a magical library"
- "A robot and human friendship in the future"
- "A wizard's quest for a lost gem in an enchanted forest"
- "A mysterious café that only appears on rainy nights"
- "An unexpected discovery on a space station"

## 💻 Code Architecture

### Streaming Implementation

```python
# Real-time token streaming setup
async for event in result.stream_events():
    if event.type == "raw_response_event":
        # Token-by-token streaming
        if hasattr(event.data, 'delta') and event.data.delta:
            token = event.data.delta
            await msg.stream_token(token)
    
    elif event.type == "run_item_stream_event":
        # Final message completion
        if event.item.type == "message_output_item":
            text_content = ItemHelpers.text_message_output(event.item)
            msg.content = text_content
```

### Agent Configuration

```python
# Specialized storytelling agent
agent = Agent(
    name="StoryTeller",
    instructions="""You are a creative storyteller. Create engaging 
    short stories (200-400 words) with vivid descriptions, interesting 
    characters, and compelling plots.""",
    model=model
)
```

### SSL Configuration

```python
# Handle certificate verification issues
http_client = httpx.AsyncClient(verify=False)
external_client = AsyncOpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url=BASE_URL,
    http_client=http_client
)
```

## 🎨 User Experience Flow

1. **Welcome Screen**: Users see instructions and example prompts
2. **Input Processing**: Users enter their story theme
3. **Streaming Response**: Story text appears progressively
4. **Completion**: Full story is displayed with completion notification

### Visual Streaming Effect

```
User Input: "A magical forest adventure"

Streaming Output:
In the heart of →
In the heart of the →
In the heart of the Whispering →
In the heart of the Whispering Woods, →
In the heart of the Whispering Woods, young →
In the heart of the Whispering Woods, young girl →
...
```

## 🔧 Customization

### Modifying Story Instructions

```python
# Update agent instructions in main.py
agent = Agent(
    name="StoryTeller",
    instructions="Your custom storytelling instructions here...",
    model=model
)
```

### Changing AI Models

Update your `.env` file:
```env
MODEL_NAME=anthropic/claude-3-haiku    # Alternative model
MODEL_NAME=openai/gpt-4                # Another option
```

### Adjusting Streaming Behavior

```python
# For faster streaming, process every delta
await msg.stream_token(token)

# For slower, more controlled streaming
if len(accumulated_text) % 5 == 0:  # Every 5 characters
    await msg.stream_token(token)
```

## 🚨 Troubleshooting

### Common Issues

**1. Connection Errors**
```
Error: Connection error.
```
- **Solution**: Ensure SSL bypass is configured and API key is valid

**2. Port Already in Use**
```
Error: Port 8000 already in use
```
- **Solution**: Use a different port: `chainlit run main.py -w --port 8001`

**3. No Streaming Effect**
- **Cause**: Only processing `run_item_stream_event`
- **Solution**: Ensure `raw_response_event` handling is enabled

**4. API Key Issues**
```
ValueError: OPENROUTER_API_KEY is not set
```
- **Solution**: Check your `.env` file and ensure the API key is valid

### Development Tips

- Use `--active` flag to avoid virtual environment warnings
- Enable watch mode (`-w`) for development
- Check browser console for any JavaScript errors
- Monitor terminal output for streaming events

## 🔒 Security Considerations

### Production Deployment

1. **API Key Management**:
   ```bash
   # Use environment variables, not hardcoded values
   export OPENROUTER_API_KEY="your-key"
   ```

2. **SSL Configuration**:
   ```python
   # For production, use proper SSL verification
   http_client = httpx.AsyncClient(verify=True)
   ```

3. **Input Validation**:
   - Sanitize user inputs
   - Implement rate limiting
   - Add content filtering if needed

## 📚 Learning Resources

- [Chainlit Documentation - Streaming](https://docs.chainlit.io/advanced-features/streaming)
- [OpenAI Agents SDK - Streaming](https://openai.github.io/openai-agents-python/streaming/)

## 🎯 Future Enhancements

### Potential Features
- **Multi-language Story Generation**
- **Story Length Customization**
- **Character Voice Selection**
- **Interactive Story Branching**
- **Story Export Functionality**
- **Theme-based Story Templates**

### Technical Improvements
- **WebSocket Implementation** for even faster streaming
- **Caching Layer** for improved performance
- **Load Balancing** for multiple users
- **Story Persistence** with database integration

## 📄 License

This project is open source and available under the MIT License.

---

**Experience the Magic of Real-time AI Storytelling! ✨**

Built with ❤️ using Chainlit, OpenAI Agents, and modern streaming technologies.
