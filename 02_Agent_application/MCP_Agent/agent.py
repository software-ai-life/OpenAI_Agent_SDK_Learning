from agents.run_context import RunContextWrapper
from agents import Agent,Runner, AsyncOpenAI, OpenAIChatCompletionsModel, set_default_openai_client
from agents.mcp import MCPServerStdio
from agents.run import RunConfig
from dotenv import load_dotenv
import httpx
import os
import chainlit as cl
from typing import cast


# 載入環境變數
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = "gemini-2.5-flash-lite-preview-06-17"

if not API_KEY:
    raise ValueError("GEMINI_API_KEY is not set. Please ensure it is defined in your .env file.")

@cl.on_chat_start
async def start():
    http_client = httpx.AsyncClient(verify=False)

    external_client = AsyncOpenAI(
        api_key=API_KEY,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        http_client=http_client
    )
    
    set_default_openai_client(external_client)


    model = OpenAIChatCompletionsModel(
        model=MODEL_NAME,
        openai_client=external_client
    )

    config = RunConfig(
        model=model,
        model_provider=external_client,
        tracing_disabled=True
    )

    fileserver = MCPServerStdio(
        params={
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-filesystem", "C:/AI_Agent/OpenAISDK"],
        }
    )
    BraveServer = MCPServerStdio(
        params={
        "command": "npx",
        "args": [
            "-y",
            "@modelcontextprotocol/server-brave-search"
        ],
        "env": {
            "BRAVE_API_KEY": "******"
            }
        },
        client_session_timeout_seconds = 15
    )


    agent=Agent(
        name="MCP Tools Assistant",
        instructions="Use the MCP tools to achieve the task",
        mcp_servers=[fileserver, BraveServer],
        model=model
    )

    cl.user_session.set("config", config)
    cl.user_session.set("agent", agent)
    cl.user_session.set("fileserver", fileserver)  # 新增這行
    cl.user_session.set("BraveServer", BraveServer)  # 新增這行

    # Send welcome message with examples
    welcome_msg = """ MCP Agent 已啟動

    """
    await cl.Message(content=welcome_msg).send()

@cl.on_message
async def main(message: cl.Message):
    """Generate tool using based on user input with streaming."""

    # Create a new message object for streaming
    msg = cl.Message(content="")
    await msg.send()

    agent: Agent = cast(Agent, cl.user_session.get("agent"))
    config: RunConfig = cast(RunConfig, cl.user_session.get("config"))
    fileserver = cl.user_session.get("fileserver")  # 新增這行
    BraveServer = cl.user_session.get("BraveServer")  # 新增這行
    if fileserver and not getattr(fileserver, 'is_connected', False):
        await fileserver.connect()
    if BraveServer and not getattr(BraveServer, 'is_connected', False):
        await BraveServer.connect()

    try:
        # Create tool calling prompt
        prompt = f""" 請幫我使用mcp tools 來完成以下任務：

        任務：{message.content}
        """

        result = await Runner.run(agent, prompt, run_config=config)

        if hasattr(result, "final_output"):
            msg.content = result.final_output
        else:
            msg.content = str(result)
        await msg.update()

    except Exception as e:
        msg.content = f"❌ 抱歉，工具呼叫時發生錯誤：{str(e)}\n\n請嘗試重新輸入您的任務。"
        await msg.update()
        print(f"Error: {str(e)}")
                                     

