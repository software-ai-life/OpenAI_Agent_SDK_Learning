import os
import asyncio
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel, set_default_openai_client, set_tracing_disabled
from agents.run import RunConfig
from dotenv import load_dotenv
import httpx
from embedding_and_db import answer_from_knowledge_base

# 載入環境變數
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = "gemini-1.5-flash"

if not API_KEY:
    raise ValueError("GEMINI_API_KEY is not set. Please ensure it is defined in your .env file.")

http_client = httpx.AsyncClient(verify=False)

external_client = AsyncOpenAI(
    api_key=API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    http_client=http_client
)
set_default_openai_client(external_client)


model = OpenAIChatCompletionsModel(
    model=MODEL_NAME,
    openai_client=external_client
)

config = RunConfig(
    model=model,
    model_provider=external_client,
    tracing_disabled=True
)


# Create an agent that can use the knowledge base tool
# Use OpenAIChatCompletionsModel with the external_client
qa_agent = Agent(
    name="QA Agent",
    instructions="You are a helpful assistant. If the user asks a question, use your tools to find information in the knowledge base and answer with that information.",
    tools=[answer_from_knowledge_base],
    # Use OpenAIChatCompletionsModel with the pre-configured external_client
    model=model
)


async def main():
    agent_question = "Which domestic animal was originally bred from wolves? what do you know about Apollo?"

    # Run the agent
    result = await Runner.run(qa_agent, agent_question)

    # Extract and print the final answer
    print("Agent result:", result)
    print("Agent's answer:", result.final_output)

if __name__ == "__main__":
    asyncio.run(main())