import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import List, Optional

import aiofiles
import aiofiles.os
from .errors import ParseError


@dataclass
class FileMetadata:
    """FileMetadata struct for cache validation."""

    modified_time: int
    size: int
    parsed_path: str


class CacheManager:
    """Manages the local file cache for parsed documents, using metadata-based validation to avoid serving stale content."""

    def __init__(self, cache_dir: Path, skippable_extensions: List[str]):
        self.cache_dir = cache_dir
        self.skippable_extensions = skippable_extensions
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_cache_key(self, file_path: str) -> str:
        """DEPRECATED: This method is no longer used in the new caching strategy."""
        raise NotImplementedError

    def _get_metadata_path(self, file_path: str) -> Path:
        """Constructs the path for the metadata JSON file."""
        filename = Path(file_path).name
        return self.cache_dir / f"{filename}.metadata.json"

    def _get_parsed_path(self, file_path: str) -> Path:
        """Constructs the path for the parsed markdown file."""
        filename = Path(file_path).name
        return self.cache_dir / f"{filename}.md"

    @staticmethod
    async def _get_file_metadata(file_path: str) -> FileMetadata:
        """Gets metadata for the source file."""
        try:
            stat = await aiofiles.os.stat(file_path)
            return FileMetadata(
                modified_time=int(stat.st_mtime), size=stat.st_size, parsed_path=""
            )
        except FileNotFoundError:
            raise ParseError(f"File not found for metadata check: {file_path}")

    def should_skip_file(self, file_path: str) -> bool:
        """Determines if a file should be skipped from parsing."""
        return Path(file_path).suffix.lower() in self.skippable_extensions

    async def get_cached_result(self, file_path: str) -> Optional[Path]:
        """Returns the path to the cached result if it exists and is valid."""
        metadata_path = self._get_metadata_path(file_path)
        if not await aiofiles.os.path.exists(metadata_path):
            return None

        try:
            current_metadata = await self._get_file_metadata(file_path)

            async with aiofiles.open(metadata_path, "r") as f:
                content = await f.read()
                cached_metadata_dict = json.loads(content)
            cached_metadata = FileMetadata(**cached_metadata_dict)

            parsed_file = Path(cached_metadata.parsed_path)
            if (
                cached_metadata.modified_time == current_metadata.modified_time
                and cached_metadata.size == current_metadata.size
                and await aiofiles.os.path.exists(parsed_file)
            ):
                return parsed_file
        except (json.JSONDecodeError, FileNotFoundError, TypeError):
            # If metadata is corrupt, file is missing, or schema mismatch, treat as cache miss
            return None

        return None

    async def write_results_to_disk(self, file_path: str, content: str) -> Path:
        """Writes the parsed content and its corresponding metadata to the cache."""
        parsed_path = self._get_parsed_path(file_path)
        metadata_path = self._get_metadata_path(file_path)

        async with aiofiles.open(parsed_path, "w", encoding="utf-8") as f:
            await f.write(content)

        file_metadata = await self._get_file_metadata(file_path)
        file_metadata.parsed_path = str(parsed_path)

        async with aiofiles.open(metadata_path, "w") as f:
            await f.write(json.dumps(asdict(file_metadata), indent=2))

        return parsed_path