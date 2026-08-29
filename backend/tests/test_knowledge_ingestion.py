import pytest
import os
import tempfile
from app.services.knowledge_service import (
    KnowledgeIngestionService,
    parse_frontmatter,
    chunk_markdown_document,
)
from app.services.vector_store import LocalVectorStore
from app.services.embedding_service import EmbeddingService


def test_parse_frontmatter():
    doc = """---
source_id: KB-TEST-001
title: Test Title
skill: test skill
keywords: [alpha, beta, gamma]
---

# Heading

Some content here.
"""
    meta, body = parse_frontmatter(doc)
    assert meta["source_id"] == "KB-TEST-001"
    assert meta["title"] == "Test Title"
    assert meta["skill"] == "test skill"
    assert meta["keywords"] == ["alpha", "beta", "gamma"]
    assert "# Heading" in body


def test_chunk_markdown_document():
    body = """# Main Title

Introduction text.

## Core Concepts
Concept 1 details.
Concept 2 details.

## Practice Projects
Build a task manager.
"""
    chunks = chunk_markdown_document(
        source_id="KB-T1",
        title="Testing Doc",
        skill="Python",
        metadata={"category": "test"},
        markdown_body=body,
    )

    assert len(chunks) == 3
    assert chunks[0].section == "Overview"
    assert chunks[1].section == "Core Concepts"
    assert chunks[2].section == "Practice Projects"
    assert all(c.source_id == "KB-T1" for c in chunks)
    assert all(c.skill == "python" for c in chunks)


@pytest.mark.asyncio
async def test_idempotent_ingestion():
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Create dummy doc
        doc_path = os.path.join(tmp_dir, "sample.md")
        with open(doc_path, "w", encoding="utf-8") as f:
            f.write("""---
source_id: KB-SAMPLE-01
title: Sample Skill
skill: sample
---
## Overview
Sample overview text.

## Core Concepts
Sample concept text.
""")

        store = LocalVectorStore()
        emb_service = EmbeddingService(api_key=None)
        service = KnowledgeIngestionService(vector_store=store, embedding_service=emb_service, knowledge_dir=tmp_dir)

        # First ingestion
        res1 = await service.ingest_all()
        assert res1["files_ingested"] == 1
        initial_chunk_count = len(store.get_all_chunks())
        assert initial_chunk_count > 0

        # Second ingestion (idempotency check)
        res2 = await service.ingest_all()
        assert res2["files_ingested"] == 1
        second_chunk_count = len(store.get_all_chunks())
        assert second_chunk_count == initial_chunk_count, "Duplicate ingestion must not duplicate chunk records"
