from fastapi import FastAPI, Body, Path, Query, HTTPException # type: ignore
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from main import run_agent

app: FastAPI = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or restrict to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Chat(BaseModel):
    input: str



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