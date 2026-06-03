"""Request validation helpers."""

from __future__ import annotations

MIN_QUESTION_LENGTH = 3
MAX_QUESTION_LENGTH = 1200
MAX_TITLE_LENGTH = 80


def validate_question_payload(payload):
    """Validate a JSON request body containing a question."""
    if not isinstance(payload, dict):
        return None, {
            "error": "invalid_json",
            "message": "Request body must be a JSON object.",
        }

    if "question" not in payload:
        return None, {
            "error": "missing_question",
            "message": "Request body must include a question field.",
        }

    question = payload["question"]

    if not isinstance(question, str):
        return None, {
            "error": "invalid_question",
            "message": "Question must be a string.",
        }

    question = question.strip()

    if not question:
        return None, {
            "error": "empty_question",
            "message": "Question cannot be blank.",
        }

    if len(question) < MIN_QUESTION_LENGTH:
        return None, {
            "error": "question_too_short",
            "message": f"Question must be at least {MIN_QUESTION_LENGTH} characters long.",
        }

    if len(question) > MAX_QUESTION_LENGTH:
        return None, {
            "error": "question_too_long",
            "message": f"Question must be {MAX_QUESTION_LENGTH} characters or fewer.",
        }

    return question, None


def validate_thread_payload(payload):
    """Validate an optional thread title payload."""
    if not isinstance(payload, dict):
        return None, {
            "error": "invalid_json",
            "message": "Request body must be a JSON object.",
        }

    title = payload.get("title", "New deployment chat")

    if title is None:
        title = "New deployment chat"

    if not isinstance(title, str):
        return None, {
            "error": "invalid_title",
            "message": "Thread title must be a string.",
        }

    title = title.strip() or "New deployment chat"

    if len(title) > MAX_TITLE_LENGTH:
        title = title[:MAX_TITLE_LENGTH].rstrip()

    return title, None
