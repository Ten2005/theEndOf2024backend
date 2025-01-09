from fastapi.testclient import TestClient
from main import app
import schemas
import test_data_main

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}

def test_summarize():
    request_data = schemas.SummarizeRequest(text="This is a test text.")
    response = client.post("/summarize", json=request_data.model_dump())
    assert response.status_code == 200
    assert "summary" in response.json()
    assert isinstance(response.json()["summary"], str)


def test_chat():
    for data in test_data_main.chat_test_data:
        request_data = schemas.ChatRequest(
            content=data["content"],
            messages=data["messages"],
            chatRound=data["chatRound"]
        )
        response = client.post("/chat", json=request_data.model_dump())
        assert response.status_code == 200
        assert "reply" in response.json()
        if (data["chatRound"] == 0 or data["chatRound"] == 1 or data["chatRound"] == 2):
            assert isinstance(response.json()["reply"], str)
        else:
            assert response.json()["reply"] == ""

def test_complete():
    for data in test_data_main.complete_test_data:
        request_data = schemas.CompleteRequest(
            user_id=data["user_id"],
            messages=data["messages"],
            timestamp=data["timestamp"]
        )
    response = client.post("/complete", json=request_data.model_dump())
    assert response.status_code == 200

def test_sessions():
    request_data = schemas.SessionRequest(user_id='string')
    response = client.post("/sessions", json=request_data.model_dump())
    assert response.status_code == 200
