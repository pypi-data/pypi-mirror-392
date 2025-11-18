import numpy as np
import pytest
from src.semtools.workspace.store import DocMeta, LineEmbedding


class TestStore:
    @pytest.mark.asyncio
    async def test_upsert_and_get_document_metadata(self, workspace_store):
        
        meta = DocMeta(path="/a/b.txt", size_bytes=123, mtime=456)

        
        await workspace_store.upsert_document_metadata([meta])
        retrieved = await workspace_store.get_existing_docs(["/a/b.txt"])

        
        assert "/a/b.txt" in retrieved
        assert retrieved["/a/b.txt"].size_bytes == 123

    @pytest.mark.asyncio
    async def test_upsert_and_search_line_embeddings(self, workspace_store):
        
        embedding = LineEmbedding(path="/a/c.txt", line_number=5, embedding=list(np.ones(8)))
        await workspace_store.upsert_line_embeddings([embedding])

        
        results = await workspace_store.search_line_embeddings(
            list(np.ones(8)), ["/a/c.txt"], 1
        )

        
        assert len(results) == 1
        assert results[0].path == "/a/c.txt"
        assert results[0].line_number == 5
        assert results[0].distance == pytest.approx(0, abs=1e-6)

    @pytest.mark.asyncio
    async def test_delete_documents(self, workspace_store):
        
        meta = DocMeta(path="/a/d.txt", size_bytes=1, mtime=1)
        embedding = LineEmbedding(path="/a/d.txt", line_number=1, embedding=[0.1] * 8)
        await workspace_store.upsert_document_metadata([meta])
        await workspace_store.upsert_line_embeddings([embedding])

        
        await workspace_store.delete_documents(["/a/d.txt"])

        
        assert not await workspace_store.get_existing_docs(["/a/d.txt"])
        assert not await workspace_store.search_line_embeddings(
            [0.1] * 8, ["/a/d.txt"], 1
        )

    @pytest.mark.asyncio
    async def test_get_all_document_paths(self, workspace_store):
        
        await workspace_store.upsert_document_metadata([
            DocMeta(path="/a/e.txt", size_bytes=1, mtime=1),
            DocMeta(path="/a/f.txt", size_bytes=1, mtime=1)
        ])

        assert set(await workspace_store.get_all_document_paths()) == {"/a/e.txt", "/a/f.txt"}

    @pytest.mark.asyncio
    async def test_get_stats(self, workspace_store):
        
        await workspace_store.upsert_document_metadata([DocMeta(path="/a/g.txt", size_bytes=1, mtime=1)])
        stats = await workspace_store.get_stats()
        assert stats.total_documents == 1
        assert not stats.has_index
        assert stats.index_type is None

    @pytest.mark.asyncio
    async def test_ensure_index_creation(self, workspace_store):
        """Verify that an index is created automatically when enough data is present."""
        # LanceDB requires a certain amount of data to train an IVF_PQ index.
        embeddings = [
            LineEmbedding(path="/a/b.txt", line_number=i, embedding=[float(i)] * 8)
            for i in range(300)
        ]
        await workspace_store.upsert_line_embeddings(embeddings)

        tbl = await workspace_store.db.open_table("line_embeddings")
        indices = await tbl.list_indices()
        assert len(indices) == 1

    @pytest.mark.asyncio
    async def test_ensure_index_skips_on_insufficient_data(self, workspace_store):
        
        embedding = LineEmbedding(path="/a/h.txt", line_number=1, embedding=[0.1] * 8)

        await workspace_store.upsert_line_embeddings([embedding])
        stats = await workspace_store.get_stats()
        assert not stats.has_index

    @pytest.mark.asyncio
    async def test_search_with_empty_subset_paths(self, workspace_store):
        assert not await workspace_store.search_line_embeddings([0.1] * 8, [], 1)

    @pytest.mark.asyncio
    async def test_delete_non_existent_document(self, workspace_store):
        # Should not raise an exception
        await workspace_store.delete_documents(["/non/existent.txt"])