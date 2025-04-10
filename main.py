import os
from typing import List
import dotenv

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from supabase import create_client, Client
import uvicorn

import utils
import schemas

dotenv.load_dotenv()

supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_ANON_KEY")
    )

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
async def chat(request: schemas.Messages):
    reply = utils.get_chat_reply(request.messages)
    return {"reply": reply}

@app.post("/complete")
async def complete(request: schemas.CompleteRequest):
    utils.process_result(request.user_id, request.messages, request.gender)
    result = utils.GPT_analyze(request.user_id)
    utils.generate_suggestion(request.user_id, str(result))
    utils.generate_ten_bulls_advice(request.user_id, str(result))
    return {"status": "success", "result": result}

@app.post("/review")
async def review(request: schemas.ReviewRequest):
    log_response = supabase.table("art_log_data").select("*").eq("user_id", request.user_id).order("id").execute()
    user_response = supabase.table("art_users").select("*").eq("user_id", request.user_id).execute()
    return {"log_data": log_response.data, "user_data": user_response.data}

@app.post("/ten_bulls_data")
async def ten_bulls_data(request: schemas.TenBullsDataRequest):
    user_data = supabase.table("art_users").select("*").eq("user_id", request.user_id).execute()
    return {"advice": user_data.data[0]["ten_bulls_advice"], "level": user_data.data[0]["ten_bulls_level"]}

@app.post("/feedback")
async def feedback(request: schemas.FeedbackRequest):
    supabase.table("art_feedback").insert({
        "user_id": request.user_id,
        "try_num": request.scores[0],
        "scores": request.scores[1:],
    }).execute()
    return {"status": "success"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)