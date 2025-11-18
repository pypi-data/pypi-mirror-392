from dataclasses import dataclass
from typing import List

from ..workspace.store import RankedLine

@dataclass
class FormattedResult:
    """A unified structure for presenting a search result to the user."""

    header: str
    lines: List[str]
    highlighted_line_index: int  # relative to `lines`, -1 if none


class SearchResultFormatter:
    """Handles the formatting of search results for display."""

    def __init__(self, n_lines: int, is_tty: bool):
        self.n_lines = n_lines
        self.is_tty = is_tty

    @staticmethod
    def _format_header_with_context(ranked_line: RankedLine, start: int, end: int) -> str:
        """Formats the header showing a line range."""
        return f"{ranked_line.path}:{start + 1}::{end} ({ranked_line.distance:.4f})"

    @staticmethod
    def _format_header_simple(ranked_line: RankedLine) -> str:
        """Formats a simpler header for when file content is unavailable."""
        return f"{ranked_line.path}:{ranked_line.line_number + 1} ({ranked_line.distance:.4f})"

    def format_results(self, results: List[RankedLine]) -> List[FormattedResult]:
        """Formats a list of raw search results into a display-ready format."""
        if not results:
            return []

        return [self._format_ranked_line(res) for res in results]

    def _format_ranked_line(self, ranked_line: RankedLine) -> FormattedResult:
        """Formats a single workspace-backed RankedLine, reading the file for context."""
        start = max(0, ranked_line.line_number - self.n_lines)
        header = self._format_header_simple(ranked_line)

        try:
            with open(ranked_line.path, "r", encoding="utf-8") as f:
                lines = [line.rstrip("\n") for line in f.readlines()]
            end = min(len(lines), ranked_line.line_number + self.n_lines + 1)
            context_lines = lines[start:end]

            formatted_lines, highlighted_index = [], -1
            for i, line in enumerate(context_lines):
                line_num = start + i
                line_to_print = f"{line_num + 1:4}: {line}"
                if line_num == ranked_line.line_number and self.is_tty:
                    highlighted_index = i
                formatted_lines.append(line_to_print)

            return FormattedResult(
                header=self._format_header_with_context(ranked_line, start, end),
                lines=formatted_lines,
                highlighted_line_index=highlighted_index,
            )
        except (IOError, UnicodeDecodeError):
            return FormattedResult(
                header=header,
                lines=["    [Error: Could not read file content]"],
                highlighted_line_index=-1,
            )