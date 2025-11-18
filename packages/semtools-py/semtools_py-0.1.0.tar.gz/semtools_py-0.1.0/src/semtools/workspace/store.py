import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from lancedb.index import IvfPq
import lancedb
import lancedb.db
import pyarrow as pa

from .models import WorkspaceConfig, WorkspaceStats


@dataclass
class DocMeta:
    """Metadata for a document in the workspace."""

    path: str
    size_bytes: int
    mtime: int

    def id(self) -> int:
        """Generates a deterministic 32-bit signed integer ID from the path."""
        h = hashlib.sha256(self.path.encode("utf-8")).digest()
        return int.from_bytes(h[:4], byteorder="big", signed=True)


@dataclass
class LineEmbedding:
    """Represents a single line's embedding and metadata."""

    path: str
    line_number: int
    embedding: List[float]

    def id(self) -> int:
        """Generates a deterministic 32-bit signed integer ID from path and line number."""
        h = hashlib.sha256(f"{self.path}:{self.line_number}".encode("utf-8")).digest()
        return int.from_bytes(h[:4], byteorder="big", signed=True)


@dataclass
class RankedLine:
    """Represents a search result from the workspace store."""

    path: str
    line_number: int
    distance: float


class Store:
    """Manages all database interactions for a semtools workspace."""

    def __init__(self, db: lancedb.db.AsyncConnection, config: WorkspaceConfig):
        self.db = db
        self.config = config

    @staticmethod
    def chunk_list(data: List, chunk_size: int) -> List[List]:
        """Yield successive n-sized chunks from a list."""
        if not data:
            return []
        return [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]

    @staticmethod
    def _build_path_filter(paths: List[str]) -> str:
        """Builds a SQL 'IN' clause for a list of paths, escaping single quotes."""
        escaped_paths = [p.replace("'", "''") for p in paths]
        quoted_paths = [f"'{p}'" for p in escaped_paths]
        return f"path IN ({', '.join(quoted_paths)})"

    @classmethod
    async def create(cls, config: WorkspaceConfig) -> "Store":
        db_path = Path(config.root_dir)
        db_path.mkdir(parents=True, exist_ok=True)
        db = await lancedb.connect_async(str(db_path))
        return cls(db, config)

    async def get_existing_docs(self, paths: List[str]) -> Dict[str, DocMeta]:
        """Gets existing document metadata for the given paths."""
        if not paths or "documents" not in await self.db.table_names():
            return {}

        existing_docs = {}
        tbl = await self.db.open_table("documents")

        for chunk in self.chunk_list(paths, self.config.in_batch_size):
            path_filter = self._build_path_filter(chunk)
            results = await tbl.query().where(path_filter).to_list()
            for r in results:
                existing_docs[r["path"]] = DocMeta(
                    path=r["path"], size_bytes=r["size_bytes"], mtime=r["mtime"]
                )

        return existing_docs

    async def _delete_document_metadata(self, paths: List[str]) -> None:
        if not paths or "documents" not in await self.db.table_names():
            return
        tbl = await self.db.open_table("documents")
        for chunk in self.chunk_list(paths, self.config.in_batch_size):
            path_filter = self._build_path_filter(chunk)
            await tbl.delete(path_filter)

    async def _delete_line_embeddings(self, paths: List[str]) -> None:
        if not paths or "line_embeddings" not in await self.db.table_names():
            return
        tbl = await self.db.open_table("line_embeddings")
        for chunk in self.chunk_list(paths, self.config.in_batch_size):
            path_filter = self._build_path_filter(chunk)
            await tbl.delete(path_filter)

    async def delete_documents(self, paths: List[str]) -> None:
        """Deletes documents and all associated line embeddings by path."""
        await self._delete_document_metadata(paths)
        await self._delete_line_embeddings(paths)

    async def upsert_document_metadata(self, metas: List[DocMeta]) -> None:
        """Upserts document metadata for tracking file changes."""
        if not metas:
            return

        paths = [m.path for m in metas]
        await self._delete_document_metadata(paths)

        data = [
            {"id": m.id(), "path": m.path, "size_bytes": m.size_bytes, "mtime": m.mtime}
            for m in metas
        ]

        if "documents" not in await self.db.table_names():
            schema = pa.schema(
                [
                    pa.field("id", pa.int32()),
                    pa.field("path", pa.string()),
                    pa.field("size_bytes", pa.int64()),
                    pa.field("mtime", pa.int64()),
                ]
            )
            await self.db.create_table("documents", data=data, schema=schema)
        else:
            tbl = await self.db.open_table("documents")
            await tbl.add(data)

    async def upsert_line_embeddings(self, line_embeddings: List[LineEmbedding]) -> None:
        """Upserts line-level embeddings for documents."""
        if not line_embeddings:
            return

        paths = sorted(list({le.path for le in line_embeddings}))
        await self._delete_line_embeddings(paths)

        dim = len(line_embeddings[0].embedding)
        data = [
            {
                "id": le.id(),
                "path": le.path,
                "line_number": le.line_number,
                "vector": le.embedding,
            }
            for le in line_embeddings
        ]

        if "line_embeddings" not in await self.db.table_names():
            schema = pa.schema(
                [
                    pa.field("id", pa.int32()),
                    pa.field("path", pa.string()),
                    pa.field("line_number", pa.int32()),
                    pa.field("vector", pa.list_(pa.float32(), dim)),
                ]
            )
            await self.db.create_table("line_embeddings", data=data, schema=schema)
        else:
            tbl = await self.db.open_table("line_embeddings")
            await tbl.add(data)

        await self._ensure_line_vector_index()

    async def _ensure_line_vector_index(self) -> None:
        """Ensures a vector index exists for the line embeddings table."""
        tbl = await self.db.open_table("line_embeddings")
        indexes = await tbl.list_indices()
        if not indexes:
            try:
                # Let LanceDB create an automatic index
                await tbl.create_index("vector", config=IvfPq(distance_type="cosine"))
            except Exception as e:
                # Handling for insufficient data for PQ training
                if "Not enough data to train" in str(e) or "Requires 256 rows" in str(e):
                    print(
                        "Warning: Skipping line embeddings vector index creation due to insufficient data. "
                        "Database will use brute-force search."
                    )
                else:
                    raise e

    async def get_all_document_paths(self) -> List[str]:
        """Gets all document paths in the workspace."""
        if "documents" not in await self.db.table_names():
            return []
        tbl = await self.db.open_table("documents")
        results = await tbl.query().select(["path"]).to_list()
        return [row["path"] for row in results]

    async def get_stats(self) -> WorkspaceStats:
        """Get statistics about the workspace store."""
        table_names = await self.db.table_names()
        doc_count = 0
        has_index = False

        if "documents" in table_names:
            doc_table = await self.db.open_table("documents")
            doc_count = await doc_table.count_rows()

        if "line_embeddings" in table_names:
            line_table = await self.db.open_table("line_embeddings")
            if len(await line_table.list_indices()) > 0:
                has_index = True

        return WorkspaceStats(
            total_documents=doc_count,
            has_index=has_index,
            index_type="IVF_PQ" if has_index else None,
        )

    async def search_line_embeddings(
        self,
        query_vec: List[float],
        subset_paths: List[str],
        top_k: int,
        max_distance: Optional[float] = None,
    ) -> List[RankedLine]:
        """Searches line embeddings directly for precise results."""
        if not subset_paths or "line_embeddings" not in await self.db.table_names():
            return []

        all_results = []
        tbl = await self.db.open_table("line_embeddings")

        for chunk in self.chunk_list(subset_paths, self.config.in_batch_size):
            path_filter = self._build_path_filter(chunk)
            query = (
                tbl.vector_search(query_vec)
                .where(path_filter)
                .limit(top_k * self.config.oversample_factor)
                .distance_type("cosine")
            )
            results = await query.to_list()
            for r in results:
                all_results.append(
                    RankedLine(path=r["path"], line_number=r["line_number"], distance=r["_distance"])
                )

        all_results.sort(key=lambda rkd_l: rkd_l.distance)

        if max_distance is not None:
            return [r for r in all_results if r.distance <= max_distance]

        return all_results[:top_k]