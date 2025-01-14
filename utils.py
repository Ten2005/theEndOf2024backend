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

def vectorize_message(message):
    response = client.embeddings.create(
        model="text-embedding-ada-002",
        input=message
    )
    return response.data[0].embedding

def calculate_similarities(sentenceList, content):
    content_embedding = vectorize_message(content)
    similarities = []
    for i, sentence in enumerate(sentenceList):
        sentence_embedding = vectorize_message(sentence)
        similarity = sum(a * b for a, b in zip(content_embedding, sentence_embedding))
        similarities.append((similarity, i))
    return similarities

def get_valid_context(messages):
    print(messages)
    sentenceList = []
    for message in messages:
        sentences = split_content_to_sentences(message.content)
        sentenceList += sentences

    similarities = calculate_similarities(sentenceList, messages[-1].content)

    similarities.sort(reverse=True)
    top_n = min(10, len(similarities))
    top_10_contexts = [sentenceList[idx[1]] for idx in similarities[:top_n]]

    return top_10_contexts

def get_chat_reply(messages):
    valid_contexts = get_valid_context(messages)

    match messages[-1].chatRound:
        case 0:
            return get_chat_first_reply(messages[-1].content, valid_contexts)
        case 1:
            return get_chat_second_reply(messages[-1].content, valid_contexts)
        case 2:
            return get_chat_third_reply(messages[-1].content, valid_contexts)
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
    messages = messages[1:]
    imageSessions = []
    chunk_size = 7
    
    for i in range(0, len(messages), chunk_size):
        chunk = messages[i:i + chunk_size]
        if len(chunk) > 0:
            imageSessions.append({
                "imageNumber": (i // chunk_size) + 1,
                "messages": chunk
            })

    return imageSessions

def convert_to_prompt(messages):
    prompt = [
        {
            "role": "system",
            "content": 
            """
            会話内容を分析して、ユーザーの感情スコアを0~1の範囲で分析して下さい。（大きいほど感情が強い）
            返答はJSON形式で返して下さい。
            """
        }
    ]
    for message in messages:
        # Map any custom roles to OpenAI's accepted roles
        role = "user" if message.role == "user" else "assistant"
        prompt.append({"role": role, "content": message.content})
    return prompt

def save_raw_result(user_id, messages):
    prompt = convert_to_prompt(messages)
    scores_dict = get_emotions(prompt)

    # Convert Message objects to dictionaries
    serializable_messages = [
        {
            "role": message.role,
            "content": message.content,
            "chatRound": message.chatRound if hasattr(message, 'chatRound') else None,
            "imageNumber": message.imageNumber if hasattr(message, 'imageNumber') else None
        }
        for message in messages
    ]

    response = supabase.table("log_data").insert({
        "user_id": user_id,
        "emotions": scores_dict,
        "content": serializable_messages,
    }).execute()

    return response.data[0]['user_id']

def content_to_text(data):
    text_content = ""
    for contents in data:
        for content in contents:
            if content["role"] == "user":
                text_content += content["content"]
    return text_content

def analyze_text(text):
    print(text)
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": """
                入力されたテキストは、様々な画像についてのユーザーの感想や、それに関する会話の発言内容です。
                その内容を分析して、ユーザーの性格や、その画像に対するユーザーの印象を分析して下さい。
                また、ユーザーが潜在的に抱えてそうな悩みや価値観を分析してください。
                出力はテキストのみで、マークダウンなどは使用しないでください。
                """
                },
            {
                "role": "user",
                "content": text
                }
        ]
    )
    return completion.choices[0].message.content

def GPT_analyze(user_id):
    response = supabase.table("log_data").select("content").eq("user_id", user_id).order("id").execute()
    text_content = content_to_text([content["content"] for content in response.data])
    analysis_result = analyze_text(text_content)
    
    try:
        result = supabase.table("users").update({
            "GPT_analysis": analysis_result
        }).eq("user_id", user_id).execute()

        if not result.data:
            result = supabase.table("users").insert({
                "user_id": user_id,
                "GPT_analysis": analysis_result
            }).execute()
            
    except Exception as e:
        print(f"Error: {e}")
        raise
        
    return analysis_result

# def get_user_messages(user_id):
#     try:
#         response = supabase.table("users").select("sentences").eq("user_id", user_id).execute()
#         return response.data[0]['sentences']
#     except (IndexError, KeyError):
#         response = supabase.table("users").insert({
#             "user_id": user_id,
#             "sentences": []
#         }).execute()
#         return response.data[0]['sentences']

# def store_sentences(user_id, messages):
#     messages = messages[1:]
#     new_messages = []
#     for message in messages:
#         if message["isUser"]:
#             message["vector"] = vectorize_message(message["content"])
#             new_messages.append(message)
#     existing_sentences = get_user_messages(user_id)
#     stored_messages = existing_sentences + new_messages

#     response = supabase.table("users").update({
#         "sentences": stored_messages
#     }).eq("user_id", user_id).execute()

#     return response.data[0]['user_id']
