# Code Review AI Agent System

這是一個基於 OpenAI Agents 框架建構的程式碼審查系統，採用多代理人協作的架構，提供全面的程式碼審查服務。

## 🏗️ 系統架構

### 專門代理人
1. **語法檢查代理人** (`syntax_checker_agent`)
   - 檢查語法錯誤、編譯錯誤
   - 檢查缺少的導入語句
   - 型別錯誤檢查
   - 變數未定義問題

2. **性能檢查代理人** (`performance_checker_agent`)
   - 時間複雜度分析
   - 空間複雜度分析
   - 不必要的迴圈檢查
   - 記憶體洩漏風險評估
   - 演算法效率建議

3. **安全檢查代理人** (`security_checker_agent`)
   - SQL 注入漏洞檢查
   - XSS 跨站腳本攻擊風險
   - 身份驗證和授權問題
   - 敏感資料暴露檢查
   - 輸入驗證檢查

4. **代碼風格檢查代理人** (`style_checker_agent`)
   - 命名慣例檢查
   - 程式碼格式和縮排
   - 函數和類別設計原則
   - 程式碼註解和文檔
   - 可讀性和可維護性

### 統籌代理人
**程式碼審查協調員** (`orchestrator_agent`)
- 協調所有專門代理人
- 按順序執行完整的審查流程
- 總結所有檢查結果
- 提供優先級排序的改進建議

## 🚀 快速開始

### 環境需求
- Python 3.8+
- OpenAI Agents 框架
- Gemini API 金鑰

### 安裝依賴
```bash
uv add openai-agents python-dotenv httpx
```

### 環境設定
創建 `.env` 檔案並設定：
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

### 運行程式
```bash
python code_review_agent.py
```

## 💻 使用方法

### 基本使用流程

1. **啟動程式**
   ```bash
   python code_review_agent.py
   ```

2. **輸入程式碼**
   - 貼上您要審查的程式碼
   - 輸入 `END` 結束程式碼輸入
   - 輸入 `exit` 退出程式

3. **查看審查報告**
   - 系統會自動進行四個層面的檢查
   - 輸出完整的審查報告和建議

### 範例互動

```
=== 程式碼審查 AI Agent ===
請貼上您要審查的程式碼，或輸入 'exit' 結束程式

==================================================
請輸入您的程式碼（可以多行輸入，輸入 'END' 結束）：
def calculate_sum(numbers):
    total = 0
    for i in range(len(numbers)):
        total += numbers[i]
    return total
END

🔍 開始進行程式碼審查...

📋 程式碼審查報告：
============================================================
[詳細的審查報告將顯示在這裡]
============================================================
```

## 🔧 自訂設定

### 修改代理人指令
您可以在 `code_review_agent.py` 中修改各個代理人的 `instructions` 參數：

```python
syntax_checker_agent = Agent(
    name="syntax_checker_agent",
    instructions="您的自訂指令...",
    handoff_description="代理人描述",
    model=model
)
```

### 添加新的檢查類型
1. 創建新的專門代理人
2. 將其添加到統籌代理人的 `tools` 列表中

```python
# 新的代理人
new_checker_agent = Agent(
    name="new_checker_agent",
    instructions="新檢查器的指令...",
    handoff_description="新檢查器的描述",
    model=model
)

# 添加到統籌代理人
orchestrator_agent = Agent(
    # ... 其他配置
    tools=[
        # ... 現有工具
        new_checker_agent.as_tool(
            tool_name="new_check",
            tool_description="新檢查功能的描述",
        ),
    ],
    model=model
)
```

## 🎯 最佳實踐

### 程式碼輸入建議
- 提供完整的函數或類別定義
- 包含相關的導入語句
- 確保程式碼片段有足夠的上下文

### 審查結果使用
- 按照優先級處理建議
- 重點關注安全漏洞和語法錯誤
- 考慮性能優化建議的實施成本
- 逐步改善程式碼風格

## 🚨 注意事項

1. **API 限制**：請注意 Gemini API 的使用限制和費用
2. **程式碼隱私**：敏感程式碼請在本地環境使用
3. **結果參考**：AI 審查結果僅供參考，仍需人工判斷
4. **大型檔案**：對於大型程式碼檔案，建議分段審查

## 🔍 範例程式碼審查

### 輸入範例
```python
import requests

def get_user_data(user_id):
    url = f"https://api.example.com/users/{user_id}"
    response = requests.get(url)
    return response.json()

users = []
for i in range(1, 1000):
    user = get_user_data(i)
    users.append(user)
```

### 可能的審查結果
- **語法檢查**：未發現語法錯誤
- **性能問題**：循環中的 HTTP 請求會造成性能瓶頸
- **安全問題**：缺少錯誤處理和輸入驗證
- **風格建議**：考慮使用批量 API 調用

## 📝 待辦功能

- [ ] 支援多種程式語言
- [ ] 集成靜態分析工具
- [ ] 支援檔案上傳
- [ ] 生成詳細的修正建議
- [ ] 支援團隊協作審查

## 🤝 貢獻指南

歡迎提交 Issue 和 Pull Request 來改善這個程式碼審查系統！