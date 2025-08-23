from agents import Agent, Runner, AsyncOpenAI , OpenAIChatCompletionsModel, function_tool, RunContextWrapper,handoff
from agents.run import RunConfig
from dotenv import load_dotenv, find_dotenv
import os
import asyncio
from openai.types.responses import ResponseTextDeltaEvent
from tavily import TavilyClient, AsyncTavilyClient
from pydantic import BaseModel
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX

_: bool = load_dotenv()

gemini_api_key = os.environ.get("GEMINI_API_KEY")
tavily_api_key = os.environ.get("TAVILY_API_KEY")

if not gemini_api_key:
    raise ValueError("Please set the  gemini api key")


if not  tavily_api_key:
    raise ValueError("Please set the tavily  api key")

tavily_client = AsyncTavilyClient(tavily_api_key)

async def is_search_allowed(wrapper: RunContextWrapper, agent: Agent) -> bool:
    return True

@function_tool(name_override='web_search' , description_override='Search the web and google', is_enabled=is_search_allowed)
async def web_search(query: str) -> str:
    """Web Search and Google Search"""
    print(f"--- Web search tool ---- \n" )
    response = await tavily_client.search(query=query)
    # print(response)
    return response


@function_tool
async def extract_url(url : list):
    print("[EXTRACT URL TOOL]")
    response = await tavily_client.extract(url)
    return response

class EscilationData(BaseModel):
    topic: str
    reason: str

def on_planning(wrapper: RunContextWrapper, input: EscilationData):
    print("\n On Planning Agent Handoffs \n Input" , input)

def on_search(wrapper: RunContextWrapper , input: EscilationData):
    print("\n On Search Agent Handoffs \n Input" , input)


def on_parallel_search(wrapper: RunContextWrapper , input: EscilationData):
    print("\n On Parallel Search Agent Handoffs \n Input" , input)



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
    tracing_disabled=False
)

parallel_search_agent: Agent = Agent(
    name='parallel_search_agent',
    instructions=f''' {RECOMMENDED_PROMPT_PREFIX}
    You will search the user query deeply over the internet atleast 3 times.''',
    tools=[web_search, extract_url]
)

search_agent: Agent = Agent(
    name='search_agent',
    instructions=f''' {RECOMMENDED_PROMPT_PREFIX}
    you can search over the internet. You will pass the response to parallel_search_agent
    ''',
    tools=[ web_search , extract_url],
    handoffs=[
        handoff(agent=parallel_search_agent , on_handoff=on_parallel_search , input_type=EscilationData)
    ]    

)

planning_agent: Agent = Agent(
    name="planning_agent",
    instructions=f'''  {RECOMMENDED_PROMPT_PREFIX}
    You are planning agent who will break the user query into parts and then transfer to other agents
    ''',
    handoffs=[
        handoff(agent=search_agent, on_handoff=on_search, input_type=EscilationData ),
        handoff(agent=parallel_search_agent , on_handoff=on_parallel_search , input_type=EscilationData)
    ]
)






async def run_agent():
    agent: Agent = Agent(
        name='orchestrator_agent',
        instructions=f""" {RECOMMENDED_PROMPT_PREFIX}""",
        tools=[planning_agent.as_tool(
            tool_name='planning_tool',
            tool_description="Planning and Dividing the topic"
        )]
        # handoffs=[
        #     handoff(agent=planning_agent, on_handoff=on_planning , input_type=EscilationData),
        # ]
    )

    response: Runner =  Runner.run_streamed(
        agent,
        "Search deeply about difference between Agentic AI and Generative AI",
        run_config=config
    )

    print(response.last_agent.name)
    async for event in response.stream_events():
        if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
            print(event.data.delta , end="" , flush=True)


asyncio.run(run_agent())

    