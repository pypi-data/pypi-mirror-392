import asyncio
import os
import aiofiles
import aiofiles.os
import numpy as np
from scipy.spatial.distance import cosine
from typing import List, Optional

from model2vec import StaticModel

from ..workspace import Store, Workspace, WorkspaceError
from ..workspace.store import DocMeta, LineEmbedding, RankedLine
from .enums import EmbeddingModel
from .loader import DocumentLoader
from .models import Document


class Searcher:
    """
    Encapsulates the logic for semantic search.
    """

    def __init__(
        self,
        model: Optional[StaticModel] = None,
        model_name: EmbeddingModel = EmbeddingModel.POTION_MULTI_LINGUAL_128M,
    ):
        self.model = model or StaticModel.from_pretrained(model_name)
        self.processing_semaphore = asyncio.Semaphore(10)  # Limit concurrent file processing

    async def search(
        self,
        query: str,
        files: List[str],
        top_k: int = 3,
        max_distance: Optional[float] = None,
        ignore_case: bool = False,
    ) -> List[RankedLine]:
        """
        Orchestrates a search across files or stdin, dispatching to workspace or
        in-memory search as appropriate.
        """
        if not query or not query.strip():
            raise ValueError("Query cannot be empty.")

        ws = None
        if os.getenv("SEMTOOLS_WORKSPACE") and files:
            # Validate workspace exists before doing any expensive work
            ws = await Workspace.open()

        doc_loader = DocumentLoader(self.model, ignore_case=ignore_case)
        query_embedding_array = await doc_loader.encode([query])
        query_embedding = query_embedding_array[0]

        if ws:
            return await self._search_with_workspace(
                ws, query_embedding, files, top_k, max_distance, doc_loader
            )
        return await self._search_in_memory(
            query_embedding, files, top_k, max_distance, doc_loader
        )

    @staticmethod
    def _rank_results(
        documents: List[Document],
        query_embedding: np.ndarray,
        top_k: int,
        max_distance: Optional[float],
    ) -> List[RankedLine]:
        """Performs the core search logic on a list of in-memory documents."""
        raw_results = []
        for doc in documents:
            for i, line_embedding in enumerate(doc.embeddings):
                # Skip zero vectors to prevent NaN distances from cosine similarity
                if not np.any(line_embedding):
                    continue
                distance = cosine(query_embedding, line_embedding)
                if max_distance is None or distance <= max_distance:
                    raw_results.append(
                        RankedLine(path=doc.path, line_number=i, distance=distance)
                    )

        raw_results.sort(key=lambda x: x.distance)

        final_results = raw_results if max_distance is not None else raw_results[:top_k]
        return final_results

    async def _search_in_memory(
        self,
        query_embedding: np.ndarray,
        files: List[str],
        top_k: int,
        max_distance: Optional[float],
        doc_loader: DocumentLoader,
    ) -> List[RankedLine]:
        """Performs a standard, stateless search in memory."""
        documents = await doc_loader.load(files)

        if not documents:
            return []

        return self._rank_results(
            documents, query_embedding, top_k, max_distance
        )

    async def _process_file_for_workspace(
        self, file_path: str, existing_docs: dict, doc_loader: DocumentLoader
    ):
        """Async helper to check and process a single file for workspace update, with concurrency limiting."""
        async with self.processing_semaphore:
            try:
                stat = await aiofiles.os.stat(file_path)
                current_meta = DocMeta(
                    path=file_path, size_bytes=stat.st_size, mtime=int(stat.st_mtime)
                )
            except FileNotFoundError:
                return None, None

            existing_meta = existing_docs.get(file_path)
            if (
                not existing_meta
                or existing_meta.mtime != current_meta.mtime
                or existing_meta.size_bytes != current_meta.size_bytes
            ):
                doc = await doc_loader.load_file(file_path)

                if not doc or not doc.lines:
                    return [], current_meta

                lines_to_upsert = [ 
                    LineEmbedding(
                        path=doc.path, line_number=i, embedding=emb.tolist()
                    )
                    for i, emb in enumerate(doc.embeddings)
                    if np.any(emb)  # Filter out zero vectors
                ]
                return lines_to_upsert, current_meta

            return None, None

    async def _search_with_workspace(
        self,
        ws: Workspace,
        query_embedding: np.ndarray,
        files: List[str],
        top_k: int,
        max_distance: Optional[float],
        doc_loader: DocumentLoader,
    ) -> List[RankedLine]:
        """Handles the search logic when a workspace is active."""
        store = await Store.create(ws.config)

        # 1. Analyze document states concurrently, but in batches to conserve memory.
        existing_docs = await store.get_existing_docs(files)

        file_chunks = Store.chunk_list(files, ws.config.file_process_chunk_size)

        for chunk in file_chunks:
            tasks = [
                self._process_file_for_workspace(fp, existing_docs, doc_loader)
                for fp in chunk
            ]
            results = await asyncio.gather(*tasks)

            all_lines_to_upsert = [
                line for res in results if res[0] for line in res[0]
            ]
            all_docs_to_upsert = [res[1] for res in results if res[1]]

            # 2. Update workspace if necessary (per chunk)
            if all_lines_to_upsert:
                await store.upsert_line_embeddings(all_lines_to_upsert)
            if all_docs_to_upsert:
                await store.upsert_document_metadata(all_docs_to_upsert)

        # 3. Search the workspace
        return await store.search_line_embeddings(
            query_embedding.tolist(), files, top_k, max_distance
        )