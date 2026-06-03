"""LangChain RAG service for LaunchBot."""

from __future__ import annotations

from langchain_core.output_parsers import StrOutputParser
from langchain_ollama import ChatOllama

from app.config import Config
from app.services.prompt_templates import build_prompt_template
from app.services.response_formatter import (
    format_fallback_response,
    format_rag_debug,
    format_sources,
    format_success_response,
)
from app.services.vector_store import get_vector_store


class RAGServiceError(RuntimeError):
    """Raised when the RAG pipeline cannot complete."""


def build_chat_model() -> ChatOllama:
    """Create the Ollama chat model wrapper."""
    return ChatOllama(
        model=Config.GENERATION_MODEL,
        base_url=Config.OLLAMA_BASE_URL,
        temperature=Config.TEMPERATURE,
    )


def build_chain(prompt_template=None, llm=None):
    """Compose prompt, model, and output parser into a LangChain runnable chain."""
    prompt_template = prompt_template or build_prompt_template()
    llm = llm or build_chat_model()

    return prompt_template | llm | StrOutputParser()


def retrieve_context(question: str, *, vector_store=None, top_k: int = Config.TOP_K):
    """Retrieve documents and distances from Chroma."""
    vector_store = vector_store or get_vector_store()
    return vector_store.similarity_search_with_score(question, k=top_k)


def has_usable_context(scored_documents) -> bool:
    """Return True when retrieval produced at least one non-empty document."""
    return any((document.page_content or "").strip() for document, _distance in scored_documents)


def format_context(scored_documents) -> str:
    """Format retrieved documents into a prompt-ready context block."""
    blocks = []

    for index, (document, distance) in enumerate(scored_documents, start=1):
        metadata = document.metadata or {}

        blocks.append(
            "\n".join(
                [
                    f"[Context {index}]",
                    f"Source ID: {metadata.get('source_id', 'unknown')}",
                    f"Title: {metadata.get('title', 'Untitled source')}",
                    f"Section: {metadata.get('section', 'General')}",
                    f"Category: {metadata.get('category', 'Uncategorized')}",
                    f"Chunk ID: {metadata.get('chunk_id', 'unknown')}",
                    f"Distance: {float(distance):.4f}" if distance is not None else "Distance: unknown",
                    "Text:",
                    document.page_content.strip(),
                ]
            )
        )

    return "\n\n".join(blocks)


def answer_question(
    question: str,
    *,
    vector_store=None,
    chain=None,
    top_k: int = Config.TOP_K,
) -> dict:
    """Run the RAG workflow for one validated question."""
    cleaned_question = question.strip()

    try:
        scored_documents = retrieve_context(
            cleaned_question,
            vector_store=vector_store,
            top_k=top_k,
        )
    except Exception as exc:  # pragma: no cover - depends on local Ollama/Chroma state
        raise RAGServiceError(
            f"Retrieval failed. Check Chroma and the embedding model. Details: {exc}"
        ) from exc

    context = format_context(scored_documents)
    has_context = has_usable_context(scored_documents)
    rag_debug = format_rag_debug(
        scored_documents=scored_documents,
        context=context,
        fallback=not has_context,
        top_k=top_k,
    )

    if not has_context:
        return format_fallback_response(rag_debug)

    try:
        chain = chain or build_chain()
        answer = chain.invoke(
            {
                "context": context,
                "question": cleaned_question,
            }
        )
    except Exception as exc:  # pragma: no cover - depends on local Ollama state
        raise RAGServiceError(
            f"Generation failed. Check Ollama and the generation model. Details: {exc}"
        ) from exc

    answer = str(answer).strip()

    if not answer:
        rag_debug["fallback"] = True
        return format_fallback_response(rag_debug)

    return format_success_response(
        answer=answer,
        sources=format_sources(scored_documents),
        rag_debug=rag_debug,
    )
