from dataclasses import dataclass
import numpy as np
from typing import List


@dataclass
class Document:
    """Internal representation of a file's content and embeddings."""

    path: str
    lines: List[str]
    embeddings: np.ndarray