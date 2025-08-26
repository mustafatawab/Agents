from agents import Agent , Runner, OpenAIChatCompletionsModel, AsyncOpenAI, function_tool, RunContextWrapper, handoff
from dotenv import load_dotenv
import os
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX
from tavily import TavilyClient, AsyncTavilyClient
_: bool = load_dotenv()

gemini_api_key: str = os.environ.get("GEMINI_API_KEY")
tavily_api_key: str = os.environ.get("TAVILY_API_KEY")
openai_api_key: str = os.environ.get("OPENAI_API_KEY")
os.environ["OPENAI_API_KEY"] = openai_api_key

if not gemini_api_key:
    raise ValueError("Please Set GEMINI API key")

if not tavily_api_key: 
    raise ValueError("Tavily api key is not defined in your env file")

tavily_client = TavilyClient(api_key=tavily_api_key)


client: AsyncOpenAI = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url='https://generativelanguage.googleapis.com/v1beta/openai/'
)

general_model: OpenAIChatCompletionsModel = OpenAIChatCompletionsModel(
    openai_client=client,
    model="gemini-2.0-flash"
)

@function_tool
async def web_search( query : str) -> str:
    """ Perform Deep Web Search"""
    print(f"\n -- Searching -- Query = {query} \n" )
    res = tavily_client.search(query=query, max_results=10)
    print(f"\n -- Tavily Respoonse - {res} \n")
    return res

def main_instructions(context : RunContextWrapper, agent: Agent) -> str:
    print("-- Main Instructions -- ")
    return (
        f"{RECOMMENDED_PROMPT_PREFIX}",
        "You are Orchestrator agent"
    )

planning_agent = Agent(
    name="Planning Agent",
    instructions="""Break down complex research questions into sub-tasks. Handoff to the appropriate research agent.
    For comparisons, create sub-tasks like 'Pros of X' and 'Cons of X'.""",
    model=general_model
)

research_agent_a = Agent(
    name="Research Agent A",
    instructions="Conduct in-depth research on assigned sub-tasks using tools. Summarize findings with sources.",
    tools=[web_search],
    model=general_model
)

research_agent_b = Agent(
    name="Research Agent B",
    instructions="Conduct in-depth research on assigned sub-tasks using tools. Summarize findings with sources.",
    model=general_model,
    tools=[web_search],
)

source_checker_agent = Agent(
    name="Source Checker",
    instructions="""Rate sources: High (.edu, .gov, major news), Medium (Wikipedia, industry sites), Low (blogs, forums).
    Flag questionable info and conflicts (e.g., 'Source A says X, but Source B says Y').""",
    model=general_model

)

synthesis_agent = Agent(
    name="Synthesis Agent",
    instructions="""Synthesize findings into a coherent report. Organize by themes, include key insights, trends, and numbered citations [1], [2].
    Add full source details at the end.""",
    model=general_model  

)

research_agent_a.handoffs = [handoff(source_checker_agent)]
research_agent_b.handoffs = [handoff(source_checker_agent)]
source_checker_agent.handoffs = [handoff(synthesis_agent)]
planning_agent.handoffs = [handoff(agent=research_agent_a) , handoff(agent=research_agent_b)]

orchestrator_agent: Agent = Agent(
    name='orchestrator agent',
    instructions=f"{RECOMMENDED_PROMPT_PREFIX}",
    model=general_model,
    handoffs=[planning_agent]
)


user_prompt = input("Enter your prompt : ")
result: Runner = Runner.run_sync(
    starting_agent=orchestrator_agent,
    input=user_prompt
)

print(result.final_output)