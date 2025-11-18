from unittest.mock import MagicMock, patch

import pytest
from src.semtools.search.loader import DocumentLoader


class TestDocumentLoader:
    @pytest.mark.asyncio
    async def test_load_from_files(self, mock_file):
        mock_model = MagicMock()
        loader = DocumentLoader(model=mock_model)

        documents = await loader.load([str(mock_file)])

        assert len(documents) == 1
        assert documents[0].path == str(mock_file)
        assert len(documents[0].lines) == 20  # From MOCK_FILE_CONTENT
        mock_model.encode.assert_called_once()

    @pytest.mark.asyncio
    async def test_load_from_stdin(self, mocker):
        mock_model = MagicMock()
        loader = DocumentLoader(model=mock_model)
        mocker.patch("sys.stdin.isatty", return_value=False)
        mocker.patch("sys.stdin.readlines", return_value=["line 1\n", "line 2\n"])

        documents = await loader.load([])

        assert len(documents) == 1
        assert documents[0].path == "<stdin>"
        assert documents[0].lines == ["line 1", "line 2"]

    @pytest.mark.asyncio
    async def test_load_non_existent_file(self):
        loader = DocumentLoader(model=MagicMock())

        documents = await loader.load(["/non/existent/file.txt"])

        assert not documents

    @pytest.mark.asyncio
    async def test_load_empty_file(self, tmp_path):
        empty_file = tmp_path / "empty.txt"
        empty_file.touch()
        loader = DocumentLoader(model=MagicMock())

        documents = await loader.load([str(empty_file)])

        assert not documents

    @pytest.mark.asyncio
    async def test_create_document_from_lines(self):
        mock_model = MagicMock()
        loader = DocumentLoader(model=mock_model)

        doc = await loader._create_document_from_lines("path", ["line 1"])

        assert doc is not None
        assert doc.path == "path"
        mock_model.encode.assert_called_once_with(["line 1"])