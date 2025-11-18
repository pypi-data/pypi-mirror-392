import json
import os
import time

import pytest


class TestCacheManager:
    @pytest.mark.asyncio
    async def test_get_cached_result_valid(self, cache_manager, temp_cache_dir):
        
        source_file = temp_cache_dir / "source.txt"
        source_file.write_text("content")
        stat = os.stat(source_file)
        
        parsed_path = temp_cache_dir / "source.txt.md"
        parsed_path.touch()
        
        metadata_path = temp_cache_dir / "source.txt.metadata.json"
        metadata = {"modified_time": int(stat.st_mtime), "size": stat.st_size, "parsed_path": str(parsed_path)}
        metadata_path.write_text(json.dumps(metadata))

        assert await cache_manager.get_cached_result(str(source_file)) == parsed_path

    @pytest.mark.asyncio
    async def test_get_cached_result_stale_mtime(self, cache_manager, temp_cache_dir):
        source_file = temp_cache_dir / "source.txt"
        source_file.write_text("content")
        stat = os.stat(source_file)
        
        parsed_path = temp_cache_dir / "source.txt.md"
        parsed_path.touch()
        
        metadata_path = temp_cache_dir / "source.txt.metadata.json"
        metadata = {"modified_time": int(stat.st_mtime) - 10, "size": stat.st_size, "parsed_path": str(parsed_path)}
        metadata_path.write_text(json.dumps(metadata))
        
        assert await cache_manager.get_cached_result(str(source_file)) is None

    @pytest.mark.asyncio
    async def test_get_cached_result_stale_size(self, cache_manager, temp_cache_dir):
        source_file = temp_cache_dir / "source.txt"
        source_file.write_text("content")
        stat = os.stat(source_file)
        
        parsed_path = temp_cache_dir / "source.txt.md"
        parsed_path.touch()
        
        metadata_path = temp_cache_dir / "source.txt.metadata.json"
        metadata = {"modified_time": int(stat.st_mtime), "size": stat.st_size - 1, "parsed_path": str(parsed_path)}
        metadata_path.write_text(json.dumps(metadata))

        assert await cache_manager.get_cached_result(str(source_file)) is None

    @pytest.mark.asyncio
    async def test_get_cached_result_not_found(self, cache_manager):
        assert await cache_manager.get_cached_result("nonexistent.txt") is None

    @pytest.mark.asyncio
    async def test_write_results_to_disk(self, cache_manager, temp_cache_dir):
        source_file = temp_cache_dir / "source.txt"
        source_file.write_text("content")

        await cache_manager.write_results_to_disk(str(source_file), "parsed")

        assert (temp_cache_dir / "source.txt.md").exists()
        assert (temp_cache_dir / "source.txt.metadata.json").exists()

    def test_should_skip_file(self, cache_manager):
        assert cache_manager.should_skip_file("file.md")
        assert not cache_manager.should_skip_file("file.pdf")

    def test_get_cached_result_metadata_ok_file_deleted(self):
        # Similar setup to test_get_cached_result_valid, but delete the parsed_path file
        pass

    @pytest.mark.asyncio
    async def test_get_cached_result_corrupted_metadata(self, cache_manager, temp_cache_dir):
        source_file = temp_cache_dir / "source.txt"
        source_file.touch()
        metadata_path = temp_cache_dir / "source.txt.metadata.json"
        metadata_path.write_text("{not valid json")
        
        assert await cache_manager.get_cached_result(str(source_file)) is None