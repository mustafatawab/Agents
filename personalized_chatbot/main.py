
from agents import Agent, Runner, AsyncOpenAI , OpenAIChatCompletionsModel , set_tracing_disabled, RunContextWrapper, function_tool, Session
from openai.types.responses import ResponseTextDeltaEvent
from agents.run import RunConfig
from dotenv import load_dotenv, find_dotenv
import os
from userContext import Person
import asyncio

_: bool = load_dotenv(find_dotenv())
gemini_key=os.environ.get('GEMINI_API_KEY')

if not gemini_key:
    raise ValueError("Please set the gemini api key")

set_tracing_disabled(True)
client: AsyncOpenAI = AsyncOpenAI(
    api_key=gemini_key,
    base_url='https://generativelanguage.googleapis.com/v1beta/openai/'
)


llm_model : OpenAIChatCompletionsModel = OpenAIChatCompletionsModel(
    openai_client=client,
    model="gemini-2.0-flash"
)

person = Person()

@function_tool
def all_about_me(wrapper: RunContextWrapper[Person]) -> Person:
    f""" All About {wrapper.context.name} """
    print("All About Me Tool Calling ::")
    return wrapper.context

async def instructions(wrapper: RunContextWrapper[Person], agent: Agent) -> str:
    # print(wrapper.context)
    # print(person)
    return wrapper.context.agent_instructions


async def run_agent(input: str) -> str:
    agent: Agent = Agent(name=f"{person.name} Bot" , instructions=instructions, model=llm_model, )
    response = ""
    runner : Runner =  Runner.run_streamed(agent, input , context=person)
    async for event in runner.stream_events():
        if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
            print(event.data.delta , end="" , flush=True)
            response += event.data.delta
    return response
    # result = await Runner.run(agent , input, context=person)
    # return str(result.final_output)



asyncio.run(run_agent("what services you provide. Please tell me about yourself "))