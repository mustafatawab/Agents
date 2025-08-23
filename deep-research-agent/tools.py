from agents import function_tool, Agent, RunContextWrapper
from dotenv import load_dotenv
import os
from tavily import TavilyClient, AsyncTavilyClient



load_dotenv()

tavily_api_key: str = os.environ.get("TAVILY_API_KEY")
if not tavily_api_key:
    raise ValueError("TAVILY API is not set")

tavily_client: AsyncTavilyClient = AsyncTavilyClient(tavily_api_key)


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

