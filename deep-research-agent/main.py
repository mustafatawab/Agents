from agents import Agent, Runner, AsyncOpenAI , OpenAIChatCompletionsModel, function_tool
from agents.run import RunConfig
from dotenv import load_dotenv, find_dotenv
import os
import asyncio
from openai.types.responses import ResponseTextDeltaEvent
from tavily import TavilyClient

_: bool = load_dotenv()

gemini_api_key = os.environ.get("GEMINI_API_KEY")
tavily_api_key = os.environ.get("TAVILY_API_KEY")

if not gemini_api_key:
    raise ValueError("Please set the  gemini api key")


if not  tavily_api_key:
    raise ValueError("Please set the tavily  api key")

tavily_client = TavilyClient(tavily_api_key)
client: AsyncOpenAI = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url='https://generativelanguage.googleapis.com/v1beta/openai/'
)


model: OpenAIChatCompletionsModel = OpenAIChatCompletionsModel(
    openai_client=client,
    model='gemini-2.0-flash'
)

config: RunConfig = RunConfig(
    model=model,
    model_provider=client,
    tracing_disabled=True
)

async def run_agent():
    agent: Agent = Agent(
        name='General Assitant',
        instructions='You are general assitant'
    )

    response: Runner =  Runner.run_streamed(
        agent,
        "Hi",
        run_config=config
    )

    # print(response)
    async for event in response.stream_events():
        if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
            print(event.data.delta , end="" , flush=True)


asyncio.run(run_agent())

    