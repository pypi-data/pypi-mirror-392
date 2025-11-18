import asyncio
import time
from pathlib import Path

import httpx

from .config import LlamaParseConfig
from .enums import JobStatus
from .errors import ParseHttpError, ParseRetryExhaustedError, ParseTimeoutError


class ParseClient:
    """A client for interacting with the LlamaParse API."""

    def __init__(self, config: LlamaParseConfig, verbose: bool = False, timeout: int = 60):
        self.config = config
        self.verbose = verbose
        self.http_client = httpx.AsyncClient(timeout=timeout)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.http_client.aclose()

    def _get_upload_url(self) -> str:
        """Constructs the upload URL."""
        return f"{self.config.base_url}{self.config.upload_endpoint}"

    def _get_status_url(self, job_id: str) -> str:
        """Constructs the status URL for a given job ID."""
        return f"{self.config.base_url}{self.config.job_endpoint_template.format(job_id=job_id)}"

    def _get_result_url(self, job_id: str) -> str:
        """Constructs the result URL for a given job ID."""
        status_url = self._get_status_url(job_id)
        return f"{status_url}{self.config.result_endpoint_suffix}"

    async def create_parse_job(self, file_path: str) -> str:
        """Creates a parse job for a single file."""
        url = self._get_upload_url()
        headers = {"Authorization": f"Bearer {self.config.api_key}"}

        with open(file_path, "rb") as f:
            files = {"file": (Path(file_path).name, f.read())}
            response = await self.http_client.post(
                url, headers=headers, files=files, data=self.config.parse_kwargs
            )

        if not response.is_success:
            raise ParseHttpError(
                f"Upload failed with status {response.status_code}: {response.text}"
            )

        return response.json()["id"]

    async def get_job_result(self, job_id: str) -> str | None:
        """Polls for the result of a parsing job until completion or timeout."""
        start_time = time.monotonic()
        status_url = self._get_status_url(job_id)
        result_url = self._get_result_url(job_id)
        headers = {"Authorization": f"Bearer {self.config.api_key}"}

        while True:
            if time.monotonic() - start_time > self.config.max_timeout:
                raise ParseTimeoutError(f"Job {job_id} timed out.")

            await asyncio.sleep(self.config.check_interval)

            # Let network exceptions propagate to be handled by the retry wrapper.
            status_response = await self.http_client.get(status_url, headers=headers)
            status_response.raise_for_status()
            status = status_response.json()["status"]

            if status == JobStatus.SUCCESS:
                result_response = await self.http_client.get(result_url, headers=headers)
                result_response.raise_for_status()
                return result_response.json()["markdown"]
            elif status in [JobStatus.ERROR, JobStatus.CANCELED]:
                # This is a terminal job failure, not a network error. Do not retry.
                raise ParseHttpError(f"Job {job_id} failed with status: {status}")
            elif status == JobStatus.PENDING:
                if self.verbose:
                    print(f"Job still pending: {job_id}")
            else:
                # Unknown status should also be a non-retryable error.
                raise ParseHttpError(f"Job {job_id} has unknown status: {status}")

    async def create_job_with_retry(self, file_path: str) -> str:
        """Creates a parse job, retrying on failure."""
        last_exception = None
        for attempt in range(self.config.max_retries + 1):
            try:
                return await self.create_parse_job(file_path)
            except (httpx.ConnectError, httpx.TimeoutException, httpx.HTTPStatusError) as e:
                last_exception = e
                await self._handle_retry(attempt, e)

        raise ParseRetryExhaustedError("Job creation failed after all retries.") from last_exception

    async def poll_for_result_with_retry(self, job_id: str) -> str | None:
        """Polls for a job result, retrying the entire polling process on failure."""

        last_exception = None
        for attempt in range(self.config.max_retries + 1):
            try:
                return await self.get_job_result(job_id)
            except (httpx.ConnectError, httpx.TimeoutException, httpx.HTTPStatusError) as e:
                last_exception = e
                await self._handle_retry(attempt, e)

        raise ParseRetryExhaustedError("Polling failed after all retries.") from last_exception

    async def _handle_retry(self, attempt: int, e: Exception):
        is_server_error = (
            isinstance(e, httpx.HTTPStatusError)
            and 500 <= e.response.status_code < 600
        )
        if not (isinstance(e, (httpx.ConnectError, httpx.TimeoutException)) or is_server_error):
            raise e

        if attempt >= self.config.max_retries:
            return  # Let the loop finish and the caller raise the final error

        delay = (self.config.retry_delay_ms / 1000.0) * (self.config.backoff_multiplier ** attempt)
        if self.verbose:
            print(
                f"Request failed (attempt {attempt + 1}/{self.config.max_retries + 1}): {e}. "
                f"Retrying in {delay:.2f}s..."
            )
        await asyncio.sleep(delay)
