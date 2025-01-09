from pydantic import BaseModel
from typing import List

class Emotions(BaseModel):
    joy: float
    sadness: float
    anger: float
    fear: float

class SummarizeRequest(BaseModel):
    text: str

class ChatRequest(BaseModel):
    content: str
    messages: List[str]
    chatRound: int

class Message(BaseModel):
    content: str
    isUser: bool

class CompleteRequest(BaseModel):
    user_id: str
    messages: List[Message]
    timestamp: str

class SessionRequest(BaseModel):
    user_id: str