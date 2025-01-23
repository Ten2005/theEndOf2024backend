import uvicorn
from fastapi import FastAPI, HTTPException
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
async def chat(request: schemas.Messages):
    reply = utils.get_chat_reply(request.messages)
    return {"reply": reply}

@app.post("/complete")
async def complete(request: schemas.CompleteRequest):
    if not request.user_id or not request.messages or not request.timestamp or not request.gender:
        raise HTTPException(status_code=400, detail="Missing required fields")
    utils.save_raw_result(request.user_id, request.messages, request.gender)
    result = utils.GPT_analyze(request.user_id)
    
    utils.generate_suggestion(request.user_id, str(result))
    utils.generate_ten_bulls_advice(request.user_id, str(result))
    
    return {"status": "success", "result": result}

@app.post("/review")
async def review(request: schemas.ReviewRequest):
    log_response = supabase.table("log_data").select("*").eq("user_id", request.user_id).order("id").execute()
    user_response = supabase.table("users").select("*").eq("user_id", request.user_id).execute()
    return {"log_data": log_response.data, "user_data": user_response.data}

@app.post("/ten_bulls_data")
async def ten_bulls_data(request: schemas.TenBullsDataRequest):
    user_data = supabase.table("users").select("*").eq("user_id", request.user_id).execute()
    return {"advice": user_data.data[0]["ten_bulls_advice"], "level": user_data.data[0]["ten_bulls_level"]}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)