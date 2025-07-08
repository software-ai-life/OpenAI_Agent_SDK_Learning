import os
import httpx
from dotenv import load_dotenv
from typing import cast
import chainlit as cl
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel
from agents.run import RunConfig

# Load the environment variables from the .env file
load_dotenv()

# Get configuration from environment variables
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
BASE_URL = os.getenv("BASE_URL", "https://openrouter.ai/api/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "qwen/qwen3-30b-a3b:free")

# Check if the API key is present; if not, raise an error
if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY is not set. Please ensure it is defined in your .env file.")


@cl.on_chat_start
async def start():
    """Set up the story generator when a user connects."""
    # Create HTTP client with SSL bypass to handle certificate issues
    http_client = httpx.AsyncClient(verify=False)
    
    external_client = AsyncOpenAI(
        api_key=OPENROUTER_API_KEY,
        base_url=BASE_URL,
        http_client=http_client
    )

    model = OpenAIChatCompletionsModel(
        model=MODEL_NAME,
        openai_client=external_client
    )

    config = RunConfig(
        model=model,
        model_provider=external_client,
        tracing_disabled=True
    )

    # Create a story generator agent with specific instructions
    agent: Agent = Agent(
        name="StoryTeller", 
        instructions="""You are a creative storyteller. When given a theme, genre, character, or setting, 
        you create engaging short stories (200-400 words) with vivid descriptions, interesting characters, 
        and compelling plots. Always include dialogue, emotions, and sensory details to make the story 
        come alive. Write in a narrative style that flows naturally and keeps readers engaged.""",
        model=model
    )
    
    cl.user_session.set("config", config)
    cl.user_session.set("agent", agent)

    # Send welcome message with examples
    welcome_msg = """🌟 **歡迎來到 AI 故事生成器！** 📚

我會根據您提供的主題、角色或情境為您創作一個精彩的短篇故事。

**✨ 範例輸入：**
• "一隻會說話的貓咪在圖書館的冒險"
• "未來世界的機器人與人類的友誼"
• "森林中的魔法師與失落的寶石"
• "雨夜裡神秘咖啡店的故事"
• "太空站上的意外發現"

請告訴我您想要什麼樣的故事主題，我會即時為您創作！🎭"""

    await cl.Message(content=welcome_msg).send()

@cl.on_message
async def main(message: cl.Message):
    """Generate a story based on user input with streaming."""
    
    # Create a new message object for streaming
    msg = cl.Message(content="")
    await msg.send()

    agent: Agent = cast(Agent, cl.user_session.get("agent"))
    config: RunConfig = cast(RunConfig, cl.user_session.get("config"))

    try:
        # Create story prompt
        story_prompt = f"""請根據以下主題創作一個短篇故事：

        主題：{message.content}

        請創作一個約200-400字的完整故事，包含：
        - 生動的場景描述
        - 有趣的角色
        - 引人入勝的情節
        - 適當的對話
        - 令人滿意的結局

        現在開始創作故事："""

        print(f"\n[GENERATING STORY FOR]: {message.content}\n")
        
        # Run the agent with streaming enabled
        result = Runner.run_streamed(agent, story_prompt, run_config=config)

        # Stream the response token by token
        async for event in result.stream_events():
            if event.type == "raw_response_event":
                # Process raw response events for token-by-token streaming
                if hasattr(event.data, 'delta') and event.data.delta:
                    token = event.data.delta
                    await msg.stream_token(token)
            elif event.type == "run_item_stream_event":
                if event.item.type == "message_output_item":
                    # This handles the final complete message
                    from agents import ItemHelpers
                    text_content = ItemHelpers.text_message_output(event.item)
                    if text_content:
                        # Ensure the final content is set correctly
                        msg.content = text_content

        # Log the interaction
        print(f"Story Theme: {message.content}")
        print(f"Generated Story Length: {len(msg.content)} characters")
        print("Story generation completed!")

    except Exception as e:
        msg.content = f"❌ 抱歉，生成故事時發生錯誤：{str(e)}\n\n請嘗試重新輸入您的故事主題。"
        await msg.update()
        print(f"Error: {str(e)}")

