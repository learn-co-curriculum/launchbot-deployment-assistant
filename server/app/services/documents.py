"""Load deployment runbook chunks and convert them into LangChain documents."""

from __future__ import annotations

import json
from pathlib import Path

from langchain_core.documents import Document


DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "runbook_chunks.json"


def load_runbook_records(data_path: Path = DATA_PATH) -> list[dict]:
    """Load runbook chunk dictionaries from JSON."""
    with open(data_path, "r", encoding="utf-8") as file:
        return json.load(file)


def load_runbook_documents(data_path: Path = DATA_PATH) -> list[Document]:
    """Return LangChain Document objects with page content and metadata."""
    documents = []

    for record in load_runbook_records(data_path):
        documents.append(
            Document(
                page_content=record["text"],
                metadata={
                    "chunk_id": record["chunk_id"],
                    "source_id": record["source_id"],
                    "title": record["title"],
                    "category": record["category"],
                    "section": record["section"],
                },
                id=record["chunk_id"],
            )
        )

    return documents
