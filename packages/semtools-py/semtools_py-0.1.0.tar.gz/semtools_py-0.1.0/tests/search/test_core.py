import os
from unittest.mock import MagicMock, patch
import numpy as np

import pytest
from pathlib import Path

from semtools.workspace import WorkspaceError
from src.semtools.search.core import Searcher
from src.semtools.workspace.store import DocMeta, RankedLine


class TestSearcher:
    @pytest.mark.asyncio
    async def test_search_in_memory(self, searcher: Searcher, mock_file: Path):
        query = "fox"
        files = [str(mock_file)]

        results = await searcher.search(query=query, files=files, top_k=1)

        assert results
        assert len(results) == 1
        result = results[0]
        assert isinstance(result, RankedLine)
        assert result.path == str(mock_file)
        assert result.line_number == 0

    @pytest.mark.asyncio
    async def test_search_in_memory_no_results(self, mocker):
        mocker.patch("sys.stdin.isatty", return_value=True)
        searcher = Searcher()
        query = "a query that will not be found"
        files = []

        results = await searcher.search(query=query, files=files, top_k=1)

        assert not results

    @pytest.mark.asyncio
    async def test_search_with_empty_query(self, searcher: Searcher, mock_file: Path):
        with pytest.raises(ValueError, match="Query cannot be empty."):
            await searcher.search(query="", files=[str(mock_file)])

    @pytest.mark.asyncio
    async def test_search_with_ignore_case(self, tmp_path):
        # This test correctly mocks the model to verify the input it receives.
        file = tmp_path / "test.txt"
        file.write_text("Hello\nhello")

        mock_model = MagicMock()
        mock_model.encode.return_value = [[0.1], [0.1]]  # Dummy embeddings

        searcher = Searcher(model=mock_model)
        await searcher.search("hello", [str(file)], ignore_case=True)

        # Assert that the lines sent for embedding were lowercased
        mock_model.encode.assert_any_call(["hello", "hello"])

    @pytest.mark.asyncio
    @patch("src.semtools.search.core.Workspace.open")
    @patch("src.semtools.search.loader.DocumentLoader.encode")
    @patch("os.getenv", return_value="test_ws")
    async def test_search_fails_early_if_workspace_not_found(
        self, mock_getenv, mock_encode, mock_ws_open, searcher: Searcher, mock_file: Path
    ):
        mock_ws_open.side_effect = WorkspaceError("Workspace not found")

        with pytest.raises(WorkspaceError, match="Workspace not found"):
            await searcher.search(query="test", files=[str(mock_file)])

        mock_encode.assert_not_awaited()

    @pytest.mark.asyncio
    @patch("src.semtools.search.core.Workspace.open")
    @patch("src.semtools.search.core.Store.create")
    @patch("os.getenv", return_value="test_ws")
    async def test_search_with_workspace_no_changes(
        self, mock_getenv, mock_store_create, mock_ws_open, searcher: Searcher, mock_file: Path
    ):
        mock_store = mock_store_create.return_value
        real_stat = os.stat(mock_file)
        mock_store.get_existing_docs.return_value = {
            str(mock_file): DocMeta(path=str(mock_file), size_bytes=real_stat.st_size, mtime=int(real_stat.st_mtime))
        }

        await searcher.search(
            query="fox", files=[str(mock_file)], top_k=1, max_distance=None, ignore_case=False
        )

        mock_store.upsert_line_embeddings.assert_not_awaited()
        mock_store.upsert_document_metadata.assert_not_awaited()
        mock_store.search_line_embeddings.assert_awaited_once()

    @pytest.mark.asyncio
    @patch("src.semtools.search.core.Workspace.open")
    @patch("src.semtools.search.core.Store.create")
    @patch("os.getenv", return_value="test_ws")
    async def test_search_with_workspace_new_file(
        self, mock_getenv, mock_store_create, mock_ws_open, searcher: Searcher, mock_file: Path
    ):
        mock_store = mock_store_create.return_value
        mock_store.get_existing_docs.return_value = {}  # No existing docs

        await searcher.search(
            query="fox", files=[str(mock_file)], top_k=1, max_distance=None, ignore_case=False
        )

        mock_store.upsert_line_embeddings.assert_awaited_once()
        mock_store.upsert_document_metadata.assert_awaited_once()
        mock_store.search_line_embeddings.assert_awaited_once()

    @pytest.mark.asyncio
    @patch("src.semtools.search.core.Workspace.open")
    @patch("src.semtools.search.core.Store.create")
    @patch("os.getenv", return_value="test_ws")
    async def test_search_with_workspace_modified_file(
        self, mock_getenv, mock_store_create, mock_ws_open, searcher: Searcher, mock_file: Path
    ):
        mock_store = mock_store_create.return_value
        mock_store.get_existing_docs.return_value = {
            str(mock_file): DocMeta(path=str(mock_file), size_bytes=1, mtime=1)  # Stale meta
        }

        await searcher.search(
            query="fox", files=[str(mock_file)], top_k=1, max_distance=None, ignore_case=False
        )

        mock_store.upsert_line_embeddings.assert_awaited_once()
        mock_store.upsert_document_metadata.assert_awaited_once()

    def test_rank_results_with_top_k(self, searcher: Searcher, mock_documents):
        query_embedding = np.array([0.1, 0.2])  # Closest to doc1, line 1

        results = searcher._rank_results(
            documents=mock_documents, query_embedding=query_embedding, top_k=1, max_distance=None
        )

        assert len(results) == 1
        assert results[0].path == "/fake/doc1.txt"
        assert results[0].line_number == 0

    def test_rank_results_with_max_distance(self, searcher: Searcher, mock_documents):
        query_embedding = np.array([0.4, 0.5])  # Equidistant to doc1 line 2 and doc2 line 1

        results = searcher._rank_results(
            documents=mock_documents, query_embedding=query_embedding, top_k=10, max_distance=0.0005
        )

        assert len(results) == 2
        paths = {r.path for r in results}
        assert "/fake/doc1.txt" in paths
        assert "/fake/doc2.txt" in paths

    def test_rank_results_empty(self, searcher: Searcher):
        results = searcher._rank_results(
            documents=[], query_embedding=np.array([0, 0]), top_k=1, max_distance=None
        )
        assert not results