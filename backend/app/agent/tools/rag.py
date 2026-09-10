from langchain.tools import tool, ToolRuntime
from app.agent.constants import ALLOWED_RAG_COMPANIES, MIN_RAG_SCORE
from app.agent.utils import normalize_company
from app.shared.vector_store import index
from app.agent.provider.gemini import embeddings_model
from app.agent.grader import grade_document


@tool
def rag_search(query: str, company: list[str], runtime: ToolRuntime):
    """Retrieve and validate financial documents using semantic search with relevance filtering."""
    _user = runtime.context["user"]

    company = [normalize_company(c) for c in company]
    allowed = [c for c in company if c in ALLOWED_RAG_COMPANIES]

    if not allowed:
        return {"found": False, "sources": []}

    embedding = embeddings_model.embed_query(query)

    results = index.query(
        vector=embedding,
        top_k=20,
        include_metadata=True,
        namespace="10k",
        filter={"company": {"$in": allowed}},
    )

    candidates = [m for m in results.matches if m.score >= MIN_RAG_SCORE]

    # per doc grading
    final = []
    for m in sorted(candidates, key=lambda x: x.score, reverse=True):
        doc = m.metadata["text"]

        if grade_document(query, doc):
            final.append(
                {
                    "company": m.metadata["company"],
                    "document": m.metadata["source"],
                    "page": m.metadata["page"],
                    "content": doc,
                    "score": m.score,
                }
            )

        if len(final) == 6:
            break

    if not final:
        return {"found": False, "sources": []}

    return {"found": True, "sources": final}
