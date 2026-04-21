"""
Voice Agent 範例 - OpenAI Agents SDK

展示如何使用 Voice Pipeline 建立語音互動的 Agent。
"""

import os
import asyncio
import random
import httpx
from dotenv import load_dotenv

from agents import (
    Agent,
    AsyncOpenAI,
    OpenAIChatCompletionsModel,
    function_tool,
)

# Voice 功能需要額外安裝：pip install "openai-agents[voice]"

from agents.voice import (
    AudioInput,
    SingleAgentVoiceWorkflow,
    VoicePipeline,
)
import numpy as np
import sounddevice as sd
VOICE_AVAILABLE = True

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
            verify=False,
            limits=httpx.Limits(
                max_connections=1000,
                max_keepalive_connections=100
            )
        )
    ),
)


# ============= 範例 1: 基本的 Voice Agent =============

print("=" * 60)
print("範例 1: 基本的 Voice Agent")
print("=" * 60)


@function_tool
def get_weather(city: str) -> str:
    """取得城市的天氣資訊"""
    print(f"[debug] get_weather called with city: {city}")
    choices = ["晴天", "多雲", "下雨", "下雪"]
    return f"{city} 的天氣是 {random.choice(choices)}"


@function_tool
def get_temperature(city: str) -> str:
    """取得城市的溫度"""
    print(f"[debug] get_temperature called with city: {city}")
    temp = random.randint(10, 35)
    return f"{city} 目前的溫度是 {temp}°C"


# 建立基本的天氣 Agent
weather_agent = Agent(
    name="WeatherAssistant",
    instructions="你是天氣助手。與使用者對話時要有禮貌且簡潔。",
    model=model,
    tools=[get_weather, get_temperature],
)


async def example1_basic_voice_agent():
    """範例 1: 基本的 Voice Agent"""
    
    if not VOICE_AVAILABLE:
        print("⚠️  Voice 功能未安裝，跳過此範例")
        return
    
    try:
        print("\n建立 Voice Pipeline...")
        workflow = SingleAgentVoiceWorkflow(weather_agent)
        pipeline = VoicePipeline(workflow=workflow)
        
        # 準備 3 秒的靜音音訊作為輸入
        buffer = np.zeros(24000 * 3, dtype=np.int16)
        audio_input = AudioInput(buffer=buffer)
        
        print("執行 Pipeline...")
        print("注意：由於使用 Gemini API，STT/TTS 可能不支援")
        
        # 實際執行需要 OpenAI API
        result = await pipeline.run(audio_input)
        player = sd.OutputStream(samplerate=24000, channels=1, dtype=np.int16)
        player.start()
        async for event in result.stream():
            if event.type == "voice_stream_event_audio":
                player.write(event.data)
        
        print("✅ Pipeline 設定完成（實際執行需要 OpenAI API）")
        
    except Exception as e:
        print(f"❌ 錯誤: {e}")


# ============= 範例 2: Multi-Agent with Handoff =============

print("\n\n" + "=" * 60)
print("範例 2: Multi-Agent 系統（含 Handoff）")
print("=" * 60)


@function_tool
def translate_to_spanish(text: str) -> str:
    """翻譯成西班牙文"""
    print(f"[debug] translate_to_spanish called with: {text}")
    return f"[西班牙文] {text}"


@function_tool
def translate_to_chinese(text: str) -> str:
    """翻譯成中文"""
    print(f"[debug] translate_to_chinese called with: {text}")
    return f"[中文] {text}"


# 建立西班牙文 Agent
spanish_agent = Agent(
    name="SpanishAgent",
    instructions="你是西班牙文專家。與使用者對話時使用西班牙文，保持禮貌和簡潔。",
    model=model,
    tools=[translate_to_spanish],
)

# 建立中文 Agent
chinese_agent = Agent(
    name="ChineseAgent",
    instructions="你是中文專家。與使用者對話時使用繁體中文，保持禮貌和簡潔。",
    model=model,
    tools=[translate_to_chinese],
)

# 建立主要的分流 Agent
triage_agent = Agent(
    name="TriageAgent",
    instructions="""你是語言分流助手。根據使用者的語言需求轉交給適當的 Agent。
    保持禮貌和簡潔。""",
    model=model,
    handoffs=[spanish_agent, chinese_agent],
    tools=[get_weather],
)


async def example2_multi_agent_voice():
    """範例 2: Multi-Agent Voice 系統"""
    
    if not VOICE_AVAILABLE:
        print("⚠️  Voice 功能未安裝，跳過此範例")
        return
    
    try:
        print("\n建立 Multi-Agent Voice Pipeline...")
        workflow = SingleAgentVoiceWorkflow(triage_agent)
        pipeline = VoicePipeline(workflow=workflow)
        
        buffer = np.zeros(24000 * 3, dtype=np.int16)
        audio_input = AudioInput(buffer=buffer)
        
        print("✅ Multi-Agent Pipeline 設定完成")
        print(f"   主要 Agent: {triage_agent.name}")
        print(f"   可轉交: {[a.name for a in triage_agent.handoffs]}")
        
    except Exception as e:
        print(f"❌ 錯誤: {e}")


# ============= 範例 3: 使用麥克風錄音 =============

print("\n\n" + "=" * 60)
print("範例 3: 使用麥克風錄音")
print("=" * 60)


async def example3_microphone_input():
    """範例 3: 使用麥克風錄音"""
    
    if not VOICE_AVAILABLE:
        print("⚠️  Voice 功能未安裝，跳過此範例")
        return
    
    try:
        print("\n錄音 3 秒...")
        duration = 3
        sample_rate = 24000
        
        recording = sd.rec(
            int(duration * sample_rate),
            samplerate=sample_rate,
            channels=1,
            dtype=np.int16
        )
        sd.wait()
        
        print("✅ 錄音完成")
        
        audio_input = AudioInput(buffer=recording.flatten())
        print(f"   音訊長度: {len(recording.flatten())} 樣本")
        print(f"   時長: {duration} 秒")
        
        # 可以將這個 audio_input 傳給 pipeline.run()
        
    except Exception as e:
        print(f"❌ 錯誤: {e}")


# ============= 範例 4: 完整的 Voice Pipeline =============

print("\n\n" + "=" * 60)
print("範例 4: 完整的 Voice Pipeline")
print("=" * 60)


async def example4_complete_pipeline():
    """範例 4: 完整的 Voice Pipeline（需要 OpenAI API）"""
    
    if not VOICE_AVAILABLE:
        print("⚠️  Voice 功能未安裝，跳過此範例")
        return
    
    try:
        print("\n建立完整的 Voice Pipeline...")
        
        # 建立 Pipeline
        workflow = SingleAgentVoiceWorkflow(weather_agent)
        pipeline = VoicePipeline(workflow=workflow)
        
        # 準備音訊輸入
        buffer = np.zeros(24000 * 3, dtype=np.int16)
        audio_input = AudioInput(buffer=buffer)
        
        print("執行 Pipeline...")
        print("注意：實際執行需要 OpenAI API 的 STT/TTS")
        
        # 實際執行（需要 OpenAI API）
        # result = await pipeline.run(audio_input)
        # 
        # # 設定音訊播放器
        # player = sd.OutputStream(
        #     samplerate=24000,
        #     channels=1,
        #     dtype=np.int16
        # )
        # player.start()
        # 
        # # 串流播放
        # async for event in result.stream():
        #     if event.type == "voice_stream_event_audio":
        #         player.write(event.data)
        # 
        # player.stop()
        # player.close()
        
        print("✅ Pipeline 設定完成（Gemini API 不支援完整的 Voice 功能）")
        
    except Exception as e:
        print(f"❌ 錯誤: {e}")



# ============= 主程式 =============

async def main():
    """執行所有範例"""
    
    print("\n🎙️ Voice Agent 範例")
    print("=" * 60)
    
    if not VOICE_AVAILABLE:
        print("\n⚠️  Voice 功能未安裝")
        print("請執行: pip install \"openai-agents[voice]\"")
        print()
    
    # 範例 1: 基本的 Voice Agent
    await example1_basic_voice_agent()
    
    # 範例 2: Multi-Agent Voice 系統
    await example2_multi_agent_voice()
    
    # 範例 3: 使用麥克風錄音
    await example3_microphone_input()
    
    # 範例 4: 完整的 Voice Pipeline
    await example4_complete_pipeline()
    
    print("\n" + "=" * 60)
    print("✅ 所有範例執行完成")
    print("=" * 60)
    print("\n⚠️  重要：Voice Pipeline 需要 OpenAI API 的 STT/TTS")
    print("   Gemini API 不支援完整的 Voice 功能")


if __name__ == "__main__":
    asyncio.run(main())
