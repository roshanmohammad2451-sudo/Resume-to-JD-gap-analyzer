import glob
import logging
import os
import re
from typing import List, Dict, Any, Tuple
from app.services.vector_store import KnowledgeChunk, BaseVectorStore, default_vector_store
from app.services.embedding_service import EmbeddingService, default_embedding_service
from app.services.gap_engine import normalize_skill_name
from app.core.config import settings

logger = logging.getLogger(__name__)


def parse_frontmatter(content: str) -> Tuple[Dict[str, Any], str]:
    """
    Extracts YAML-style frontmatter headers if present at the top of markdown documents.
    """
    metadata: Dict[str, Any] = {}
    body = content

    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            fm_text = parts[1].strip()
            body = parts[2].strip()
            for line in fm_text.splitlines():
                if ":" in line:
                    key, val = line.split(":", 1)
                    key = key.strip()
                    val = val.strip()
                    if val.startswith("[") and val.endswith("]"):
                        # Simple list parsing
                        items = [x.strip(" '\"") for x in val[1:-1].split(",") if x.strip()]
                        metadata[key] = items
                    else:
                        metadata[key] = val.strip("'\"")

    return metadata, body


def chunk_markdown_document(
    source_id: str,
    title: str,
    skill: str,
    metadata: Dict[str, Any],
    markdown_body: str,
) -> List[KnowledgeChunk]:
    """
    Splits markdown document into semantic sections based on level-2 headings (##).
    Preserves document metadata and assigns stable chunk IDs.
    """
    chunks: List[KnowledgeChunk] = []
    norm_skill = normalize_skill_name(skill)

    # Split on H2 headings (## Heading)
    sections = re.split(r"(^##\s+.+$)", markdown_body, flags=re.MULTILINE)

    if len(sections) <= 1:
        # Single chunk document
        chunk_id = f"{source_id}_chunk_01"
        chunks.append(
            KnowledgeChunk(
                chunk_id=chunk_id,
                source_id=source_id,
                skill=norm_skill,
                title=title,
                section="General",
                text=markdown_body.strip(),
                metadata=metadata,
            )
        )
        return chunks

    current_section = "Overview"
    current_content = sections[0].strip()
    idx = 1

    if current_content:
        chunks.append(
            KnowledgeChunk(
                chunk_id=f"{source_id}_chunk_{idx:02d}",
                source_id=source_id,
                skill=norm_skill,
                title=title,
                section=current_section,
                text=current_content,
                metadata=metadata,
            )
        )
        idx += 1

    for i in range(1, len(sections), 2):
        header_line = sections[i].strip()
        section_name = header_line.lstrip("#").strip()
        section_body = sections[i + 1].strip() if (i + 1) < len(sections) else ""
        combined_text = f"{section_name}\n\n{section_body}".strip()

        if not combined_text:
            continue

        chunk_id = f"{source_id}_chunk_{idx:02d}"
        chunks.append(
            KnowledgeChunk(
                chunk_id=chunk_id,
                source_id=source_id,
                skill=norm_skill,
                title=title,
                section=section_name,
                text=combined_text,
                metadata={**metadata, "section": section_name},
            )
        )
        idx += 1

    return chunks


class KnowledgeIngestionService:
    """
    Service responsible for parsing markdown documents from data/knowledge/,
    chunking text, computing vector embeddings, and indexing in the vector store.
    """

    def __init__(
        self,
        vector_store: BaseVectorStore = default_vector_store,
        embedding_service: EmbeddingService = default_embedding_service,
        knowledge_dir: str = settings.KNOWLEDGE_BASE_DIR,
    ):
        self.vector_store = vector_store
        self.embedding_service = embedding_service
        self.knowledge_dir = knowledge_dir

    def _resolve_knowledge_dir(self) -> str:
        """Finds knowledge directory relative to workspace root."""
        if os.path.isabs(self.knowledge_dir) and os.path.exists(self.knowledge_dir):
            return self.knowledge_dir

        candidates = [
            self.knowledge_dir,
            os.path.join("..", self.knowledge_dir),
            os.path.join(os.path.dirname(__file__), "..", "..", "..", self.knowledge_dir),
            os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../data/knowledge")),
        ]
        for c in candidates:
            if os.path.exists(c) and os.path.isdir(c):
                return os.path.abspath(c)
        return self.knowledge_dir

    async def ingest_file(self, file_path: str) -> List[KnowledgeChunk]:
        """Ingests a single markdown file into the vector store."""
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        metadata, body = parse_frontmatter(content)
        base_name = os.path.splitext(os.path.basename(file_path))[0]

        source_id = metadata.get("source_id", f"KB-{base_name.upper()}-001")
        title = metadata.get("title", base_name.replace("_", " ").title())
        skill = metadata.get("skill", base_name.replace("_", " "))

        chunks = chunk_markdown_document(
            source_id=source_id,
            title=title,
            skill=skill,
            metadata=metadata,
            markdown_body=body,
        )

        # Generate embeddings for chunks
        for chunk in chunks:
            # Semantic text combines title, skill, and chunk body for rich embedding context
            semantic_text = f"Skill: {chunk.skill} | Topic: {chunk.title} | Section: {chunk.section}\n{chunk.text}"
            chunk.embedding = await self.embedding_service.get_embedding(semantic_text)

        await self.vector_store.add_chunks(chunks)
        return chunks

    async def ingest_all(self, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Ingests all knowledge documents from data/knowledge/.
        Idempotent: running twice updates/overwrites cleanly without duplicating records.
        """
        target_dir = self._resolve_knowledge_dir()
        if not os.path.exists(target_dir):
            logger.warning("Knowledge directory not found at: %s", target_dir)
            return {"status": "error", "message": f"Directory not found: {target_dir}", "files_ingested": 0, "chunks_indexed": 0}

        pattern = os.path.join(target_dir, "*.md")
        files = glob.glob(pattern)

        if not files:
            logger.warning("No markdown files found in knowledge directory: %s", target_dir)
            return {"status": "warning", "message": "No files found", "files_ingested": 0, "chunks_indexed": 0}

        if force_refresh:
            self.vector_store.clear()

        total_chunks = 0
        ingested_files = []

        for file_path in files:
            try:
                chunks = await self.ingest_file(file_path)
                total_chunks += len(chunks)
                ingested_files.append(os.path.basename(file_path))
            except Exception as e:
                logger.error("Failed to ingest file %s: %s", file_path, e)

        logger.info(
            "Successfully ingested %d knowledge files with %d total chunks into vector store.",
            len(ingested_files),
            total_chunks
        )

        return {
            "status": "ok",
            "files_ingested": len(ingested_files),
            "chunks_indexed": total_chunks,
            "file_list": ingested_files,
        }


default_knowledge_service = KnowledgeIngestionService()
