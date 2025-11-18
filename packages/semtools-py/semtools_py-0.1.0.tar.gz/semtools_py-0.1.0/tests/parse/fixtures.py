from pathlib import Path
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from src.semtools.parse.backend import LlamaParseBackend
from src.semtools.parse.cache import CacheManager
from src.semtools.parse.client import ParseClient
from src.semtools.parse.config import LlamaParseConfig


@pytest.fixture
def temp_cache_dir(tmp_path: Path) -> Path:
    """A temporary directory for cache testing."""
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir()
    return cache_dir


@pytest.fixture
def llama_parse_config(temp_cache_dir: Path) -> LlamaParseConfig:
    """Provides a LlamaParseConfig instance for testing."""
    return LlamaParseConfig(
        api_key="test-api-key",
        cache_dir=temp_cache_dir,
        num_ongoing_requests=2,
        check_interval=1,
        max_timeout=10,
    )


@pytest.fixture
def cache_manager(llama_parse_config: LlamaParseConfig) -> CacheManager:
    """Provides a CacheManager instance."""
    return CacheManager(llama_parse_config.cache_dir, llama_parse_config.skippable_extensions)


@pytest.fixture
def parse_client_mock(mocker: MockerFixture) -> MagicMock:
    """Mocks the ParseClient."""
    return mocker.create_autospec(ParseClient, instance=True)