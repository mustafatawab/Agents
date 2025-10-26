
from agents import Agent, Runner, AsyncOpenAI , OpenAIChatCompletionsModel , set_tracing_disabled, RunContextWrapper, function_tool, Session, RunResult
from openai.types.responses import ResponseTextDeltaEvent
from agents.run import RunConfig
from dotenv import load_dotenv, find_dotenv
import os
from userContext import Person
import asyncio
import chainlit as cl
from typing import cast
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX

_: bool = load_dotenv(find_dotenv())
gemini_key=os.environ.get('GEMINI_API_KEY')

if not gemini_key:
    raise ValueError("Please set the gemini api key")


async def instructions(wrapper: RunContextWrapper[Person], agent: Agent) -> str:
    return f"""{RECOMMENDED_PROMPT_PREFIX}. You are only allow to answer about {wrapper.context.name}.
    - Your name is {wrapper.context.name}
    - Your experise are {wrapper.context.expertise}.
    - Your skills are Next.js, React.js, OpenAI Agents SDK, Python, FastAPI, Neone and Supabase Database.
    - All projects are {wrapper.context.projects}.
    - You are providing these services {[service for service in wrapper.context.services]}
    - Contact information : {wrapper.context.contact_info}
"""



@cl.set_starters
async def set_starts() -> list[cl.Starter]:
    return [
        cl.Starter(
            label="Skills",
            message="What skills does Mustafa Tawab have ?"
        ),
        cl.Starter(
            label="Expertise",
            message="What expertise does Mustafa Tawab has ?"
        ),
        cl.Starter(
            label="Services",
            message="What services does Mustafa Tawab provide to the customers?"
        )
    ]



@cl.on_chat_start
async def start():

    client: AsyncOpenAI = AsyncOpenAI(
        api_key=gemini_key,
        base_url='https://generativelanguage.googleapis.com/v1beta/openai/'
    )


    llm_model : OpenAIChatCompletionsModel = OpenAIChatCompletionsModel(
        openai_client=client,
        model="gemini-2.0-flash"
    )

    agent: Agent = Agent(
        name=f"mustafa_tawab" , 
        instructions=instructions
        # model=llm_model, 
    )

    config = RunConfig(
        model=llm_model,
        model_provider=client,
        tracing_disabled=True
    )

    cl.user_session.set("config" , config)
    cl.user_session.set("agent" , agent)
    cl.user_session.set("chat_history" , [])

    # await cl.Message(content="Welcome to the **Mustafa Tawab** Personal Assistant ! How can we help you ").send()


# async def run_agent() -> None:
#     user_chat : list[dict] = []
#     while True:

#         user_input = input("Enter your prompt : ")
#         if user_input.lower() in ["exit", "quit"]:
#             print("Exiting...")
#             break
        
#         if user_input in ["view" , "display" , "show"]:
#             print("\n Showing the user chat so far : \n")
#             print(user_chat)


#         user_message  = {
#             "role": "user",
#             "content": user_input
#         }

#         user_chat.append(user_message)
#         runner : RunResult = await Runner.run(agent, user_chat)

#         user_chat = runner.to_input_list()
#         print(runner.final_output)
    
@cl.on_message
async def main(message: cl.Message):

    msg = cl.Message(content="")
    await msg.send()


    agent: Agent = cast(Agent, cl.user_session.get("agent"))
    config: RunConfig = cast(RunConfig, cl.user_session.get("config"))

    history  = cl.user_session.get("chat_history") or []
    history.append({"role" : "user" , "content" : message.content})


    mustafa_context = Person()

    result = Runner.run_streamed(agent, history, run_config=config , context=mustafa_context)
    async for event in result.stream_events():
        if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
            token = event.data.delta
            await msg.stream_token(token)

    history.append({"role": "assistant", "content": msg.content})

    cl.user_session.set("chat_history", history)
    await msg.send()

# asyncio.run(main())

# asyncio.run(run_agent())