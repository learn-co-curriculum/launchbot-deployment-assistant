"""LangChain + Chroma vector store helpers."""

from __future__ import annotations

import shutil
from pathlib import Path

from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings

from app.config import Config
from app.services.documents import load_runbook_documents


def build_embedding_model():
    """Create the Ollama embedding wrapper used by Chroma."""
    return OllamaEmbeddings(
        model=Config.EMBEDDING_MODEL,
        base_url=Config.OLLAMA_BASE_URL,
    )


def get_vector_store() -> Chroma:
    """Return the persistent Chroma vector store."""
    Path(Config.CHROMA_PATH).mkdir(parents=True, exist_ok=True)

    return Chroma(
        collection_name=Config.COLLECTION_NAME,
        persist_directory=Config.CHROMA_PATH,
        embedding_function=build_embedding_model(),
    )


def reset_chroma_db(path: str = Config.CHROMA_PATH) -> None:
    """Delete the Chroma directory so the demo can be reseeded cleanly."""
    db_path = Path(path)
    if db_path.exists():
        shutil.rmtree(db_path)


def seed_vector_store(reset: bool = True) -> int:
    """Seed Chroma with the deployment runbook chunks."""
    if reset:
        reset_chroma_db()

    documents = load_runbook_documents()
    vector_store = get_vector_store()
    ids = [doc.metadata["chunk_id"] for doc in documents]
    vector_store.add_documents(documents, ids=ids)

    return len(documents)


def collection_count() -> int:
    """Return the number of records in the Chroma collection."""
    vector_store = get_vector_store()
    return vector_store._collection.count()
