import asyncio
from pathlib import Path
from typing import List

from .cache import CacheManager
from .client import ParseClient
from .config import LlamaParseConfig


class LlamaParseBackend:
    """Orchestrates the document parsing process using the LlamaParse API."""

    def __init__(self, config_path: str, verbose: bool = False, timeout: int = 60):
        config = LlamaParseConfig.from_config_file(Path(config_path))
        self.config = config
        self.verbose = verbose
        self.timeout = timeout
        self.cache_manager = CacheManager(
            config.cache_dir, config.skippable_extensions
        )
        self.semaphore = asyncio.Semaphore(config.num_ongoing_requests)

    async def parse(self, files: List[str]) -> List[str]:
        """
        Parses a list of files concurrently, handling caching and API interaction.
        """
        tasks = []
        final_results = []

        # Use a single client for connection pooling, which is more efficient
        async with ParseClient(self.config, self.verbose, timeout=self.timeout) as client:
            for file_path in files:
                if self.cache_manager.should_skip_file(file_path):
                    if self.verbose:
                        print(f"Skipping readable file: {file_path}")
                    final_results.append(file_path)
                    continue

                cached_path = await self.cache_manager.get_cached_result(file_path)
                if cached_path:
                    if self.verbose:
                        print(f"Using cached result for: {file_path}")
                    final_results.append(str(cached_path))
                    continue

                task = asyncio.create_task(
                    self._process_single_document(client, file_path)
                )
                tasks.append(task)

            processed_results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in processed_results:
            if isinstance(result, Exception):
                print(f"Error processing a file: {result}")
            elif result:
                final_results.append(result)

        return final_results

    async def _process_single_document(
        self, client: ParseClient, file_path: str
    ) -> str:
        """Processes a single file: uploads, polls for result, and caches it."""
        async with self.semaphore:
            if self.verbose:
                print(f"Processing file: {file_path}")

            job_id = await client.create_job_with_retry(file_path)
            markdown_content = await client.poll_for_result_with_retry(job_id)

            result_path = await self.cache_manager.write_results_to_disk(
                file_path, markdown_content
            )
            return str(result_path)
