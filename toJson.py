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

print(get_emotions([
    {"role": "system", "content": "会話内容を分析して、ユーザーの感情スコアを0~1の範囲で分析して下さい。（大きいほど感情が強い）"},
    {"role": "user", "content": "最近、仕事が上手くいかなくて悩んでいます。プロジェクトの締め切りも迫っているのに、なかなか前に進めない。"},
    {"role": "assistant", "content": "つらい状況なのですね。具体的にどんな部分で行き詰まりを感じていますか？"},
    {"role": "user", "content": "チームメンバーとの意見の食い違いが多くて。私の提案する方向性に反対する人が多いんです。でも、このままじゃプロジェクトが失敗すると確信しているんです。"},
    {"role": "assistant", "content": "ご自身の信念と周囲との調和の難しさを感じていらっしゃるのですね。"},
    {"role": "user", "content": "そうなんです。かといって強引に押し通すのも良くないし...。昨日は眠れないほど考え込んでしまって。"},
    {"role": "assistant", "content": "責任感が強いからこそのお悩みかもしれませんね。一人で抱え込みすぎていませんか？"},
    {"role": "user", "content": "実は...以前の会社でも似たような経験があって、結局退職することになったんです。また同じことを繰り返すのが怖くて。"},
    {"role": "assistant", "content": "過去のトラウマが現在の不安を強めているのかもしれませんね。でも、その経験があるからこそ見える解決策もあるのではないでしょうか。"},
    {"role": "user", "content": "確かに...でも、正直なところ自信を失っています。リーダーとしての自分の能力に疑問を感じてしまって。"},
    {"role": "assistant", "content": "自己否定的になってしまうのも無理はありません。でも、こうして真摯に向き合おうとされている姿勢自体が、すでにリーダーシップの表れだと思います。"},
]))