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
MODEL_NAME = "gemini-1.5-flash"


# self-hosted
BASE_URL = "https://ai-k8s.garmin.com/generative/stage/gpt-120b-service/v1"
API_KEY = "none"
MODEL_NAME = "gpt-oss-120b"

if not API_KEY:
    raise ValueError("GEMINI_API_KEY is not set. Please ensure it is defined in your .env file.")

# Create HTTP client with SSL bypass
http_client = httpx.AsyncClient(verify=False)

# external_client = AsyncOpenAI(
#     api_key=API_KEY,
#     base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
#     http_client=http_client
# )

external_client = AsyncOpenAI(
    base_url=BASE_URL,
    api_key=API_KEY,
    http_client=http_client
    )

model = OpenAIChatCompletionsModel(
    model=MODEL_NAME,
    openai_client=external_client
)

# 技術分析代理人
technical_analysis_agent = Agent(
    name="technical_analysis_agent",
    instructions="""您是一個專業的股票技術分析師。請分析股票的技術指標和圖表模式：

**技術指標分析：**
- 移動平均線 (MA, EMA)
- 相對強弱指數 (RSI)
- 布林通道 (Bollinger Bands)
- MACD 指標
- 成交量分析
- 支撐和阻力位

**圖表模式識別：**
- 頭肩頂/底形態
- 雙頂/雙底
- 三角形整理
- 旗形和三角旗
- 缺口分析

**趨勢分析：**
- 短期、中期、長期趨勢
- 趨勢強度和持續性
- 趨勢反轉信號

請提供具體的技術分析建議和風險評估。""",
    handoff_description="專門進行股票技術分析和圖表模式識別",
    model=model
)

# 基本面分析代理人
fundamental_analysis_agent = Agent(
    name="fundamental_analysis_agent",
    instructions="""您是一個專業的股票基本面分析師。請分析公司的基本面數據：

**財務指標分析：**
- 市盈率 (P/E)
- 市淨率 (P/B)
- 市銷率 (P/S)
- 股息收益率
- 債務比率
- 現金流分析

**公司基本面：**
- 營收增長率
- 利潤率趨勢
- 市場份額
- 競爭優勢
- 管理團隊評估
- 行業地位

**宏觀經濟因素：**
- 行業前景
- 經濟週期影響
- 政策法規變化
- 市場競爭格局

**估值分析：**
- 內在價值評估
- 相對估值比較
- 成長性評估
- 風險因素分析

請提供詳細的基本面分析報告和投資建議。""",
    handoff_description="專門進行股票基本面分析和公司估值",
    model=model
)

# 市場情緒分析代理人
market_sentiment_agent = Agent(
    name="market_sentiment_agent",
    instructions="""您是一個專業的市場情緒分析師。請分析股票相關的市場情緒和輿論：

**新聞情緒分析：**
- 財經新聞影響
- 分析師評級變化
- 市場評論和預測
- 社交媒體情緒

**市場情緒指標：**
- 恐慌指數 (VIX)
- 投資者信心指數
- 機構投資者動向
- 散戶投資者情緒

**事件驅動分析：**
- 財報發布影響
- 管理層變動
- 併購重組消息
- 政策法規變化

**情緒趨勢：**
- 短期情緒波動
- 長期情緒趨勢
- 情緒極端值分析
- 情緒反轉信號

請提供市場情緒分析報告和對股價的潛在影響評估。""",
    handoff_description="專門分析市場情緒、新聞影響和投資者心理",
    model=model
)

# 分類代理人 (Triage Agent)
triage_agent = Agent(
    name="stock_triage_agent",
    instructions="""您是一個股票分析分類專家。根據用戶的請求內容，決定將任務交給哪個專門代理人：

**分類規則：**

1. **技術分析代理人** - 當用戶詢問：
   - 技術指標 (RSI, MACD, 移動平均線等)
   - 圖表模式 (頭肩頂、雙頂等)
   - 趨勢分析
   - 支撐阻力位
   - 短期交易建議
   - 進場/出場時機

2. **基本面分析代理人** - 當用戶詢問：
   - 財務指標 (P/E, P/B, 股息等)
   - 公司估值
   - 長期投資建議
   - 公司基本面
   - 行業分析
   - 價值投資

3. **市場情緒分析代理人** - 當用戶詢問：
   - 新聞影響
   - 市場情緒
   - 分析師評級
   - 社交媒體討論
   - 事件驅動分析
   - 投資者心理

**綜合分析請求** - 如果用戶要求全面分析，您可以：
- 先進行技術分析
- 再進行基本面分析
- 最後進行市場情緒分析
- 提供綜合建議

請根據用戶的具體需求，選擇最適合的專門代理人進行分析。""",
    handoffs=[technical_analysis_agent, fundamental_analysis_agent, market_sentiment_agent],
    model=model
)


@cl.on_chat_start
async def start():
    """設置股票分析代理人系統。"""
    
    config = RunConfig(
        model=model,
        model_provider=external_client,
        tracing_disabled=True
    )
    
    # 將代理人和配置存儲在會話中
    cl.user_session.set("config", config)
    cl.user_session.set("triage_agent", triage_agent)

    # 發送歡迎消息
    welcome_msg = """📈 **歡迎來到股票分析 AI Agent 系統！** 💹

我是您的專業股票分析助手，提供三種專門分析服務：

**🔍 分析功能：**
• **技術分析** - 圖表模式、技術指標、趨勢分析
• **基本面分析** - 財務指標、公司估值、行業分析  
• **市場情緒分析** - 新聞影響、投資者心理、輿論分析

**💡 使用方法：**
請描述您的分析需求，我會自動選擇最適合的專家為您分析！

**✨ 範例輸入：**
• "分析 AAPL 的技術指標" → 技術分析專家
• "評估 TSLA 的財務狀況" → 基本面分析專家
• "查看 NVIDIA 的市場情緒" → 市場情緒分析專家
• "全面分析台積電" → 綜合分析

**📊 分析內容：**
- 技術指標 (RSI, MACD, 移動平均線)
- 財務比率和估值
- 市場情緒和新聞影響
- 投資建議和風險評估

請描述您的分析需求，我會立即為您選擇最適合的專家！🚀"""

    await cl.Message(content=welcome_msg).send()


@cl.on_message
async def main(message: cl.Message):
    """處理股票分析請求。"""
    
    # 創建分析中的消息
    msg = cl.Message(content="📊 **正在分析您的請求...**\n\n請稍候，我正在選擇最適合的專家為您分析...")
    await msg.send()

    # 獲取代理人和配置
    triage_agent: Agent = cast(Agent, cl.user_session.get("triage_agent"))
    config: RunConfig = cast(RunConfig, cl.user_session.get("config"))

    try:
        print(f"\n[STOCK ANALYSIS REQUEST]: {message.content}\n")
        
        # 執行分類和專業分析
        result = await Runner.run(triage_agent, message.content, run_config=config)
        
        # 格式化分析報告
        analysis_report = f"""📈 **股票分析報告**

**分析請求：** {message.content}

{result.final_output}

---
**分析完成！** 如需其他分析，請直接描述您的需求。"""

        # 更新消息內容
        msg.content = analysis_report
        await msg.update()

        # 記錄分析完成
        print(f"Stock analysis completed for: {message.content}")
        print("=" * 60)

    except Exception as e:
        error_msg = f"""❌ **分析過程中發生錯誤**

錯誤詳情：{str(e)}

**建議：**
• 請確認您的分析需求描述清楚
• 檢查網路連接是否正常
• 稍後再試一次

如問題持續，請聯絡技術支援。"""

        msg.content = error_msg
        await msg.update()
        print(f"Error during stock analysis: {str(e)}")


if __name__ == "__main__":
    # 這裡不需要 asyncio.run(main())，因為 chainlit 會處理
    pass
