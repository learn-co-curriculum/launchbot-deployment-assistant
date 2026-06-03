"""Format RAG responses for the API and React UI."""

from __future__ import annotations

from app.config import Config


def format_sources(scored_documents) -> list[dict]:
    """Return source metadata for retrieved documents without exposing full chunk text."""
    sources = []
    seen_chunk_ids = set()

    for document, distance in scored_documents:
        metadata = document.metadata or {}
        chunk_id = metadata.get("chunk_id")

        if chunk_id in seen_chunk_ids:
            continue

        seen_chunk_ids.add(chunk_id)

        sources.append(
            {
                "source_id": metadata.get("source_id", "unknown"),
                "title": metadata.get("title", "Untitled source"),
                "category": metadata.get("category", "Uncategorized"),
                "section": metadata.get("section", "General"),
                "chunk_id": chunk_id,
                "distance": round(float(distance), 4) if distance is not None else None,
            }
        )

    return sources


def format_rag_debug(
    *,
    scored_documents,
    context: str,
    fallback: bool = False,
    top_k: int = Config.TOP_K,
) -> dict:
    """Return developer-facing RAG metadata for verification."""
    return {
        "pipeline": "LangChain prompt template → ChatOllama → StrOutputParser",
        "components": {
            "vector_store": "Chroma",
            "retrieval_method": "similarity_search_with_score",
            "prompt_template": "ChatPromptTemplate",
            "chat_model": "ChatOllama",
            "output_parser": "StrOutputParser",
        },
        "retrieved_count": len(scored_documents),
        "retrieved_chunk_ids": [
            (document.metadata or {}).get("chunk_id")
            for document, _distance in scored_documents
        ],
        "top_k": top_k,
        "context_characters": len(context),
        "fallback": fallback,
        "score_type": "Chroma distance; lower usually means closer for this lesson setup",
        "models": {
            "embedding": Config.EMBEDDING_MODEL,
            "generation": Config.GENERATION_MODEL,
        },
    }


def format_success_response(answer: str, sources: list[dict], rag_debug: dict) -> dict:
    """Return the successful API response."""
    return {
        "answer": answer,
        "sources": sources,
        "rag": rag_debug,
    }


def format_fallback_response(rag_debug: dict | None = None) -> dict:
    """Return a safe fallback response."""
    return {
        "answer": Config.FALLBACK_MESSAGE,
        "sources": [],
        "rag": rag_debug
        or {
            "fallback": True,
            "retrieved_count": 0,
            "models": {
                "embedding": Config.EMBEDDING_MODEL,
                "generation": Config.GENERATION_MODEL,
            },
        },
    }
