from agents import Agent, Runner, AsyncOpenAI , OpenAIChatCompletionsModel, RunContextWrapper,handoff, function_tool
from agents.run import RunConfig
from dotenv import load_dotenv
import os
import asyncio
from openai.types.responses import ResponseTextDeltaEvent
from tavily import TavilyClient, AsyncTavilyClient
from pydantic import BaseModel
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX
# from .synthesis_agent import synthesis_agent, on_synthesis
# from .research_agent import research_agent

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


# def on_parallel_search(wrapper: RunContextWrapper , input: EscilationData):
#     print("\n On Parallel Search Agent Handoffs \n Input" , input)



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

report_agent: Agent = Agent(
    name='report_agent',
    instructions=f'''
                You will final professional research. You should transfer to the orchestrator_agent.
                ''',
    model=model,
    tools=[web_search, extract_url]
)

search_agent: Agent = Agent(
    name='search_agent',
    instructions=f''' {RECOMMENDED_PROMPT_PREFIX}
    you can search over the internet. You will pass the response to parallel_search_agent
    ''',
    model=model,
    tools=[ web_search , extract_url],
    # handoffs=[
    #     handoff(agent=parallel_search_agent , on_handoff=on_parallel_search , input_type=EscilationData)
    # ]    

)


planning_agent: Agent = Agent(
    name="planning_agent",
    instructions=f'''  
    You are planning agent who will break the user query into parts and then must transfer to report_agent
    ''',
    model=model,
    handoffs=[
        handoff(agent=search_agent, on_handoff=on_search, input_type=EscilationData ),
        # handoff(agent=parallel_search_agent , on_handoff=on_parallel_search , input_type=EscilationData)
    ]
)



def on_synthesis(wrapper : RunContextWrapper , input: EscilationData):
    print("On Synthesis Agent -- Input" , input)

synthesis_agent: Agent = Agent(
    name='synthesis_agent',
    instructions=f' You will gather information and combines findings into organized insights. Then you must transfer to the planning_agent',
    model=model,
    handoffs=[handoff(agent=planning_agent , on_handoff=on_planning , input_type=EscilationData)]
)



lead_agent: Agent = Agent(
    name='orchestrator_agent',
    instructions=f""" {RECOMMENDED_PROMPT_PREFIX}. You will first transfer to the synthesis_agent""",
    tools=[
    search_agent.as_tool(
        tool_name='search_web',
        tool_description="Search Goolge and Web"
    ),
    report_agent.as_tool(
        tool_name='report_writer',
        tool_description='professional report writer'
    )
    ],
    handoffs=[
        handoff(agent=synthesis_agent, on_handoff=on_synthesis , input_type=EscilationData),
    ]
)

def on_lead_agent(wrapper: RunContextWrapper , input : EscilationData):
    print(f"On Lead Agent --- input {input}")

def on_report_agent(wrapper: RunContextWrapper , input : EscilationData):
    print(f"On Report Agent --- input {input}")


planning_agent.handoffs.append(handoff(agent=report_agent , on_handoff=on_report_agent , input_type=EscilationData))
report_agent.handoffs.append(handoff(agent=lead_agent, on_handoff=on_synthesis , input_type=EscilationData))


async def run_agent():

    response: Runner =  Runner.run_streamed(
        lead_agent,
        "Search deeply about difference between Agentic AI and Generative AI",
        run_config=config,
        max_turns=15
    )

    # print(response.last_agent.name)
    async for event in response.stream_events():
        if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
            print(event.data.delta , end="" , flush=True)


asyncio.run(run_agent())

    