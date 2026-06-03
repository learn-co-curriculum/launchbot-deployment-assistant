import app.routes.api as api_routes
from app import create_app
from app.config import Config
from app.services.rag_service import RAGServiceError


class TestConfig(Config):
    TESTING = True
    DATABASE_PATH = "instance/test-launchbot.sqlite"
    CHROMA_PATH = "instance/test-chroma"


def make_client():
    flask_app = create_app(TestConfig)
    return flask_app.test_client()


def test_create_thread_and_show_thread():
    client = make_client()

    response = client.post("/api/threads", json={"title": "Deploy test"})

    assert response.status_code == 201

    thread_id = response.get_json()["thread"]["id"]
    show_response = client.get(f"/api/threads/{thread_id}")

    assert show_response.status_code == 200
    assert show_response.get_json()["thread"]["title"] == "Deploy test"


def test_thread_message_stores_rag_response(monkeypatch):
    def fake_answer_question(question):
        return {
            "answer": "Deploy the app on a public server.",
            "sources": [{"source_id": "DEP-101"}],
            "rag": {"fallback": False, "retrieved_count": 1},
        }

    monkeypatch.setattr(api_routes, "answer_question", fake_answer_question)

    client = make_client()
    created = client.post("/api/threads", json={"title": "Test"}).get_json()
    thread_id = created["thread"]["id"]

    response = client.post(
        f"/api/threads/{thread_id}/messages",
        json={"question": "Why does localhost not work?"},
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["messages"][-1]["role"] == "assistant"
    assert data["sources"][0]["source_id"] == "DEP-101"


def test_ask_route_rejects_blank_question(monkeypatch):
    client = make_client()
    response = client.post("/api/ask", json={"question": "   "})

    assert response.status_code == 400
    assert response.get_json()["error"] == "empty_question"


def test_ask_route_returns_502_for_rag_error(monkeypatch):
    def fake_answer_question(question):
        raise RAGServiceError("Ollama unavailable")

    monkeypatch.setattr(api_routes, "answer_question", fake_answer_question)

    client = make_client()
    response = client.post("/api/ask", json={"question": "How do I deploy?"})

    assert response.status_code == 502
    assert response.get_json()["error"] == "rag_service_error"
