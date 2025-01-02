from openai import OpenAI
client = OpenAI(api_key="sk-proj-VXwOqtddCTupSiDzHxGAT3BlbkFJ4TRPnMl1rl981wB7qB51")

completion = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "developer", "content": "ユーザーが画像を見て感じたメモ書きを、整理して下さい。（コメントは不要）"},
        {
            "role": "user",
            "content": "少年が悩んでいる　悲しそう　グローブがある　親との関係悪そう"
        }
    ]
)

print(completion.choices[0].message.content)