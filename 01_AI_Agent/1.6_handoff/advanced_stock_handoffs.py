# Advanced Stock Handoffs Examples
# 展示各種 handoff 進階用法

import asyncio
import os
import httpx
import chainlit as cl
from typing import cast
from dotenv import load_dotenv
from pydantic import BaseModel
from agents import Agent, ItemHelpers, MessageOutputItem, Runner, trace, AsyncOpenAI, OpenAIChatCompletionsModel, handoff, RunContextWrapper
from agents.run import RunConfig
from agents.extensions import handoff_filters
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX, prompt_with_handoff_instructions

# Load environment variables
load_dotenv()

# Get configuration from environment variables
API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = "gemini-1.5-flash"

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

# ============================================================================
# 1. 基本 Handoff 代理人
# ============================================================================

# 技術分析代理人 - 使用推薦的 handoff 提示
technical_analysis_agent = Agent(
    name="technical_analysis_agent",
    instructions=f"""{RECOMMENDED_PROMPT_PREFIX}
    您是一個專業的股票技術分析師。請分析股票的技術指標和圖表模式：

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

# 基本面分析代理人 - 使用推薦的 handoff 提示
fundamental_analysis_agent = Agent(
    name="fundamental_analysis_agent",
    instructions=f"""{RECOMMENDED_PROMPT_PREFIX}
    您是一個專業的股票基本面分析師。請分析公司的基本面數據：

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

# ============================================================================
# 2. 自訂 Handoff 輸入數據模型
# ============================================================================

class EscalationData(BaseModel):
    """升級分析請求數據模型"""
    reason: str
    urgency_level: str = "normal"  # low, normal, high
    user_experience: str = "beginner"  # beginner, intermediate, expert

class TechnicalAnalysisData(BaseModel):
    """技術分析請求數據模型"""
    timeframe: str = "daily"  # daily, weekly, monthly
    indicators: list[str] = ["RSI", "MACD", "MA"]
    focus_area: str = "trend"  # trend, pattern, support_resistance

class FundamentalAnalysisData(BaseModel):
    """基本面分析請求數據模型"""
    analysis_depth: str = "standard"  # quick, standard, comprehensive
    focus_metrics: list[str] = ["P/E", "P/B", "ROE"]
    comparison_peers: bool = True

# ============================================================================
# 3. Handoff 回調函數
# ============================================================================

async def on_technical_handoff(ctx: RunContextWrapper[None], input_data: TechnicalAnalysisData):
    """技術分析 handoff 回調函數"""
    print(f"🔍 技術分析 handoff 被調用")
    print(f"   時間框架: {input_data.timeframe}")
    print(f"   關注指標: {', '.join(input_data.indicators)}")
    print(f"   重點領域: {input_data.focus_area}")
    
    # 可以在這裡添加數據預處理邏輯
    # 例如：獲取歷史價格數據、計算技術指標等

async def on_fundamental_handoff(ctx: RunContextWrapper[None], input_data: FundamentalAnalysisData):
    """基本面分析 handoff 回調函數"""
    print(f"📊 基本面分析 handoff 被調用")
    print(f"   分析深度: {input_data.analysis_depth}")
    print(f"   關注指標: {', '.join(input_data.focus_metrics)}")
    print(f"   同業比較: {input_data.comparison_peers}")
    
    # 可以在這裡添加數據預處理邏輯
    # 例如：獲取財務數據、計算財務比率等

async def on_escalation_handoff(ctx: RunContextWrapper[None], input_data: EscalationData):
    """升級分析 handoff 回調函數"""
    print(f"🚨 升級分析 handoff 被調用")
    print(f"   原因: {input_data.reason}")
    print(f"   緊急程度: {input_data.urgency_level}")
    print(f"   用戶經驗: {input_data.user_experience}")
    
    # 可以在這裡添加緊急處理邏輯
    # 例如：記錄緊急請求、通知管理員等

# ============================================================================
# 4. 自訂 Handoff 對象
# ============================================================================

# 技術分析 handoff - 自訂工具名稱和描述
technical_handoff = handoff(
    agent=technical_analysis_agent,
    tool_name_override="analyze_technical_indicators",
    tool_description_override="深入分析股票技術指標、圖表模式和趨勢，提供專業的技術分析建議",
    on_handoff=on_technical_handoff,
    input_type=TechnicalAnalysisData,
)

# 基本面分析 handoff - 使用輸入過濾器
fundamental_handoff = handoff(
    agent=fundamental_analysis_agent,
    tool_name_override="evaluate_fundamentals",
    tool_description_override="全面評估公司基本面、財務指標和估值，提供長期投資建議",
    on_handoff=on_fundamental_handoff,
    input_type=FundamentalAnalysisData,
    input_filter=handoff_filters.remove_all_tools,  # 移除所有工具調用歷史
)

# 升級分析 handoff - 自訂回調和輸入
escalation_agent = Agent(
    name="escalation_agent",
    instructions=f"""{RECOMMENDED_PROMPT_PREFIX}
    您是一個高級股票分析專家，專門處理複雜或緊急的分析請求。
    
    您會收到升級請求的原因和緊急程度信息。請根據這些信息：
    1. 提供更深入的分析
    2. 考慮用戶的經驗水平
    3. 給出更詳細的建議
    4. 提供風險警告
    
    請確保分析既專業又易懂。""",
    handoff_description="處理複雜或緊急的股票分析請求",
    model=model
)

escalation_handoff = handoff(
    agent=escalation_agent,
    tool_name_override="escalate_analysis",
    tool_description_override="升級到高級分析專家，處理複雜或緊急的分析請求",
    on_handoff=on_escalation_handoff,
    input_type=EscalationData,
)

# ============================================================================
# 5. 主分類代理人 - 使用自訂 Handoffs
# ============================================================================

# 使用 prompt_with_handoff_instructions 自動添加 handoff 指令
triage_agent = Agent(
    name="advanced_stock_triage_agent",
    instructions=prompt_with_handoff_instructions("""您是一個高級股票分析分類專家。根據用戶的請求內容，決定將任務交給哪個專門代理人：

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

3. **升級分析代理人** - 當用戶：
   - 要求更深入的分析
   - 表達對分析結果不滿意
   - 需要緊急建議
   - 有複雜的投資需求

**Handoff 輸入數據：**
- 對於技術分析：提供時間框架、關注指標、重點領域
- 對於基本面分析：提供分析深度、關注指標、是否同業比較
- 對於升級分析：提供升級原因、緊急程度、用戶經驗

請根據用戶的具體需求，選擇最適合的專門代理人進行分析。"""),
    handoffs=[technical_handoff, fundamental_handoff, escalation_handoff],
    model=model
)

# ============================================================================
# 6. Chainlit 界面
# ============================================================================

@cl.on_chat_start
async def start():
    """設置高級股票分析代理人系統。"""
    
    config = RunConfig(
        model=model,
        model_provider=external_client,
        tracing_disabled=True
    )
    
    # 將代理人和配置存儲在會話中
    cl.user_session.set("config", config)
    cl.user_session.set("triage_agent", triage_agent)

    # 發送歡迎消息
    welcome_msg = """🚀 **歡迎來到高級股票分析 AI Agent 系統！** 💹

這是一個展示各種 handoff 進階用法的系統：

**🔧 進階功能：**
• **自訂輸入數據** - 技術分析、基本面分析、升級分析
• **Handoff 回調** - 實時記錄和分析請求
• **輸入過濾器** - 清理對話歷史
• **自訂工具名稱** - 更專業的工具描述

**💡 使用方法：**
請描述您的分析需求，系統會自動選擇最適合的專家！

**✨ 範例輸入：**
• "分析 AAPL 的技術指標，關注 RSI 和 MACD"
• "評估 TSLA 的財務狀況，深度分析"
• "我需要緊急分析 NVIDIA，有重要決策"
• "全面分析台積電，需要專家建議"

**📊 進階特性：**
- 自訂數據模型傳遞
- Handoff 事件回調
- 輸入過濾和清理
- 專業工具命名

請描述您的分析需求，體驗進階 handoff 功能！🚀"""

    await cl.Message(content=welcome_msg).send()


@cl.on_message
async def main(message: cl.Message):
    """處理股票分析請求。"""
    
    # 創建分析中的消息
    msg = cl.Message(content="📊 **正在分析您的請求...**\n\n請稍候，我正在選擇最適合的專家並準備分析數據...")
    await msg.send()

    # 獲取代理人和配置
    triage_agent: Agent = cast(Agent, cl.user_session.get("triage_agent"))
    config: RunConfig = cast(RunConfig, cl.user_session.get("config"))

    try:
        print(f"\n[ADVANCED STOCK ANALYSIS REQUEST]: {message.content}\n")
        
        # 執行分類和專業分析
        result = await Runner.run(triage_agent, message.content, run_config=config)
        
        # 格式化分析報告
        analysis_report = f"""📈 **高級股票分析報告**

**分析請求：** {message.content}

{result.final_output}

---
**分析完成！** 如需其他分析，請直接描述您的需求。

*本系統使用了進階 handoff 功能，包括自訂數據模型、回調函數和輸入過濾器。*"""

        # 更新消息內容
        msg.content = analysis_report
        await msg.update()

        # 記錄分析完成
        print(f"Advanced stock analysis completed for: {message.content}")
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
        print(f"Error during advanced stock analysis: {str(e)}")


if __name__ == "__main__":
    # 這裡不需要 asyncio.run(main())，因為 chainlit 會處理
    pass 