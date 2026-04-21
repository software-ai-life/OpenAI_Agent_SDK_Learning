"""
Session Memory 範例 - OpenAI Agents SDK with Chainlit

展示如何使用 Session Memory 保存對話歷史，並透過 Chainlit 建立聊天介面。
"""

import os
import asyncio
import httpx
from dotenv import load_dotenv

from agents import (
    Agent,
    Runner,
    SQLiteSession,
    AsyncOpenAI,
    OpenAIChatCompletionsModel,
    function_tool,
)

import chainlit as cl

# 載入環境變數
load_dotenv()

# 取得設定
API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = "gemini-2.5-flash"
BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"

if not API_KEY:
    raise ValueError("GEMINI_API_KEY is not set")

# 設定模型
model = OpenAIChatCompletionsModel(
    model=MODEL_NAME,
    openai_client=AsyncOpenAI(
        base_url=BASE_URL,
        api_key=API_KEY,
        http_client=httpx.AsyncClient(
            verify=False,
            limits=httpx.Limits(
                max_connections=1000,
                max_keepalive_connections=100
            )
        )
    ),
)


# ============= 工具定義 =============

@function_tool
def get_weather(city: str) -> str:
    """取得城市的天氣資訊"""
    import random
    choices = ["晴天", "多雲", "下雨", "下雪"]
    return f"{city} 的天氣是 {random.choice(choices)}"


@function_tool
def get_user_info(user_id: str) -> str:
    """取得使用者資訊"""
    # 模擬資料
    users = {
        "user_123": {"name": "王小明", "level": "VIP"},
        "user_456": {"name": "李小華", "level": "一般"},
    }
    if user_id in users:
        user = users[user_id]
        return f"使用者：{user['name']}, 等級：{user['level']}"
    return "找不到使用者"


# ============= Agent 定義 =============

assistant = Agent(
    name="Assistant",
    instructions="你是一個友善的助手。回答要簡潔明瞭。",
    model=model,
    tools=[get_weather, get_user_info],
)


# ============= Chainlit 事件處理 =============

@cl.on_chat_start
async def on_chat_start():
    """當聊天開始時"""
    # 取得或建立 session ID
    session_id = cl.user_session.get("id")
    if not session_id:
        session_id = f"user_{id(cl.user_session)}"
    
    # 建立 SQLite Session（持久化儲存）
    session = SQLiteSession(
        session_id=session_id,
        db_path="chat_history.db"
    )
    
    # 儲存到 Chainlit session
    cl.user_session.set("agent_session", session)
    cl.user_session.set("session_id", session_id)
    
    # 歡迎訊息
    await cl.Message(
        content=f"👋 歡迎！我是你的助手。\n\n📝 Session ID: `{session_id}`\n\n我會記住我們的對話內容！"
    ).send()


@cl.on_message
async def on_message(message: cl.Message):
    """當收到訊息時"""
    # 取得 session
    session = cl.user_session.get("agent_session")
    
    # 建立思考中訊息
    msg = cl.Message(content="")
    await msg.send()
    
    try:
        # 執行 Agent（自動載入對話歷史）
        result = await Runner.run(
            assistant,
            message.content,
            session=session
        )
        
        # 更新訊息
        msg.content = result.final_output
        await msg.update()
        
    except Exception as e:
        msg.content = f"❌ 發生錯誤: {str(e)}"
        await msg.update()


@cl.on_chat_end
async def on_chat_end():
    """當聊天結束時"""
    session_id = cl.user_session.get("session_id")
    await cl.Message(
        content=f"👋 再見！\n\n對話已儲存（Session: `{session_id}`）"
    ).send()


# ============= 範例 1: 基本的 Session Memory =============

async def example1_basic_session():
    """範例 1: 基本的 Session Memory"""
    
    print("=" * 60)
    print("範例 1: 基本的 Session Memory")
    print("=" * 60)
    
    # 建立 Session（記憶體模式）
    session = SQLiteSession("example_123")
    
    # 第一輪對話
    print("\n第一輪:")
    print("User: 金門大橋在哪個城市？")
    result = await Runner.run(
        assistant,
        "金門大橋在哪個城市？",
        session=session
    )
    print(f"Agent: {result.final_output}")
    
    # 第二輪對話（Agent 會記住前一輪）
    print("\n第二輪:")
    print("User: 那個城市在哪個州？")
    result = await Runner.run(
        assistant,
        "那個城市在哪個州？",
        session=session
    )
    print(f"Agent: {result.final_output}")
    
    # 第三輪對話
    print("\n第三輪:")
    print("User: 那個州的人口是多少？")
    result = await Runner.run(
        assistant,
        "那個州的人口是多少？",
        session=session
    )
    print(f"Agent: {result.final_output}")


# ============= 範例 2: 持久化 Session =============

async def example2_persistent_session():
    """範例 2: 持久化 Session"""
    
    print("\n\n" + "=" * 60)
    print("範例 2: 持久化 Session")
    print("=" * 60)
    
    # 建立持久化 Session
    session = SQLiteSession(
        "user_123",
        "conversations.db"  # 儲存到檔案
    )
    
    print("\n對話會儲存到 conversations.db 檔案")
    
    # 第一次對話
    print("\n第一次對話:")
    print("User: 我的名字是小明")
    result = await Runner.run(
        assistant,
        "我的名字是小明",
        session=session
    )
    print(f"Agent: {result.final_output}")
    
    # 第二次對話
    print("\n第二次對話:")
    print("User: 我的名字是什麼？")
    result = await Runner.run(
        assistant,
        "我的名字是什麼？",
        session=session
    )
    print(f"Agent: {result.final_output}")


# ============= 範例 3: Session 操作 =============

async def example3_session_operations():
    """範例 3: Session 操作"""
    
    print("\n\n" + "=" * 60)
    print("範例 3: Session 操作")
    print("=" * 60)
    
    session = SQLiteSession("operations_test")
    
    # 執行對話
    await Runner.run(assistant, "你好", session=session)
    await Runner.run(assistant, "今天天氣如何？", session=session)
    
    # 取得所有對話
    print("\n取得所有對話歷史:")
    items = await session.get_items()
    for i, item in enumerate(items, 1):
        role = item.get("role", "unknown")
        content = str(item.get("content", ""))[:50]
        print(f"  {i}. {role}: {content}...")
    
    # 取得最近 2 筆
    print("\n取得最近 2 筆:")
    recent_items = await session.get_items(limit=2)
    for item in recent_items:
        role = item.get("role", "unknown")
        content = str(item.get("content", ""))[:50]
        print(f"  - {role}: {content}...")
    
    # 移除最後一筆
    print("\n移除最後一筆:")
    last_item = await session.pop_item()
    if last_item:
        print(f"  移除: {last_item.get('role')}")
    
    # 清空 session
    print("\n清空 session:")
    await session.clear_session()
    items = await session.get_items()
    print(f"  剩餘項目: {len(items)}")


# ============= 範例 4: 多個 Session =============

async def example4_multiple_sessions():
    """範例 4: 多個 Session"""
    
    print("\n\n" + "=" * 60)
    print("範例 4: 多個 Session")
    print("=" * 60)
    
    # 建立不同使用者的 Session
    session1 = SQLiteSession("user_alice", "multi_users.db")
    session2 = SQLiteSession("user_bob", "multi_users.db")
    
    # Alice 的對話
    print("\nAlice 的對話:")
    print("User: 我住在台北")
    result = await Runner.run(
        assistant,
        "我住在台北",
        session=session1
    )
    print(f"Agent: {result.final_output}")
    
    # Bob 的對話
    print("\nBob 的對話:")
    print("User: 我住在台南")
    result = await Runner.run(
        assistant,
        "我住在台南",
        session=session2
    )
    print(f"Agent: {result.final_output}")
    
    # Alice 繼續對話
    print("\nAlice 繼續對話:")
    print("User: 我住在哪裡？")
    result = await Runner.run(
        assistant,
        "我住在哪裡？",
        session=session1
    )
    print(f"Agent: {result.final_output}")
    
    # Bob 繼續對話
    print("\nBob 繼續對話:")
    print("User: 我住在哪裡？")
    result = await Runner.run(
        assistant,
        "我住在哪裡？",
        session=session2
    )
    print(f"Agent: {result.final_output}")


# ============= 主程式 =============

async def main():
    """執行範例（不含 Chainlit）"""
    
    print("\n🗄️ Session Memory 範例")
    print("=" * 60)
    print("\n注意：Chainlit 介面請使用 'chainlit run main.py'\n")
    
    # 範例 1: 基本的 Session Memory
    await example1_basic_session()
    
    # 範例 2: 持久化 Session
    await example2_persistent_session()
    
    # 範例 3: Session 操作
    await example3_session_operations()
    
    # 範例 4: 多個 Session
    await example4_multiple_sessions()
    
    print("\n" + "=" * 60)
    print("✅ 所有範例執行完成")
    print("=" * 60)
    
    print("\n啟動 Chainlit 介面:")
    print("  chainlit run main.py")


if __name__ == "__main__":
    asyncio.run(main())
