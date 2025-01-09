import schemas

data_test_get_chat_reply = [
    {
        "content": "string",
        "messages": ['string', 'string'],
        "chatRound": 0
    },
    {
        "content": "string",
        "messages": ['string'],
        "chatRound": 1
    },
    {
        "content": "string",
        "messages": ['string', 'string'],
        "chatRound": 2
    },
    {
        "content": "string",
        "messages": ['string', 'string', 'string'],
        "chatRound": 3
    },
    {
        "content": "string",
        "messages": ['string', 'string', 'string', 'string'],
        "chatRound": -1
    }
]

data_test_get_emotions = [
[
    {
        "role": "system",
        "content": 
        """
        会話内容を分析して、ユーザーの感情スコアを0~1の範囲で分析して下さい。（大きいほど感情が強い）
        返答はJSON形式で返して下さい。
            """
    },
    {
        "role": "user",
        "content": "こんにちは"
    },
    {
        "role": "assistant",
        "content": "はい、こんにちは"
    },
    {
        "role": "user",
        "content": "ありがとう"
    },
    {
        "role": "assistant",
        "content": "ありがとうございます"
    }
],[
    {
        "role": "system",
        "content": 
        """
        会話内容を分析して、ユーザーの感情スコアを0~1の範囲で分析して下さい。（大きいほど感情が強い）
        返答はJSON形式で返して下さい。
            """
    },
    {
        "role": "user",
        "content": "ありがとう"
    },
    {
        "role": "assistant",
        "content": "ありがとうございます"
    }
]
]

data_test_get_user_messages = [
    'string',
    'bfed1991-a797-409f-98a4-5301251315fe'
    ]

data_test_store_sentences = [
    {
        "user_id": "string",
        "messages": [
            {"content": "string", "isUser": True},
            {"content": "string", "isUser": True},
            {"content": "string", "isUser": False},
            {"content": "string", "isUser": True}
        ]
    },
    {
        "user_id": "string_test",
        "messages": [
            {"content": "string_test", "isUser": True},
            {"content": "string_test", "isUser": False}
        ]
    },
    {
        "user_id": "bfed1991-a797-409f-98a4-5301251315fe",
        "messages": [
            {"content": "string_test2", "isUser": True},
            {"content": "string_test2", "isUser": True},
            {"content": "string_test2", "isUser": False},
            {"content": "string_test2", "isUser": True},
            {"content": "string_test2", "isUser": False}
        ]
    }
]