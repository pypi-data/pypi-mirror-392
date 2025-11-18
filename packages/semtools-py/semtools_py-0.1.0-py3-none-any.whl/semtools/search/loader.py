import asyncio
import sys
from typing import List, Optional

import aiofiles
import numpy as np
from model2vec import StaticModel

from .models import Document


class DocumentLoader:
    """Handles loading and processing of documents from various sources."""

    def __init__(self, model: StaticModel, ignore_case: bool = False):
        self.model = model
        self.ignore_case = ignore_case
        self._lock = asyncio.Lock()

    async def encode(self, lines: List[str]) -> np.ndarray:
        """Asynchronously encodes lines by running the sync encoder in a thread."""
        lines_for_embedding = (
            [line.lower() for line in lines] if self.ignore_case else lines
        )
        async with self._lock:
            return await asyncio.to_thread(self.model.encode, lines_for_embedding)

    @staticmethod
    def normalize_lines(raw_lines: List[str]) -> List[str]:
        """Removes trailing newlines from a list of strings."""
        return [line.rstrip("\n") for line in raw_lines]

    @staticmethod
    def apply_case_sensitivity(lines: List[str], ignore_case: bool) -> List[str]:
        """Applies case folding to a list of strings if required."""
        if ignore_case:
            return [line.lower() for line in lines]
        return lines

    async def load(self, files: List[str]) -> List[Document]:
        """Loads documents from files or stdin."""
        if not files and not sys.stdin.isatty():
            return await self._load_from_stdin()
        return await self._load_from_files(files)

    async def load_file(self, file_path: str) -> Optional[Document]:
        """Loads and processes a single file."""
        try:
            async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
                raw_lines = await f.readlines()
                if lines := self.normalize_lines(raw_lines):
                    return await self._create_document_from_lines(file_path, lines)
        except (IOError, UnicodeDecodeError):
            return None
        return None

    async def _load_from_stdin(self) -> List[Document]:
        """Loads a single document from stdin."""
        documents: List[Document] = []
        raw_lines = await asyncio.to_thread(sys.stdin.readlines)
        if stdin_lines := self.normalize_lines(raw_lines):
            if doc := await self._create_document_from_lines("<stdin>", stdin_lines):
                documents.append(doc)
        return documents

    async def _load_from_files(self, files: List[str]) -> List[Document]:
        """Loads documents from a list of file paths."""
        tasks = [self.load_file(fp) for fp in files]
        results = await asyncio.gather(*tasks)
        return [doc for doc in results if doc is not None]

    async def _create_document_from_lines(
        self, file_path: str, lines: List[str]
    ) -> Optional[Document]:
        """Creates a Document from lines of text."""
        embeddings = await self.encode(lines)

        return Document(
            path=file_path, lines=lines, embeddings=np.array(embeddings)
        )