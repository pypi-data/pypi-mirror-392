from enum import StrEnum


class EmbeddingModel(StrEnum):
    """Semantic embedding models supported by the search functionality."""

    POTION_MULTI_LINGUAL_128M = "minishlab/potion-multilingual-128M"
