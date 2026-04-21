# Voice Agent 教學

使用 OpenAI Agents SDK 的 Voice Pipeline 建立支援語音互動的 Agent。

## 📚 學習目標

- 理解 Voice Pipeline 的三步驟流程（STT → Agent → TTS）
- 建立支援語音的 Agent
- 處理音訊輸入和輸出
- 整合 Multi-Agent 和 Handoff
- 使用麥克風錄音作為輸入

## 🎯 什麼是 Voice Agent？

Voice Agent 透過 **VoicePipeline** 實現語音互動，包含三個步驟：

```
🎤 音訊輸入
   ↓
📝 語音轉文字 (STT - Speech-to-Text)
   ↓
🤖 Agent 處理
   ↓
🔊 文字轉語音 (TTS - Text-to-Speech)
   ↓
🎧 音訊輸出
```

### 核心組件

| 組件 | 說明 |
|------|------|
| **VoicePipeline** | 管理完整的語音處理流程 |
| **AudioInput** | 封裝輸入的音訊資料（numpy array） |
| **SingleAgentVoiceWorkflow** | 單一 Agent 的工作流 |
| **VoiceStreamEvent** | 串流輸出音訊事件 |

## 📦 安裝

```bash
pip install "openai-agents[voice]"
```

這會安裝：
- `numpy` - 音訊資料處理
- `sounddevice` - 音訊錄音和播放
- 其他相關套件

## � 範例說明

本章節包含 4 個實際可執行的範例：

### 範例 1: 基本的 Voice Agent

建立包含工具的天氣助手 Agent，並設定 Voice Pipeline。

**程式碼重點：**
```python
# 建立 Agent
weather_agent = Agent(
    name="WeatherAssistant",
    instructions="你是天氣助手。與使用者對話時要有禮貌且簡潔。",
    tools=[get_weather, get_temperature],
)

# 建立 Voice Pipeline
workflow = SingleAgentVoiceWorkflow(weather_agent)
pipeline = VoicePipeline(workflow=workflow)

# 準備音訊輸入（3 秒靜音）
buffer = np.zeros(24000 * 3, dtype=np.int16)
audio_input = AudioInput(buffer=buffer)

# 執行並播放
result = await pipeline.run(audio_input)
player = sd.OutputStream(samplerate=24000, channels=1, dtype=np.int16)
player.start()
async for event in result.stream():
    if event.type == "voice_stream_event_audio":
        player.write(event.data)
```

### 範例 2: Multi-Agent Voice 系統

建立支援多語言的分流系統，包含 Handoff 機制。

**系統架構：**
```
TriageAgent (分流)
  ├─→ SpanishAgent (西班牙文)
  └─→ ChineseAgent (中文)
```

**程式碼重點：**
```python
# 建立專門的 Agent
spanish_agent = Agent(name="SpanishAgent", ...)
chinese_agent = Agent(name="ChineseAgent", ...)

# 建立分流 Agent
triage_agent = Agent(
    name="TriageAgent",
    handoffs=[spanish_agent, chinese_agent],
    tools=[get_weather],
)

# 使用 Triage Agent 建立 Pipeline
workflow = SingleAgentVoiceWorkflow(triage_agent)
pipeline = VoicePipeline(workflow=workflow)
```

### 範例 3: 使用麥克風錄音

使用 `sounddevice` 錄製麥克風音訊作為 Pipeline 輸入。

**程式碼重點：**
```python
# 錄音 3 秒
duration = 3
sample_rate = 24000

recording = sd.rec(
    int(duration * sample_rate),
    samplerate=sample_rate,
    channels=1,
    dtype=np.int16
)
sd.wait()

# 轉換為 AudioInput
audio_input = AudioInput(buffer=recording.flatten())
```

**適用場景：**
- 即時語音對話
- 語音指令系統
- 互動式應用

### 範例 4: 完整的 Voice Pipeline

展示完整的 Voice Pipeline 流程，包含錯誤處理。

**程式碼重點：**
```python
# 建立 Pipeline
workflow = SingleAgentVoiceWorkflow(weather_agent)
pipeline = VoicePipeline(workflow=workflow)

# 執行（需要 OpenAI API）
result = await pipeline.run(audio_input)

# 設定播放器
player = sd.OutputStream(
    samplerate=24000,
    channels=1,
    dtype=np.int16
)
player.start()

# 串流播放
async for event in result.stream():
    if event.type == "voice_stream_event_audio":
        player.write(event.data)

player.stop()
player.close()
```

## 🎵 音訊格式規格

Voice Pipeline 使用的音訊格式：

| 項目 | 規格 |
|------|------|
| 採樣率 | 24000 Hz (24 kHz) |
| 位元深度 | 16-bit |
| 聲道 | 單聲道 (mono) |
| 格式 | PCM |
| 資料型別 | numpy.int16 |

**計算音訊長度：**
```python
duration_seconds = 3
sample_rate = 24000
buffer_size = sample_rate * duration_seconds  # 72000 樣本
buffer = np.zeros(buffer_size, dtype=np.int16)
```

## 🎯 Voice Pipeline 流程

### 三步驟處理

**步驟 1: 語音轉文字 (STT)**
- 使用 OpenAI Whisper 模型
- 將音訊轉成文字

**步驟 2: Agent 處理**
- Agent 接收文字輸入
- 執行工具、處理 Handoff
- 產生文字回應

**步驟 3: 文字轉語音 (TTS)**
- 使用 OpenAI TTS 模型
- 將回應轉成語音

### 建立和執行

```python
# 1. 建立 Workflow
workflow = SingleAgentVoiceWorkflow(agent)

# 2. 建立 Pipeline
pipeline = VoicePipeline(workflow=workflow)

# 3. 準備輸入
audio_input = AudioInput(buffer=your_audio_buffer)

# 4. 執行
result = await pipeline.run(audio_input)

# 5. 處理輸出
async for event in result.stream():
    if event.type == "voice_stream_event_audio":
        # 播放音訊
        player.write(event.data)
```

## 🎯 實際應用場景

### 1. 客服系統
- 自動接聽電話
- 問題分類和轉接
- 多語言支援

### 2. 智慧家居
- 語音控制家電
- 場景設定
- 資訊查詢

### 3. 車載助手
- 導航指引
- 免持通話
- 音樂控制

### 4. 無障礙工具
- 視障輔助
- 聽障輔助
- 操作簡化

## 🔗 相關資源

- [官方文件 - Voice Quickstart](https://openai.github.io/openai-agents-python/voice/quickstart/)
- [官方範例 - voice/static](https://github.com/openai/openai-agents-python/tree/main/examples/voice/static)
- [OpenAI Realtime API](https://openai.github.io/openai-agents-python/realtime/quickstart/)
- [Handoff 機制](../1.6_handoff/)
- [sounddevice 文件](https://python-sounddevice.readthedocs.io/)
