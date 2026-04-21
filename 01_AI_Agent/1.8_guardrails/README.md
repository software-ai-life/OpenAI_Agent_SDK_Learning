# Guardrails 教學

## 🛡️ 什麼是 Guardrails（護欄機制）？

想像一下，你在高速公路上開車，道路兩旁有**護欄**保護你的安全，防止車子偏離道路。

在 AI 應用中，**Guardrails** 就是類似的安全機制，用來：
- 🚫 阻止不當的使用者輸入
- 🔒 防止 AI 洩漏敏感資訊
- ✅ 確保 AI 的回應符合品質標準
- 🛡️ 保護系統和使用者的安全

---

## 🎯 為什麼需要 Guardrails？

### ❌ 沒有 Guardrails 的風險

**情境 1：敏感資訊洩漏**
```
使用者：「我的信用卡號是 1234-5678-9012-3456，幫我查詢餘額」
AI：「好的，您的信用卡號是 1234-5678-9012-3456...」
```
💥 **問題：** AI 直接重複了信用卡號，可能被記錄或洩漏！

**情境 2：不當內容**
```
使用者：輸入髒話或攻擊性言論
AI：可能產生不適當的回應
```
💥 **問題：** AI 可能被誘導產生有害內容！

**情境 3：超出範圍的問題**
```
使用者：「明天股票會漲還是跌？」（對技術助手詢問）
AI：開始回答投資建議
```
💥 **問題：** AI 回答了不該回答的問題，可能誤導使用者！

### ✅ 有 Guardrails 的保護

**情境 1：敏感資訊防護**
```
使用者：「我的信用卡號是 1234-5678-9012-3456」
Guardrail：⚠️ 阻擋！請不要輸入信用卡號碼等敏感資訊！
```
✨ **保護：** 在資料進入 AI 前就被攔截！

**情境 2：內容過濾**
```
使用者：輸入不當言論
Guardrail：⚠️ 阻擋！您的輸入包含不適當的內容，請重新表達。
```
✨ **保護：** 不當內容被過濾，維護系統品質！

**情境 3：主題限制**
```
使用者：「明天股票會漲還是跌？」
Guardrail：⚠️ 阻擋！此助手僅回答技術相關問題。
```
✨ **保護：** AI 只在專業範圍內回答，避免誤導！

---

## 📚 Guardrails 的兩種類型

### 1️⃣ Input Guardrails（輸入防護）

**作用時機：** 在使用者輸入進入 AI 之前
**目的：** 過濾不當輸入、保護系統

```
使用者輸入 → [Input Guardrails 檢查] → AI 處理 → 輸出
              ↓ 如果不通過
              ❌ 直接拒絕，不給 AI 處理
```

**常見用途：**
- 🚫 過濾髒話和不當言論
- 🔒 防止敏感資訊輸入（信用卡、身份證）
- 📋 限制討論主題範圍
- ⏰ 限制使用時間（營業時間）
- 📏 限制輸入長度

### 2️⃣ Output Guardrails（輸出防護）

**作用時機：** 在 AI 回應傳給使用者之前
**目的：** 確保輸出安全、品質良好

```
使用者輸入 → AI 處理 → [Output Guardrails 檢查] → 輸出給使用者
                       ↓ 如果不通過
                       ❌ 阻擋或修改輸出
```

**常見用途：**
- 🔐 遮罩敏感資訊（email、電話）
- ✅ 確保回應品質（長度、完整性）
- 🚫 防止有害內容產生
- 📝 格式化輸出內容
- 🎯 確保回答準確性

---

## 🎯 學習重點

1. ✅ 理解 Input 和 Output Guardrails 的差異
2. ✅ 學會實作基本的內容過濾
3. ✅ 掌握敏感資訊保護機制
4. ✅ 建立自訂的 Guardrails
5. ✅ 組合多個 Guardrails 提供完整保護

---

## 📋 本教學包含的範例

### 範例 1: 沒有 Guardrails 的 Agent ❌
**展示問題：** 看看沒有防護的 AI 可能遇到什麼風險
- 可能處理敏感資訊
- 可能產生不當內容
- 缺乏品質控制

### 範例 2: Input Guardrails（輸入防護）🛡️
**保護機制：**
- ✅ 敏感資訊過濾（信用卡、身份證）
- ✅ 主題限制（只回答技術問題）
- ✅ 內容審查

### 範例 3: Output Guardrails（輸出防護）🔒
**保護機制：**
- ✅ 隱私保護（自動遮罩 email、電話）
- ✅ 品質控制（檢查回應長度和內容）
- ✅ 有害內容過濾

### 範例 4: 組合使用 Guardrails 💪
**完整保護：**
- ✅ 同時使用輸入和輸出防護
- ✅ 多層防護機制
- ✅ 建立安全可靠的 AI 系統

### 範例 5: 自訂 Guardrail ⚙️
**客製化：**
- ✅ 建立營業時間限制
- ✅ 學會撰寫自己的 Guardrail
- ✅ 滿足特定業務需求

---

## 🔧 如何實作 Guardrail？

### 核心概念

根據 OpenAI Agents SDK 官方文件，Guardrails 使用 **decorator（裝飾器）** 方式實作，而不是繼承類別。

**重要：**
- 使用 `@input_guardrail` 和 `@output_guardrail` decorators
- 回傳 `GuardrailFunctionOutput` 物件
- 使用 `tripwire_triggered` 控制是否阻擋（True=阻擋，False=通過）

### Input Guardrail 範例

```python
from agents import input_guardrail, GuardrailFunctionOutput, RunContextWrapper, TResponseInputItem
import re

@input_guardrail
async def sensitive_info_guardrail(
    ctx: RunContextWrapper[None],
    agent: Agent,
    input: str | list[TResponseInputItem]
) -> GuardrailFunctionOutput:
    """防止使用者輸入敏感資訊"""
    
    # 將輸入轉為字串
    input_text = input if isinstance(input, str) else str(input)
    
    # 檢查是否包含信用卡號
    if re.search(r'\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}', input_text):
        return GuardrailFunctionOutput(
            output_info="偵測到信用卡號",
            tripwire_triggered=True  # 阻擋輸入
        )
    
    # 通過檢查
    return GuardrailFunctionOutput(
        output_info="通過敏感資訊檢查",
        tripwire_triggered=False  # 允許通過
    )
```

**解釋：**
1. 使用 `@input_guardrail` decorator
2. 函式接收 `ctx`（上下文）、`agent`（Agent物件）、`input`（使用者輸入）
3. 回傳 `GuardrailFunctionOutput`：
   - `tripwire_triggered=True` → 觸發警報，阻擋執行
   - `tripwire_triggered=False` → 通過檢查
   - `output_info` → 提供檢查資訊（用於日誌）

### Output Guardrail 範例

```python
from agents import output_guardrail, GuardrailFunctionOutput, RunContextWrapper
import re

@output_guardrail
async def privacy_guardrail(
    ctx: RunContextWrapper,
    agent: Agent,
    output: str
) -> GuardrailFunctionOutput:
    """檢測輸出中的敏感資訊"""
    
    # 檢查是否包含 email
    if re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', output):
        return GuardrailFunctionOutput(
            output_info="偵測到 email",
            tripwire_triggered=True  # 阻擋包含 email 的輸出
        )
    
    # 通過檢查
    return GuardrailFunctionOutput(
        output_info="通過隱私檢查",
        tripwire_triggered=False
    )
```

**解釋：**
1. 使用 `@output_guardrail` decorator
2. 函式接收 `ctx`、`agent`、`output`（AI的輸出）
3. 同樣使用 `tripwire_triggered` 控制是否阻擋

**注意：** Output Guardrails 主要用於**檢測和阻擋**，不適合用來修改輸出內容。如需修改輸出，建議在 Agent 層級處理。

### 使用 Guardrails

```python
from agents import Agent, Runner, InputGuardrailTripwireTriggered, OutputGuardrailTripwireTriggered

# 建立 Agent，直接設定 guardrails
agent = Agent(
    name="ProtectedAssistant",
    instructions="你是一個安全的助手",
    model=model,
    input_guardrails=[
        sensitive_info_guardrail,  # 注意：傳入函式本身，不是實例
    ],
    output_guardrails=[
        privacy_guardrail,
    ]
)

# 執行（自動套用 Guardrails）
try:
    result = await Runner.run(agent, "使用者的問題")
    print(result.final_output)
except InputGuardrailTripwireTriggered as e:
    print(f"輸入被阻擋: {e}")
except OutputGuardrailTripwireTriggered as e:
    print(f"輸出被阻擋: {e}")
```

**重要差異：**
- ✅ Guardrails 直接設定在 `Agent` 上
- ✅ 傳入 guardrail 函式本身（不用實例化）
- ✅ 使用專屬的例外類別 `InputGuardrailTripwireTriggered` 和 `OutputGuardrailTripwireTriggered`

---

## 🚀 快速開始

### 步驟 1: 安裝套件

```bash
pip install openai-agents python-dotenv httpx openai
```

### 步驟 2: 設定 API 金鑰

建立 `.env` 檔案：

```env
GEMINI_API_KEY=你的API金鑰
```

### 步驟 3: 執行範例

```bash
python main.py
```

---

## 💡 實際應用場景

### 💼 企業內部 AI 助手

**需求：**
- 防止洩漏商業機密
- 限制存取時間
- 記錄使用日誌

**Guardrails 設計：**
```python
import logging
from datetime import datetime

@output_guardrail
async def confidentiality_guardrail(ctx, agent, output) -> GuardrailFunctionOutput:
    """防止機密資訊洩漏"""
    
    CONFIDENTIAL_KEYWORDS = ["機密", "內部", "未公開"]
    
    if any(word in output for word in CONFIDENTIAL_KEYWORDS):
        # 記錄警告並阻擋
        logging.warning(f"嘗試輸出機密資訊: {output[:50]}")
        return GuardrailFunctionOutput(
            tripwire_triggered=True,
            output_info="⚠️ 偵測到機密資訊，已阻擋輸出"
        )
    
    return GuardrailFunctionOutput(tripwire_triggered=False)

@input_guardrail
async def working_hours_guardrail(ctx, agent, input) -> GuardrailFunctionOutput:
    """限制工作時間使用"""
    
    hour = datetime.now().hour
    if not (9 <= hour < 18):  # 09:00 - 18:00
        return GuardrailFunctionOutput(
            tripwire_triggered=True,
            output_info="⚠️ 請在工作時間（09:00-18:00）使用"
        )
    
    return GuardrailFunctionOutput(tripwire_triggered=False)

# 使用方式
agent = Agent(
    name="EnterpriseBot",
    instructions="你是企業內部助手，協助員工處理日常工作。",
    model=model,
    input_guardrails=[working_hours_guardrail],
    output_guardrails=[confidentiality_guardrail]
)
```

---

## 💬 總結

**Guardrails 的核心價值：**

1. 🛡️ **安全第一** - 保護系統和使用者
2. 🔒 **隱私保護** - 防止敏感資訊洩漏
3. ✅ **品質保證** - 確保 AI 輸出符合標準
4. 🎯 **業務控制** - 讓 AI 在規範內運作
5. 📊 **風險管理** - 降低 AI 應用的風險

**記住：**
- Guardrails 就像汽車的安全帶和護欄
- Input Guardrails = 入口管制（檢查誰能進來）
- Output Guardrails = 出口管制（檢查什麼能出去）
- 多層防護 = 更安全的系統

**現在就開始為你的 AI Agent 加上 Guardrails，讓它更安全、更可靠！** 🚀

---

**相關資源：**
- 📖 查看 `main.py` 完整範例程式碼
- 🔗 [OpenAI Agents SDK 文件](https://github.com/openai/openai-agents-python)
- 🛡️ [AI 安全最佳實踐](https://www.example.com)
