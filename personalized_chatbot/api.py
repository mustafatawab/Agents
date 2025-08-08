from fastapi import FastAPI, Body, Path, Query, HTTPException
from pydantic import BaseModel
from main import run_agent


class Chat(BaseModel):
    input: str

app: FastAPI = FastAPI()


@app.get("/")
def root():
    return {
       "Message" : "Welcome to the Personalized Chat Bot"
    }


@app.post("/chat")
async def chat(message: Chat):
    try:

        response = await run_agent(str(message.input))
        print("Response " , response)
        return {
            "Response" : response
        }
    except Exception as e:
        raise HTTPException(status_code=404, details=str(e))