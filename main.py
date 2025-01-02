from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from openai import OpenAI
import spacy
import os
import dotenv
from supabase import create_client, Client

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

def get_summary(text):
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "ユーザーが画像を見て感じたメモ書きを、整理して下さい（コメントは不要）。分量が少なければ、簡単に整理してそのまま返して下さい。"},
            {"role": "user", "content": text}
        ]
    )
    return completion.choices[0].message.content

def get_chat_first_reply(content, valid_contexts):
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": f'''
            ユーザーが画像を見て感じたことについて会話しています。この情報に加え、ユーザーの過去の発言の中で関連度の大きいものを参考に、ユーザーの感じていそうな漠然とした悩み・感情を追及する質問をして下さい。返答は20文字以内にして下さい。カウンセラーのような口調で質問して下さい。
            関連度の大きい発言：{valid_contexts}
            '''
            },
            {
                "role": "user",
                "content": content
                }
        ]
    )
    return completion.choices[0].message.content + "-相談AI-"

def get_chat_second_reply(content, valid_contexts):
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": f'''
            ユーザーが画像を見て感じたことについて会話しています。この情報に加え、ユーザーの過去の発言の中で関連度の大きいものを参考に、ユーザーの持っていそうな人生観を追及する質問をして下さい。返答は20文字以内にして下さい。敬語は使わずに哲学者のような口調で質問して下さい。
            関連度の大きい発言：{valid_contexts}
            '''
            },
            {
                "role": "user",
                "content": content
                }
        ]
    )
    return completion.choices[0].message.content + "-不条理AI-"

def get_chat_third_reply(content, valid_contexts):
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": f'''
            ユーザーが画像を見て感じたことについて会話しています。この情報に加え、ユーザーの過去の発言の中で関連度の大きいものを参考に、ユーザーの考えに対して飛躍のある抽象的な質問をして下さい。返答は10文字以内にして下さい。敬語は使わずに禅僧のような口調で質問して下さい。
            関連度の大きい発言：{valid_contexts}
            '''
            },
            {
                "role": "user",
                "content": content
                }
        ]
    )
    return completion.choices[0].message.content + "-禅AI-"

def split_content_to_sentences(content):
    nlp = spacy.load("ja_core_news_lg")
    doc = nlp(content)
    return [sent.text for sent in doc.sents]

def get_valid_context(content, messages):
    sentenceList = []
    for message in messages:
        sentences = split_content_to_sentences(message)
        sentenceList += sentences

    # contentとsentenceListの各文との類似度を計算
    nlp = spacy.load("ja_core_news_lg")
    content_doc = nlp(content)
    
    # 類似度とインデックスのペアのリストを作成
    similarities = []
    for i, sentence in enumerate(sentenceList):
        sentence_doc = nlp(sentence)
        if content_doc.vector_norm and sentence_doc.vector_norm:
            similarity = content_doc.similarity(sentence_doc)
            similarities.append((similarity, i))
    
    # 類似度でソートして上位20件を取得
    similarities.sort(reverse=True)
    top_n = min(20, len(similarities))
    top_20_indices = [idx for _, idx in similarities[:top_n]]
    
    # 上位20件の文を元の順序で取得
    top_20_indices.sort()
    valid_contexts = [sentenceList[i] for i in top_20_indices]

    return valid_contexts

def get_chat_reply(content, messages, chatRound):

    valid_contexts = get_valid_context(content, messages)

    match chatRound:
        case 0:
            return get_chat_first_reply(content, valid_contexts)
        case 1:
            return get_chat_second_reply(content, valid_contexts)
        case 2:
            return get_chat_third_reply(content, valid_contexts)

class Emotions(BaseModel):
    joy: float
    sadness: float
    anger: float
    fear: float

def analyze_save_result(unique_id, result):
    formatted_result = [
        {
            "content": msg.content,
            "isUser": msg.isUser
        } for msg in result
    ]

    messages = [
        {"role": "system", "content": "会話内容を分析して、ユーザーの感情スコアを0~1の範囲で分析して下さい。（大きいほど感情が強い）"}
    ]
    
    for message in formatted_result:
        if message["isUser"]:
            messages.append({"role": "user", "content": message["content"]})
        else:
            messages.append({"role": "assistant", "content": message["content"]})

    completion = client.beta.chat.completions.parse(
        model="gpt-4o",
        messages=messages,
        response_format=Emotions,
    )
    scores = completion.choices[0].message.parsed
    # Emotionsオブジェクトを辞書に変換
    scores_dict = scores.model_dump()
    
    supabase.table("sessions").update({
        "emotions": scores_dict
    }).eq("id", unique_id).execute()


def save_raw_result(user_id, messages):
    imageSessions = []

    formatted_messages = [
        {
            "content": msg.content,
            "isUser": msg.isUser
        } for msg in messages
    ]
    
    # メッセージを7つずつのグループに分割
    if len(formatted_messages) >= 7:
        for i in range(len(formatted_messages) // 7):
            imageSessions.append({
                "imageNumber": i + 1,
                "messages": formatted_messages[i * 7:(i + 1) * 7],
            })
    else:
        imageSessions.append({
            "imageNumber": 1,
            "messages": formatted_messages,
        })
    
    response = supabase.table("sessions").insert({
        "user_id": user_id,
        "image_sessions": imageSessions,
    }).execute()
    
    # レスポンスからIDを正しく取得
    return response.data[0]['id']  # 修正: 挿入されたレコードのIDを返す

@app.get("/")
async def root():
    return {"message": "Hello World"}

class SummarizeRequest(BaseModel):
    text: str

@app.post("/summarize")
async def summarize(request: SummarizeRequest):
    summary = get_summary(request.text)
    return {"summary": summary}

class ChatRequest(BaseModel):
    content: str
    messages: List[str]
    chatRound: int

@app.post("/chat")
async def chat(request: ChatRequest):
    reply = get_chat_reply(request.content, request.messages, request.chatRound)
    return {"reply": reply}

class Message(BaseModel):
    content: str
    isUser: bool

class CompleteRequest(BaseModel):
    user_id: str
    messages: List[Message]
    timestamp: str

@app.post("/complete")
async def complete(request: CompleteRequest):
    unique_id = save_raw_result(request.user_id, request.messages)
    analyze_save_result(unique_id, request.messages)

class SessionRequest(BaseModel):
    user_id: str

@app.post("/sessions")
async def sessions(request: SessionRequest):
    response = supabase.table("sessions").select("*").eq("user_id", request.user_id).execute()
    return response.data

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
