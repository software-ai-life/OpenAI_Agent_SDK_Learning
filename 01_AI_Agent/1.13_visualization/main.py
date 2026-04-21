"""
Agent Visualization 教學 - OpenAI Agents SDK

此範例展示如何使用視覺化功能來繪製 Agent 的結構圖。
視覺化可以幫助你理解 Agent、Tool 和 Handoff 之間的關係。

學習重點：
1. 安裝視覺化套件
2. 產生 Agent 結構圖
3. 理解視覺化元素
4. 自訂和儲存圖表
5. 多 Agent 系統視覺化
"""

import os
import httpx
from dotenv import load_dotenv
from typing import List

from agents import (
    Agent,
    AsyncOpenAI,
    OpenAIChatCompletionsModel,
    function_tool,
)

# 視覺化功能需要額外安裝：pip install "openai-agents[viz]"
try:
    from agents.extensions.visualization import draw_graph
    VISUALIZATION_AVAILABLE = True
except ImportError:
    VISUALIZATION_AVAILABLE = False
    print("⚠️  視覺化功能未安裝，請執行: pip install \"openai-agents[viz]\"")

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


# ============= 範例 1: 簡單的 Agent 視覺化 =============

print("=" * 60)
print("範例 1: 簡單的 Agent 視覺化")
print("=" * 60)

"""
最基本的視覺化：單一 Agent + Tools
"""


@function_tool
def get_weather(city: str) -> str:
    """取得城市天氣"""
    return f"{city} 的天氣是晴天"


@function_tool
def calculate_distance(city_a: str, city_b: str) -> str:
    """計算兩個城市之間的距離"""
    return f"{city_a} 到 {city_b} 的距離約 100 公里"


simple_agent = Agent(
    name="WeatherAgent",
    instructions="你是天氣助手，可以提供天氣資訊和距離計算",
    model=model,
    tools=[get_weather, calculate_distance],
)


def example1_simple_visualization():
    """範例 1: 簡單的 Agent 視覺化"""
    
    if not VISUALIZATION_AVAILABLE:
        print("\n⚠️  視覺化功能未安裝，跳過此範例")
        return
    
    print("\n產生 WeatherAgent 的視覺化圖表...")
    

    # 產生並儲存圖表
    graph = draw_graph(simple_agent, filename="example1_simple_agent")
    
    print(f"\n✅ 圖表已儲存為: example1_simple_agent.png")
    print("\n圖表包含：")
    print("  - 黃色方框: Agent (WeatherAgent)")
    print("  - 綠色橢圓: Tools (get_weather, calculate_distance)")
    print("  - 虛線箭頭: Tool 呼叫關係")


# ============= 範例 2: Multi-Agent 系統視覺化 =============

print("\n\n" + "=" * 60)
print("範例 2: Multi-Agent 系統視覺化")
print("=" * 60)

"""
展示多個 Agent 之間的 Handoff 關係
"""


@function_tool
def translate_to_spanish(text: str) -> str:
    """翻譯成西班牙文"""
    return f"[西班牙文翻譯] {text}"


@function_tool
def translate_to_english(text: str) -> str:
    """翻譯成英文"""
    return f"[英文翻譯] {text}"


# 建立專門的語言 Agent
spanish_agent = Agent(
    name="SpanishAgent",
    instructions="你只會說西班牙文，負責處理西班牙文相關的任務",
    model=model,
    tools=[translate_to_spanish],
)

english_agent = Agent(
    name="EnglishAgent",
    instructions="你只會說英文，負責處理英文相關的任務",
    model=model,
    tools=[translate_to_english],
)

# 建立分流 Agent
triage_agent = Agent(
    name="TriageAgent",
    instructions="""你是分流助手，根據使用者的語言需求，將任務轉交給適當的 Agent：
    - 西班牙文任務 -> SpanishAgent
    - 英文任務 -> EnglishAgent""",
    model=model,
    handoffs=[spanish_agent, english_agent],
)


def example2_multi_agent_visualization():
    """範例 2: Multi-Agent 系統視覺化"""
    
    if not VISUALIZATION_AVAILABLE:
        print("\n⚠️  視覺化功能未安裝，跳過此範例")
        return
    
    print("\n產生 Multi-Agent 系統的視覺化圖表...")
    
    try:
        # 產生並儲存圖表
        graph = draw_graph(triage_agent, filename="example2_multi_agent")
        
        print(f"\n✅ 圖表已儲存為: example2_multi_agent.png")
        print("\n圖表包含：")
        print("  - 黃色方框: Agents (TriageAgent, SpanishAgent, EnglishAgent)")
        print("  - 綠色橢圓: Tools (translate_to_spanish, translate_to_english)")
        print("  - 實線箭頭: Agent 之間的 Handoff")
        print("  - 虛線箭頭: Agent 到 Tool 的呼叫")
    except Exception as e:
        if "ExecutableNotFound" in str(type(e).__name__) or "dot" in str(e):
            print("\n❌ Graphviz 未安裝，跳過此範例")
        else:
            print(f"\n❌ 發生錯誤: {e}")


# ============= 範例 3: 複雜的工作流視覺化 =============

print("\n\n" + "=" * 60)
print("範例 3: 複雜的工作流視覺化")
print("=" * 60)

"""
展示更複雜的 Agent 系統，包含多層 Handoff
"""


@function_tool
def search_database(query: str) -> str:
    """搜尋資料庫"""
    return f"資料庫搜尋結果: {query}"


@function_tool
def analyze_data(data: str) -> str:
    """分析資料"""
    return f"資料分析: {data}"


@function_tool
def generate_report(analysis: str) -> str:
    """產生報告"""
    return f"報告: {analysis}"


# 建立專門的工作 Agent
search_agent = Agent(
    name="SearchAgent",
    instructions="負責搜尋資料庫",
    model=model,
    tools=[search_database],
)

analysis_agent = Agent(
    name="AnalysisAgent",
    instructions="負責分析資料",
    model=model,
    tools=[analyze_data],
)

report_agent = Agent(
    name="ReportAgent",
    instructions="負責產生報告",
    model=model,
    tools=[generate_report],
)

# 建立協調 Agent
coordinator_agent = Agent(
    name="CoordinatorAgent",
    instructions="""你是協調者，負責管理整個工作流：
    1. 需要搜尋時，轉交給 SearchAgent
    2. 需要分析時，轉交給 AnalysisAgent
    3. 需要報告時，轉交給 ReportAgent""",
    model=model,
    handoffs=[search_agent, analysis_agent, report_agent],
)


def example3_complex_workflow_visualization():
    """範例 3: 複雜的工作流視覺化"""
    
    if not VISUALIZATION_AVAILABLE:
        print("\n⚠️  視覺化功能未安裝，跳過此範例")
        return
    
    print("\n產生複雜工作流的視覺化圖表...")
    
    try:
        # 產生並儲存圖表
        graph = draw_graph(coordinator_agent, filename="example3_complex_workflow")
        
        print(f"\n✅ 圖表已儲存為: example3_complex_workflow.png")
        print("\n圖表包含：")
        print("  - 4 個 Agents: CoordinatorAgent + 3 個專門 Agents")
        print("  - 3 個 Tools: search_database, analyze_data, generate_report")
        print("  - 顯示完整的工作流結構")
    except Exception as e:
        if "ExecutableNotFound" in str(type(e).__name__) or "dot" in str(e):
            print("\n❌ Graphviz 未安裝，跳過此範例")
        else:
            print(f"\n❌ 發生錯誤: {e}")


# ============= 範例 4: 理解視覺化元素 =============

print("\n\n" + "=" * 60)
print("範例 4: 理解視覺化元素")
print("=" * 60)

"""
說明視覺化圖表中各種元素的含義
"""


def example4_understanding_visualization():
    """範例 4: 理解視覺化元素"""
    
    print("\n視覺化圖表元素說明：")
    print("\n1. 節點類型：")
    print("   - 黃色矩形: Agent (代理)")
    print("   - 綠色橢圓: Tool (工具)")
    print("   - 灰色矩形: MCP Server (若有使用)")
    print("   - __start__: 執行起點")
    print("   - __end__: 執行終點")
    
    print("\n2. 連線類型：")
    print("   - 實線箭頭: Agent 到 Agent 的 Handoff (轉交)")
    print("   - 虛線箭頭: Agent 到 Tool 的呼叫")
    print("   - 虛線箭頭: Agent 到 MCP Server 的呼叫")
    
    print("\n3. 圖表結構：")
    print("   - 從 __start__ 開始")
    print("   - 顯示所有可能的執行路徑")
    print("   - 以 __end__ 結束")
    
    print("\n4. 使用場景：")
    print("   - 📊 理解系統架構")
    print("   - 🔍 除錯 Agent 互動")
    print("   - 📝 文件化系統設計")
    print("   - 👥 團隊溝通和討論")


# ============= 範例 5: 自訂圖表輸出 =============

print("\n\n" + "=" * 60)
print("範例 5: 自訂圖表輸出")
print("=" * 60)

"""
展示如何自訂圖表的顯示和儲存方式
"""


def example5_custom_output():
    """範例 5: 自訂圖表輸出"""
    
    if not VISUALIZATION_AVAILABLE:
        print("\n⚠️  視覺化功能未安裝，跳過此範例")
        return
    
    print("\n圖表輸出方式：")
    
    # 方式 1: 預設顯示（內嵌顯示）
    print("\n1. 預設顯示（內嵌）：")
    print("   graph = draw_graph(agent)")
    print("   - 在 Jupyter Notebook 中會內嵌顯示")
    
    # 方式 2: 在新視窗中顯示
    print("\n2. 在新視窗中顯示：")
    print("   draw_graph(agent).view()")
    print("   - 會開啟系統預設的圖片檢視器")
    
    # 方式 3: 儲存為檔案
    print("\n3. 儲存為檔案：")
    print("   draw_graph(agent, filename='my_agent')")
    print("   - 會產生 my_agent.png 檔案")
    
    # 實際產生一個範例
    print("\n產生範例圖表...")
    try:
        graph = draw_graph(simple_agent, filename="example5_custom_output")
        
        print(f"\n✅ 圖表已儲存為: example5_custom_output.png")
        print("\n提示：")
        print("  - 可以使用各種圖片檢視器開啟")
        print("  - 適合加入到文件或簡報中")
        print("  - 方便與團隊分享")
    except Exception as e:
        if "ExecutableNotFound" in str(type(e).__name__) or "dot" in str(e):
            print("\n❌ Graphviz 未安裝，跳過此範例")
        else:
            print(f"\n❌ 發生錯誤: {e}")


# ============= 範例 6: 實際應用場景 =============

print("\n\n" + "=" * 60)
print("範例 6: 實際應用場景")
print("=" * 60)

"""
展示視覺化在實際開發中的應用
"""


def example6_practical_use_cases():
    """範例 6: 實際應用場景"""
    
    print("\n視覺化的實際應用：")
    
    print("\n1. 🏗️ 設計階段：")
    print("   - 規劃 Multi-Agent 系統架構")
    print("   - 確定 Agent 之間的互動關係")
    print("   - 設計 Tool 的配置")
    
    print("\n2. 🔧 開發階段：")
    print("   - 驗證實作是否符合設計")
    print("   - 快速理解現有程式碼結構")
    print("   - 重構時評估影響範圍")
    
    print("\n3. 🐛 除錯階段：")
    print("   - 找出 Handoff 的問題")
    print("   - 確認 Tool 是否正確連接")
    print("   - 理解執行流程")
    
    print("\n4. 📚 文件化：")
    print("   - 產生系統架構圖")
    print("   - 撰寫技術文件")
    print("   - 製作教學材料")
    
    print("\n5. 👥 團隊協作：")
    print("   - Code Review 時的視覺輔助")
    print("   - 向非技術人員說明系統")
    print("   - 新成員快速上手")


# ============= 範例 7: 視覺化最佳實踐 =============

print("\n\n" + "=" * 60)
print("範例 7: 視覺化最佳實踐")
print("=" * 60)

"""
分享使用視覺化功能的最佳實踐
"""


def example7_best_practices():
    """範例 7: 視覺化最佳實踐"""
    
    print("\n視覺化最佳實踐：")
    
    print("\n1. 命名規範：")
    print("   ✅ 使用清楚描述性的 Agent 名稱")
    print("   ✅ Tool 名稱應該表達其功能")
    print("   ❌ 避免使用模糊的縮寫")
    
    print("\n2. 結構設計：")
    print("   ✅ 保持 Agent 層級不要太深（建議 2-3 層）")
    print("   ✅ 每個 Agent 的 Handoff 數量適中（建議 3-5 個）")
    print("   ❌ 避免過於複雜的循環結構")
    
    print("\n3. 文件管理：")
    print("   ✅ 定期更新視覺化圖表")
    print("   ✅ 為不同版本保留圖表記錄")
    print("   ✅ 在 README 中包含系統架構圖")
    
    print("\n4. 版本控制：")
    print("   ✅ 將視覺化程式碼加入版本控制")
    print("   ⚠️  考慮是否將 PNG 檔案加入 git")
    print("   ✅ 使用 CI/CD 自動產生圖表")
    
    print("\n5. 除錯技巧：")
    print("   ✅ 先畫圖再寫程式碼")
    print("   ✅ 出問題時先檢查視覺化圖表")
    print("   ✅ 比對預期和實際的圖表差異")


# ============= 主程式 =============

def main():
    """執行所有範例"""
    
    print("\n")
    print("📊 Agent Visualization 教學")
    print("=" * 60)
    
    if not VISUALIZATION_AVAILABLE:
        print("\n⚠️  警告：視覺化功能未安裝")
        print("請執行以下指令安裝：")
        print("  pip install \"openai-agents[viz]\"")
        print("\n將繼續執行範例說明...\n")
    else:
        print("\n檢查 Graphviz 安裝狀態...")
        import shutil
        if not shutil.which("dot"):
            print("\n⚠️  警告：Graphviz 未安裝或未加入 PATH")
            print("\n安裝步驟：")
            print("  1. 使用 Chocolatey: choco install graphviz")
            print("  2. 或從官網下載: https://graphviz.org/download/")
            print("     - 下載 Windows 安裝檔")
            print("     - 執行安裝程式")
            print("     - 勾選 'Add Graphviz to the system PATH'")
            print("  3. 重新啟動 terminal")
            print("\n將繼續執行範例說明（圖表產生會失敗）...\n")
        else:
            print("✅ Graphviz 已安裝\n")
    
    # 範例 1: 簡單的 Agent 視覺化
    example1_simple_visualization()
    
    # 範例 2: Multi-Agent 系統視覺化
    example2_multi_agent_visualization()
    
    # 範例 3: 複雜的工作流視覺化
    example3_complex_workflow_visualization()
    
    # 範例 4: 理解視覺化元素
    example4_understanding_visualization()
    
    # 範例 5: 自訂圖表輸出
    example5_custom_output()
    
    # 範例 6: 實際應用場景
    example6_practical_use_cases()
    
    # 範例 7: 視覺化最佳實踐
    example7_best_practices()
    
    print("\n\n" + "=" * 60)
    print("✅ 所有範例執行完成！")
    print("=" * 60)
    
    if VISUALIZATION_AVAILABLE:
        print("\n產生的圖表檔案：")
        print("  - example1_simple_agent.png")
        print("  - example2_multi_agent.png")
        print("  - example3_complex_workflow.png")
        print("  - example5_custom_output.png")
    
    print("\n提示：")
    print("- 視覺化需要安裝 Graphviz")
    print("- 圖表會儲存在目前工作目錄")
    print("- 適合用於文件化和團隊溝通")


if __name__ == "__main__":
    main()
