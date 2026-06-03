from app.services.validation import validate_question_payload, validate_thread_payload


def test_validate_question_accepts_trimmed_question():
    question, error = validate_question_payload({"question": "  Why deploy to AWS?  "})

    assert error is None
    assert question == "Why deploy to AWS?"


def test_validate_question_rejects_blank_question():
    question, error = validate_question_payload({"question": "   "})

    assert question is None
    assert error["error"] == "empty_question"


def test_validate_thread_payload_defaults_title():
    title, error = validate_thread_payload({})

    assert error is None
    assert title == "New deployment chat"
