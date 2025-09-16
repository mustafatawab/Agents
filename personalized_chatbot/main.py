
from agents import Agent, Runner, AsyncOpenAI , OpenAIChatCompletionsModel , set_tracing_disabled, RunContextWrapper, function_tool, Session, RunResult
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

client: AsyncOpenAI = AsyncOpenAI(
    api_key=gemini_key,
    base_url='https://generativelanguage.googleapis.com/v1beta/openai/'
)


llm_model : OpenAIChatCompletionsModel = OpenAIChatCompletionsModel(
    openai_client=client,
    model="gemini-2.0-flash"
)


@function_tool
def all_about_me(wrapper: RunContextWrapper[Person]) -> Person:
    f""" All About {wrapper.context.name} """
    print("All About Me Tool Calling ::")
    return wrapper.context

async def instructions(wrapper: RunContextWrapper[Person], agent: Agent) -> str:
    # print(wrapper.context)
    # print(person)
    return (
        f"{wrapper.context.agent_instructions}"
        f" You are a personal assistant for {wrapper.context.name}. "
        f"Your name is {agent.name}. "
        f"You are very helpful and you always try to help {wrapper.context.name} in the best way possible. "
        
    )


agent: Agent = Agent(
    name=f"personalized_bot" , 
    instructions="You are personalized bot for Mustafa Tawab.",
    model=llm_model, 
)

async def run_agent() -> None:
    user_chat : list[dict] = []
    while True:

        user_input = input("Enter your prompt : ")
        if user_input.lower() in ["exit", "quit"]:
            print("Exiting...")
            break
        
        if user_input in ["view" , "display" , "show"]:
            print("\n Showing the user chat so far : \n")
            print(user_chat)


        user_message  = {
            "role": "user",
            "content": user_input
        }

        user_chat.append(user_message)
        runner : RunResult = await Runner.run(agent, user_chat)

        user_chat = runner.to_input_list()
        print(runner.final_output)

asyncio.run(run_agent())