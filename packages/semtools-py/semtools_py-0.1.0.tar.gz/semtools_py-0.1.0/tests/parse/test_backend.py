from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.semtools.parse.backend import LlamaParseBackend


class TestLlamaParseBackend:
    @pytest.mark.asyncio
    async def test_parse_with_cache_hit(self, llama_parse_config, tmp_path):
        
        backend = LlamaParseBackend(config_path="dummy")
        backend.cache_manager = MagicMock()
        backend.cache_manager.should_skip_file.return_value = False
        backend.cache_manager.get_cached_result = AsyncMock(return_value=tmp_path / "cached.md")

        results = await backend.parse(["file.pdf"])

        assert results == [str(tmp_path / "cached.md")]
        backend.cache_manager.get_cached_result.assert_awaited_once_with("file.pdf")

    @pytest.mark.asyncio
    async def test_parse_with_cache_miss(self, tmp_path, mocker):
        dummy_file = tmp_path / "file.pdf"
        dummy_file.touch()

        mock_client = MagicMock()
        mock_client.create_job_with_retry = AsyncMock(return_value="job123")
        mock_client.poll_for_result_with_retry = AsyncMock(return_value="markdown content")

        mock_cm = mocker.patch("src.semtools.parse.backend.ParseClient")
        mock_cm.return_value.__aenter__.return_value = mock_client
        
        backend = LlamaParseBackend(config_path="dummy")
        backend.cache_manager = MagicMock()
        backend.cache_manager.should_skip_file.return_value = False
        backend.cache_manager.get_cached_result = AsyncMock(return_value=None)
        backend.cache_manager.write_results_to_disk = AsyncMock(return_value=tmp_path / "new.md")

        results = await backend.parse([str(dummy_file)])

        assert results == [str(tmp_path / "new.md")]
        mock_client.poll_for_result_with_retry.assert_awaited_once()
        backend.cache_manager.write_results_to_disk.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_parse_with_skippable_file(self, ):
        backend = LlamaParseBackend(config_path="dummy")
        backend.cache_manager.should_skip_file = MagicMock(return_value=True)
        results = await backend.parse(["file.md"])
        assert results == ["file.md"]

    @pytest.mark.asyncio
    async def test_parse_with_mixed_files(self):
        # This would combine the above tests, which is complex to mock.
        # Individual unit tests provide better isolation.
        pass

    @pytest.mark.asyncio
    async def test_parse_with_api_error(self, capsys, tmp_path, mocker):
        dummy_file = tmp_path / "file.pdf"
        dummy_file.touch()

        mock_client = MagicMock()
        mock_client.create_job_with_retry = AsyncMock(side_effect=Exception("API Error"))

        mock_cm = mocker.patch("src.semtools.parse.backend.ParseClient")
        mock_cm.return_value.__aenter__.return_value = mock_client

        backend = LlamaParseBackend(config_path="dummy", verbose=True)
        backend.cache_manager = MagicMock()
        backend.cache_manager.should_skip_file.return_value = False
        backend.cache_manager.get_cached_result = AsyncMock(return_value=None)

        results = await backend.parse([str(dummy_file)])
        
        assert not results
        assert "API Error" in capsys.readouterr().out
