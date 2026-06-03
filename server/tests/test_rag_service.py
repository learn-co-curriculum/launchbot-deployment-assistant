from app.services.rag_service import answer_question, format_context, has_usable_context


class FakeDocument:
    def __init__(self, page_content, metadata):
        self.page_content = page_content
        self.metadata = metadata


class FakeVectorStore:
    def __init__(self, results):
        self.results = results
        self.query = None
        self.k = None

    def similarity_search_with_score(self, question, k):
        self.query = question
        self.k = k
        return self.results


class FakeChain:
    def __init__(self, answer="Use the public server URL and verify /api/health."):
        self.answer = answer
        self.inputs = None

    def invoke(self, inputs):
        self.inputs = inputs
        return self.answer


def sample_doc():
    return FakeDocument(
        page_content="A localhost URL points to the computer making the request.",
        metadata={
            "chunk_id": "chunk-localhost-001",
            "source_id": "DEP-101",
            "title": "Localhost vs Public Hosting",
            "category": "Deployment Concepts",
            "section": "Why localhost is not shareable",
        },
    )


def test_has_usable_context_rejects_empty_context():
    assert has_usable_context([]) is False
    assert has_usable_context([(FakeDocument("   ", {}), 0.9)]) is False


def test_format_context_includes_metadata_distance_and_text():
    context = format_context([(sample_doc(), 0.12345)])

    assert "DEP-101" in context
    assert "Localhost vs Public Hosting" in context
    assert "0.1235" in context
    assert "localhost URL" in context


def test_answer_question_runs_chain_with_retrieved_context():
    vector_store = FakeVectorStore([(sample_doc(), 0.12)])
    chain = FakeChain()

    response = answer_question(
        "  Why can my friend not open localhost?  ",
        vector_store=vector_store,
        chain=chain,
        top_k=2,
    )

    assert vector_store.query == "Why can my friend not open localhost?"
    assert vector_store.k == 2
    assert chain.inputs["question"] == "Why can my friend not open localhost?"
    assert "localhost URL" in chain.inputs["context"]
    assert response["answer"] == "Use the public server URL and verify /api/health."
    assert response["sources"][0]["source_id"] == "DEP-101"
    assert response["rag"]["retrieved_count"] == 1
    assert response["rag"]["fallback"] is False


def test_answer_question_returns_fallback_without_calling_chain():
    vector_store = FakeVectorStore([])
    chain = FakeChain(answer="This should not be used.")

    response = answer_question(
        "What is the lunch menu?",
        vector_store=vector_store,
        chain=chain,
        top_k=2,
    )

    assert chain.inputs is None
    assert response["sources"] == []
    assert response["rag"]["fallback"] is True
