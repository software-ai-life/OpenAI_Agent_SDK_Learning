"""
Guardrails 教學 - OpenAI Agents SDK

此範例展示如何使用 Guardrails（護欄機制）來控制和保護 AI Agent 的行為。
Guardrails 就像是給 AI 設定的安全規則，確保 AI 的回應符合我們的要求。

學習重點：
1. 什麼是 Input Guardrails（輸入防護）
2. 什麼是 Output Guardrails（輸出防護）
3. 如何實作內容過濾
4. 如何防止敏感資訊洩漏
5. 如何確保回應品質
"""

import os
import httpx
import asyncio
import re
from dotenv import load_dotenv
from typing import List, Optional, Literal
from pydantic import BaseModel, Field

from agents import (
    Agent,
    Runner,
    AsyncOpenAI,
    OpenAIChatCompletionsModel,
    set_tracing_disabled,
    input_guardrail,
    output_guardrail,
    GuardrailFunctionOutput,
    InputGuardrailTripwireTriggered,
    OutputGuardrailTripwireTriggered,
    RunContextWrapper,
    TResponseInputItem,
)

# 載入環境變數
load_dotenv()

# 取得設定
API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = "gemini-2.5-flash"
BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"

if not API_KEY:
    raise ValueError("GEMINI_API_KEY is not set. Please ensure it is defined in your .env file.")


# ============= 定義 Guardrails（護欄機制）=============

# 定義不當詞彙清單
BLOCKED_WORDS = [
    "靠", "幹", "他媽的", "fuck", "shit", "不雅詞彙",
    "攻擊性詞彙", "歧視詞彙"
]

ALLOWED_TOPICS = [
    "程式", "編程", "程式碼", "bug", "除錯", "開發",
    "python", "javascript", "技術", "軟體", "演算法",
    "資料結構", "api", "database", "資料庫"
]

TOXIC_PATTERNS = [
    "傷害", "暴力", "攻擊", "仇恨", "歧視",
    "自殘", "非法", "危險行為"
]


@input_guardrail
async def profanity_guardrail(
    ctx: RunContextWrapper[None],
    agent: Agent,
    input: str | list[TResponseInputItem]
) -> GuardrailFunctionOutput:
    """輸入防護：過濾不當言論和髒話"""
    
    # 將輸入轉為字串
    input_text = input if isinstance(input, str) else str(input)
    input_lower = input_text.lower()
    
    # 檢查是否包含不當詞彙
    for word in BLOCKED_WORDS:
        if word.lower() in input_lower:
            return GuardrailFunctionOutput(
                output_info="包含不當詞彙",
                tripwire_triggered=True  # 觸發警報，阻擋輸入
            )
    
    # 通過檢查
    return GuardrailFunctionOutput(
        output_info="通過不當言論檢查",
        tripwire_triggered=False
    )


@input_guardrail
async def sensitive_info_guardrail(
    ctx: RunContextWrapper[None],
    agent: Agent,
    input: str | list[TResponseInputItem]
) -> GuardrailFunctionOutput:
    """輸入防護：防止使用者輸入敏感個資"""
    
    input_text = input if isinstance(input, str) else str(input)
    
    # 檢查是否包含信用卡號
    credit_card_pattern = r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b'
    if re.search(credit_card_pattern, input_text):
        return GuardrailFunctionOutput(
            output_info="偵測到信用卡號",
            tripwire_triggered=True
        )
    
    # 檢查是否包含身份證號（台灣格式）
    id_pattern = r'\b[A-Z][12]\d{8}\b'
    if re.search(id_pattern, input_text):
        return GuardrailFunctionOutput(
            output_info="偵測到身份證號",
            tripwire_triggered=True
        )
    
    return GuardrailFunctionOutput(
        output_info="通過敏感資訊檢查",
        tripwire_triggered=False
    )


@input_guardrail
async def topic_restriction_guardrail(
    ctx: RunContextWrapper[None],
    agent: Agent,
    input: str | list[TResponseInputItem]
) -> GuardrailFunctionOutput:
    """輸入防護：限制討論主題（只能討論技術問題）"""
    
    input_text = input if isinstance(input, str) else str(input)
    input_lower = input_text.lower()
    
    # 檢查是否包含任何允許的主題關鍵字
    has_allowed_topic = any(topic in input_lower for topic in ALLOWED_TOPICS)
    
    if not has_allowed_topic and len(input_text) > 20:
        return GuardrailFunctionOutput(
            output_info="不在允許的主題範圍內",
            tripwire_triggered=True
        )
    
    return GuardrailFunctionOutput(
        output_info="通過主題限制檢查",
        tripwire_triggered=False
    )


@output_guardrail
async def privacy_guardrail(
    ctx: RunContextWrapper,
    agent: Agent,
    output: str
) -> GuardrailFunctionOutput:
    """輸出防護：防止 AI 洩漏敏感資訊（自動遮罩）"""
    
    # 檢查是否包含電子郵件
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if re.search(email_pattern, output):
        # 注意：這裡只是檢測，實際遮罩需要在 agent 層級處理
        # 或者使用其他機制，因為 output guardrail 主要用於阻擋，不是修改
        return GuardrailFunctionOutput(
            output_info="偵測到 email",
            tripwire_triggered=True  # 阻擋包含 email 的輸出
        )
    
    # 檢查是否包含電話號碼
    phone_pattern = r'\b0\d{1,3}[-\s]?\d{3,4}[-\s]?\d{4}\b'
    if re.search(phone_pattern, output):
        return GuardrailFunctionOutput(
            output_info="偵測到電話號碼",
            tripwire_triggered=True
        )
    
    return GuardrailFunctionOutput(
        output_info="通過隱私檢查",
        tripwire_triggered=False
    )


@output_guardrail
async def response_quality_guardrail(
    ctx: RunContextWrapper,
    agent: Agent,
    output: str
) -> GuardrailFunctionOutput:
    """輸出防護：確保回應品質"""
    
    # 檢查回應長度
    if len(output.strip()) < 10:
        return GuardrailFunctionOutput(
            output_info="回應太短",
            tripwire_triggered=True
        )
    
    # 檢查是否包含常見的錯誤訊息
    error_phrases = ["我不知道", "我無法", "我沒有資訊", "無法回答"]
    if any(phrase in output for phrase in error_phrases):
        return GuardrailFunctionOutput(
            output_info="無法提供有效回答",
            tripwire_triggered=True
        )
    
    return GuardrailFunctionOutput(
        output_info="通過品質檢查",
        tripwire_triggered=False
    )


@output_guardrail
async def toxic_content_guardrail(
    ctx: RunContextWrapper,
    agent: Agent,
    output: str
) -> GuardrailFunctionOutput:
    """輸出防護：防止 AI 產生有害內容"""
    
    output_lower = output.lower()
    
    for pattern in TOXIC_PATTERNS:
        if pattern in output_lower:
            return GuardrailFunctionOutput(
                output_info=f"偵測到有害內容: {pattern}",
                tripwire_triggered=True
            )
    
    return GuardrailFunctionOutput(
        output_info="通過有害內容檢查",
        tripwire_triggered=False
    )


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


async def example_1_without_guardrails():
    """範例 1: 沒有 Guardrails 的 Agent（不安全）"""
    print("\n" + "="*70)
    print("範例 1: 沒有 Guardrails 的 Agent")
    print("="*70)
    print("這個 Agent 沒有任何防護機制，可能會產生問題...\n")
    
    client = await create_client()
    model = OpenAIChatCompletionsModel(model=MODEL_NAME, openai_client=client)
    
    agent = Agent(
        name="UnprotectedAssistant",
        instructions="你是一個助手，回答使用者的問題。",
        model=model,
    )
    
    # 測試各種輸入
    test_inputs = [
        "請告訴我 Python 的基本語法",
        "我的信用卡號是 1234-5678-9012-3456，幫我查詢餘額",
    ]
    
    for i, user_input in enumerate(test_inputs, 1):
        print(f"測試 {i}: {user_input}")
        result = await Runner.run(agent, user_input)
        print(f"回應: {result.final_output[:100]}...")
        print("-" * 70)


async def example_2_input_guardrails():
    """範例 2: 使用 Input Guardrails（輸入防護）"""
    print("\n" + "="*70)
    print("範例 2: 使用 Input Guardrails")
    print("="*70)
    print("這個 Agent 有輸入防護機制，會過濾不當輸入...\n")
    
    client = await create_client()
    model = OpenAIChatCompletionsModel(model=MODEL_NAME, openai_client=client)
    
    # 建立帶有輸入防護的 Agent
    agent = Agent(
        name="ProtectedAssistant",
        instructions="你是一個技術助手，專門回答程式設計相關問題。",
        model=model,
        input_guardrails=[
            sensitive_info_guardrail,
            topic_restriction_guardrail,
        ]
    )
    
    # 測試各種輸入
    test_inputs = [
        "請教我 Python 的迴圈怎麼寫？",
        "我的身份證是 A123456789，幫我查詢資料",
        "今天天氣如何？",
    ]
    
    for i, user_input in enumerate(test_inputs, 1):
        print(f"\n測試 {i}: {user_input}")
        try:
            result = await Runner.run(agent, user_input)
            print(f"✅ 通過檢查")
            print(f"回應: {result.final_output[:150]}...")
        except InputGuardrailTripwireTriggered as e:
            print(f"❌ 被 Input Guardrail 阻擋: {str(e)}")
        except Exception as e:
            print(f"❌ 錯誤: {str(e)}")
        print("-" * 70)


async def example_3_output_guardrails():
    """範例 3: 使用 Output Guardrails（輸出防護）"""
    print("\n" + "="*70)
    print("範例 3: 使用 Output Guardrails")
    print("="*70)
    print("這個 Agent 有輸出防護機制，會檢查和修改輸出內容...\n")
    
    client = await create_client()
    model = OpenAIChatCompletionsModel(model=MODEL_NAME, openai_client=client)
    
    agent = Agent(
        name="SafeAssistant",
        instructions="""你是一個助手。
        注意：為了測試 Guardrails，有時候請在回答中包含範例電子郵件或電話號碼。""",
        model=model,
        output_guardrails=[
            privacy_guardrail,
            response_quality_guardrail,
            toxic_content_guardrail,
        ]
    )
    
    # 測試輸入
    test_inputs = [
        "如何聯繫 Python 官方支援？請提供聯絡方式。",
        "Python 是什麼？",  # 測試回應品質
    ]
    
    for i, user_input in enumerate(test_inputs, 1):
        print(f"\n測試 {i}: {user_input}")
        try:
            result = await Runner.run(agent, user_input)
            print(f"✅ 輸出通過檢查")
            print(f"回應: {result.final_output[:200]}...")
        except OutputGuardrailTripwireTriggered as e:
            print(f"❌ 輸出被 Output Guardrail 阻擋: {str(e)}")
        except Exception as e:
            print(f"❌ 錯誤: {str(e)}")
        print("-" * 70)


async def example_4_combined_guardrails():
    """範例 4: 同時使用輸入和輸出防護"""
    print("\n" + "="*70)
    print("範例 4: 完整的 Guardrails 保護")
    print("="*70)
    print("這個 Agent 同時有輸入和輸出防護，提供完整保護...\n")
    
    client = await create_client()
    model = OpenAIChatCompletionsModel(model=MODEL_NAME, openai_client=client)
    
    agent = Agent(
        name="FullyProtectedAssistant",
        instructions="""你是一個專業的程式設計助手。
        - 只回答技術相關問題
        - 提供清楚、有幫助的回答
        - 不洩漏任何敏感資訊""",
        model=model,
        input_guardrails=[
            profanity_guardrail,
            sensitive_info_guardrail,
            topic_restriction_guardrail,
        ],
        output_guardrails=[
            privacy_guardrail,
            response_quality_guardrail,
            toxic_content_guardrail,
        ]
    )
    
    # 測試輸入
    test_inputs = [
        "Python 的 list 和 tuple 有什麼差別？",
        "如何在 Python 中處理例外？",
        "我的密碼是 123456，幫我存檔",
        "推薦一部電影給我",
    ]
    
    for i, user_input in enumerate(test_inputs, 1):
        print(f"\n測試 {i}: {user_input}")
        try:
            result = await Runner.run(agent, user_input)
            print(f"✅ 成功處理")
            print(f"回應: {result.final_output[:200]}...")
        except (InputGuardrailTripwireTriggered, OutputGuardrailTripwireTriggered) as e:
            print(f"❌ 被 Guardrail 阻擋: {str(e)}")
        except Exception as e:
            print(f"❌ 錯誤: {str(e)}")
        print("-" * 70)


async def example_5_custom_guardrail():
    """範例 5: 自訂 Guardrail（時間限制）"""
    print("\n" + "="*70)
    print("範例 5: 自訂 Guardrail - 營業時間限制")
    print("="*70)
    print("這個範例展示如何建立自訂的 Guardrail...\n")
    
    from datetime import datetime
    
    @input_guardrail
    async def business_hours_guardrail(
        ctx: RunContextWrapper[None],
        agent: Agent,
        input: str | list[TResponseInputItem]
    ) -> GuardrailFunctionOutput:
        """自訂防護：限制只能在營業時間使用"""
        current_hour = datetime.now().hour
        
        # 營業時間：9:00 - 18:00
        if 9 <= current_hour < 18:
            return GuardrailFunctionOutput(
                output_info=f"在營業時間內 ({current_hour}:00)",
                tripwire_triggered=False
            )
        else:
            return GuardrailFunctionOutput(
                output_info=f"非營業時間 ({current_hour}:00)，營業時間：9:00-18:00",
                tripwire_triggered=True
            )
    
    client = await create_client()
    model = OpenAIChatCompletionsModel(model=MODEL_NAME, openai_client=client)
    
    agent = Agent(
        name="BusinessAssistant",
        instructions="你是客服助手，協助客戶解決問題。",
        model=model,
        input_guardrails=[business_hours_guardrail]
    )
    
    print(f"目前時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n測試: 我需要技術支援")
    
    try:
        result = await Runner.run(agent, "我需要技術支援")
        print(f"✅ 在營業時間內，可以服務")
        print(f"回應: {result.final_output[:150]}...")
    except InputGuardrailTripwireTriggered as e:
        print(f"❌ 被 Guardrail 阻擋: {str(e)}")
    except Exception as e:
        print(f"❌ 錯誤: {str(e)}")
    
    print("-" * 70)


async def main():
    """主程式 - 執行所有範例"""
    print("\n" + "="*70)
    print("🛡️  Guardrails 教學 - OpenAI Agent SDK")
    print("="*70)
    print("Guardrails 是保護 AI Agent 的安全機制，就像護欄一樣")
    print("防止 AI 做出不當行為或洩漏敏感資訊")
    print("="*70)
    
    # 關閉追蹤以提高效能
    set_tracing_disabled(disabled=True)
    
    try:
        # 執行範例（可以選擇要執行哪些）
        # await example_1_without_guardrails()
        # await example_2_input_guardrails()
        # await example_3_output_guardrails()
        # await example_4_combined_guardrails()
        await example_5_custom_guardrail()
        
        print("\n" + "="*70)
        print("✅ 所有範例執行完成！")
        print("="*70)
        print("\n💡 重點回顧：")
        print("1. Input Guardrails：在 AI 處理前檢查使用者輸入")
        print("2. Output Guardrails：在回應使用者前檢查 AI 輸出")
        print("3. 使用 @input_guardrail 和 @output_guardrail decorator")
        print("4. Guardrails 回傳 GuardrailFunctionOutput")
        print("5. tripwire_triggered=True 會觸發例外並阻擋執行")
        print("6. 可以自訂 Guardrails 滿足特定需求")
        print("7. 多個 Guardrails 可以組合使用")
        print("8. Guardrails 讓 AI 應用更安全、更可靠")
        
    except Exception as e:
        print(f"\n❌ 錯誤: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
