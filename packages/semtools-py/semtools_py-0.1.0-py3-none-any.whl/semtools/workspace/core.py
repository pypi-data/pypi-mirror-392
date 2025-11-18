import json
import asyncio
import shutil
import os
import aiofiles.os
from dataclasses import asdict
from pathlib import Path

from ..config import APP_HOME_DIR
from .errors import WorkspaceError
from .models import WorkspaceConfig, WorkspaceStats
from .store import Store


class Workspace:
    """Manages semtools workspaces, configurations, and paths."""

    def __init__(self, config: WorkspaceConfig):
        self.config = config

    @classmethod
    async def open(cls) -> "Workspace":
        """Asynchronously opens the active workspace configuration."""
        active_name = cls.get_active_workspace_name()
        config_path = cls._get_config_path_for(active_name)

        if not await aiofiles.os.path.exists(config_path):
            raise WorkspaceError(
                f"Workspace '{active_name}' not found. Run 'workspace use {active_name}' to create it."
            )

        async with aiofiles.open(config_path, "r") as f:
            content = await f.read()
            config_data = json.loads(content)
        config = WorkspaceConfig(**config_data)

        return cls(config)

    @classmethod
    async def prune_active_workspace(cls) -> list[str]:
        """Opens the active workspace and prunes it."""
        ws = await cls.open()
        return await ws.prune()

    async def save(self) -> None:
        """Saves the current workspace configuration to disk."""
        config_path = self._get_config_path_for(self.config.name)

        await aiofiles.os.makedirs(config_path.parent, exist_ok=True)
        async with aiofiles.open(config_path, "w") as f:
            await f.write(json.dumps(asdict(self.config), indent=2))

    @staticmethod
    def get_active_workspace_name() -> str:
        """Gets the name of the active workspace from the environment variable."""
        active = os.getenv("SEMTOOLS_WORKSPACE")
        if not active:
            raise WorkspaceError(
                "No active workspace. Set the SEMTOOLS_WORKSPACE environment variable."
            )
        return active

    @staticmethod
    def _get_root_path(name: str) -> Path:
        """Gets the root directory path for a named workspace."""
        return APP_HOME_DIR / "workspaces" / name

    @classmethod
    def _get_config_path_for(cls, name: str) -> Path:
        """Gets the path to the config.json file for a named workspace."""
        return cls._get_root_path(name) / "config.json"

    @classmethod
    async def create_or_use(cls, name: str) -> None:
        """Configures a new or existing workspace."""
        config_path = cls._get_config_path_for(name)
        if not await aiofiles.os.path.exists(config_path):
            root_dir = cls._get_root_path(name)
            config = cls(config=WorkspaceConfig(name=name, root_dir=str(root_dir)))
            await config.save()

    @classmethod
    async def delete(cls, name: str) -> None:
        """Permanently deletes a workspace and all its data."""
        root_path = cls._get_root_path(name)
        if not await aiofiles.os.path.exists(root_path):
            raise WorkspaceError(f"Workspace '{name}' not found at {root_path}")

        await asyncio.to_thread(shutil.rmtree, root_path)

    @classmethod
    async def get_active_workspace_with_stats(cls) -> tuple["Workspace", "WorkspaceStats"]:
        """Opens the active workspace and gets its stats."""
        ws = await cls.open()
        stats = await ws.get_status()
        return ws, stats

    async def get_status(self) -> WorkspaceStats:
        """Gets status and basic stats for the workspace."""
        store = await Store.create(self.config)
        return await store.get_stats()

    async def prune(self) -> list[str]:
        """Removes stale or missing files from the store and returns their paths."""
        store = await Store.create(self.config)
        all_paths = await store.get_all_document_paths()

        # Check for existence of files concurrently
        tasks = [aiofiles.os.stat(p) for p in all_paths]
        stat_results = await asyncio.gather(*tasks, return_exceptions=True)
        missing_paths = [
            path for path, res in zip(all_paths, stat_results)
            if isinstance(res, FileNotFoundError)
        ]

        if missing_paths:
            await store.delete_documents(missing_paths)

        return missing_paths