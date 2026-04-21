"""
Structured Output 教學 - OpenAI Agent SDK

此範例展示如何使用 OpenAI Agent SDK 來產生結構化輸出。
結構化輸出可以確保 AI 回應符合特定的資料格式，方便程式進行後續處理。

學習重點：
1. 使用 Pydantic 定義資料結構
2. 讓 Agent 輸出符合結構的資料
3. 驗證和使用結構化輸出
4. 多種實用的結構化輸出範例
"""

import os
import httpx
import asyncio
import json
from dotenv import load_dotenv
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

from agents import (
    Agent,
    Runner,
    AsyncOpenAI,
    OpenAIChatCompletionsModel,
    RunConfig,
    set_tracing_disabled,
)

# Load environment variables
load_dotenv()

# Get configuration from environment variables
API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = "gemini-2.5-flash" 
BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"

if not API_KEY:
    raise ValueError("GEMINI_API_KEY is not set. Please ensure it is defined in your .env file.")


# ============= 定義結構化輸出的資料模型 =============

class PersonInfo(BaseModel):
    """個人資訊結構"""
    name: str = Field(description="人物姓名")
    age: int = Field(description="年齡")
    occupation: str = Field(description="職業")
    hobbies: List[str] = Field(description="興趣愛好列表")
    email: Optional[str] = Field(default=None, description="電子郵件（選填）")


class BookReview(BaseModel):
    """書籍評論結構"""
    title: str = Field(description="書名")
    author: str = Field(description="作者")
    rating: int = Field(description="評分 (1-5)", ge=1, le=5)
    summary: str = Field(description="內容摘要")
    pros: List[str] = Field(description="優點列表")
    cons: List[str] = Field(description="缺點列表")
    recommendation: str = Field(description="推薦理由")


class Recipe(BaseModel):
    """食譜結構"""
    name: str = Field(description="菜名")
    cuisine: str = Field(description="菜系類型")
    difficulty: str = Field(description="難度等級: 簡單/中等/困難")
    prep_time: int = Field(description="準備時間（分鐘）")
    cook_time: int = Field(description="烹飪時間（分鐘）")
    servings: int = Field(description="份量（人份）")
    ingredients: List[str] = Field(description="食材列表")
    steps: List[str] = Field(description="烹飪步驟")
    tips: Optional[List[str]] = Field(default=None, description="烹飪技巧")


class TaskAnalysis(BaseModel):
    """任務分析結構"""
    task_name: str = Field(description="任務名稱")
    priority: str = Field(description="優先級: 高/中/低")
    estimated_hours: float = Field(description="預估工時")
    subtasks: List[str] = Field(description="子任務列表")
    dependencies: Optional[List[str]] = Field(default=None, description="依賴項")
    risks: List[str] = Field(description="潛在風險")
    resources_needed: List[str] = Field(description="所需資源")


class ProductAnalysis(BaseModel):
    """產品分析結構"""
    product_name: str = Field(description="產品名稱")
    category: str = Field(description="產品類別")
    target_audience: str = Field(description="目標受眾")
    key_features: List[str] = Field(description="主要功能特色")
    strengths: List[str] = Field(description="優勢")
    weaknesses: List[str] = Field(description="劣勢")
    market_opportunities: List[str] = Field(description="市場機會")
    threats: List[str] = Field(description="威脅")
    pricing_strategy: str = Field(description="定價策略建議")


# ============= 建立 Agent 和執行函式 =============

async def create_client():
    """建立 OpenAI 客戶端"""
    http_client = httpx.AsyncClient(verify=False)
    client = AsyncOpenAI(
        base_url=BASE_URL,
        api_key=API_KEY,
        http_client=http_client
    )
    return client


async def example_1_person_info():
    """範例 1: 從文字中提取結構化的個人資訊"""
    print("\n" + "="*60)
    print("範例 1: 提取個人資訊")
    print("="*60)
    
    client = await create_client()
    model = OpenAIChatCompletionsModel(
        model=MODEL_NAME,
        openai_client=client
    )
    
    agent = Agent(
        name="InfoExtractor",
        instructions="""你是一個專業的資訊提取助手。
        當用戶提供一段文字描述時，請仔細分析並提取其中的個人資訊。
        請確保資料格式正確且完整。""",
        model=model,
    )
    
    text = """
    張小明今年28歲，是一位軟體工程師。
    他平時喜歡打籃球、閱讀科技書籍和玩電動遊戲。
    可以透過 xiaoming.zhang@example.com 聯繫他。
    """
    
    result = await Runner.run(
        agent,
        f"請從以下文字中提取個人資訊，並以 JSON 格式輸出：\n{text}\n\n"
        f"請確保輸出符合以下結構：\n{PersonInfo.model_json_schema()}"
    )
    
    print(f"\n原始文字：\n{text}")
    print(f"\n提取結果：\n{result.final_output}")
    

async def example_2_book_review():
    """範例 2: 生成結構化的書籍評論"""
    print("\n" + "="*60)
    print("範例 2: 生成書籍評論")
    print("="*60)
    
    client = await create_client()
    model = OpenAIChatCompletionsModel(
        model=MODEL_NAME,
        openai_client=client
    )
    
    agent = Agent(
        name="BookReviewer",
        instructions="""你是一位專業的書評家。
        請為指定的書籍撰寫詳細的評論，包含評分、優缺點和推薦理由。
        評分範圍是 1-5 分，其中 5 分最高。""",
        model=model,
    )
    
    book_name = "Python 程式設計入門"
    
    result = await Runner.run(
        agent,
        f"請為《{book_name}》這本書撰寫一份詳細的評論。\n\n"
        f"請確保輸出符合以下 JSON 結構：\n{BookReview.model_json_schema()}"
    )
    
    print(f"\n書籍：{book_name}")
    print(f"\n評論結果：\n{result.final_output}")


async def example_3_recipe():
    """範例 3: 生成結構化的食譜"""
    print("\n" + "="*60)
    print("範例 3: 生成食譜")
    print("="*60)
    
    client = await create_client()
    model = OpenAIChatCompletionsModel(
        model=MODEL_NAME,
        openai_client=client
    )
    
    agent = Agent(
        name="ChefAssistant",
        instructions="""你是一位專業的廚師助手。
        請提供詳細的食譜資訊，包含食材、步驟、時間和烹飪技巧。
        確保資訊清楚、易懂、可執行。""",
        model=model,
    )
    
    dish = "蒜香奶油蝦"
    
    result = await Runner.run(
        agent,
        f"請提供「{dish}」的詳細食譜。\n\n"
        f"請確保輸出符合以下 JSON 結構：\n{Recipe.model_json_schema()}"
    )
    
    print(f"\n菜名：{dish}")
    print(f"\n食譜：\n{result.final_output}")


async def example_4_task_analysis():
    """範例 4: 任務分析與分解"""
    print("\n" + "="*60)
    print("範例 4: 任務分析")
    print("="*60)
    
    client = await create_client()
    model = OpenAIChatCompletionsModel(
        model=MODEL_NAME,
        openai_client=client
    )
    
    agent = Agent(
        name="ProjectManager",
        instructions="""你是一位經驗豐富的專案經理。
        請分析任務需求，將其分解為可執行的子任務，
        並評估所需時間、資源和潛在風險。""",
        model=model,
    )
    
    task = "開發一個電商網站的購物車功能"
    
    result = await Runner.run(
        agent,
        f"請分析以下任務並提供詳細的分解：{task}\n\n"
        f"請確保輸出符合以下 JSON 結構：\n{TaskAnalysis.model_json_schema()}"
    )
    
    print(f"\n任務：{task}")
    print(f"\n分析結果：\n{result.final_output}")


async def example_5_product_analysis():
    """範例 5: 產品 SWOT 分析"""
    print("\n" + "="*60)
    print("範例 5: 產品分析")
    print("="*60)
    
    client = await create_client()
    model = OpenAIChatCompletionsModel(
        model=MODEL_NAME,
        openai_client=client
    )
    
    agent = Agent(
        name="ProductAnalyst",
        instructions="""你是一位專業的產品分析師。
        請進行詳細的產品分析，包含 SWOT 分析（優勢、劣勢、機會、威脅）
        和定價策略建議。""",
        model=model,
    )
    
    product = "智慧手環健康追蹤裝置"
    
    result = await Runner.run(
        agent,
        f"請為「{product}」進行詳細的產品分析。\n\n"
        f"請確保輸出符合以下 JSON 結構：\n{ProductAnalysis.model_json_schema()}"
    )
    
    print(f"\n產品：{product}")
    print(f"\n分析結果：\n{result.final_output}")


async def main():
    """主程式 - 執行所有範例"""
    print("\n Structured Output 教學 - OpenAI Agent SDK")
    print("=" * 60)
    print("本教學展示如何使用結構化輸出來確保 AI 回應符合特定格式")
    print("=" * 60)
    
    # 關閉追蹤以提高效能
    set_tracing_disabled(disabled=True)
    
    # 執行所有範例
    try:
        await example_1_person_info()
        await example_2_book_review()
        await example_3_recipe()
        await example_4_task_analysis()
        await example_5_product_analysis()
        
        print("\n" + "="*60)
        print("✅ 所有範例執行完成！")
        print("="*60)
        print("\n💡 重點回顧：")
        print("1. 使用 Pydantic 定義清晰的資料結構")
        print("2. 透過 model_json_schema() 提供結構給 Agent")
        print("3. 在 instructions 中說明輸出要求")
        print("4. 結構化輸出讓資料更容易驗證和使用")
        print("5. 可用於資訊提取、資料生成、分析等場景")
        
    except Exception as e:
        print(f"\n❌ 錯誤: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

