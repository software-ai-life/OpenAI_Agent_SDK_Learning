# 🎭 Multi-Agent Orchestration 教學

## 📖 什麼是 Multi-Agent Orchestration？

**Orchestration（協調/編排）** 是指如何讓多個 AI Agent 一起工作來完成複雜任務。

想像一個公司：
- 🏢 **單一 Agent** = 一個人做所有事情（累死了！）
- 🎭 **Multi-Agent** = 專業分工，各司其職（有效率！）

**為什麼需要多個 Agents？**

| 單一 Agent ❌ | Multi-Agent ✅ |
|--------------|----------------|
| 要懂所有領域 | 每個專精一領域 |
| 指令複雜冗長 | 每個指令簡潔 |
| 難以除錯 | 容易找出問題點 |
| 效能瓶頸 | 可以並行處理 |

---

## 🎯 兩種協調方式

### 方式 1: 透過 LLM 協調 🤖

**特點：** 讓 AI 自己決定流程

```
使用者問題 → LLM 判斷 → 選擇合適的 Agent → 執行 → 可能再轉給其他 Agent
```

**優點：**
- ✅ 彈性高，能處理複雜情境
- ✅ 不需要預先定義所有流程
- ✅ LLM 可以根據情況動態調整

**缺點：**
- ❌ 不夠可預測（每次可能不同）
- ❌ 成本較高（多次 LLM 呼叫）
- ❌ 較慢（需要推理和決策）

**適合場景：**
- 問題類型多樣化（客服系統）
- 需要複雜推理和判斷
- 流程不固定

### 方式 2: 透過程式碼協調 💻

**特點：** 你的程式碼控制流程

```
使用者問題 → 你的程式邏輯判斷 → 呼叫指定的 Agent → 執行 → 按照既定流程
```

**優點：**
- ✅ 可預測（每次都一樣）
- ✅ 成本較低
- ✅ 較快
- ✅ 容易測試和除錯

**缺點：**
- ❌ 需要預先設計流程
- ❌ 彈性較低
- ❌ 處理例外情況較困難

**適合場景：**
- 流程固定（內容產生流水線）
- 需要精確控制
- 效能和成本敏感

---

## 🚀 快速開始

### 步驟 1: 安裝套件

```bash
pip install openai-agents python-dotenv httpx openai pydantic
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

## 📚 範例說明

### 範例 1: 透過 LLM 協調 - 客服系統 🎧

**場景：** 客服系統有多個專業客服

```python
from agents import Agent

# 定義專業 Agents
billing_agent = Agent(
    name="BillingAgent",
    instructions="你是帳單專家...",
    model=model,
)

technical_agent = Agent(
    name="TechnicalAgent",
    instructions="你是技術支援專家...",
    model=model,
)

# Triage Agent 負責分流
triage_agent = Agent(
    name="TriageAgent",
    instructions="你負責了解問題並轉給適當的專家...",
    model=model,
    handoffs=[billing_agent, technical_agent],  # 可以轉給這些 Agents
)

# 執行
result = await Runner.run(triage_agent, "我的帳單為什麼這麼高？")
```

**運作流程：**
```
使用者: "我的帳單為什麼這麼高？"
    ↓
TriageAgent 判斷: 這是帳單問題
    ↓
Handoff → BillingAgent 處理
    ↓
回覆: "讓我查看您的帳單明細..."
```

**重點：**
- 使用 `handoffs` 參數設定可以轉給誰
- LLM 會自動判斷何時轉移
- 不需要寫 if-else 判斷邏輯

---

### 範例 2: 透過程式碼協調 - 任務分類 🏷️

**場景：** 根據任務類型選擇專家

```python
from pydantic import BaseModel, Field
from typing import Literal

# 定義分類結構
class TaskCategory(BaseModel):
    category: Literal["research", "writing", "coding", "analysis"]
    confidence: float
    reason: str

# 分類器
classifier_agent = Agent(
    name="ClassifierAgent",
    instructions="判斷任務類型...",
    model=model,
    output_schema=TaskCategory,  # 輸出結構化資料
)

# 專家們
research_agent = Agent(name="ResearchAgent", ...)
writing_agent = Agent(name="WritingAgent", ...)

# 你的程式碼控制流程
task = "幫我研究 AI 的最新發展"

# 步驟 1: 分類
result = await Runner.run(classifier_agent, task)
category = result.final_output_as(TaskCategory)

# 步驟 2: 根據分類選擇專家
experts = {
    "research": research_agent,
    "writing": writing_agent,
}
expert = experts[category.category]

# 步驟 3: 執行
final_result = await Runner.run(expert, task)
```

**運作流程：**
```
任務: "幫我研究 AI 的最新發展"
    ↓
ClassifierAgent → 輸出: TaskCategory(category="research", ...)
    ↓
你的程式碼: 選擇 research_agent
    ↓
ResearchAgent 執行 → 回覆研究結果
```

**重點：**
- 使用 `output_schema` 取得結構化輸出
- 用 Python 程式碼控制流程
- 可預測且容易測試

---

### 範例 3: 順序執行（Chaining）⛓️

**場景：** 產生部落格文章的完整流程

```
研究 → 建立大綱 → 撰寫 → 評論 → 修改
```

```python
# 定義每個步驟的 Agent
researcher = Agent(name="Researcher", instructions="收集資訊", ...)
outliner = Agent(name="Outliner", instructions="建立大綱", ...)
writer = Agent(name="Writer", instructions="撰寫文章", ...)
critic = Agent(name="Critic", instructions="評論品質", ...)
editor = Agent(name="Editor", instructions="修改文章", ...)

# 順序執行
topic = "AI 如何改變教育"

# 步驟 1
research_result = await Runner.run(researcher, f"研究：{topic}")
research = research_result.final_output

# 步驟 2（使用前一步的結果）
outline_result = await Runner.run(outliner, f"根據研究建立大綱：\n{research}")
outline = outline_result.final_output

# 步驟 3
article_result = await Runner.run(writer, f"根據大綱撰寫：\n{outline}")
article = article_result.final_output

# 步驟 4
critique_result = await Runner.run(critic, f"評論文章：\n{article}")
critique = critique_result.final_output

# 步驟 5（條件執行）
if critique.score < 8:
    final_result = await Runner.run(editor, f"修改：\n{article}\n建議：\n{critique}")
else:
    final_result = article
```

**重點：**
- 每個 Agent 專注一件事
- 前一步的輸出是下一步的輸入
- 可以加入條件判斷（if-else）

---

### 範例 4: 並行執行（Parallel）⚡

**場景：** 同時從多個角度分析

```python
import asyncio

# 定義不同角度的分析師
market_analyst = Agent(name="MarketAnalyst", instructions="市場分析", ...)
tech_analyst = Agent(name="TechAnalyst", instructions="技術分析", ...)
user_analyst = Agent(name="UserAnalyst", instructions="使用者分析", ...)
risk_analyst = Agent(name="RiskAnalyst", instructions="風險分析", ...)

# 同時執行（使用 asyncio.gather）
topic = "公司應該投資開發 AI 聊天機器人嗎？"

results = await asyncio.gather(
    Runner.run(market_analyst, f"市場角度分析：{topic}"),
    Runner.run(tech_analyst, f"技術角度分析：{topic}"),
    Runner.run(user_analyst, f"使用者角度分析：{topic}"),
    Runner.run(risk_analyst, f"風險角度分析：{topic}"),
)

# 整理所有結果
for result in results:
    print(result.final_output)
```

**時間比較：**
- 順序執行：4 個 Agent × 10 秒 = 40 秒 ⏰
- 並行執行：max(10, 10, 10, 10) = 10 秒 ⚡

**重點：**
- 使用 `asyncio.gather` 同時執行
- 適合獨立的任務（不互相依賴）
- 大幅節省時間

---

### 範例 5: 迴圈執行與評估 🔄

**場景：** 持續改進直到達標

```python
# 產生器和評估者
code_generator = Agent(name="CodeGenerator", instructions="寫程式碼", ...)
code_reviewer = Agent(name="CodeReviewer", instructions="評估程式碼", ...)

# 迴圈執行
task = "寫一個 Python 函式讀取 JSON 檔案"
max_iterations = 3
current_code = None

for iteration in range(1, max_iterations + 1):
    print(f"第 {iteration} 次迭代")
    
    # 產生或改進程式碼
    if current_code is None:
        prompt = task
    else:
        prompt = f"改進程式碼：\n{current_code}\n建議：\n{feedback}"
    
    code_result = await Runner.run(code_generator, prompt)
    current_code = code_result.final_output
    
    # 評估品質
    review_result = await Runner.run(code_reviewer, f"評估：\n{current_code}")
    quality = review_result.final_output_as(CodeQuality)
    
    # 檢查是否達標
    if quality.is_acceptable:
        print(f"✅ 達標！")
        break
    else:
        feedback = quality.suggestions
        print(f"繼續改進...")
```

**運作流程：**
```
第 1 次: 產生程式碼 → 評估（6/10）→ 不達標，繼續
第 2 次: 根據建議改進 → 評估（7/10）→ 不達標，繼續
第 3 次: 再次改進 → 評估（9/10）→ ✅ 達標！
```

**重點：**
- 使用 `while` 或 `for` 迴圈
- 讓 Agent 自我改進
- 設定最大迭代次數避免無限循環

---

## 🎓 常見問題 Q&A

### Q1: 何時該用 LLM 協調？何時該用程式碼協調？

**A:** 根據需求選擇：

| 情況 | 建議方式 | 原因 |
|------|---------|------|
| 客服系統（問題多樣） | LLM 協調 | 需要彈性判斷 |
| 內容產生流水線 | 程式碼協調 | 流程固定 |
| 成本/效能敏感 | 程式碼協調 | 較便宜快速 |
| 需要複雜推理 | LLM 協調 | LLM 擅長推理 |
| 需要精確控制 | 程式碼協調 | 可預測性高 |

**混合使用也可以！**
```python
# 用程式碼控制主流程
task_type = classify_task(user_input)  # 程式碼分類

if task_type == "complex":
    # 複雜任務用 LLM 協調
    result = await Runner.run(smart_agent_with_handoffs, user_input)
else:
    # 簡單任務用固定流程
    result = await simple_workflow(user_input)
```

### Q2: Handoffs 和程式碼呼叫 Agent 有什麼不同？

**A:** 主要差異：

| 比較項目 | Handoffs | 程式碼呼叫 |
|---------|----------|-----------|
| **誰決定** | LLM 自己判斷 | 你的程式碼決定 |
| **何時轉移** | LLM 認為需要時 | 你指定的時候 |
| **可預測性** | 低 | 高 |
| **彈性** | 高 | 低 |

**Handoffs 範例：**
```python
agent = Agent(
    name="MainAgent",
    handoffs=[expert1, expert2],  # LLM 自己決定要不要轉
)
```

**程式碼呼叫範例：**
```python
result1 = await Runner.run(agent1, task)
result2 = await Runner.run(agent2, result1.output)  # 你決定何時呼叫
```

### Q3: 如何追蹤 Multi-Agent 的執行流程？

**A:** 幾種方法：

**方法 1: 檢查 Handoff 歷史**
```python
result = await Runner.run(triage_agent, query)

# 查看轉移路徑
if hasattr(result, 'handoff_history'):
    path = ' → '.join([h.agent_name for h in result.handoff_history])
    print(f"執行路徑: {path}")
```

**方法 2: 加入日誌**
```python
import logging

logging.basicConfig(level=logging.INFO)

# 在每個步驟記錄
logger.info(f"執行 Agent: {agent.name}")
result = await Runner.run(agent, task)
logger.info(f"結果: {result.final_output[:100]}")
```

**方法 3: 使用 Tracing**
```python
from agents import set_tracing_disabled

# 啟用追蹤
set_tracing_disabled(False)

# 執行後可以在追蹤系統看到完整流程
```

### Q4: Multi-Agent 的成本會不會很高？

**A:** 要看協調方式：

**LLM 協調成本：**
- 每次 Handoff 判斷都需要呼叫 LLM
- 如果轉移多次，成本會累積
- 適合：準確度優先的場景

**程式碼協調成本：**
- 只有實際執行的 Agent 才呼叫 LLM
- 流程確定，成本可預測
- 適合：成本敏感的場景

**降低成本技巧：**
```python
# 1. 使用較便宜的模型做分類
classifier = Agent(
    model=cheap_model,  # 用便宜的模型
    output_schema=TaskCategory,
)

# 2. 只在需要時才用強大的模型
if task_is_complex:
    expert = Agent(model=expensive_powerful_model)
else:
    expert = Agent(model=cheap_model)

# 3. 並行執行節省時間（但不會省錢）
await asyncio.gather(agent1.run(), agent2.run())  # 快但費用相同
```

### Q5: 如何處理 Agent 之間的資料傳遞？

**A:** 幾種模式：

**模式 1: 直接傳遞輸出**
```python
# 簡單文字傳遞
result1 = await Runner.run(agent1, task)
result2 = await Runner.run(agent2, result1.final_output)
```

**模式 2: 使用結構化資料**
```python
# 使用 Pydantic 模型確保資料格式
class ResearchData(BaseModel):
    findings: List[str]
    sources: List[str]

researcher = Agent(output_schema=ResearchData, ...)
result = await Runner.run(researcher, task)
data = result.final_output_as(ResearchData)

# 傳給下一個 Agent
writer = Agent(...)
article = await Runner.run(writer, f"根據研究撰寫：\n{data.findings}")
```

**模式 3: 使用共享 Context**
```python
# 建立共享的上下文物件
class SharedContext:
    def __init__(self):
        self.research_data = None
        self.outline = None
        self.article = None

context = SharedContext()

# 每個 Agent 更新 context
result = await Runner.run(researcher, task)
context.research_data = result.final_output

result = await Runner.run(outliner, context.research_data)
context.outline = result.final_output

# 其他 Agents 可以存取所有資料
```

### Q6: Multi-Agent 系統如何除錯？

**A:** 除錯技巧：

**技巧 1: 逐步測試**
```python
# 先單獨測試每個 Agent
async def test_individual_agents():
    result = await Runner.run(agent1, test_input)
    print(f"Agent1 輸出: {result.final_output}")
    
    result = await Runner.run(agent2, test_input)
    print(f"Agent2 輸出: {result.final_output}")

# 再測試整個流程
async def test_full_pipeline():
    # ...完整流程
```

**技巧 2: 加入檢查點**
```python
async def pipeline_with_checkpoints():
    # 檢查點 1
    result1 = await Runner.run(agent1, task)
    print(f"[檢查點 1] {result1.final_output}")
    assert len(result1.final_output) > 0, "Agent1 沒有輸出"
    
    # 檢查點 2
    result2 = await Runner.run(agent2, result1.final_output)
    print(f"[檢查點 2] {result2.final_output}")
    
    return result2
```

**技巧 3: 視覺化流程**
```python
# 記錄執行流程
execution_log = []

async def tracked_run(agent, input):
    start = time.time()
    result = await Runner.run(agent, input)
    duration = time.time() - start
    
    execution_log.append({
        'agent': agent.name,
        'duration': duration,
        'output_length': len(result.final_output)
    })
    
    return result

# 執行後檢視
for log in execution_log:
    print(f"{log['agent']}: {log['duration']:.2f}s, {log['output_length']} chars")
```

---

## 💡 最佳實踐

### ✅ DO（應該做的）

**1. 每個 Agent 專注單一任務**
```python
# ✅ 好：職責明確
researcher = Agent(name="Researcher", instructions="只負責研究和收集資訊")
writer = Agent(name="Writer", instructions="只負責撰寫文章")

# ❌ 不好：一個 Agent 做太多事
super_agent = Agent(instructions="研究、撰寫、評論、修改...")
```

**2. 使用清晰的 Agent 命名**
```python
# ✅ 好：一看就懂
billing_expert = Agent(name="BillingExpert", ...)
technical_support = Agent(name="TechnicalSupport", ...)

# ❌ 不好：名稱不清楚
agent1 = Agent(name="Agent1", ...)
helper = Agent(name="Helper", ...)
```

**3. 使用結構化輸出確保資料品質**
```python
# ✅ 好：資料格式確定
class Analysis(BaseModel):
    score: int
    issues: List[str]
    suggestions: str

agent = Agent(output_schema=Analysis, ...)

# ❌ 不好：自由文字，難以處理
agent = Agent(instructions="回答分數、問題和建議...")
```

**4. 設定合理的重試和超時**
```python
# ✅ 好：有容錯機制
max_retries = 3
for attempt in range(max_retries):
    try:
        result = await Runner.run(agent, task)
        break
    except Exception as e:
        if attempt == max_retries - 1:
            raise
        await asyncio.sleep(1)

# ❌ 不好：沒有錯誤處理
result = await Runner.run(agent, task)  # 失敗就掛了
```

### ❌ DON'T（不應該做的）

**1. 不要讓 Agent 互相依賴太深**
```python
# ❌ 不好：A 依賴 B，B 依賴 C，C 依賴 A（循環依賴）
agent_a = Agent(handoffs=[agent_b])
agent_b = Agent(handoffs=[agent_c])
agent_c = Agent(handoffs=[agent_a])  # 危險！
```

**2. 不要無限制的 Handoffs**
```python
# ❌ 不好：可能無限轉移
agent = Agent(
    handoffs=[agent1, agent2, agent3, ...],  # 太多選擇
    instructions="隨時可以轉給任何專家"  # 沒有明確規則
)

# ✅ 好：有明確的轉移規則
agent = Agent(
    handoffs=[billing_agent, tech_agent],
    instructions="""
    只在遇到以下情況轉移：
    - 帳單問題 → BillingAgent
    - 技術問題 → TechAgent
    否則自己處理
    """
)
```

**3. 不要忽略錯誤處理**
```python
# ❌ 不好：任何錯誤都會中斷整個流程
result1 = await Runner.run(agent1, task)
result2 = await Runner.run(agent2, result1.output)
result3 = await Runner.run(agent3, result2.output)

# ✅ 好：有降級方案
try:
    result = await Runner.run(agent1, task)
except Exception as e:
    logger.error(f"Agent1 失敗: {e}")
    result = await Runner.run(fallback_agent, task)
```

---

## 🎯 實戰練習建議

### 初學者練習（1-2 天）

**練習 1: 簡單的客服系統**
- 建立 3 個專業 Agent（帳單、技術、一般）
- 使用 Handoffs 實現自動轉接
- 測試不同類型的問題

**練習 2: 兩階段流程**
- Agent 1：分析使用者需求
- Agent 2：根據需求產生回應
- 使用結構化輸出傳遞資料

### 進階練習（3-5 天）

**練習 3: 內容產生流水線**
- 實作 4-5 個步驟的順序流程
- 每個步驟有明確的輸入輸出
- 加入品質檢查和重試機制

**練習 4: 並行資料處理**
- 同時處理多個獨立任務
- 整合所有結果
- 比較順序執行和並行執行的時間差異

### 專家練習（5+ 天）

**練習 5: 混合協調系統**
- 結合 LLM 協調和程式碼協調
- 實作複雜的決策流程
- 加入監控和日誌系統

**練習 6: 自我改進系統**
- 實作評估 + 改進循環
- 設定品質門檻
- 追蹤改進歷程

---

## 📊 效能考量

### 順序 vs 並行

**順序執行：**
```python
# 總時間 = 所有 Agent 時間總和
start = time.time()
r1 = await Runner.run(agent1, task)  # 10 秒
r2 = await Runner.run(agent2, r1.output)  # 10 秒
r3 = await Runner.run(agent3, r2.output)  # 10 秒
total = time.time() - start  # ~30 秒
```

**並行執行：**
```python
# 總時間 = 最慢的 Agent 時間
start = time.time()
results = await asyncio.gather(
    Runner.run(agent1, task),  # 10 秒
    Runner.run(agent2, task),  # 15 秒
    Runner.run(agent3, task),  # 8 秒
)
total = time.time() - start  # ~15 秒（最慢的）
```

### 成本優化

| 策略 | 說明 | 節省 |
|------|------|------|
| **快取結果** | 相同問題不重複呼叫 | ~50% |
| **用便宜模型分類** | 簡單任務用小模型 | ~30% |
| **批次處理** | 一次處理多個任務 | ~20% |
| **提早終止** | 達標就停止迭代 | ~40% |

---

## 💬 總結

**Multi-Agent Orchestration 的核心概念：**

1. **分工合作** - 每個 Agent 專精一件事
2. **兩種協調**：
   - 🤖 LLM 協調：彈性但成本高
   - 💻 程式碼協調：快速且可控
3. **四種模式**：
   - ⛓️ 順序執行（Chaining）
   - ⚡ 並行執行（Parallel）
   - 🔄 迴圈改進（Loop）
   - 🎭 動態轉移（Handoffs）

**選擇建議：**

| 你的需求 | 推薦方式 |
|---------|---------|
| 問題多樣化、需要判斷 | LLM 協調 + Handoffs |
| 固定流程、可預測 | 程式碼協調 + Chaining |
| 追求速度 | 並行執行 |
| 追求品質 | 迴圈改進 |
| 成本敏感 | 程式碼協調 |

**記住：不要過度設計！從簡單開始，根據需求逐步增加複雜度。** 🚀

---

## 🔗 延伸閱讀

- [OpenAI Agents SDK - Multi-Agent 官方文件](https://openai.github.io/openai-agents-python/multi_agent/)
- [OpenAI Agents SDK - Handoffs 詳細說明](https://openai.github.io/openai-agents-python/handoffs/)
- [Structured Outputs 教學](../1.7_structured_output/)
- [Guardrails 教學](../1.8_guardrails/)

---

**現在就開始建立你的 Multi-Agent 系統，讓多個 AI 一起為你工作！** 🎭✨
