import os
import dotenv
from openai import OpenAI
from pydantic import BaseModel
import json

dotenv.load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class Emotions(BaseModel):
    joy: float
    sadness: float
    anger: float
    fear: float

def get_emotions(messages):
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            *messages,
            {
                "role": "system",
                "content": "人は誰しも裏表があります。感情スコアを以下のJSON形式で返してください: {\"joy\": 0.0-1.0, \"sadness\": 0.0-1.0, \"anger\": 0.0-1.0, \"fear\": 0.0-1.0}"
            }
        ],
        functions=[{
            "name": "get_emotions",
            "parameters": {
                "type": "object",
                "properties": {
                    "joy": {"type": "number", "minimum": 0, "maximum": 1},
                    "sadness": {"type": "number", "minimum": 0, "maximum": 1},
                    "anger": {"type": "number", "minimum": 0, "maximum": 1},
                    "fear": {"type": "number", "minimum": 0, "maximum": 1}
                },
                "required": ["joy", "sadness", "anger", "fear"]
            }
        }],
        function_call={"name": "get_emotions"}
    )
    response_json = json.loads(completion.choices[0].message.function_call.arguments)
    return {
        "joy": response_json["joy"],
        "sadness": response_json["sadness"], 
        "anger": response_json["anger"],
        "fear": response_json["fear"]
    }

def split_messages(messages):
    imageSessions = []
    # メッセージを7つずつのグループに分割
    if len(messages) >= 7:
        for i in range(len(messages) // 7):
            imageSessions.append({
                "imageNumber": i + 1,
                "messages": messages[i * 7:(i + 1) * 7],
            })
        if len(messages) % 7 > 0:
            imageSessions.append({
                "imageNumber": len(messages) // 7 + 1,
                "messages": messages[(len(messages) // 7) * 7:],
            })
    else:
        imageSessions.append({
            "imageNumber": 1,
            "messages": messages,
        })
    return imageSessions

