# Agent Visualization 教學

使用 OpenAI Agent SDK 的視覺化功能，產生清晰的 Agent 系統架構圖。

## 📚 學習目標

- 安裝和設定視覺化套件
- 產生 Agent 結構圖
- 理解視覺化圖表的元素
- 視覺化 Multi-Agent 系統
- 在實際開發中應用視覺化

## 📦 安裝

```bash
pip install "openai-agents[viz]"
```

**系統需求：** 需要安裝 Graphviz
- Windows: `choco install graphviz` 或從 [官網](https://graphviz.org/download/) 下載
- macOS: `brew install graphviz`
- Linux: `sudo apt-get install graphviz`

## 🎨 視覺化元素

| 元素 | 外觀 | 說明 |
|------|------|------|
| Agent | 🟨 黃色矩形 | AI Agent |
| Tool | 🟢 綠色橢圓 | 工具函式 |
| MCP Server | ⬜ 灰色矩形 | MCP 伺服器 |
| Handoff | ➡️ 實線箭頭 | Agent 轉交 |
| Tool Call | ··➡️ 虛線箭頭 | 呼叫工具 |

##  快速開始

```python
from agents import Agent, function_tool
from agents.extensions.visualization import draw_graph

@function_tool
def get_weather(city: str) -> str:
    return f"{city} 的天氣是晴天"

agent = Agent(
    name="WeatherAgent",
    instructions="你是天氣助手",
    tools=[get_weather],
)

# 產生圖表
draw_graph(agent)                      # 內嵌顯示（Jupyter）
draw_graph(agent, filename="diagram")  # 儲存為檔案
draw_graph(agent).view()               # 新視窗顯示
```

## 📋 範例說明

### 範例 1: 簡單的 Agent 視覺化
展示單一 Agent 與多個 Tools 的關係，理解基本的視覺化元素。

**學習重點：**
- `draw_graph()` 的基本用法
- 識別 Agent 節點和 Tool 節點

### 範例 2: Multi-Agent 系統視覺化
建立包含分流機制的 Multi-Agent 系統，展示 Agent 之間的 Handoff。

**學習重點：**
- Agent 之間的轉交關係
- Triage Agent 的設計模式

### 範例 3: 複雜的工作流視覺化
展示三層 Agent 架構：協調者 → 專門 Agent → 執行工具。

**學習重點：**
- 多層次的系統設計
- 協調者模式的視覺化

### 範例 4: 理解視覺化元素
詳細說明圖表中各種節點和連線的含義。

### 範例 5: 自訂圖表輸出
展示三種不同的圖表輸出方式。

### 範例 6: 實際應用場景
介紹在系統設計、除錯、文件化等階段的應用。

### 範例 7: 視覺化最佳實踐
分享命名規範和結構設計的經驗。

## 💡 使用技巧

### 清晰的命名
使用有意義的名稱，避免 `agent1`、`agent2` 這類命名。

```python
# ✅ 好的命名
weather_agent = Agent(name="WeatherAgent", ...)
finance_agent = Agent(name="FinanceAgent", ...)

# ❌ 不好的命名
a1 = Agent(name="A1", ...)
agent2 = Agent(name="agent2", ...)
```

### 適當的層級
保持 2-3 層的結構，避免過深的嵌套。

```python
# ✅ 適中的結構
coordinator -> [worker1, worker2, worker3]

# ❌ 過深的結構
level1 -> level2 -> level3 -> level4 -> level5
```

### 合理的 Handoff 數量
單一 Agent 的 Handoff 建議不超過 5 個。

## 🎯 實際應用

### 1. 系統設計階段
在寫程式碼前先視覺化設計，驗證架構合理性。

### 2. 程式碼 Review
在 Pull Request 中附上系統架構圖，幫助 Reviewer 理解變更。

```python
draw_graph(main_agent, filename="pr_architecture")
```

### 3. 文件化
自動產生和更新系統架構文件。

```python
draw_graph(agent, filename=f"docs/architecture_v{version}")
```

### 4. 除錯
當系統行為異常時，先檢查架構圖是否符合預期。

## 📊 圖表解讀

### 簡單系統
```
__start__ → WeatherAgent → get_weather
                         → get_forecast
          → __end__
```
單一 Agent，兩個 Tools，線性流程。

### Multi-Agent 系統
```
__start__ → TriageAgent ⇒ SpanishAgent → translate
                        ⇒ EnglishAgent → spell_check
          → __end__
```
分流 Agent 根據需求轉交給專門的 Agent，實線箭頭 (⇒) 表示 Handoff。

## ⚠️ 常見問題

### Q1: 圖表無法產生？
確認已安裝 Graphviz：
```bash
dot -V
```
若未安裝，參考上方安裝說明。

### Q2: 圖表太複雜看不清楚？
考慮重新設計：
- 減少 Agent 的層級深度
- 將相關 Agent 組合成模組
- 拆分成多個獨立的子系統

### Q3: 如何在 CI/CD 中使用？
設定 GitHub Actions 自動產生圖表：

```yaml
- name: Generate Architecture Diagram
  run: |
    pip install "openai-agents[viz]"
    python generate_diagram.py
```

### Q4: 可以自訂圖表樣式嗎？
`draw_graph()` 使用預設樣式。若需要自訂：
- 修改產生的 DOT 檔案
- 使用其他視覺化工具（如 D3.js）

## 📝 練習

1. **基礎練習**：建立一個包含 3 個 Tools 的 Agent，產生視覺化圖表
2. **進階練習**：設計客服系統，包含分流、技術支援、帳務查詢等 Agent
3. **實戰練習**：為現有專案產生架構圖，加入 README 文件中

## 🔗 相關資源

- [官方文件](https://openai.github.io/openai-agents-python/visualization/)
- [Graphviz 官網](https://graphviz.org/)
- [Multi-Agent 系統設計](../1.9_orchestrate/)
- [Handoff 機制](../1.6_handoff/)

---

**下一步學習：**
- Context Management - 管理 Agent 的上下文
- Guardrails - 設定 Agent 的安全防護

祝學習愉快！ 🚀
