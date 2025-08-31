import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_check():
    """Test the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_chat_health():
    """Test the chat service health check"""
    response = client.get("/chat/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_chat_endpoint_faq():
    """Test chat endpoint with FAQ response"""
    response = client.post("/chat/", json={"message": "What is your name?"})
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "source" in data
    assert data["source"] in ["faq", "gpt", "fallback"]

def test_chat_endpoint_empty_message():
    """Test chat endpoint with empty message"""
    response = client.post("/chat/", json={"message": ""})
    assert response.status_code == 400

def test_chat_endpoint_missing_message():
    """Test chat endpoint without message field"""
    response = client.post("/chat/", json={})
    assert response.status_code == 422

def test_get_faqs():
    """Test getting all FAQs"""
    response = client.get("/chat/faqs")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_add_faq():
    """Test adding a new FAQ"""
    faq_data = {
        "question": "Test question?",
        "answer": "Test answer."
    }
    response = client.post("/chat/faqs", json=faq_data)
    assert response.status_code == 200
    data = response.json()
    assert data["question"] == faq_data["question"]
    assert data["answer"] == faq_data["answer"]

def test_get_logs():
    """Test getting fallback logs"""
    response = client.get("/chat/logs?limit=5")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

if __name__ == "__main__":
    pytest.main([__file__]) 