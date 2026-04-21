# 進階 Handoff 用法範例

這個文件展示了基於 [OpenAI Agents 官方文檔](https://openai.github.io/openai-agents-python/handoffs/) 的各種進階 handoff 用法。

## 🏗️ 系統架構

### 1. 基本 Handoff 代理人
```python
# 使用推薦的 handoff 提示
technical_analysis_agent = Agent(
    name="technical_analysis_agent",
    instructions=f"""{RECOMMENDED_PROMPT_PREFIX}
    您的代理人指令...
    """,
    handoff_description="專門進行股票技術分析",
    model=model
)
```

### 2. 自訂輸入數據模型
```python
class TechnicalAnalysisData(BaseModel):
    """技術分析請求數據模型"""
    timeframe: str = "daily"  # daily, weekly, monthly
    indicators: list[str] = ["RSI", "MACD", "MA"]
    focus_area: str = "trend"  # trend, pattern, support_resistance
```

### 3. Handoff 回調函數
```python
async def on_technical_handoff(ctx: RunContextWrapper[None], input_data: TechnicalAnalysisData):
    """技術分析 handoff 回調函數"""
    print(f"🔍 技術分析 handoff 被調用")
    print(f"   時間框架: {input_data.timeframe}")
    # 可以在這裡添加數據預處理邏輯
```

### 4. 自訂 Handoff 對象
```python
technical_handoff = handoff(
    agent=technical_analysis_agent,
    tool_name_override="analyze_technical_indicators",
    tool_description_override="深入分析股票技術指標、圖表模式和趨勢",
    on_handoff=on_technical_handoff,
    input_type=TechnicalAnalysisData,
)
```

## 🔧 進階功能詳解

### 1. **自訂工具名稱和描述**
```python
handoff(
    agent=agent,
    tool_name_override="custom_tool_name",
    tool_description_override="自訂的工具描述",
)
```

**優勢：**
- 更專業的工具名稱
- 更清晰的工具描述
- 更好的用戶體驗

### 2. **輸入數據模型**
```python
class EscalationData(BaseModel):
    reason: str
    urgency_level: str = "normal"
    user_experience: str = "beginner"
```

**優勢：**
- 結構化數據傳遞
- 類型安全
- 預設值支援

### 3. **Handoff 回調函數**
```python
async def on_handoff(ctx: RunContextWrapper[None], input_data: YourDataModel):
    # 實時記錄和分析
    # 數據預處理
    # 外部 API 調用
    # 日誌記錄
```

**用途：**
- 實時監控 handoff 事件
- 數據預處理和準備
- 外部系統集成
- 性能監控

### 4. **輸入過濾器**
```python
from agents.extensions import handoff_filters

handoff(
    agent=agent,
    input_filter=handoff_filters.remove_all_tools,  # 移除所有工具調用
)
```

**可用的過濾器：**
- `remove_all_tools` - 移除所有工具調用歷史
- `remove_system_messages` - 移除系統消息
- `keep_last_n_messages` - 只保留最後 N 條消息

### 5. **推薦的 Handoff 提示**
```python
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX, prompt_with_handoff_instructions

# 方法 1：手動添加
instructions=f"""{RECOMMENDED_PROMPT_PREFIX}
您的代理人指令...
"""

# 方法 2：自動添加
instructions=prompt_with_handoff_instructions("您的代理人指令...")
```

## 📊 使用場景

### 1. **技術分析請求**
```
用戶輸入：分析 AAPL 的技術指標，關注 RSI 和 MACD
系統處理：
- 分類代理人識別為技術分析需求
- 調用 technical_handoff
- 回調函數記錄：timeframe=daily, indicators=["RSI", "MACD"]
- 技術分析代理人進行專業分析
```

### 2. **基本面分析請求**
```
用戶輸入：評估 TSLA 的財務狀況，深度分析
系統處理：
- 分類代理人識別為基本面分析需求
- 調用 fundamental_handoff
- 輸入過濾器清理對話歷史
- 基本面分析代理人進行深度分析
```

### 3. **升級分析請求**
```
用戶輸入：我需要緊急分析 NVIDIA，有重要決策
系統處理：
- 分類代理人識別為緊急需求
- 調用 escalation_handoff
- 回調函數記錄緊急程度和原因
- 升級分析代理人提供高級建議
```

## 🚀 啟動系統

### 環境設定
```bash
# 安裝依賴
uv add openai-agents python-dotenv httpx chainlit pydantic

# 設定環境變數
echo "GEMINI_API_KEY=your_api_key_here" > .env
```

### 運行程式
```bash
# 基本版本
chainlit run stock_agent.py

# 進階版本
chainlit run advanced_stock_handoffs.py
```

## 🎯 最佳實踐

### 1. **數據模型設計**
- 使用 Pydantic 確保類型安全
- 提供合理的預設值
- 使用描述性的欄位名稱

### 2. **回調函數設計**
- 保持回調函數輕量級
- 避免長時間阻塞操作
- 適當的錯誤處理

### 3. **分類邏輯**
- 明確的分類規則
- 考慮邊界情況
- 提供回退機制

### 4. **工具命名**
- 使用描述性的工具名稱
- 提供清晰的工具描述
- 保持命名一致性

## 🔍 調試技巧

### 1. **啟用追蹤**
```python
from agents import set_tracing_disabled
set_tracing_disabled(disabled=False)  # 啟用追蹤
```

### 2. **日誌記錄**
```python
async def on_handoff(ctx, input_data):
    print(f"Handoff 被調用: {input_data}")
    # 記錄到文件或外部系統
```

### 3. **性能監控**
```python
import time

async def on_handoff(ctx, input_data):
    start_time = time.time()
    # 執行操作
    duration = time.time() - start_time
    print(f"Handoff 執行時間: {duration:.2f}秒")
```

## 📝 擴展建議

### 1. **添加更多專門代理人**
- 市場情緒分析
- 風險評估專家
- 投資組合優化

### 2. **集成外部 API**
- 股票數據 API
- 新聞 API
- 社交媒體 API

### 3. **添加緩存機制**
- 分析結果緩存
- 數據預處理緩存
- 用戶偏好緩存

### 4. **實現 A/B 測試**
- 不同分析策略
- 不同代理人組合
- 用戶反饋收集

## 🤝 貢獻指南

歡迎提交 Issue 和 Pull Request 來改善這個進階 handoff 系統！

## 📄 授權

本專案採用 MIT 授權條款。 