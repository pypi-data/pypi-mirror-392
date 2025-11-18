from unittest.mock import patch

import pytest

pytest_plugins = [
    "tests.parse.fixtures",
    "tests.search.fixtures",
    "tests.workspace.fixtures",
]


@pytest.fixture(autouse=True, scope="session")
def mock_env_vars():
    """Sets fake environment variables for the entire test session."""
    with patch.dict("os.environ", {"LLAMA_CLOUD_API_KEY": "test-api-key-from-conftest"}):
        yield
