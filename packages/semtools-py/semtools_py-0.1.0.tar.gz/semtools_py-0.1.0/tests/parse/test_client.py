from unittest.mock import AsyncMock

import pytest
from httpx import Response, Request, HTTPStatusError

from src.semtools.parse.client import ParseClient
from src.semtools.parse.errors import ParseHttpError, ParseRetryExhaustedError, ParseTimeoutError
from src.semtools.parse.enums import JobStatus


class TestParseClient:
    @pytest.mark.asyncio
    async def test_create_parse_job_success(self, llama_parse_config, tmp_path):
        client = ParseClient(llama_parse_config)
        client.http_client = AsyncMock(post=AsyncMock(return_value=Response(200, json={"id": "job123"}, request=Request("POST", "http://dummy.url"))))
        file = tmp_path / "test.pdf"
        file.touch()

        job_id = await client.create_parse_job(str(file))

        assert job_id == "job123"

    @pytest.mark.asyncio
    async def test_create_parse_job_http_error(self, llama_parse_config, tmp_path):
        client = ParseClient(llama_parse_config)
        client.http_client = AsyncMock(post=AsyncMock(return_value=Response(500, text="Server Error", request=Request("POST", "http://dummy.url"))))
        file = tmp_path / "test.pdf"
        file.touch()

        with pytest.raises(ParseHttpError):
            await client.create_parse_job(str(file))

    @pytest.mark.asyncio
    async def test_get_job_result_success(self, llama_parse_config):
        client = ParseClient(llama_parse_config)
        client.http_client = AsyncMock()
        client.http_client.get.side_effect = [
            Response(200, json={"status": JobStatus.SUCCESS}, request=Request("GET", "http://dummy.url")),
            Response(200, json={"markdown": "content"}, request=Request("GET", "http://dummy.url"))
        ]
        result = await client.get_job_result("job123")
        assert result == "content"

    @pytest.mark.asyncio
    async def test_get_job_result_pending_then_success(self, llama_parse_config):
        llama_parse_config.check_interval = 0.1
        client = ParseClient(llama_parse_config)
        client.http_client = AsyncMock()
        client.http_client.get.side_effect = [
            Response(200, json={"status": JobStatus.PENDING}, request=Request("GET", "http://dummy.url")),
            Response(200, json={"status": JobStatus.SUCCESS}, request=Request("GET", "http://dummy.url")),
            Response(200, json={"markdown": "content"}, request=Request("GET", "http://dummy.url"))
        ]
        result = await client.get_job_result("job123")
        assert result == "content"

    @pytest.mark.asyncio
    async def test_get_job_result_timeout(self, llama_parse_config, mocker):
        mocker.patch("time.monotonic", side_effect=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
        llama_parse_config.max_timeout = 10
        llama_parse_config.check_interval = 0.1
        client = ParseClient(llama_parse_config)
        client.http_client = AsyncMock()
        client.http_client.get.return_value = Response(200, json={"status": JobStatus.PENDING}, request=Request("GET", "http://dummy.url"))
        with pytest.raises(ParseTimeoutError):
            await client.get_job_result("job123")

    @pytest.mark.asyncio
    async def test_get_job_result_job_failure(self, llama_parse_config):
        client = ParseClient(llama_parse_config)
        client.http_client = AsyncMock()
        client.http_client.get.return_value = Response(200, json={"status": JobStatus.ERROR}, request=Request("GET", "http://dummy.url"))
        with pytest.raises(ParseHttpError):
            await client.get_job_result("job123")

    @pytest.mark.asyncio
    async def test_create_job_with_retry(self, llama_parse_config, tmp_path):
        llama_parse_config.max_retries = 1
        llama_parse_config.retry_delay_ms = 1
        client = ParseClient(llama_parse_config)
        client.http_client = AsyncMock()
        client.http_client.post.side_effect = [
            HTTPStatusError("error", request=Request("POST", "http://dummy.url"), response=Response(500, request=Request("POST", "http://dummy.url"))),
            Response(200, json={"id": "job123"}, request=Request("POST", "http://dummy.url"))
        ]
        file = tmp_path / "test.pdf"
        file.touch()
        job_id = await client.create_job_with_retry(str(file))
        assert job_id == "job123"

    @pytest.mark.asyncio
    async def test_create_job_with_retry_exhausted(self, llama_parse_config, tmp_path):
        llama_parse_config.max_retries = 1
        llama_parse_config.retry_delay_ms = 1
        client = ParseClient(llama_parse_config)
        client.http_client = AsyncMock()
        client.http_client.post.side_effect = [
            HTTPStatusError("error", request=Request("POST", "http://dummy.url"), response=Response(500, request=Request("POST", "http://dummy.url"))),
            HTTPStatusError("error", request=Request("POST", "http://dummy.url"), response=Response(500, request=Request("POST", "http://dummy.url")))
        ]
        file = tmp_path / "test.pdf"
        file.touch()

        with pytest.raises(ParseRetryExhaustedError):
            await client.create_job_with_retry(str(file))

    @pytest.mark.asyncio
    async def test_poll_for_result_with_retry(self, llama_parse_config):
        llama_parse_config.max_retries = 1
        llama_parse_config.retry_delay_ms = 1
        client = ParseClient(llama_parse_config)
        client.http_client = AsyncMock()
        client.http_client.get.side_effect = [
            HTTPStatusError("error", request=Request("GET", "http://dummy.url"), response=Response(500, request=Request("GET", "http://dummy.url"))),
            Response(200, json={"status": JobStatus.SUCCESS}, request=Request("GET", "http://dummy.url")),
            Response(200, json={"markdown": "content"}, request=Request("GET", "http://dummy.url"))
        ]
        result = await client.poll_for_result_with_retry("job123")
        assert result == "content"

    @pytest.mark.asyncio
    async def test_poll_for_result_with_retry_exhausted(self, llama_parse_config):
        llama_parse_config.max_retries = 1
        llama_parse_config.retry_delay_ms = 1
        client = ParseClient(llama_parse_config)
        client.http_client = AsyncMock()
        client.http_client.get.side_effect = [
            HTTPStatusError("error", request=Request("GET", "http://dummy.url"), response=Response(500, request=Request("GET", "http://dummy.url"))),
            HTTPStatusError("error", request=Request("GET", "http://dummy.url"), response=Response(500, request=Request("GET", "http://dummy.url")))
        ]

        with pytest.raises(ParseRetryExhaustedError):
            await client.poll_for_result_with_retry("job123")