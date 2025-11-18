from unittest.mock import AsyncMock, patch

import pytest
from click.testing import CliRunner

from src.semtools.cli import search, workspace
from src.semtools.workspace.errors import WorkspaceError
from src.semtools.workspace.models import WorkspaceStats


@pytest.fixture
def runner():
    return CliRunner()


def test_search_workspace_not_found(runner, mocker):
    mocker.patch("os.getenv", return_value="test_ws")
    mock_searcher = mocker.patch("src.semtools.cli.Searcher").return_value
    mock_searcher.search.side_effect = WorkspaceError("Workspace not found")

    with runner.isolated_filesystem():
        with open("file.txt", "w") as f:
            f.write("test")
        result = runner.invoke(search, ["query", "file.txt"])

    assert result.exit_code == 1
    assert "Error: Workspace not found" in result.output


@patch("src.semtools.cli.Workspace.get_active_workspace_with_stats", new_callable=AsyncMock)
def test_workspace_status(mock_get_stats, runner):
    ws_mock = AsyncMock()
    ws_mock.config.name = "test_ws"
    ws_mock.config.root_dir = "/fake/dir"
    stats_mock = WorkspaceStats(total_documents=10, has_index=True, index_type="IVF_PQ")

    mock_get_stats.return_value = (ws_mock, stats_mock)

    result = runner.invoke(workspace, ["status"])

    assert result.exit_code == 0
    assert "Active workspace: test_ws" in result.output
    assert "Documents: 10" in result.output
    assert "Index: Yes (IVF_PQ)" in result.output


@patch("src.semtools.cli.Workspace.prune_active_workspace", new_callable=AsyncMock)
def test_workspace_prune(mock_prune, runner):
    mock_prune.return_value = ["/fake/stale.txt"]

    result = runner.invoke(workspace, ["prune"])

    assert result.exit_code == 0
    assert "Found 1 stale documents" in result.output
    assert "- /fake/stale.txt" in result.output
    assert "Removed 1 stale documents" in result.output


@patch("src.semtools.cli.Workspace.prune_active_workspace", new_callable=AsyncMock)
def test_workspace_prune_no_stale(mock_prune, runner):
    mock_prune.return_value = []
    result = runner.invoke(workspace, ["prune"])
    assert result.exit_code == 0
    assert "No stale documents found. Workspace is clean." in result.output