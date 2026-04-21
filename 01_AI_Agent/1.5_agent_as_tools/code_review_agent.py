# Imports
import asyncio
import os
import httpx
import chainlit as cl
from typing import cast
from dotenv import load_dotenv
from agents import Agent, ItemHelpers, MessageOutputItem, Runner, trace, AsyncOpenAI, OpenAIChatCompletionsModel
from agents.run import RunConfig

# Load environment variables
load_dotenv()

# Get configuration from environment variables
API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = "gemini-2.5-flash"

if not API_KEY:
    raise ValueError("GEMINI_API_KEY is not set. Please ensure it is defined in your .env file.")

# Create HTTP client with SSL bypass
http_client = httpx.AsyncClient(verify=False)

external_client = AsyncOpenAI(
    api_key=API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    http_client=http_client
)

model = OpenAIChatCompletionsModel(
    model=MODEL_NAME,
    openai_client=external_client
)

# 語法檢查代理人
syntax_checker_agent = Agent(
    name="syntax_checker_agent",
    instructions="""您是一個專業的程式碼語法檢查器。請檢查程式碼中的：
    - 語法錯誤
    - 編譯錯誤
    - 缺少的導入語句
    - 型別錯誤
    - 變數未定義的問題
    請提供清晰的錯誤說明和修正建議。""",
    handoff_description="專門檢查程式碼語法和基本錯誤",
    model=model
)

# 性能檢查代理人
performance_checker_agent = Agent(
    name="performance_checker_agent",
    instructions="""您是一個專業的程式碼性能分析師。請檢查程式碼中的：
    - 時間複雜度問題
    - 空間複雜度問題
    - 不必要的迴圈
    - 記憶體洩漏風險
    - 低效率的演算法
    - 資料庫查詢優化建議
    請提供性能優化建議和最佳實踐。""",
    handoff_description="專門分析程式碼性能和效率問題",
    model=model
)

# 代碼風格檢查代理人
style_checker_agent = Agent(
    name="style_checker_agent",
    instructions="""您是一個專業的程式碼風格檢查師。請檢查程式碼中的：
    - 命名慣例是否一致
    - 程式碼格式和縮排
    - 函數和類別的設計原則
    - 程式碼註解和文檔
    - 程式碼重複和可重用性
    - 設計模式的應用
    - 程式碼可讀性
    請提供程式碼風格改進建議。""",
    handoff_description="專門檢查程式碼風格和最佳實踐",
    model=model
)

# 統籌 Code Review 代理人
orchestrator_agent = Agent(
    name="code_review_orchestrator",
    instructions=(
        "您是一個專業的程式碼審查協調員。您使用提供的工具來進行全面的程式碼審查。"
        "當用戶請求程式碼審查時，您會按順序調用相關的專門工具："
        "1. 首先進行語法檢查"
        "2. 然後進行性能分析"
        "3. 最後進行程式碼風格檢查"
        "您會總結所有檢查結果，並提供優先級排序的改進建議。"
        "您絕不自己進行審查，而是始終使用提供的專門工具。"
    ),
    tools=[
        syntax_checker_agent.as_tool(
            tool_name="check_syntax",
            tool_description="檢查程式碼語法錯誤和基本問題",
        ),
        performance_checker_agent.as_tool(
            tool_name="analyze_performance",
            tool_description="分析程式碼性能和效率問題",
        ),
        style_checker_agent.as_tool(
            tool_name="review_style",
            tool_description="檢查程式碼風格和最佳實踐",
        ),
    ],
    model=model
)


@cl.on_chat_start
async def start():
    """設置程式碼審查代理人系統。"""
    
    config = RunConfig(
        model=model,
        model_provider=external_client,
        tracing_disabled=True
    )
    
    # 將代理人和配置存儲在會話中
    cl.user_session.set("config", config)
    cl.user_session.set("orchestrator_agent", orchestrator_agent)

    # 發送歡迎消息
    welcome_msg = """🔍 **歡迎來到程式碼審查 AI Agent 系統！** 📋

我是您的專業程式碼審查助手，提供多層面的程式碼分析服務：

**🔧 審查功能：**
• **語法檢查** - 檢查語法錯誤、編譯問題、型別錯誤
• **性能分析** - 分析時間複雜度、記憶體使用、演算法效率
• **風格檢查** - 審查命名慣例、程式碼格式、設計原則

**💡 使用方法：**
直接貼上您要審查的程式碼，我會自動進行全面的分析並提供詳細的改進建議！

**✨ 範例輸入：**
```python
def calculate_sum(numbers):
    total = 0
    for i in range(len(numbers)):
        total += numbers[i]
    return total
```

請貼上您要審查的程式碼，我會立即開始分析！🚀"""

    await cl.Message(content=welcome_msg).send()


@cl.on_message
async def main(message: cl.Message):
    """處理程式碼審查請求。"""
    
    # 創建審查中的消息
    msg = cl.Message(content="🔍 **正在進行程式碼審查...**\n\n請稍候，我正在調用專門的代理人進行全面分析...")
    await msg.send()

    # 獲取代理人和配置
    orchestrator_agent: Agent = cast(Agent, cl.user_session.get("orchestrator_agent"))
    config: RunConfig = cast(RunConfig, cl.user_session.get("config"))

    try:
        # 創建審查提示
        review_prompt = f"""請對以下程式碼進行全面的審查：

```
{message.content}
```

請按順序進行：
1. 語法和基本錯誤檢查
2. 性能和效率分析  
3. 程式碼風格和最佳實踐檢查

最後提供優先級排序的改進建議。"""

        print(f"\n[CODE REVIEW REQUEST]: {len(message.content)} characters\n")
        
        # 執行程式碼審查
        result = await Runner.run(orchestrator_agent, review_prompt, run_config=config)
        
        # 格式化審查報告
        review_report = f"""📋 **程式碼審查報告**

{result.final_output}

---
**審查完成！** 如需進一步分析其他程式碼，請直接貼上新的程式碼。"""

        # 更新消息內容
        msg.content = review_report
        await msg.update()

        # 記錄審查完成
        print(f"Code review completed for {len(message.content)} characters")
        print("=" * 60)

    except Exception as e:
        error_msg = f"""❌ **審查過程中發生錯誤**

錯誤詳情：{str(e)}

**建議：**
• 請確認程式碼格式正確
• 檢查網路連接是否正常
• 稍後再試一次

如問題持續，請聯絡技術支援。"""

        msg.content = error_msg
        await msg.update()
        print(f"Error during code review: {str(e)}")


if __name__ == "__main__":
    # 這裡不需要 asyncio.run(main())，因為 chainlit 會處理
    pass 