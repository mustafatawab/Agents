from agents import Agent, Runner, AsyncOpenAI , OpenAIChatCompletionsModel, RunContextWrapper,handoff, function_tool, ModelSettings
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
    print("\n\n On Planning Agent Handoffs \n Input" , input)
    print("\n")

def on_search(wrapper: RunContextWrapper , input: EscilationData):
    print("\n\n On Search Agent Handoffs \n Input" , input)
    print("\n")


def on_lead_agent(wrapper: RunContextWrapper , input : EscilationData):
    print(f"\n\n On Lead Agent --- input {input}")
    print("\n")

def on_report_agent(wrapper: RunContextWrapper , input : EscilationData):
    print(f"\n\n On Report Agent --- input {input}")
    print("\n")


def on_synthesis(wrapper : RunContextWrapper , input: EscilationData):
    print("\n\n On Synthesis Agent -- Input" , input)
    print("\n")

def on_citation(wrapper : RunContextWrapper , input: EscilationData):
    print("\n\n On Citation Agent -- Input" , input)
    print("\n")


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
    You Synthesize findings into a coherent report. Organize by themes, include key insights, trends, and numbered citations [1], [2].
    Add full source details at the end. And get better result to the user to understand in a concise way. You can use your own tools to get better solutions.
                ''',
    model=model,
    tools=[extract_url],
    model_settings=ModelSettings(temperature=1 )
)

search_agent_a: Agent = Agent(
    name='search_agent',
    instructions=f'''
   You are a search agent.
    1. Use the web_search tool to gather information.
    2. Always provide citations with URLs.
    3. After summarizing, ALWAYS handoff to report_agent.
    ''',
    model=model,
    tools=[ web_search],
    handoffs=[
        handoff(agent=report_agent , on_handoff=on_report_agent , input_type=EscilationData)
    ],
    model_settings=ModelSettings(temperature=0.5 )


)

search_agent_b: Agent = Agent(
    name='search_agent',
    instructions=f'''
    You are a search agent.
    1. Use the web_search tool to gather information.
    2. Always provide citations with URLs.
    3. After summarizing, ALWAYS handoff to report_agent.
     ''',
    model=model,
    tools=[ web_search],
    handoffs=[
        handoff(agent=report_agent , on_handoff=on_report_agent , input_type=EscilationData)
    ],
    model_settings=ModelSettings(temperature=0.5 )


)



planning_agent: Agent = Agent(
    name="planning_agent",
    instructions='''  
   You are a planning agent. Break the user query into sub-tasks.
    For each sub-task, output exactly ONE JSON object:
    {"topic": "<sub task>", "reason": "<why this sub-task>"}

    ⚠️ Always handoff to a search_agent
    ''',
    model=model,
    handoffs=[
        handoff(agent=search_agent_a, on_handoff=on_search, input_type=EscilationData ),
        handoff(agent=search_agent_a, on_handoff=on_search, input_type=EscilationData ),
    ],
    model_settings=ModelSettings(temperature=1 )

)


citation_checker: Agent = Agent(
    name="citation_checker",
    instructions="""
    You are a citation and source verification agent.
    1. Verify all citations in the report using the extract_url tool.
    2. Ensure each claim has at least one valid, relevant source.
    3. Flag broken or irrelevant links.
    4. Return a clean report with corrected citations.
    """,
    model=model,
    tools=[extract_url],
    model_settings=ModelSettings(temperature=0.3)
)


lead_agent: Agent = Agent(
    name='orchestrator_agent',
    instructions=f"""
    You are the orchestrator. Your ONLY job is to:
    1. Receive the user query.
    2. Pass it to the planning_agent.
    3. Do not answer the query yourself.
    4. Do not ask the user for clarification — just delegate.
    """,
    tools=[web_search],
    handoffs=[
        handoff(agent=planning_agent, on_handoff=on_planning, input_type=EscilationData),

    ],
    model_settings=ModelSettings(temperature=0.2 )

)


report_agent.handoffs.append(handoff(agent=citation_checker, on_handoff=on_citation , input_type=EscilationData))


async def run_agent():

    while True:
        user_prompt = input("Enter your prompt (quit or exit for ending conversation) : ")
        if user_prompt.lower() == "quit" or user_prompt == "exit":
            break
        
        response: Runner =  Runner.run_streamed(
            lead_agent,
            user_prompt,
            run_config=config,
            max_turns=20
        )

        # print(response.last_agent.name)
        print("\n LLM Response \n")
        async for event in response.stream_events():
            if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
                print(event.data.delta , end="" , flush=True)


asyncio.run(run_agent())

    