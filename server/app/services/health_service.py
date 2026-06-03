"""Health checks for external services used by LaunchBot."""

from __future__ import annotations

import json
from urllib.error import URLError
from urllib.request import urlopen

from app.services.vector_store import collection_count


def check_ollama(base_url: str, timeout: float = 2.0) -> dict:
    """Check whether the Ollama REST API is reachable."""
    url = base_url.rstrip("/") + "/api/tags"

    try:
        with urlopen(url, timeout=timeout) as response:  # nosec - local teaching service URL
            payload = json.loads(response.read().decode("utf-8"))
    except (URLError, TimeoutError, json.JSONDecodeError, OSError) as exc:
        return {
            "available": False,
            "base_url": base_url,
            "error": str(exc),
        }

    models = [model.get("name") for model in payload.get("models", [])]

    return {
        "available": True,
        "base_url": base_url,
        "models": models,
    }


def vector_store_count() -> int:
    """Return the Chroma collection count."""
    return collection_count()
