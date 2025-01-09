import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from openai import OpenAI
import os
import dotenv
from supabase import create_client, Client

import utils
import schemas

dotenv.load_dotenv()

supabase: Client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_ANON_KEY"))

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/summarize")
async def summarize(request: schemas.SummarizeRequest):
    summary = utils.get_summary(request.text)
    return {"summary": summary}

@app.post("/chat")
async def chat(request: schemas.ChatRequest):
    reply = utils.get_chat_reply(request.content, request.messages, request.chatRound)
    return {"reply": reply}

@app.post("/complete")
async def complete(request: schemas.CompleteRequest):
    unique_id = utils.save_raw_result(request.user_id, request.messages)
    return {"unique_id": unique_id}

@app.post("/sessions")
async def sessions(request: schemas.SessionRequest):
    response = supabase.table("sessions").select("*").eq("user_id", request.user_id).order("id").execute()
    print(response)
    return response.data

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
