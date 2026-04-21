"""
Multi-Agent Orchestration 教學 - OpenAI Agents SDK

此範例展示如何協調多個 AI Agent 一起工作，完成複雜任務。
學習兩種主要的協調方式：
1. 透過 LLM 協調（使用 Handoffs）
2. 透過程式碼協調（使用結構化輸出和流程控制）

學習重點：
1. Agent to Agent Handoffs（代理間轉移）
2. 使用 Structured Output 進行任務分類
3. 順序執行多個 Agents（Chaining）
4. 並行執行多個 Agents（Parallel）
5. 迴圈執行與評估（Loop with Evaluation）
"""

import os
import httpx
import asyncio
from dotenv import load_dotenv
from typing import List, Literal
from pydantic import BaseModel, Field

from agents import (
    Agent,
    Runner,
    AsyncOpenAI,
    OpenAIChatCompletionsModel,
    set_tracing_disabled,
)

# 載入環境變數
load_dotenv()

# 取得設定
API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = "gemini-2.5-flash"
BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"

if not API_KEY:
    raise ValueError("GEMINI_API_KEY is not set. Please ensure it is defined in your .env file.")

# 設定模型
model = OpenAIChatCompletionsModel(
    model_name=f"models/{MODEL_NAME}",
    client=AsyncOpenAI(
        base_url=BASE_URL,
        api_key=API_KEY,
        http_client=httpx.AsyncClient(
            limits=httpx.Limits(
                max_connections=1000,
                max_keepalive_connections=100
            )
        )
    ),
)

# 關閉追蹤
set_tracing_disabled(True)


# ============= 方式 1: 透過 LLM 協調（使用 Handoffs）=============

print("=" * 60)
print("範例 1: 透過 LLM 協調 - 客服系統")
print("=" * 60)

"""
場景：客服系統有多個專業代理
- Triage Agent：負責分類問題
- Billing Agent：處理帳單問題
- Technical Agent：處理技術問題
- Refund Agent：處理退款問題

使用 Handoffs 讓 LLM 自動決定要轉給哪個專業代理
"""

# 定義專業代理
billing_agent = Agent(
    name="BillingAgent",
    instructions="""
    你是帳單專家，負責處理所有帳單相關問題。
    你可以：
    - 查詢帳單明細
    - 解釋收費項目
    - 調整付款方式
    
    回答時要清楚說明收費細節。
    """,
    model=model,
)

technical_agent = Agent(
    name="TechnicalAgent",
    instructions="""
    你是技術支援專家，負責處理所有技術問題。
    你可以：
    - 排除系統故障
    - 提供使用教學
    - 解決連線問題
    
    回答時要提供明確的步驟。
    """,
    model=model,
)

refund_agent = Agent(
    name="RefundAgent",
    instructions="""
    你是退款處理專家，負責處理退款申請。
    你可以：
    - 評估退款資格
    - 處理退款申請
    - 說明退款流程
    
    回答時要說明退款政策和預計時間。
    """,
    model=model,
)

# Triage Agent 負責分流
triage_agent = Agent(
    name="TriageAgent",
    instructions="""
    你是客服系統的第一線人員，負責了解客戶問題並轉給適當的專家。
    
    根據問題類型，轉給：
    - BillingAgent：帳單、收費、付款相關問題
    - TechnicalAgent：系統、功能、操作相關問題  
    - RefundAgent：退款、取消訂閱相關問題
    
    如果問題簡單，可以直接回答，不需要轉給專家。
    """,
    model=model,
    handoffs=[billing_agent, technical_agent, refund_agent],
)


async def example1_llm_orchestration():
    """範例 1: 透過 LLM 協調"""
    
    # 測試不同類型的問題
    test_queries = [
        "我想知道上個月的帳單為什麼這麼高？",
        "我的應用程式一直當機，該怎麼辦？",
        "我想取消訂閱並申請退款",
    ]
    
    for query in test_queries:
        print(f"\n{'=' * 60}")
        print(f"使用者問題: {query}")
        print(f"{'=' * 60}")
        
        result = await Runner.run(triage_agent, query)
        
        print(f"\n最終回應: {result.final_output}")
        
        # 顯示轉移歷史
        if hasattr(result, 'handoff_history') and result.handoff_history:
            print(f"\n轉移路徑: {' → '.join([h.agent_name for h in result.handoff_history])}")


# ============= 方式 2: 透過程式碼協調 - 結構化輸出分類 =============

print("\n\n" + "=" * 60)
print("範例 2: 透過程式碼協調 - 任務分類")
print("=" * 60)

"""
場景：根據任務類型分類，然後選擇對應的專家處理
使用 Structured Output 讓 LLM 輸出結構化的分類結果
"""

# 定義任務分類結構
class TaskCategory(BaseModel):
    """任務分類"""
    category: Literal["research", "writing", "coding", "analysis"] = Field(
        description="任務類型：research(研究), writing(寫作), coding(程式設計), analysis(分析)"
    )
    confidence: float = Field(
        description="分類信心度（0-1）",
        ge=0,
        le=1
    )
    reason: str = Field(
        description="分類原因"
    )


# 分類器 Agent
classifier_agent = Agent(
    name="ClassifierAgent",
    instructions="""
    你是任務分類專家，負責判斷任務屬於哪種類型：
    
    - research：需要搜尋資訊、查找資料
    - writing：需要撰寫文章、報告、文案
    - coding：需要寫程式、修改程式碼
    - analysis：需要分析資料、解讀結果
    
    仔細判斷任務的主要需求，給出分類、信心度和原因。
    """,
    model=model,
    output_schema=TaskCategory,
)

# 各領域專家 Agent
research_agent = Agent(
    name="ResearchAgent",
    instructions="""
    你是研究專家，擅長搜尋和整理資訊。
    回答時要：
    1. 列出資訊來源（即使是假設的）
    2. 組織成結構化的內容
    3. 提供關鍵洞察
    """,
    model=model,
)

writing_agent = Agent(
    name="WritingAgent", 
    instructions="""
    你是寫作專家，擅長撰寫各種文案。
    回答時要：
    1. 結構清晰（引言、內容、結論）
    2. 語言生動有趣
    3. 符合目標受眾需求
    """,
    model=model,
)

coding_agent = Agent(
    name="CodingAgent",
    instructions="""
    你是程式設計專家，擅長寫高品質的程式碼。
    回答時要：
    1. 程式碼清晰易讀
    2. 加上註解說明
    3. 考慮錯誤處理
    """,
    model=model,
)

analysis_agent = Agent(
    name="AnalysisAgent",
    instructions="""
    你是資料分析專家，擅長解讀資料和趨勢。
    回答時要：
    1. 指出關鍵發現
    2. 提供資料解讀
    3. 給出可行建議
    """,
    model=model,
)


async def example2_structured_routing():
    """範例 2: 使用結構化輸出進行任務路由"""
    
    tasks = [
        "幫我研究 AI Agent 的最新發展趨勢",
        "寫一篇關於永續發展的部落格文章",
        "用 Python 寫一個計算費氏數列的函式",
        "分析這個月的銷售資料，找出改善方向",
    ]
    
    # 專家對應表
    expert_agents = {
        "research": research_agent,
        "writing": writing_agent,
        "coding": coding_agent,
        "analysis": analysis_agent,
    }
    
    for task in tasks:
        print(f"\n{'=' * 60}")
        print(f"任務: {task}")
        print(f"{'=' * 60}")
        
        # 步驟 1: 分類任務
        classification_result = await Runner.run(classifier_agent, task)
        category_data = classification_result.final_output_as(TaskCategory)
        
        print(f"\n分類結果:")
        print(f"  類型: {category_data.category}")
        print(f"  信心度: {category_data.confidence:.2f}")
        print(f"  原因: {category_data.reason}")
        
        # 步驟 2: 選擇對應的專家
        expert = expert_agents[category_data.category]
        print(f"\n選擇專家: {expert.name}")
        
        # 步驟 3: 讓專家處理任務
        expert_result = await Runner.run(expert, task)
        print(f"\n專家回應:\n{expert_result.final_output}")


# ============= 方式 3: 順序執行（Chaining）=============

print("\n\n" + "=" * 60)
print("範例 3: 順序執行 - 部落格文章產生流程")
print("=" * 60)

"""
場景：將複雜任務拆解成步驟，由不同 Agent 依序處理
研究 → 大綱 → 撰寫 → 評論 → 修改
"""


class BlogOutline(BaseModel):
    """部落格大綱"""
    title: str = Field(description="文章標題")
    sections: List[str] = Field(description="各段落標題列表")
    target_audience: str = Field(description="目標讀者群")
    key_points: List[str] = Field(description="要傳達的關鍵訊息")


class BlogCritique(BaseModel):
    """部落格評論"""
    score: int = Field(description="整體評分（1-10）", ge=1, le=10)
    strengths: List[str] = Field(description="優點")
    improvements: List[str] = Field(description="需要改進的地方")
    suggestions: str = Field(description="具體修改建議")


# 定義流程中的各個 Agent
researcher = Agent(
    name="Researcher",
    instructions="你是研究專家，負責收集主題相關的資訊和數據。",
    model=model,
)

outliner = Agent(
    name="Outliner",
    instructions="你是內容規劃專家，負責根據研究資料建立文章大綱。",
    model=model,
    output_schema=BlogOutline,
)

writer = Agent(
    name="Writer",
    instructions="你是專業作家，負責根據大綱撰寫完整的文章內容。",
    model=model,
)

critic = Agent(
    name="Critic",
    instructions="""
    你是編輯，負責評論文章品質。
    評估標準：
    - 內容完整性
    - 邏輯清晰度
    - 語言品質
    - 可讀性
    """,
    model=model,
    output_schema=BlogCritique,
)

editor = Agent(
    name="Editor",
    instructions="你是修訂專家，根據評論建議改善文章。",
    model=model,
)


async def example3_sequential_chain():
    """範例 3: 順序執行多個 Agents"""
    
    topic = "人工智慧如何改變教育"
    
    print(f"\n主題: {topic}")
    print(f"\n{'=' * 60}")
    
    # 步驟 1: 研究
    print("\n步驟 1: 研究階段")
    research_result = await Runner.run(
        researcher,
        f"請收集關於「{topic}」的資訊，包括現況、趨勢、案例等。"
    )
    research_content = research_result.final_output
    print(f"研究結果: {research_content[:200]}...")
    
    # 步驟 2: 建立大綱
    print("\n步驟 2: 大綱規劃")
    outline_result = await Runner.run(
        outliner,
        f"根據以下研究內容，建立部落格文章大綱：\n\n{research_content}"
    )
    outline = outline_result.final_output_as(BlogOutline)
    print(f"標題: {outline.title}")
    print(f"段落: {', '.join(outline.sections)}")
    
    # 步驟 3: 撰寫文章
    print("\n步驟 3: 撰寫文章")
    writing_result = await Runner.run(
        writer,
        f"根據以下大綱撰寫完整文章：\n\n"
        f"標題: {outline.title}\n"
        f"段落: {outline.sections}\n"
        f"關鍵訊息: {outline.key_points}\n"
        f"目標讀者: {outline.target_audience}\n\n"
        f"參考資料: {research_content}"
    )
    draft_article = writing_result.final_output
    print(f"文章草稿: {draft_article[:300]}...")
    
    # 步驟 4: 評論
    print("\n步驟 4: 編輯評論")
    critique_result = await Runner.run(
        critic,
        f"請評論以下文章：\n\n{draft_article}"
    )
    critique = critique_result.final_output_as(BlogCritique)
    print(f"評分: {critique.score}/10")
    print(f"優點: {', '.join(critique.strengths[:2])}")
    print(f"需改進: {', '.join(critique.improvements[:2])}")
    
    # 步驟 5: 修改（如果需要）
    if critique.score < 8:
        print("\n步驟 5: 修改文章")
        final_result = await Runner.run(
            editor,
            f"根據以下評論修改文章：\n\n"
            f"原文章：\n{draft_article}\n\n"
            f"評論建議：\n{critique.suggestions}"
        )
        final_article = final_result.final_output
        print(f"最終文章: {final_article[:300]}...")
    else:
        print("\n文章品質良好，無需修改！")
        final_article = draft_article
    
    return final_article


# ============= 方式 4: 並行執行（Parallel）=============

print("\n\n" + "=" * 60)
print("範例 4: 並行執行 - 多角度分析")
print("=" * 60)

"""
場景：同時從多個角度分析同一個主題
可以節省時間，因為各個分析是獨立的
"""


class Analysis(BaseModel):
    """分析結果"""
    perspective: str = Field(description="分析角度")
    key_findings: List[str] = Field(description="關鍵發現")
    recommendations: List[str] = Field(description="建議")


# 不同角度的分析師
market_analyst = Agent(
    name="MarketAnalyst",
    instructions="你是市場分析師，從市場和商業角度分析。",
    model=model,
    output_schema=Analysis,
)

tech_analyst = Agent(
    name="TechAnalyst",
    instructions="你是技術分析師，從技術和創新角度分析。",
    model=model,
    output_schema=Analysis,
)

user_analyst = Agent(
    name="UserAnalyst",
    instructions="你是使用者研究員，從使用者體驗角度分析。",
    model=model,
    output_schema=Analysis,
)

risk_analyst = Agent(
    name="RiskAnalyst",
    instructions="你是風險管理專家，從風險和挑戰角度分析。",
    model=model,
    output_schema=Analysis,
)


async def example4_parallel_execution():
    """範例 4: 並行執行多個 Agents"""
    
    topic = "公司應該投資開發 AI 聊天機器人嗎？"
    
    print(f"\n分析主題: {topic}\n")
    
    # 同時執行所有分析（使用 asyncio.gather）
    print("開始並行分析...")
    
    results = await asyncio.gather(
        Runner.run(market_analyst, f"請從市場角度分析：{topic}"),
        Runner.run(tech_analyst, f"請從技術角度分析：{topic}"),
        Runner.run(user_analyst, f"請從使用者角度分析：{topic}"),
        Runner.run(risk_analyst, f"請從風險角度分析：{topic}"),
    )
    
    # 整理結果
    analyses = [result.final_output_as(Analysis) for result in results]
    
    print("\n分析結果彙整：\n")
    for analysis in analyses:
        print(f"{'=' * 60}")
        print(f"角度: {analysis.perspective}")
        print(f"\n關鍵發現:")
        for finding in analysis.key_findings[:3]:
            print(f"  • {finding}")
        print(f"\n建議:")
        for rec in analysis.recommendations[:2]:
            print(f"  • {rec}")
        print()


# ============= 方式 5: 迴圈執行與評估 =============

print("\n\n" + "=" * 60)
print("範例 5: 迴圈執行 - 持續改進直到達標")
print("=" * 60)

"""
場景：讓 Agent 產生內容，然後評估，如果不符合標準就繼續改進
適合需要反覆優化的任務
"""


class CodeQuality(BaseModel):
    """程式碼品質評估"""
    is_acceptable: bool = Field(description="是否達到品質標準")
    score: int = Field(description="品質分數（1-10）", ge=1, le=10)
    issues: List[str] = Field(description="發現的問題")
    suggestions: str = Field(description="改進建議")


code_generator = Agent(
    name="CodeGenerator",
    instructions="""
    你是程式設計師，負責寫程式碼。
    要求：
    - 程式碼清晰
    - 有適當註解
    - 有錯誤處理
    - 有使用範例
    """,
    model=model,
)

code_reviewer = Agent(
    name="CodeReviewer",
    instructions="""
    你是資深工程師，負責 Code Review。
    評估標準：
    - 程式碼品質（可讀性、結構）
    - 錯誤處理
    - 註解完整性
    - 最佳實踐
    
    只有當分數 >= 8 才算達標（is_acceptable=True）
    """,
    model=model,
    output_schema=CodeQuality,
)


async def example5_loop_with_evaluation():
    """範例 5: 迴圈執行直到達標"""
    
    task = "寫一個 Python 函式，可以安全地讀取 JSON 檔案"
    max_iterations = 3
    
    print(f"\n任務: {task}\n")
    
    current_code = None
    iteration = 0
    
    while iteration < max_iterations:
        iteration += 1
        print(f"\n{'=' * 60}")
        print(f"第 {iteration} 次迭代")
        print(f"{'=' * 60}")
        
        # 產生或改進程式碼
        if current_code is None:
            # 第一次：產生新程式碼
            prompt = task
        else:
            # 後續：根據建議改進
            prompt = f"請根據以下建議改進程式碼：\n\n原程式碼：\n{current_code}\n\n改進建議：\n{feedback}"
        
        code_result = await Runner.run(code_generator, prompt)
        current_code = code_result.final_output
        print(f"\n產生的程式碼:\n{current_code[:400]}...")
        
        # 評估程式碼品質
        review_result = await Runner.run(
            code_reviewer,
            f"請評估以下程式碼：\n\n{current_code}"
        )
        quality = review_result.final_output_as(CodeQuality)
        
        print(f"\n評估結果:")
        print(f"  分數: {quality.score}/10")
        print(f"  是否達標: {'✅ 是' if quality.is_acceptable else '❌ 否'}")
        
        if quality.issues:
            print(f"  發現問題:")
            for issue in quality.issues[:3]:
                print(f"    • {issue}")
        
        # 檢查是否達標
        if quality.is_acceptable:
            print(f"\n✅ 程式碼品質達標！（第 {iteration} 次迭代）")
            break
        else:
            print(f"\n繼續改進...")
            feedback = quality.suggestions
    
    if not quality.is_acceptable:
        print(f"\n⚠️ 達到最大迭代次數（{max_iterations}），但仍未完全達標")
    
    return current_code


# ============= 主程式 =============

async def main():
    """執行所有範例"""
    
    print("\n")
    print("🤖 Multi-Agent Orchestration 教學")
    print("=" * 60)
    
    # 範例 1: 透過 LLM 協調（Handoffs）
    await example1_llm_orchestration()
    
    # 範例 2: 透過程式碼協調（結構化路由）
    await example2_structured_routing()
    
    # 範例 3: 順序執行（Chaining）
    await example3_sequential_chain()
    
    # 範例 4: 並行執行（Parallel）
    await example4_parallel_execution()
    
    # 範例 5: 迴圈執行與評估
    await example5_loop_with_evaluation()
    
    print("\n\n" + "=" * 60)
    print("✅ 所有範例執行完成！")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
