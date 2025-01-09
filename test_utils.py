import pytest
from unittest.mock import MagicMock
from utils import (
    get_summary,
    get_chat_reply,
    get_emotions,
    split_content_to_sentences,
    calculate_similarities,
    get_valid_context,
    split_messages,
    convert_to_messages,
    save_raw_result
)
import schemas
import test_data_utils

def setup_module(module):

    module.client = MagicMock()
    module.client.chat.completions.create.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content="Mocked response"))]
    )

    module.supabase = MagicMock()
    module.supabase.table.return_value.insert.return_value.execute.return_value = MagicMock(
        data=[{'id': 1}]
    )

def test_get_summary():
    text = "これはテストです。"
    summary = get_summary(text)
    assert isinstance(summary, str)
    assert len(summary) > 0

def test_get_chat_reply():
    for data in test_data_utils.data_test_get_chat_reply:
        content = data["content"]
        messages = data["messages"]
        chatRound = data["chatRound"]
        reply = get_chat_reply(content, messages, chatRound)
        assert isinstance(reply, str)
        assert len(reply) >= 0
        match chatRound:
            case 0:
                assert "相談AI" in reply
            case 1:
                assert "不条理AI" in reply
            case 2:
                assert "禅AI" in reply

def test_get_emotions():
    for data in test_data_utils.data_test_get_emotions:
        emotions = get_emotions(data)
        emotions_instance = schemas.Emotions(**emotions)
        assert isinstance(emotions_instance, schemas.Emotions)
        assert emotions_instance != schemas.Emotions(
            joy=0.0,
            sadness=0.0,
            anger=0.0,
            fear=0.0
            )

def test_split_content_to_sentences():
    content = "これはテストです。これは2つ目の文です。"
    sentences = split_content_to_sentences(content)
    assert sentences == ["これはテストです。", "これは2つ目の文です。"]

def test_calculate_similarities():
    sentenceList = ["これはテストです。", "これは2つ目の文です。"]
    content = "これはテストです。"
    similarities = calculate_similarities(sentenceList, content)
    assert len(similarities) == 2

def test_get_valid_context():
    content = "テストコンテンツ"
    messages = ["過去のメッセージ1", "過去のメッセージ2"]
    valid_contexts = get_valid_context(content, messages)
    assert isinstance(valid_contexts, list)

def test_split_messages():
    messages = [{"role": "user", "content": f"メッセージ{i}"} for i in range(15)]
    image_sessions = split_messages(messages)
    assert len(image_sessions) == 3

def test_convert_to_messages():
    result = [MagicMock(content="メッセージ1", isUser=True), MagicMock(content="メッセージ2", isUser=False)]
    messages = convert_to_messages(result)
    assert len(messages) == 3

def test_save_raw_result():
    user_id = "test_user"
    result = [MagicMock(content="メッセージ1", isUser=True), MagicMock(content="メッセージ2", isUser=False)]
    session_id = save_raw_result(user_id, result)
    assert isinstance(session_id, int)
    assert session_id > 0