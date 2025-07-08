import asyncio
import os
import httpx
from agents import Agent, Runner
from openai import AsyncOpenAI
from openai.types import Model
import requests
import json
from dotenv import load_dotenv

from agents import (
    Agent,
    Model,
    ModelProvider,
    OpenAIChatCompletionsModel,
    RunConfig,
    Runner,
    function_tool,
    set_tracing_disabled,
)

# Load the environment variables from the .env file
load_dotenv()

# Get configuration from environment variables
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
BASE_URL = os.getenv("BASE_URL", "https://openrouter.ai/api/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "qwen/qwen3-30b-a3b:free")


## trobleshooting

# [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: self-signed certificate in certificate chain
# openai.APIConnectionError: Connection error.

# response = requests.post(
#   url=f"{BASE_URL}/chat/completions",
#   headers={
#     "Authorization": f"Bearer {OPENROUTER_API_KEY}",
#   },
#   data=json.dumps({
#     "model": MODEL_NAME,
#     "messages": [
#       {
#         "role": "user",
#         "content": "What is the meaning of life?"
#       }
#     ]
#   }),
#   verify=False  # 繞過 SSL 驗證
# )

# print(response.json())


if not BASE_URL or not OPENROUTER_API_KEY or not MODEL_NAME:
    raise ValueError(
        "Please set EXAMPLE_BASE_URL, EXAMPLE_API_KEY, EXAMPLE_MODEL_NAME via env var or code."
    )

# 創建一個繞過 SSL 驗證的 HTTP 客戶端
http_client = httpx.AsyncClient(verify=False)

client = AsyncOpenAI(
    base_url=BASE_URL, 
    api_key=OPENROUTER_API_KEY,
    http_client=http_client
)
set_tracing_disabled(disabled=True)


async def main():
    # This agent will use the custom LLM provider
    agent = Agent(
        name="Assistant",
        instructions="You only respond in haikus.",
        model=OpenAIChatCompletionsModel(model=MODEL_NAME, openai_client=client),
    )

    result = await Runner.run(
        agent,
        "Tell me about recursion in programming.",
    )
    print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())