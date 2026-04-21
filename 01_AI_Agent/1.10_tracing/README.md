# 🔍 Tracing 教學

## 📖 什麼是 Tracing？

**Tracing（追蹤）** 就像是給你的 AI Agent 安裝「行車記錄器」，記錄所有發生的事情。

想像你在開車：
- 🚗 **沒有記錄器**：出問題時不知道發生什麼事
- 📹 **有記錄器**：可以回放，看清楚每個細節

**Tracing 記錄什麼？**
- 🤖 Agent 執行過程
- 💬 LLM 的輸入和輸出
- 🔧 Tool 的呼叫
- 🛡️ Guardrails 的檢查
- 🔄 Agent 之間的 Handoffs
- ⏱️ 每個步驟的執行時間

---

## 🎯 核心概念

### Traces vs Spans

```
Trace（追蹤）= 完整的工作流程
│
├── Span（步驟）1: Agent 執行
│   ├── Span 1.1: LLM 生成
│   └── Span 1.2: Tool 呼叫
│
├── Span 2: 另一個 Agent 執行
│   └── Span 2.1: LLM 生成
│
└── Span 3: 最終處理
```

**Trace（追蹤）**
- 代表一個完整的端到端操作
- 例如：「客服對話」、「內容產生」、「資料分析」
- 包含多個 Spans
- 有唯一的 `trace_id`

**Span（步驟）**
- 代表一個有開始和結束時間的操作
- 例如：「Agent 執行」、「LLM 生成」、「Tool 呼叫」
- 有 `started_at` 和 `ended_at` 時間戳記
- 可以有父子關係（巢狀結構）

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

**注意：** Tracing 預設是**啟用**的！

---

## 📚 範例說明

### 範例 1: 預設追蹤（自動記錄）🎬

**SDK 會自動追蹤：**
- `Runner.run()` 整個執行
- Agent 的執行
- LLM 生成
- Tool 呼叫
- Guardrails 檢查
- Handoffs 轉移

```python
from agents import Agent, Runner

agent = Agent(
    name="SimpleAgent",
    instructions="你是助手",
    model=model,
)

# SDK 自動追蹤整個過程
result = await Runner.run(agent, "你好")
```

**自動記錄的內容：**
```
Trace: "Agent workflow"
├── Agent Span: SimpleAgent
│   └── Generation Span: LLM 生成
└── 執行時間: 2.5s
```

**重點：**
- ✅ 不需要任何設定，開箱即用
- ✅ 自動記錄所有重要操作
- ✅ 可以到 OpenAI Platform 查看

---

### 範例 2: 自訂 Trace 名稱 🏷️

**為什麼要自訂？**
- 給追蹤有意義的名稱
- 將多個操作組合在一起
- 加入 metadata 方便搜尋

```python
from agents import trace

# 方式 1: 單一操作
with trace(
    workflow_name="數學計算工作流",
    metadata={"user_id": "user123", "session": "session456"}
):
    result = await Runner.run(agent, "1 + 1")

# 方式 2: 多個操作在同一個 Trace
with trace(workflow_name="連續對話") as my_trace:
    print(f"Trace ID: {my_trace.trace_id}")
    
    # 第一個問題
    result1 = await Runner.run(agent, "你好")
    
    # 第二個問題（在同一個 Trace）
    result2 = await Runner.run(agent, "再見")
```

**運作方式：**
```
Trace: "連續對話"
├── Run 1: "你好"
│   └── Agent Span
│       └── Generation Span
├── Run 2: "再見"
│   └── Agent Span
│       └── Generation Span
└── Metadata: {"conversation_id": "..."}
```

**重點：**
- 使用 `with trace()` 作為 context manager
- 自動處理開始和結束
- 可以加入 metadata 方便過濾

---

### 範例 3: 自訂 Spans（追蹤你的程式碼）📊

**什麼時候需要？**
- 追蹤資料處理步驟
- 記錄 API 呼叫
- 監控檔案操作
- 任何你想記錄的操作

```python
from agents import custom_span

async def process_user_query(user_id: str, query: str):
    # 步驟 1: 取得使用者資料
    with custom_span(
        name="fetch_user_data",
        input={"user_id": user_id},
        metadata={"step": "data_fetching"}
    ) as span:
        user_data = await fetch_user_data(user_id)
        span.set_output(user_data)  # 記錄輸出
    
    # 步驟 2: 自訂提示詞
    with custom_span(name="customize_prompt") as span:
        prompt = customize_for_user(user_data, query)
        span.set_output({"prompt": prompt})
    
    # 步驟 3: 呼叫 Agent
    result = await Runner.run(agent, prompt)
    
    return result
```

**追蹤結構：**
```
Trace: "個人化查詢"
├── Custom Span: fetch_user_data
│   ├── Input: {"user_id": "user123"}
│   └── Output: {"name": "張三", ...}
├── Custom Span: customize_prompt
│   └── Output: {"prompt": "..."}
└── Agent Span: Agent 執行
    └── Generation Span
```

**重點：**
- 使用 `custom_span()` 追蹤自己的程式碼
- 可以記錄輸入、輸出和 metadata
- 自動巢狀在當前的 Trace 中

---

### 範例 4: 追蹤 Multi-Agent 協作 🎭

**在 Multi-Agent 系統中特別有用：**
- 看到哪個 Agent 被呼叫
- 看到執行順序
- 找出瓶頸

```python
async def multi_agent_workflow(task: str):
    # 步驟 1: 分析任務
    with custom_span(name="task_analysis_phase"):
        analysis = await Runner.run(analyzer_agent, f"分析: {task}")
    
    # 步驟 2: 執行任務
    with custom_span(name="task_execution_phase"):
        result = await Runner.run(executor_agent, f"執行: {task}")
    
    return result

# 執行
with trace(workflow_name="Multi-Agent 協作"):
    result = await multi_agent_workflow("寫文章")
```

**追蹤視圖：**
```
Trace: "Multi-Agent 協作"
│
├── Custom Span: task_analysis_phase (2.1s)
│   └── Agent Span: AnalyzerAgent
│       └── Generation Span
│
└── Custom Span: task_execution_phase (5.3s)
    └── Agent Span: ExecutorAgent
        └── Generation Span

總時間: 7.4s
```

**優點：**
- 清楚看到每個階段的耗時
- 容易找出最慢的 Agent
- 方便除錯和優化

---

### 範例 5: 敏感資料處理 🔒

**預設行為：**
- 記錄 LLM 輸入/輸出
- 記錄 Tool 輸入/輸出
- ⚠️ 可能包含敏感資料

**如何保護？**

```python
from agents import RunConfig

# 方式 1: 不記錄敏感資料
config = RunConfig(
    trace_include_sensitive_data=False  # LLM 和 Tool 的輸入/輸出不記錄
)

result = await Runner.run(
    agent,
    "處理信用卡 1234-5678-9012-3456",
    config=config
)

# 方式 2: 完全關閉追蹤
config_no_trace = RunConfig(
    tracing_disabled=True  # 完全不追蹤
)

result = await Runner.run(
    agent,
    "敏感資料處理",
    config=config_no_trace
)

# 方式 3: 全域關閉
from agents import set_tracing_disabled
set_tracing_disabled(True)  # 影響所有後續執行
```
**建議：**
- 開發環境：使用預設（方便除錯）
- 生產環境：根據資料敏感度選擇

---

### 範例 6: 本地追蹤和日誌 📝

**預設：** 追蹤資料送到 OpenAI Platform

**但你也可以：**
- 在本地記錄日誌
- 送到其他追蹤系統
- 自訂處理邏輯

```python
import json
from datetime import datetime

class LocalTraceLogger:
    """本地追蹤記錄器"""
    
    def log_trace(self, trace_name: str, metadata: dict, operations: list):
        trace_record = {
            "timestamp": datetime.now().isoformat(),
            "trace_name": trace_name,
            "metadata": metadata,
            "operations": operations,
        }
        
        # 寫入檔案
        with open("traces.log", "a", encoding="utf-8") as f:
            f.write(json.dumps(trace_record, ensure_ascii=False) + "\n")

# 使用
logger = LocalTraceLogger()

async def traced_operation(name: str, agent: Agent, task: str):
    start_time = time.time()
    
    with custom_span(name=name):
        result = await Runner.run(agent, task)
        duration = time.time() - start_time
        
        # 記錄到本地
        logger.log_trace(
            trace_name=name,
            metadata={"duration_seconds": duration},
            operations=[f"Input: {task}", f"Output: {result.final_output}"]
        )
        
        return result
```

**本地日誌格式：**
```json
{
  "timestamp": "2024-01-15T10:30:45.123456",
  "trace_name": "greeting",
  "metadata": {"duration_seconds": 2.5},
  "operations": ["Input: 你好", "Output: 你好！有什麼可以幫您？"]
}
```

---

### 範例 7: 效能分析 ⚡

**使用 Tracing 找出瓶頸：**

```python
import time

class PerformanceTracker:
    """效能追蹤器"""
    
    def __init__(self):
        self.timings = []
    
    async def track_operation(self, name: str, operation):
        start = time.time()
        
        with custom_span(name=name, metadata={"tracked": True}):
            result = await operation()
            duration = time.time() - start
            
            self.timings.append({
                "name": name,
                "duration": duration
            })
            
            return result
    
    def get_report(self):
        total = sum(t["duration"] for t in self.timings)
        slowest = max(self.timings, key=lambda x: x["duration"])
        
        return {
            "total_time": round(total, 2),
            "slowest": slowest["name"],
            "slowest_time": round(slowest["duration"], 2)
        }

# 使用
tracker = PerformanceTracker()

with trace(workflow_name="效能分析"):
    await tracker.track_operation("op1", lambda: Runner.run(agent, "任務1"))
    await tracker.track_operation("op2", lambda: Runner.run(agent, "任務2"))
    
report = tracker.get_report()
print(f"總耗時: {report['total_time']}s")
print(f"最慢操作: {report['slowest']} ({report['slowest_time']}s)")
```

**輸出範例：**
```
總耗時: 7.8s
最慢操作: op2 (5.3s)

建議: 優化 op2 操作
```

---

## 💬 總結

**Tracing 的核心價值：**

1. **🔍 可見性** - 看清楚 Agent 在做什麼
2. **🐛 除錯** - 快速定位問題
3. **⚡ 優化** - 找出效能瓶頸
4. **📊 監控** - 了解生產環境狀況
5. **📝 稽核** - 記錄所有操作（合規性）

**何時使用：**

| 情境 | 建議 |
|------|------|
| 開發階段 | ✅ 全開，方便除錯 |
| 測試階段 | ✅ 全開，找出問題 |
| 生產環境 | ⚡ 選擇性開啟或取樣 |
| 處理敏感資料 | 🔒 關閉敏感資料記錄 |

---

## 🔗 延伸閱讀

- [OpenAI Agents SDK - Tracing 官方文件](https://openai.github.io/openai-agents-python/tracing/)
- [OpenAI Traces Dashboard](https://platform.openai.com/traces)
- [Multi-Agent Orchestration 教學](../1.9_orchestrate/)
- [Guardrails 教學](../1.8_guardrails/)
