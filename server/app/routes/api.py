"""API routes for LaunchBot."""

from __future__ import annotations

from flask import Blueprint, current_app, jsonify, request

from app.services.health_service import check_ollama, vector_store_count
from app.services.rag_service import RAGServiceError, answer_question
from app.services.thread_service import (
    add_message,
    create_thread,
    delete_thread,
    get_thread,
    list_threads,
)
from app.services.validation import validate_question_payload, validate_thread_payload


api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.get("/health")
def health():
    """Return a basic app health response."""
    return jsonify(
        {
            "status": "ok",
            "app": "LaunchBot Deployment Assistant",
            "database_path": current_app.config["DATABASE_PATH"],
            "chroma_path": current_app.config["CHROMA_PATH"],
            "models": {
                "generation": current_app.config["GENERATION_MODEL"],
                "embedding": current_app.config["EMBEDDING_MODEL"],
            },
        }
    )


@api_bp.get("/rag/health")
def rag_health():
    """Return health information for Ollama and the vector store."""
    try:
        chroma_count = vector_store_count()
    except Exception as exc:  # pragma: no cover - depends on local Chroma/Ollama state
        chroma_count = None
        chroma_error = str(exc)
    else:
        chroma_error = None

    ollama_status = check_ollama(current_app.config["OLLAMA_BASE_URL"])
    status = "ok" if chroma_count is not None and ollama_status["available"] else "degraded"

    return jsonify(
        {
            "status": status,
            "ollama": ollama_status,
            "chroma": {
                "collection": current_app.config["COLLECTION_NAME"],
                "count": chroma_count,
                "error": chroma_error,
            },
        }
    )


@api_bp.get("/threads")
def index_threads():
    """Return all chat threads."""
    return jsonify({"threads": list_threads(current_app.config["DATABASE_PATH"])})


@api_bp.post("/threads")
def create_chat_thread():
    """Create a new chat thread."""
    payload = request.get_json(silent=True) or {}
    title, error = validate_thread_payload(payload)

    if error:
        return jsonify(error), 400

    thread = create_thread(current_app.config["DATABASE_PATH"], title=title)
    return jsonify({"thread": thread}), 201


@api_bp.get("/threads/<thread_id>")
def show_thread(thread_id: str):
    """Return one thread and its messages."""
    thread = get_thread(current_app.config["DATABASE_PATH"], thread_id)

    if thread is None:
        return jsonify({"error": "thread_not_found", "message": "Thread not found."}), 404

    return jsonify(thread)


@api_bp.delete("/threads/<thread_id>")
def destroy_thread(thread_id: str):
    """Delete one thread and its messages."""
    deleted = delete_thread(current_app.config["DATABASE_PATH"], thread_id)

    if not deleted:
        return jsonify({"error": "thread_not_found", "message": "Thread not found."}), 404

    return jsonify({"deleted": True, "thread_id": thread_id})


@api_bp.post("/threads/<thread_id>/messages")
def create_thread_message(thread_id: str):
    """Add a user question to a thread, run RAG, and store the assistant response."""
    thread = get_thread(current_app.config["DATABASE_PATH"], thread_id)

    if thread is None:
        return jsonify({"error": "thread_not_found", "message": "Thread not found."}), 404

    payload = request.get_json(silent=True)
    question, error = validate_question_payload(payload)

    if error:
        return jsonify(error), 400

    add_message(
        current_app.config["DATABASE_PATH"],
        thread_id=thread_id,
        role="user",
        content=question,
    )

    try:
        rag_response = answer_question(question)
    except RAGServiceError as exc:
        return jsonify({"error": "rag_service_error", "message": str(exc)}), 502

    assistant_message = add_message(
        current_app.config["DATABASE_PATH"],
        thread_id=thread_id,
        role="assistant",
        content=rag_response["answer"],
        metadata={
            "sources": rag_response["sources"],
            "rag": rag_response["rag"],
        },
    )

    updated_thread = get_thread(current_app.config["DATABASE_PATH"], thread_id)

    return jsonify(
        {
            "thread": updated_thread["thread"],
            "messages": updated_thread["messages"],
            "assistant_message": assistant_message,
            "sources": rag_response["sources"],
            "rag": rag_response["rag"],
        }
    )


@api_bp.post("/ask")
def ask_once():
    """Run a one-off RAG request without storing a chat thread."""
    payload = request.get_json(silent=True)
    question, error = validate_question_payload(payload)

    if error:
        return jsonify(error), 400

    try:
        response = answer_question(question)
    except RAGServiceError as exc:
        return jsonify({"error": "rag_service_error", "message": str(exc)}), 502

    return jsonify(response)
