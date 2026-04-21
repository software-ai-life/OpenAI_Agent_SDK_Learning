# Structured Output 教學

## 📚 什麼是 Structured Output（結構化輸出）？

想像一下，你問 AI：「請推薦一部電影給我」

### ❌ 非結構化輸出（一般回應）

AI 可能會這樣回答：

```
我推薦你看《星際效應》，這是一部2014年上映的科幻電影，
由克里斯多夫·諾蘭導演。電影講述一群探險家穿越蟲洞尋找新家園的故事。
主演包含馬修·麥康納和安·海瑟薇。我給它8.6分，
因為視覺效果震撼、劇情深度夠，而且父女情感線很感人。
```

**問題來了：**
- 😰 電影名稱在哪裡？需要自己找
- 😰 評分是多少？藏在文字中間
- 😰 導演是誰？要自己解析
- 😰 格式每次都不一樣，程式很難處理
- 😰 如果要存入資料庫，還要寫一堆程式碼來解析

### ✅ 結構化輸出（有組織的回應）

使用結構化輸出，AI 會這樣回答：

```json
{
  "title": "星際效應",
  "genre": "科幻",
  "year": 2014,
  "rating": 8.6,
  "director": "克里斯多夫·諾蘭",
  "cast": ["馬修·麥康納", "安·海瑟薇", "潔西卡·崔絲坦"],
  "plot_summary": "一群探險家利用穿越蟲洞來為人類尋找新家園...",
  "reasons": [
    "視覺效果震撼",
    "探討時間與空間的深度",
    "感人的父女情感線"
  ]
}
```

**優勢：**
- 😊 資料清楚分類，一目了然
- 😊 格式固定，程式容易處理
- 😊 可以直接存入資料庫
- 😊 可以做資料驗證（例如：評分必須在 0-10 之間）
- 😊 團隊合作時大家都知道資料長什麼樣子

---

## 🎯 為什麼要學 Structured Output？

### 1️⃣ **讓 AI 的回答更可靠**
不用擔心 AI 每次回答的格式都不一樣，程式能穩定運作。

### 2️⃣ **節省開發時間**
不需要寫複雜的文字解析程式碼，AI 直接給你整理好的資料。

### 3️⃣ **方便整合到系統**
結構化的資料可以直接：
- 存入資料庫
- 轉換成 Excel
- 在網頁上顯示
- 傳給其他程式使用

### 4️⃣ **資料品質有保證**
可以設定規則，例如：
- 年齡必須是數字
- 評分必須在 1-5 之間
- 電子郵件格式要正確

---

## 🎯 學習重點

1. ✅ 理解結構化與非結構化輸出的差異
2. ✅ 使用 Pydantic 定義資料結構（就像設計表格欄位）
3. ✅ 讓 AI Agent 按照你的格式輸出資料
4. ✅ 學會 5 個實用的應用場景

---

## 📋 本教學包含的範例

### 範例 1: 個人資訊提取 👤
**情境：** 從一段自我介紹中，自動提取姓名、年齡、職業、興趣等資訊

**為什麼有用？** 
- 自動整理履歷資料
- 建立通訊錄
- 客戶資料管理

**範例輸入：**
```
張小明今年28歲，是一位軟體工程師。
他平時喜歡打籃球、閱讀科技書籍和玩電動遊戲。
```

**結構化輸出：**
```json
{
  "name": "張小明",
  "age": 28,
  "occupation": "軟體工程師",
  "hobbies": ["打籃球", "閱讀科技書籍", "玩電動遊戲"],
  "email": null
}
```

### 範例 2: 書籍評論生成 📚
**情境：** 自動產生標準化的書評，包含評分、優缺點、推薦理由

**為什麼有用？**
- 建立讀書筆記系統
- 電商網站的商品評論
- 內容管理平台

### 範例 3: 食譜生成 🍳
**情境：** 產生完整的食譜，包含食材、步驟、時間

**為什麼有用？**
- 食譜網站
- 烹飪 App
- 營養管理系統

### 範例 4: 任務分析 📊
**情境：** 將大任務拆解成小任務，評估時間和風險

**為什麼有用？**
- 專案管理工具
- 工作排程系統
- 團隊協作平台

### 範例 5: 產品分析 💼
**情境：** 進行產品的 SWOT 分析（優勢、劣勢、機會、威脅）

**為什麼有用？**
- 商業決策支援
- 市場調查報告
- 產品企劃

---

## 🔧 如何定義資料結構？

### 概念：就像設計 Excel 表格

想像你要設計一個 Excel 表格來記錄個人資訊：

| 姓名 (文字) | 年齡 (數字) | 職業 (文字) | 興趣 (清單) |
|-----------|-----------|-----------|-----------|
| 張小明    | 28        | 工程師    | 籃球, 閱讀 |

在程式中，我們用 **Pydantic** 來定義這個結構：

```python
from pydantic import BaseModel, Field
from typing import List, Optional

class PersonInfo(BaseModel):
    name: str = Field(description="人物姓名")
    age: int = Field(description="年齡")
    occupation: str = Field(description="職業")
    hobbies: List[str] = Field(description="興趣愛好列表")
    email: Optional[str] = Field(default=None, description="電子郵件（選填）")
```

**解釋：**
- `name: str` = 姓名是文字（字串）
- `age: int` = 年齡是整數
- `hobbies: List[str]` = 興趣是文字的清單（可以有多個）
- `Optional[str]` = 這個欄位可以不填
- `Field(description=...)` = 告訴 AI 這個欄位是什麼意思

### 加入資料驗證規則

你也可以設定規則，確保資料的正確性：

```python
class BookReview(BaseModel):
    title: str = Field(description="書名", min_length=1, max_length=100)
    rating: int = Field(description="評分", ge=1, le=5)  # 必須在 1-5 之間
    price: float = Field(description="價格", gt=0)  # 必須大於 0
```

**規則說明：**
- `min_length=1, max_length=100` = 書名長度必須在 1-100 字之間
- `ge=1, le=5` = greater or equal 1, less or equal 5（1-5 之間）
- `gt=0` = greater than 0（大於 0）

---

## 🚀 快速開始（三步驟）

### 步驟 1: 安裝相依套件

```bash
pip install openai-agents pydantic python-dotenv httpx openai
```

### 步驟 2: 設定 API 金鑰

建立 `.env` 檔案，填入你的 Gemini API 金鑰：

```env
GEMINI_API_KEY=你的API金鑰
```

💡 **如何取得 API 金鑰？**
前往 [Google AI Studio](https://makersuite.google.com/app/apikey) 免費申請

### 步驟 3: 執行範例

```bash
# 執行完整教學（5個範例）
python main.py
```

---

## 💡 核心觀念：如何讓 AI 產生結構化輸出？

### 完整流程示範

```python
import asyncio
from pydantic import BaseModel, Field
from typing import List
from agents import Agent, Runner, OpenAIChatCompletionsModel

# 1️⃣ 定義你想要的資料結構
class MovieRecommendation(BaseModel):
    title: str = Field(description="電影名稱")
    year: int = Field(description="上映年份")
    rating: float = Field(description="評分 0-10", ge=0, le=10)
    reasons: List[str] = Field(description="推薦理由")

# 2️⃣ 建立 AI Agent
agent = Agent(
    name="MovieExpert",
    instructions="你是專業的電影推薦專家，請根據用戶需求推薦電影。",
    model=model  # 使用 Gemini 或其他模型
)

# 3️⃣ 執行並要求結構化輸出
async def get_movie_recommendation():
    result = await Runner.run(
        agent,
        f"推薦一部科幻電影，請以 JSON 格式輸出：\n{MovieRecommendation.model_json_schema()}"
    )
    print(result.final_output)

# 4️⃣ 執行
asyncio.run(get_movie_recommendation())
```

**輸出結果：**
```json
{
  "title": "星際效應",
  "year": 2014,
  "rating": 8.6,
  "reasons": [
    "視覺效果震撼",
    "科學理論深度探討",
    "情感層面豐富"
  ]
}
```

### 重點說明

1. **定義結構** = 告訴 AI 你想要什麼欄位
2. **model_json_schema()** = 把結構轉換成 AI 能理解的格式
3. **AI 自動填寫** = AI 會按照你的結構回答
4. **取得結果** = 拿到整理好的 JSON 資料

---

## 🎓 實際應用場景（你可以做什麼？）

### 1. 📝 自動化表單填寫
**情境：** 客戶傳來一封詢價信
```
您好，我是 ABC 公司的採購經理王大明，
我們想採購 100 台筆記型電腦，請報價。
聯絡電話：02-12345678，Email: wang@abc.com
```

**結構化後：**
```json
{
  "company": "ABC 公司",
  "contact_person": "王大明",
  "position": "採購經理",
  "product": "筆記型電腦",
  "quantity": 100,
  "phone": "02-12345678",
  "email": "wang@abc.com"
}
```
→ 直接存入 CRM 系統，不用人工輸入！

### 2. 🍱 智能點餐系統
**情境：** 客人說「我要一個大杯珍奶，半糖少冰，加珍珠」

**結構化後：**
```json
{
  "drink": "珍珠奶茶",
  "size": "大杯",
  "sugar_level": "半糖",
  "ice_level": "少冰",
  "toppings": ["珍珠"]
}
```
→ 廚房系統直接收到訂單細節！

### 3. 📊 會議記錄整理
**情境：** 會議錄音轉文字後，自動提取重點

**結構化後：**
```json
{
  "meeting_date": "2025-11-07",
  "attendees": ["張經理", "李工程師", "王設計師"],
  "topics": ["產品改版計畫", "行銷策略", "預算分配"],
  "action_items": [
    {"task": "完成設計稿", "assignee": "王設計師", "deadline": "2025-11-15"},
    {"task": "撰寫技術文件", "assignee": "李工程師", "deadline": "2025-11-20"}
  ]
}
```
→ 待辦事項自動進入專案管理系統！

### 4. 🏥 健康記錄追蹤
**情境：** 「今天早餐吃了三明治和咖啡，中午吃牛肉麵，晚上跑步 30 分鐘」

**結構化後：**
```json
{
  "date": "2025-11-07",
  "meals": [
    {"time": "早餐", "items": ["三明治", "咖啡"]},
    {"time": "中餐", "items": ["牛肉麵"]}
  ],
  "exercise": [
    {"activity": "跑步", "duration": 30, "unit": "分鐘"}
  ]
}
```
→ 健康 App 自動記錄，還能計算卡路里！

---

## 📊 更多輸出範例

### 範例：個人資訊
```json
{
  "name": "張小明",
  "age": 28,
  "occupation": "軟體工程師",
  "hobbies": ["打籃球", "閱讀", "玩遊戲"],
  "email": "xiaoming.zhang@example.com"
}
```

### 範例：書籍評論
```json
{
  "title": "Python 程式設計入門",
  "author": "作者名稱",
  "rating": 4,
  "summary": "適合初學者的 Python 教材，循序漸進的教學方式。",
  "pros": ["內容清晰", "範例豐富", "適合初學者"],
  "cons": ["部分內容較舊", "缺少進階主題"],
  "recommendation": "推薦給想學 Python 的初學者"
}
```

### 範例：食譜
```json
{
  "name": "蒜香奶油蝦",
  "cuisine": "西式",
  "difficulty": "簡單",
  "prep_time": 10,
  "cook_time": 15,
  "servings": 2,
  "ingredients": [
    "草蝦 300g",
    "蒜頭 5瓣",
    "奶油 30g",
    "白酒 2大匙",
    "鹽、胡椒 適量"
  ],
  "steps": [
    "草蝦去殼去腸泥，洗淨瀝乾",
    "蒜頭切末",
    "平底鍋加熱，放入奶油融化",
    "加入蒜末爆香",
    "放入草蝦，煎至兩面金黃",
    "加入白酒、鹽、胡椒調味",
    "收汁即可起鍋"
  ],
  "tips": ["蝦子不要煎太久，會變老", "可以加入巴西里增添香氣"]
}
```

## 💬 總結

**Structured Output 的核心價值：**

1. 🎯 **讓 AI 回答更可靠** - 格式固定，不會每次都不一樣
2. ⚡ **加速開發流程** - 不用寫複雜的文字解析程式碼
3. 🔒 **資料品質保證** - 可以驗證資料是否符合規則
4. 🚀 **方便整合系統** - 直接存入資料庫或傳給其他程式

**記住：**
- 非結構化輸出 = 像是一封信（需要自己讀懂、整理）
- 結構化輸出 = 像是填好的表格（清楚明瞭、容易使用）
