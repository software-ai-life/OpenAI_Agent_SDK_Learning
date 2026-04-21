"""
Tracing 教學 - OpenAI Agents SDK

此範例展示如何使用 Tracing（追蹤）功能來除錯、監控和觀察 AI Agent 的執行過程。
Tracing 就像是給你的 Agent 安裝「行車記錄器」，記錄所有發生的事情。

學習重點：
1. 什麼是 Traces 和 Spans
2. 預設的自動追蹤
3. 建立自訂 Traces
4. 建立自訂 Spans
5. 敏感資料處理
6. 本地追蹤和日誌
"""

import os
import httpx
import asyncio
import time
import json
from datetime import datetime
from dotenv import load_dotenv
from typing import List
from pydantic import BaseModel, Field

from agents import (
    Agent,
    Runner,
    AsyncOpenAI,
    OpenAIChatCompletionsModel,
    set_tracing_disabled,
    trace,
    custom_span,
    RunConfig,
    function_tool,
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
    model=MODEL_NAME,
    openai_client=AsyncOpenAI(
        base_url=BASE_URL,
        api_key=API_KEY,
        http_client=httpx.AsyncClient(
            verify=False,  # 略過 SSL 驗證
            limits=httpx.Limits(
                max_connections=1000,
                max_keepalive_connections=100
            )
        )
    ),
)


# ============= 範例 1: 預設追蹤（自動記錄）=============

print("=" * 60)
print("範例 1: 預設追蹤 - SDK 自動記錄所有操作")
print("=" * 60)

"""
SDK 預設會自動追蹤：
- Runner.run() 整個執行過程
- 每個 Agent 的執行
- LLM 生成
- Tool 呼叫
- Guardrails 檢查
- Handoffs 轉移
"""


@function_tool
def calculate_sum(numbers: List[int]) -> int:
    """計算數字總和"""
    return sum(numbers)


@function_tool
def get_current_time() -> str:
    """取得當前時間"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


simple_agent = Agent(
    name="SimpleAgent",
    instructions="你是數學助手，可以計算數字和告訴使用者時間。",
    model=model,
    tools=[calculate_sum, get_current_time],
)


async def example1_default_tracing():
    """範例 1: 預設追蹤"""
    
    print("\n開始執行（自動追蹤中...）")
    
    # SDK 會自動記錄：
    # - Trace: 整個 run() 的執行
    # - Agent Span: SimpleAgent 的執行
    # - Generation Span: LLM 的回應
    # - Function Span: Tool 的呼叫
    
    result = await Runner.run(
        simple_agent,
        "計算 1 到 10 的總和，然後告訴我現在幾點"
    )
    
    print(f"\n結果: {result.final_output}")
    print("\n✅ 所有操作已自動記錄到追蹤系統")
    print("   （在生產環境可以到 OpenAI Platform 查看追蹤資料）")


# ============= 範例 2: 自訂 Trace 名稱 =============

print("\n\n" + "=" * 60)
print("範例 2: 自訂 Trace - 給追蹤命名和分組")
print("=" * 60)

"""
使用 trace() 來：
1. 給追蹤一個有意義的名稱
2. 將多個操作組合在一個追蹤中
3. 加入 metadata
"""


async def example2_custom_trace_name():
    """範例 2: 自訂 Trace 名稱"""
    
    # 方式 1: 單一操作的自訂名稱
    print("\n方式 1: 單一操作")
    
    with trace(
        workflow_name="數學計算工作流",
        metadata={"user_id": "user123", "session": "session456"}
    ):
        result = await Runner.run(
            simple_agent,
            "計算 5 + 10 + 15"
        )
        print(f"結果: {result.final_output}")
    
    # 方式 2: 多個操作在同一個 Trace 中
    print("\n方式 2: 多個操作組合")
    
    with trace(
        workflow_name="連續對話工作流",
        metadata={"conversation_id": "conv789"}
    ) as my_trace:
        
        print(f"Trace ID: {my_trace.trace_id}")
        
        # 第一個問題
        result1 = await Runner.run(simple_agent, "1 + 2 等於多少？")
        print(f"第一次回應: {result1.final_output}")
        
        # 第二個問題（在同一個 Trace 中）
        result2 = await Runner.run(simple_agent, "剛才的答案乘以 10 是多少？")
        print(f"第二次回應: {result2.final_output}")
        
        print(f"\n✅ 兩次操作都記錄在同一個 Trace: {my_trace.trace_id}")


# ============= 範例 3: 自訂 Spans（追蹤自己的操作）=============

print("\n\n" + "=" * 60)
print("範例 3: 自訂 Spans - 追蹤你的程式碼")
print("=" * 60)

"""
使用 custom_span() 來追蹤：
- 資料處理步驟
- API 呼叫
- 檔案操作
- 任何你想記錄的操作
"""


async def fetch_user_data(user_id: str) -> dict:
    """模擬從資料庫取得使用者資料"""
    await asyncio.sleep(0.5)  # 模擬延遲
    return {
        "user_id": user_id,
        "name": "張三",
        "preferences": ["數學", "科學"]
    }


async def process_user_query(user_id: str, query: str) -> str:
    """處理使用者查詢的完整流程"""
    
    # 步驟 1: 取得使用者資料（使用 custom_span 追蹤）
    with custom_span(name="fetch_user_data"):
        user_data = await fetch_user_data(user_id)
        # custom_span 會自動追蹤這個步驟的執行時間
    
    # 步驟 2: 根據偏好自訂提示詞
    with custom_span(name="customize_prompt"):
        custom_instruction = f"使用者喜歡 {', '.join(user_data['preferences'])}。"
    
    # 步驟 3: 呼叫 Agent
    customized_agent = Agent(
        name="CustomizedAgent",
        instructions=f"你是助手。{custom_instruction}",
        model=model,
    )
    
    result = await Runner.run(customized_agent, query)
    
    return result.final_output


async def example3_custom_spans():
    """範例 3: 自訂 Spans"""
    
    print("\n執行包含自訂 Spans 的工作流...")
    
    with trace(workflow_name="個人化查詢工作流"):
        response = await process_user_query(
            user_id="user123",
            query="推薦我一本書"
        )
        
        print(f"\n最終回應: {response}")
        print("\n✅ 所有步驟（包括自訂的）都已追蹤：")
        print("   1. fetch_user_data")
        print("   2. customize_prompt")
        print("   3. Agent execution")


# ============= 範例 4: 追蹤多個 Agent 協作 =============

print("\n\n" + "=" * 60)
print("範例 4: 追蹤 Multi-Agent - 觀察 Agent 間的互動")
print("=" * 60)

"""
在 Multi-Agent 系統中，Tracing 特別有用：
- 看到哪個 Agent 被呼叫
- 看到執行順序
- 找出瓶頸和問題
"""


class TaskAnalysis(BaseModel):
    """任務分析結果"""
    task_type: str = Field(description="任務類型")
    complexity: str = Field(description="複雜度：simple/medium/complex")
    estimated_time: int = Field(description="預估時間（秒）")


analyzer_agent = Agent(
    name="AnalyzerAgent",
    instructions=f"""你負責分析任務的類型和複雜度。
    請確保輸出符合以下 JSON 結構：
    {TaskAnalysis.model_json_schema()}""",
    model=model,
)

executor_agent = Agent(
    name="ExecutorAgent",
    instructions="你負責執行任務並產生結果",
    model=model,
)


async def multi_agent_workflow(task: str) -> str:
    """多個 Agent 的協作流程"""
    
    # 步驟 1: 分析任務
    with custom_span(name="task_analysis_phase"):
        analysis_result = await Runner.run(analyzer_agent, f"分析任務: {task}")
        # 由於 Gemini 可能無法完美支援結構化輸出，我們用簡單的方式處理
        print(f"\n任務分析結果: {analysis_result.final_output}")
    
    # 步驟 2: 執行任務
    with custom_span(name="task_execution_phase"):
        execution_result = await Runner.run(
            executor_agent,
            f"執行任務: {task}"
        )
        print(f"\n執行結果: {execution_result.final_output[:100]}...")
    
    return execution_result.final_output


async def example4_multi_agent_tracing():
    """範例 4: 追蹤多個 Agent"""
    
    print("\n執行 Multi-Agent 工作流...")
    
    with trace(
        workflow_name="Multi-Agent 協作",
        metadata={"agent_count": 2}
    ):
        result = await multi_agent_workflow("寫一篇關於 AI 的短文")
        print(f"\n✅ 完整的 Multi-Agent 執行流程已追蹤")


# ============= 範例 5: 控制敏感資料 =============

print("\n\n" + "=" * 60)
print("範例 5: 敏感資料處理 - 保護隱私")
print("=" * 60)

"""
Tracing 預設會記錄：
- LLM 的輸入/輸出
- Tool 的輸入/輸出

如果包含敏感資料，可以選擇不記錄
"""


@function_tool
def process_credit_card(card_number: str) -> str:
    """處理信用卡（模擬）"""
    return f"卡號 {card_number[-4:]} 已處理"


sensitive_agent = Agent(
    name="SensitiveAgent",
    instructions="你處理敏感資料",
    model=model,
    tools=[process_credit_card],
)


async def example5_sensitive_data():
    """範例 5: 敏感資料處理"""
    
    # 方式 1: 預設（會記錄所有資料）
    print("\n方式 1: 預設設定（記錄所有資料）")
    result1 = await Runner.run(
        sensitive_agent,
        "處理信用卡 1234-5678-9012-3456"
    )
    print(f"結果: {result1.final_output}")
    print("⚠️  輸入和輸出都被記錄（包括敏感資料）")
    
    # 方式 2: 不記錄敏感資料
    print("\n方式 2: 不記錄敏感資料")
    config = RunConfig(
        trace_include_sensitive_data=False  # 不記錄敏感資料
    )
    
    result2 = await Runner.run(
        sensitive_agent,
        "處理信用卡 1234-5678-9012-3456",
        run_config=config
    )
    print(f"結果: {result2.final_output}")
    print("✅ LLM 輸入/輸出和 Tool 輸入/輸出不會被記錄")
    
    # 方式 3: 完全關閉追蹤
    print("\n方式 3: 完全關閉追蹤")
    config_no_trace = RunConfig(
        tracing_disabled=True  # 完全不追蹤
    )
    
    result3 = await Runner.run(
        sensitive_agent,
        "處理信用卡 1234-5678-9012-3456",
        run_config=config_no_trace
    )
    print(f"結果: {result3.final_output}")
    print("✅ 完全不記錄任何追蹤資料")


# ============= 範例 6: 本地追蹤和日誌 =============

print("\n\n" + "=" * 60)
print("範例 6: 本地追蹤 - 自己處理追蹤資料")
print("=" * 60)

"""
雖然 SDK 預設會送到 OpenAI Platform，
但你也可以：
1. 在本地記錄日誌
2. 送到其他追蹤系統（Weights & Biases, Arize, etc.）
3. 自訂處理邏輯
"""


class LocalTraceLogger:
    """本地追蹤記錄器"""
    
    def __init__(self):
        self.traces = []
    
    def log_trace(self, trace_name: str, metadata: dict, operations: List[str]):
        """記錄追蹤資訊"""
        trace_record = {
            "timestamp": datetime.now().isoformat(),
            "trace_name": trace_name,
            "metadata": metadata,
            "operations": operations,
        }
        self.traces.append(trace_record)
        
        # 寫入檔案
        with open("traces.log", "a", encoding="utf-8") as f:
            f.write(json.dumps(trace_record, ensure_ascii=False) + "\n")
    
    def get_summary(self):
        """取得追蹤摘要"""
        return {
            "total_traces": len(self.traces),
            "traces": self.traces[-5:]  # 最近 5 筆
        }


# 建立本地記錄器
local_logger = LocalTraceLogger()


async def traced_operation(operation_name: str, agent: Agent, task: str):
    """包裝操作並記錄"""
    
    start_time = time.time()
    
    with custom_span(name=operation_name) as span:
        result = await Runner.run(agent, task)
        duration = time.time() - start_time
        
        # 記錄到本地
        local_logger.log_trace(
            trace_name=operation_name,
            metadata={
                "agent": agent.name,
                "duration_seconds": round(duration, 2)
            },
            operations=[
                f"Input: {task[:50]}...",
                f"Output: {result.final_output[:50]}..."
            ]
        )
        
        return result


async def example6_local_tracing():
    """範例 6: 本地追蹤"""
    
    print("\n執行操作並記錄到本地...")
    
    with trace(workflow_name="本地追蹤示範"):
        # 執行一些操作
        await traced_operation(
            "greeting",
            simple_agent,
            "說個笑話"
        )
        
        await traced_operation(
            "calculation",
            simple_agent,
            "計算 100 + 200"
        )
    
    # 顯示本地追蹤摘要
    summary = local_logger.get_summary()
    print(f"\n本地追蹤摘要:")
    print(f"  總追蹤數: {summary['total_traces']}")
    print(f"\n最近的追蹤:")
    for trace_item in summary['traces']:
        print(f"  - {trace_item['trace_name']} ({trace_item['timestamp']})")
        print(f"    Duration: {trace_item['metadata']['duration_seconds']}s")
    
    print(f"\n✅ 追蹤資料已儲存到 traces.log")


# ============= 範例 7: 追蹤效能分析 =============

print("\n\n" + "=" * 60)
print("範例 7: 效能分析 - 找出瓶頸")
print("=" * 60)

"""
使用 Tracing 來分析效能：
- 哪個步驟最慢？
- 哪個 Agent 花最多時間？
- 哪個 Tool 最常被呼叫？
"""


class PerformanceTracker:
    """效能追蹤器"""
    
    def __init__(self):
        self.timings = []
    
    async def track_operation(self, name: str, operation):
        """追蹤操作的執行時間"""
        start = time.time()
        
        with custom_span(name=name):
            result = await operation()
            duration = time.time() - start
            
            self.timings.append({
                "name": name,
                "duration": duration,
                "timestamp": datetime.now().isoformat()
            })
            
            return result
    
    def get_report(self):
        """取得效能報告"""
        if not self.timings:
            return "沒有資料"
        
        # 計算統計
        total_time = sum(t["duration"] for t in self.timings)
        slowest = max(self.timings, key=lambda x: x["duration"])
        fastest = min(self.timings, key=lambda x: x["duration"])
        
        return {
            "total_operations": len(self.timings),
            "total_time": round(total_time, 2),
            "average_time": round(total_time / len(self.timings), 2),
            "slowest": {
                "name": slowest["name"],
                "duration": round(slowest["duration"], 2)
            },
            "fastest": {
                "name": fastest["name"],
                "duration": round(fastest["duration"], 2)
            }
        }


async def example7_performance_analysis():
    """範例 7: 效能分析"""
    
    print("\n執行多個操作並分析效能...")
    
    tracker = PerformanceTracker()
    
    with trace(workflow_name="效能分析工作流"):
        # 追蹤多個操作
        await tracker.track_operation(
            "quick_calculation",
            lambda: Runner.run(simple_agent, "1 + 1")
        )
        
        await tracker.track_operation(
            "complex_calculation",
            lambda: Runner.run(simple_agent, "計算 1 到 100 的總和")
        )
        
        await tracker.track_operation(
            "time_query",
            lambda: Runner.run(simple_agent, "現在幾點？")
        )
    
    # 顯示效能報告
    report = tracker.get_report()
    print(f"\n效能報告:")
    print(f"  總操作數: {report['total_operations']}")
    print(f"  總耗時: {report['total_time']}s")
    print(f"  平均耗時: {report['average_time']}s")
    print(f"  最慢操作: {report['slowest']['name']} ({report['slowest']['duration']}s)")
    print(f"  最快操作: {report['fastest']['name']} ({report['fastest']['duration']}s)")


# ============= 主程式 =============

async def main():
    """執行所有範例"""
    
    print("\n")
    print("🔍 Tracing 教學")
    print("=" * 60)
    
    # 範例 1: 預設追蹤
    await example1_default_tracing()
    await asyncio.sleep(2)  # 避免速率限制
    
    # 範例 2: 自訂 Trace 名稱
    await example2_custom_trace_name()
    await asyncio.sleep(2)  # 避免速率限制
    
    # 範例 3: 自訂 Spans
    await example3_custom_spans()
    await asyncio.sleep(2)  # 避免速率限制
    
    # 範例 4: 追蹤多個 Agent
    await example4_multi_agent_tracing()
    await asyncio.sleep(2)  # 避免速率限制
    
    # 範例 5: 敏感資料處理
    await example5_sensitive_data()
    await asyncio.sleep(2)  # 避免速率限制
    
    # 範例 6: 本地追蹤
    await example6_local_tracing()
    await asyncio.sleep(2)  # 避免速率限制
    
    # 範例 7: 效能分析
    await example7_performance_analysis()
    
    print("\n\n" + "=" * 60)
    print("✅ 所有範例執行完成！")
    print("=" * 60)
    print("\n提示:")
    print("- 預設追蹤資料會送到 OpenAI Platform")
    print("- 可以在 https://platform.openai.com/traces 查看")
    print("- 本地日誌已儲存在 traces.log")


if __name__ == "__main__":
    # 注意：預設追蹤是啟用的
    # 如果要全域關閉，可以使用：
    # set_tracing_disabled(True)
    
    asyncio.run(main())
