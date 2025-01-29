from pydantic import BaseModel
from typing import List
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

class SuggestionContent(BaseModel):
    anxiety: str
    advice: str

def get_suggestion(text_input):
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system", 
                "content": 
                """
                入力されたテキストから悩みを分析し、それぞれの悩みに対して解釈の幅が広い助言を短く（20文字以内）行なってください。
                Json形式で出力してください。
                """
            },
            {
                "role": "user",
                "content": text_input
            }
        ],
        functions=[{
            "name": "get_suggestion",
            "parameters": {
                "type": "object",
                "properties": {
                    "anxiety": {"type": "string"},
                    "advice": {"type": "string"}
                },
                "required": ["anxiety", "advice"]
            }
        }],
        function_call={"name": "get_suggestion"},
        response_format={ "type": "json_object" }
    )

    suggestion = SuggestionContent.model_validate_json(
        completion.choices[0].message.function_call.arguments
        )
    return {
        "anxiety": suggestion.anxiety,
        "advice": suggestion.advice
    }

class SuggestionType(BaseModel):
    fortune_telling: str
    religion: str
    quote: str
    philosophy: str


def adjust_suggestion(base_suggestion):
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system", 
                "content": 
                f"""
                入力テキストはユーザーの悩み「{base_suggestion["anxiety"]}」へのアドバイスです。
                このアドバイスに対して、表現形式
                １：占い
                ２：宗教
                ３：名言
                ４：哲学
                の四つを出力してください。（具体的な行動については表現方法を変えて言及）
                Json形式で出力してください。
                """
            },
            {
                "role": "user",
                "content": base_suggestion["advice"]
            }
        ],
        functions=[{
            "name": "get_suggestion",
            "parameters": {
                "type": "object",
                "properties": {
                    "fortune_telling": {"type": "string"},
                    "religion": {"type": "string"},
                    "quote": {"type": "string"},
                    "philosophy": {"type": "string"}
                },
                "required": ["fortune_telling", "religion", "quote", "philosophy"]
            }
        }],
        function_call={"name": "get_suggestion"},
        response_format={ "type": "json_object" }
    )

    suggestion = SuggestionType.model_validate_json(
        completion.choices[0].message.function_call.arguments
        )
    return {
        "anxiety": base_suggestion["anxiety"],
        "advice": base_suggestion["advice"],
        "fortune_telling": suggestion.fortune_telling,
        "religion": suggestion.religion,
        "quote": suggestion.quote,
        "philosophy": suggestion.philosophy
    }


suggestion = get_suggestion("最近漠然とした不安で仕方がないです")
print(suggestion)
print(adjust_suggestion(suggestion))
