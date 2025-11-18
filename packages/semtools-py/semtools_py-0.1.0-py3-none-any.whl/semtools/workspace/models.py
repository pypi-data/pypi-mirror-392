from dataclasses import dataclass
from typing import Optional


@dataclass
class WorkspaceConfig:
    """Configuration for a semtools workspace."""

    name: str = "default"
    root_dir: str = ""
    in_batch_size: int = 5_000
    oversample_factor: int = 3
    file_process_chunk_size: int = 50


@dataclass
class WorkspaceStats:
    """Statistics about the workspace."""

    total_documents: int
    has_index: bool
    index_type: Optional[str]