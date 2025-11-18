from unittest.mock import MagicMock

import numpy as np
import pytest

from src.semtools.search.core import Searcher
from src.semtools.search.models import Document
from src.semtools.workspace.store import RankedLine

MOCK_FILE_CONTENT = "\n".join([
    "Line 1: The quick brown fox jumps over the lazy dog.",
    "Line 2: A journey of a thousand miles begins with a single step.",
    "Line 3: To be or not to be, that is the question.",
    "Line 4: All that glitters is not gold.",
    "Line 5: The early bird catches the worm.",
    "Line 6: Where there's a will, there's a way.",
    "Line 7: A picture is worth a thousand words.",
    "Line 8: The pen is mightier than the sword.",
    "Line 9: Actions speak louder than words.",
    "Line 10: An apple a day keeps the doctor away.",
    "Line 11: Practice makes perfect.",
    "Line 12: Look before you leap.",
    "Line 13: Honesty is the best policy.",
    "Line 14: Laughter is the best medicine.",
    "Line 15: If it ain't broke, don't fix it.",
    "Line 16: When in Rome, do as the Romans do.",
    "Line 17: Don't count your chickens before they hatch.",
    "Line 18: Every cloud has a silver lining.",
    "Line 19: A watched pot never boils.",
    "Line 20: Beggars can't be choosers.",
    ""
])

@pytest.fixture
def mock_file(tmp_path):
    """Creates a mock text file for testing."""
    file_path = tmp_path / "test.txt"
    file_path.write_text(MOCK_FILE_CONTENT)
    return file_path


@pytest.fixture
def mock_documents() -> list[Document]:
    """Provides a list of mock Document objects."""
    return [
        Document(
            path="/fake/doc1.txt",
            lines=["hello world", "this is a test"],
            embeddings=np.array([[0.1, 0.2], [0.3, 0.4]]),
        ),
        Document(
            path="/fake/doc2.txt",
            lines=["another document", "for testing purposes"],
            embeddings=np.array([[0.5, 0.6], [0.7, 0.8]]),
        ),
    ]


@pytest.fixture
def mock_ranked_lines() -> list[RankedLine]:
    """Provides a list of mock RankedLine objects."""
    return [
        RankedLine(path="/fake/doc1.txt", line_number=5, distance=0.456),
    ]


@pytest.fixture
def searcher() -> Searcher:
    """Provides a Searcher instance with a mocked model."""
    mock_model = MagicMock()
    def dynamic_encode(lines):
        return np.array([[0.1, 0.2]] * len(lines))
    mock_model.encode.side_effect = dynamic_encode
    return Searcher(model=mock_model)