# Session Memory 教學

使用 OpenAI Agents SDK 的 Session Memory 保存對話歷史，並透過 Chainlit 建立聊天介面。

## 📚 學習目標

- 理解 Session Memory 的運作原理
- 使用 SQLiteSession 儲存對話
- 執行 Session 的各種操作
- 管理多個 Session
- 整合 Chainlit 建立聊天應用

## 🎯 什麼是 Session Memory？

Session Memory 自動維護對話歷史，讓 Agent 能夠記住之前的對話內容，無需手動管理。

### 運作流程

```
執行前：自動載入對話歷史
   ↓
執行中：Agent 處理（含歷史上下文）
   ↓
執行後：自動儲存新的對話
```

### 核心組件

| 組件 | 說明 |
|------|------|
| **Session** | 儲存對話歷史的介面 |
| **SQLiteSession** | SQLite 實作（輕量級） |
| **session_id** | 唯一識別對話的 ID |
| **db_path** | 資料庫路徑（`:memory:` 或檔案路徑） |

## 📦 安裝

```bash
# 安裝 agents SDK
pip install openai-agents

# 安裝 Chainlit
pip install chainlit
```

## 📋 範例說明

本章節包含 4 個範例 + Chainlit 整合：

### 範例 1: 基本的 Session Memory

展示 Session Memory 的基本使用方式。

**程式碼重點：**
```python
from agents import Agent, Runner, SQLiteSession

# 建立 Session
session = SQLiteSession("user_123")

# 第一輪對話
result = await Runner.run(
    agent,
    "金門大橋在哪個城市？",
    session=session
)

# 第二輪對話（自動載入歷史）
result = await Runner.run(
    agent,
    "那個城市在哪個州？",  # Agent 記得是舊金山
    session=session
)
```

**關鍵特性：**
- 自動載入對話歷史
- 自動儲存新對話
- 無需手動管理 `.to_input_list()`

### 範例 2: 持久化 Session

將對話儲存到檔案，重啟後仍可繼續。

**程式碼重點：**
```python
# 儲存到檔案
session = SQLiteSession(
    "user_123",
    "conversations.db"  # 持久化儲存
)

# 對話會保存在檔案中
result = await Runner.run(agent, "我的名字是小明", session=session)

# 之後可以繼續
result = await Runner.run(agent, "我的名字是什麼？", session=session)
```

**儲存選項：**
- `:memory:` - 記憶體模式（預設）
- `"file.db"` - 檔案模式（持久化）

### 範例 3: Session 操作

展示 Session 的各種操作方法。

**可用操作：**

**取得對話歷史：**
```python
# 取得所有項目
items = await session.get_items()

# 取得最近 N 筆
items = await session.get_items(limit=5)
```

**新增項目：**
```python
items = [
    {"role": "user", "content": "你好"},
    {"role": "assistant", "content": "您好！"}
]
await session.add_items(items)
```

**移除最後一筆：**
```python
last_item = await session.pop_item()
```

**清空 Session：**
```python
await session.clear_session()
```

### 範例 4: 多個 Session

不同使用者使用獨立的 Session。

**程式碼重點：**
```python
# 不同使用者的 Session
session_alice = SQLiteSession("user_alice", "users.db")
session_bob = SQLiteSession("user_bob", "users.db")

# Alice 的對話
await Runner.run(agent, "我住在台北", session=session_alice)

# Bob 的對話
await Runner.run(agent, "我住在台南", session=session_bob)

# 各自記住自己的內容
await Runner.run(agent, "我住在哪裡？", session=session_alice)  # 台北
await Runner.run(agent, "我住在哪裡？", session=session_bob)    # 台南
```

## 🎨 Chainlit 整合

### 啟動聊天介面

```bash
chainlit run main.py
```

### 實作說明

**1. 聊天開始時：**
```python
@cl.on_chat_start
async def on_chat_start():
    session_id = f"user_{id(cl.user_session)}"
    session = SQLiteSession(session_id, "chat_history.db")
    cl.user_session.set("agent_session", session)
```

**2. 收到訊息時：**
```python
@cl.on_message
async def on_message(message: cl.Message):
    session = cl.user_session.get("agent_session")
    
    result = await Runner.run(
        assistant,
        message.content,
        session=session
    )
    
    await cl.Message(content=result.final_output).send()
```

**3. 聊天結束時：**
```python
@cl.on_chat_end
async def on_chat_end():
    # 對話已自動儲存
    pass
```

### Chainlit 特性

- ✅ 自動管理 Session
- ✅ 持久化對話歷史
- ✅ 即時顯示訊息
- ✅ 簡潔的 UI 介面

## 🎯 Session 管理最佳實踐

### 1. Session ID 命名

使用有意義的 ID：

```python
# ✅ 好的命名
session = SQLiteSession("user_12345")
session = SQLiteSession("thread_abc123")
session = SQLiteSession("support_ticket_456")

# ❌ 不好的命名
session = SQLiteSession("123")
session = SQLiteSession("temp")
```

### 2. 選擇適當的儲存方式

```python
# 開發/測試：記憶體模式
session = SQLiteSession("dev_session")

# 生產環境：檔案模式
session = SQLiteSession("user_123", "production.db")
```

### 3. 管理 Session 生命週期

```python
# 使用完畢後清理
await session.clear_session()

# 或限制歷史長度
items = await session.get_items(limit=10)  # 只保留最近 10 筆
```

### 4. 錯誤處理

```python
try:
    result = await Runner.run(agent, message, session=session)
except Exception as e:
    print(f"錯誤: {e}")
    # 可以嘗試清空 session 重新開始
    await session.clear_session()
```

## 💡 進階用法

### 修正對話

使用 `pop_item` 撤銷錯誤的對話：

```python
# 使用者輸入錯誤
result = await Runner.run(agent, "2 + 2 是多少？", session=session)

# 撤銷
await session.pop_item()  # 移除 assistant 回應
await session.pop_item()  # 移除 user 問題

# 重新輸入
result = await Runner.run(agent, "2 + 3 是多少？", session=session)
```

### 手動管理對話

```python
# 取得歷史
items = await session.get_items()

# 手動新增
custom_items = [
    {"role": "user", "content": "自訂使用者訊息"},
    {"role": "assistant", "content": "自訂助手回應"}
]
await session.add_items(custom_items)
```

### Session 共享

不同 Agent 可以共享同一個 Session：

```python
support_agent = Agent(name="Support")
billing_agent = Agent(name="Billing")
session = SQLiteSession("user_123")

# 兩個 Agent 都能看到完整的對話歷史
await Runner.run(support_agent, "幫我查帳單", session=session)
await Runner.run(billing_agent, "顯示明細", session=session)
```

## ⚠️ 常見問題

**Q: Session 會自動過期嗎？**  
不會，SQLiteSession 不會自動過期。如需 TTL 功能，可使用 `EncryptedSession`。

**Q: 如何限制對話歷史長度？**  
```python
# 方法 1: 使用 limit
items = await session.get_items(limit=20)

# 方法 2: 定期清理舊資料
# 需要自行實作清理邏輯
```

**Q: 可以使用其他資料庫嗎？**  
可以，SDK 提供多種 Session 實作：
- `SQLiteSession` - SQLite（輕量級）
- `SQLAlchemySession` - 支援 PostgreSQL、MySQL 等
- `EncryptedSession` - 加密儲存
- `AdvancedSQLiteSession` - 進階功能（分支、分析）

**Q: Chainlit 的 Session 如何管理？**  
Chainlit 為每個連線自動建立 `cl.user_session`，可以在其中儲存 Agent Session。

**Q: 如何在 Chainlit 中顯示對話歷史？**  
```python
@cl.on_chat_start
async def on_chat_start():
    session = SQLiteSession("user_123", "history.db")
    
    # 取得歷史
    items = await session.get_items()
    for item in items:
        if item.get("role") == "user":
            await cl.Message(
                author="User",
                content=item.get("content")
            ).send()
```

## 🔗 相關資源

- [官方文件 - Sessions](https://openai.github.io/openai-agents-python/sessions/)
- [官方文件 - Memory API](https://openai.github.io/openai-agents-python/ref/memory/)
- [Chainlit 文件](https://docs.chainlit.io/)
- [SQLAlchemy Sessions](https://openai.github.io/openai-agents-python/sessions/sqlalchemy_session/)
- [Advanced SQLite Sessions](https://openai.github.io/openai-agents-python/sessions/advanced_sqlite_session/)

## 📝 練習

1. **基礎練習**：建立簡單的 Session，執行多輪對話
2. **持久化練習**：建立檔案儲存的 Session，重啟程式後繼續對話
3. **Chainlit 練習**：啟動 Chainlit 介面，測試對話記憶功能
4. **進階練習**：實作對話修正功能（pop_item）

---

**執行範例：**
```bash
# 執行命令列範例
python main.py

# 啟動 Chainlit 介面
chainlit run main.py
```

祝學習愉快！ 🚀
