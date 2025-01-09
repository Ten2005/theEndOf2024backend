import schemas

chat_test_data = [
    {
        "content": "今日はとても良い天気でした",
        "messages": [],
        "chatRound": -1,
        "expected_reply": ""
    },
    {
        "content": "今日はとても良い天気でした",
        "messages": [],
        "chatRound": 0,
    },
    {
        "content": "今日はとても良い天気でした",
        "messages": [],
        "chatRound": 1,
    },
    {
        "content": "最近仕事が忙しくて疲れています",
        "messages": ["今日はとても良い天気でした"],
        "chatRound": 2,
    },
    {
        "content": "友達と楽しく話せて嬉しかった",
        "messages": ["今日はとても良い天気でした", "最近仕事が忙しくて疲れています"],
        "chatRound": 3,
    }
]

complete_test_data = [
    {
        "user_id": "string",
        "messages": [
            schemas.Message(content='string', isUser=True),
            schemas.Message(content='string', isUser=False)
        ],
        "timestamp": "string"
    },
    {
        "user_id": "",
        "messages": [
            schemas.Message(content='string', isUser=True),
            schemas.Message(content='string', isUser=False)
        ],
        "timestamp": "string"
    },
    {
        "user_id": "not_exist",
        "messages": [
            schemas.Message(content='string', isUser=True),
            schemas.Message(content='string', isUser=False)
        ],
        "timestamp": "string"
    },
    {
        "user_id": "not_exist",
        "messages": [],
        "timestamp": "string"
    }
]

sessions_test_data = [
    {
        "user_id": "string"
    }
]