import pytest
from app.services.vector_store import LocalVectorStore, KnowledgeChunk
from app.services.embedding_service import EmbeddingService
from app.services.retrieval_service import RetrievalService


@pytest.mark.asyncio
async def test_retrieval_service():
    store = LocalVectorStore()
    emb = EmbeddingService(api_key=None)

    # Ingest Python and Docker test chunks
    py_text = "Python functions, dictionaries, loops, and backend REST APIs with FastAPI."
    doc_text = "Docker containerization, Dockerfiles, images, and docker-compose.yml."

    py_vec = await emb.get_embedding(py_text)
    doc_vec = await emb.get_embedding(doc_text)

    await store.add_chunks([
        KnowledgeChunk(
            chunk_id="chunk_py_01",
            source_id="KB-PY-001",
            skill="python",
            title="Python Development",
            section="Core",
            text=py_text,
            embedding=py_vec,
        ),
        KnowledgeChunk(
            chunk_id="chunk_doc_01",
            source_id="KB-DOC-001",
            skill="docker",
            title="Docker Containers",
            section="Core",
            text=doc_text,
            embedding=doc_vec,
        ),
    ])

    retrieval = RetrievalService(vector_store=store, embedding_service=emb, min_similarity=0.30)

    # 1. Retrieve Python
    py_res = await retrieval.retrieve_for_skill("Python")
    assert py_res.status == "sufficient"
    assert len(py_res.evidence_chunks) >= 1
    assert py_res.evidence_chunks[0].source_id == "KB-PY-001"
    assert "KB-PY-001" in py_res.source_ids

    # 2. Retrieve unknown skill returns insufficient evidence
    unknown_res = await retrieval.retrieve_for_skill("QuantumComputingLanguageXYZ", min_similarity=0.85)
    assert unknown_res.status == "insufficient_evidence"
    assert len(unknown_res.evidence_chunks) == 0
