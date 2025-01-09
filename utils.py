from openai import OpenAI
import spacy
import os
import dotenv
from supabase import create_client, Client
import json

dotenv.load_dotenv()

supabase: Client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_ANON_KEY"))

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

nlp = spacy.load("ja_core_news_md")

def get_summary(text):
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": 
                """
                ユーザーが画像を見て感じたメモ書きを、整理して下さい（コメントは不要）。
                分量が少なければ、簡単に整理してそのまま返して下さい。
                """
                },
            {
                "role": "user",
                "content": text
                }
        ]
    )
    return completion.choices[0].message.content

def get_chat_first_reply(content, valid_contexts):
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": 
                f"""
                ユーザーが画像を見て感じたことについて会話しています。
                この情報に加え、ユーザーの過去の発言の中で関連度の大きいものを参考に、
                ユーザーの感じていそうな漠然とした悩み・感情を追及する質問をして下さい。
                返答は20文字以内にして下さい。カウンセラーのような口調で質問して下さい。
                関連度の大きい発言：{valid_contexts}
                """
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
                "content": 
                f"""
                ユーザーが画像を見て感じたことについて会話しています。
                この情報に加え、ユーザーの過去の発言の中で関連度の大きいものを参考に、
                ユーザーの持っていそうな人生観を追及する質問をして下さい。
                返答は20文字以内にして下さい。敬語は使わずに哲学者のような口調で質問して下さい。
                関連度の大きい発言：{valid_contexts}
                """
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
                "content": f"""
                ユーザーが画像を見て感じたことについて会話しています。
                この情報に加え、ユーザーの過去の発言の中で関連度の大きいものを参考に、
                ユーザーの考えに対して飛躍のある抽象的な質問をして下さい。返答は10文字以内にして下さい。
                敬語は使わずに禅僧のような口調で質問して下さい。
                関連度の大きい発言：{valid_contexts}
                """
            },
            {
                "role": "user",
                "content": content
                }
        ]
    )
    return completion.choices[0].message.content + "-禅AI-"

def split_content_to_sentences(content):
    doc = nlp(content)
    return [sent.text for sent in doc.sents]

def calculate_similarities(sentenceList, content):
    content_doc = nlp(content)
    similarities = []
    for i, sentence in enumerate(sentenceList):
        sentence_doc = nlp(sentence)
        if content_doc.vector_norm and sentence_doc.vector_norm:
            similarity = content_doc.similarity(sentence_doc)
            similarities.append((similarity, i))
    return similarities

def get_valid_context(content, messages):
    sentenceList = []
    for message in messages:
        sentences = split_content_to_sentences(message)
        sentenceList += sentences

    similarities = calculate_similarities(sentenceList, content)

    similarities.sort(reverse=True)
    top_n = min(10, len(similarities))
    top_10_contexts = [sentenceList[idx[1]] for idx in similarities[:top_n]]

    return top_10_contexts

def get_chat_reply(content, messages, chatRound):

    valid_contexts = get_valid_context(content, messages)

    match chatRound:
        case 0:
            return get_chat_first_reply(content, valid_contexts)
        case 1:
            return get_chat_second_reply(content, valid_contexts)
        case 2:
            return get_chat_third_reply(content, valid_contexts)
        case _:
            return ""

def get_emotions(messages):
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        functions=[{
            "name": "get_emotions",
            "parameters": {
                "type": "object",
                "properties": {
                    "joy": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                    "sadness": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                    "anger": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                    "fear": {"type": "number", "minimum": 0.0, "maximum": 1.0}
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
    chunk_size = 7
    num_chunks = len(messages) // chunk_size

    for i in range(num_chunks + (1 if len(messages) % chunk_size else 0)):
        imageSessions.append({
            "imageNumber": i + 1,
            "messages": messages[i * chunk_size:min((i + 1) * chunk_size, len(messages))]
        })

    return imageSessions

def convert_to_messages(result):
    formatted_results = [
        {
            "content": msg.content,
            "isUser": msg.isUser
        } for msg in result
    ]
    
    messages = [
        {
            "role": "system",
            "content": 
            """
            会話内容を分析して、ユーザーの感情スコアを0~1の範囲で分析して下さい。（大きいほど感情が強い）
            返答はJSON形式で返して下さい。
            """
        }
    ]

    for result in formatted_results:
        if result["isUser"]:
            messages.append({"role": "user", "content": result["content"]})
        else:
            messages.append({"role": "assistant", "content": result["content"]})

    return messages

def save_raw_result(user_id, result):
    messages = convert_to_messages(result)
    scores_dict = get_emotions(messages)
    imageSessions = split_messages(messages)

    response = supabase.table("sessions").insert({
        "user_id": user_id,
        "image_sessions": imageSessions,
        "emotions": scores_dict
    }).execute()
    
    return response.data[0]['id']