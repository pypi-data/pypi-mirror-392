from src.semtools.search.presenter import SearchResultFormatter
from src.semtools.workspace.store import RankedLine


class TestSearchResultFormatter:
    def test_format_ranked_lines(self, mock_ranked_lines, mock_file):
        
        formatter = SearchResultFormatter(n_lines=2, is_tty=True)
        mock_ranked_lines[0].path = str(mock_file)
        mock_ranked_lines[0].line_number = 5

        
        formatted = formatter.format_results(mock_ranked_lines)

        
        assert len(formatted) == 1
        assert formatted[0].header.startswith(f"{mock_file}:4::8")
        assert len(formatted[0].lines) == 5  # 2 before + 1 match + 2 after
        assert "Line 6: Where there's a will, there's a way." in "".join(formatted[0].lines)
        assert formatted[0].highlighted_line_index == 2

    def test_format_empty_results(self):
        formatter = SearchResultFormatter(n_lines=3, is_tty=True)
        assert not formatter.format_results([])

    def test_format_ranked_line_file_not_found(self):
        
        formatter = SearchResultFormatter(n_lines=3, is_tty=False)
        ranked_line = RankedLine(path="/non/existent/file.txt", line_number=1, distance=0.1)

        
        formatted = formatter.format_results([ranked_line])

        
        assert "[Error: Could not read file content]" in formatted[0].lines[0]

    def test_format_results_with_tty_disabled(self, tmp_path):
        formatter = SearchResultFormatter(n_lines=3, is_tty=False)
        mock_file = tmp_path / "test.txt"
        mock_file.write_text("line 1")
        res = RankedLine(path=str(mock_file), line_number=0, distance=0.1)

        formatted = formatter.format_results([res])

        assert formatted[0].highlighted_line_index == -1

    def test_format_results_with_tty_enabled(self, tmp_path):
        formatter = SearchResultFormatter(n_lines=3, is_tty=True)
        mock_file = tmp_path / "test.txt"
        mock_file.write_text("line 1")
        res = RankedLine(path=str(mock_file), line_number=0, distance=0.1)

        formatted = formatter.format_results([res])

        assert formatted[0].highlighted_line_index == 0

    def test_format_ranked_line_at_file_start(self, mock_ranked_lines, mock_file):
        formatter = SearchResultFormatter(n_lines=2, is_tty=True)
        mock_ranked_lines[0].path = str(mock_file)
        mock_ranked_lines[0].line_number = 0  # Match at the beginning

        formatted = formatter.format_results(mock_ranked_lines)

        assert len(formatted) == 1
        assert formatted[0].header.startswith(f"{mock_file}:1::3")
        assert "Line 1: The quick brown fox jumps over the lazy dog." in "".join(formatted[0].lines)
        assert formatted[0].highlighted_line_index == 0

    def test_format_ranked_line_at_file_end(self, mock_ranked_lines, mock_file):
        formatter = SearchResultFormatter(n_lines=2, is_tty=True)
        mock_ranked_lines[0].path = str(mock_file)
        mock_ranked_lines[0].line_number = 19  # Match at the end (20 lines total)

        formatted = formatter.format_results(mock_ranked_lines)

        assert len(formatted) == 1
        assert formatted[0].header.startswith(f"{mock_file}:18::20")
        assert "Line 20: Beggars can't be choosers." in "".join(formatted[0].lines)
        assert formatted[0].highlighted_line_index == 2  # Relative to context [17, 18, 19]

    def test_format_ranked_line_with_zero_context(self, mock_ranked_lines, mock_file):
        formatter = SearchResultFormatter(n_lines=0, is_tty=True)
        mock_ranked_lines[0].path = str(mock_file)
        mock_ranked_lines[0].line_number = 5

        formatted = formatter.format_results(mock_ranked_lines)

        assert len(formatted[0].lines) == 1
        assert formatted[0].header.startswith(f"{mock_file}:6::6")
        assert formatted[0].highlighted_line_index == 0