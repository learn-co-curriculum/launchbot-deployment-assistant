"""Configuration helpers for LaunchBot."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv


ROOT_DIR = Path(__file__).resolve().parents[1]
load_dotenv(ROOT_DIR / ".env")


def _path_from_env(name: str, default: str) -> str:
    """Return an absolute path for a path-like environment variable."""
    value = os.getenv(name, default)
    path = Path(value)

    if not path.is_absolute():
        path = ROOT_DIR / path

    return str(path)


class Config:
    """Application configuration loaded from environment variables."""

    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    DATABASE_PATH = _path_from_env("DATABASE_PATH", "instance/launchbot.sqlite")
    CHROMA_PATH = _path_from_env("CHROMA_PATH", "instance/chroma")
    COLLECTION_NAME = os.getenv("COLLECTION_NAME", "deployment_runbook")

    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
    GENERATION_MODEL = os.getenv("GENERATION_MODEL", "llama3.2")
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")

    TOP_K = int(os.getenv("TOP_K", "2"))
    TEMPERATURE = float(os.getenv("TEMPERATURE", "0"))

    FALLBACK_MESSAGE = (
        "I do not have enough approved deployment runbook context to answer that question. "
        "Check the deployment notes, AWS console, or instructor guidance before acting."
    )

    JSON_SORT_KEYS = False
