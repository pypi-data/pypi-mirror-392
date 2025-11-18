from pathlib import Path

import pytest

from src.semtools.workspace.core import Workspace, WorkspaceConfig
from src.semtools.workspace.store import Store


@pytest.fixture
def temp_workspace_dir(tmp_path: Path) -> Path:
    """Creates a temporary directory for a workspace."""
    ws_dir = tmp_path / "workspaces" / "test_ws"
    ws_dir.mkdir(parents=True)
    return ws_dir


@pytest.fixture
def workspace_config(temp_workspace_dir: Path) -> WorkspaceConfig:
    """Provides a WorkspaceConfig for testing."""
    return WorkspaceConfig(name="test_ws", root_dir=str(temp_workspace_dir))


@pytest.fixture
def workspace(workspace_config: WorkspaceConfig) -> Workspace:
    """Provides a Workspace instance."""
    return Workspace(config=workspace_config)


@pytest.fixture
async def workspace_store(workspace_config: WorkspaceConfig) -> Store:
    """Provides a workspace Store instance connected to a temporary DB."""
    return await Store.create(workspace_config)
