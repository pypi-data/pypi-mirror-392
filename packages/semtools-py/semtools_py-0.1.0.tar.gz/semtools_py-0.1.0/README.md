# SemTools for Python

A collection of high-performance command-line tools for document processing and semantic search, built in Python. It leverages modern libraries like `asyncio` for concurrency, `lancedb` for efficient vector storage, and `model2vec` for state-of-the-art local embeddings.

- **`parse`**: Parse documents (PDF, DOCX, etc.) into clean markdown using the LlamaParse API, with intelligent caching to avoid re-processing.
- **`search`**: Perform fast, local semantic search on text files. It uses multilingual embeddings to find relevant lines of text based on meaning, not just keywords.
- **`workspace`**: Manage persistent workspaces to accelerate searches over large and evolving collections of documents. Embeddings are stored and indexed, and only changed files are re-processed.

## Key Features

- **Fast Local Semantic Search**: Uses `model2vec` embeddings (`minishlab/potion-multilingual-128M`) for high-quality, multilingual semantic search that runs entirely on your machine.
- **Powerful Document Parsing**: Integrates with LlamaParse for robust parsing of complex documents like PDFs into structured markdown.
- **Efficient Caching**: The `parse` tool caches results, only re-processing files when their content changes.
- **Persistent Workspaces**: The `search` tool can use workspaces powered by LanceDB to store and index embeddings, making subsequent searches on large file sets nearly instantaneous.
- **Unix-Friendly**: Designed to be a good citizen in a Unix-style shell, easily chainable with tools like `xargs`, `grep`, and `find`.
- **Async Powered**: Built with Python's `asyncio` to handle concurrent operations efficiently, especially for parsing multiple documents.

## Installation

**Prerequisites**:
- Python 3.13 or newer.
- For the `parse` tool: A LlamaIndex Cloud API key. Get one for free at [Llama Cloud](https://cloud.llamaindex.ai).

Install from PyPI:
```bash
pip install semtools-py
```

This will make the `parse`, `search`, and `workspace` commands available in your shell.

## Quick Start

### Basic Usage

```bash
# Parse some files into a cache directory (~/.semtools/cache/parse)
parse my_dir/*.pdf

# Search some text-based files
search "some keywords" *.txt --top-k 5 --n-lines 7

# Combine parsing and search
# The parse command outputs the paths to the cached markdown files
parse my_docs/*.pdf | xargs search "API endpoints"
```

### Using Workspaces

Workspaces accelerate search by creating a persistent, indexed database of your file embeddings.

```bash
# 1. Create and select a workspace
# Workspaces are stored in ~/.semtools/workspaces/
workspace use my-project-workspace
> Workspace 'my-project-workspace' configured.
> To activate it, run:
>   export SEMTOOLS_WORKSPACE=my-project-workspace
>
> Or add this to your shell profile (.bashrc, .zshrc, etc.)

# 2. Activate the workspace in your shell
export SEMTOOLS_WORKSPACE=my-project-workspace

# 3. Prime the workspace by running an initial search.
# This will embed all specified files and build a vector index.
# This may take some time on the first run.
search "initial query" ./large_codebase/**/*.py --top-k 10

# 4. Subsequent searches are now extremely fast.
# Only new or modified files will be re-embedded.
search "a different query" ./large_codebase/**/*.py --top-k 10

# If you delete files, prune the workspace to remove stale entries
workspace prune

# Check the status of your active workspace
workspace status
> Active workspace: my-project-workspace
> Root: /home/user/.semtools/workspaces/my-project-workspace
> Documents: 1503
> Index: Yes (IVF_PQ)

# Delete a workspace permanently
workspace delete my-project-workspace
```

### Running from Source (Standalone)

If you prefer to run the tools directly from a cloned repository without installing the package globally, you can use an editable install:

```bash
# Clone the repository
git clone https://github.com/your-repo/semtools-py.git
cd semtools-py

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate

# Install in editable mode with development dependencies
pip install -e ".[dev]"
```

After this setup, the `parse`, `search`, and `workspace` commands are available directly in your shell (within the activated environment). They point to your local source code, allowing for development and standalone use.

```bash
# Now you can run the commands from your local code
parse ./my_docs/*.pdf --verbose
search "local development" ./**/*.py

### Programmatic Usage (as a Library)

You can also use `semtools` directly in your Python code. The core logic is exposed through classes like `Searcher`.

Here is an example of how to perform a search programmatically:

import asyncio
from pathlib import Path
from semtools.search import Searcher

async def main():
    # Create a dummy file to search in
    p = Path("my_document.txt")
    p.write_text("The quick brown fox jumps over the lazy dog.\nAnother line about something else.")

    # Instantiate the searcher
    searcher = Searcher()

    # Perform the search (note that it's an async operation)
    query = "fast animal"
    files = [str(p)]
    results = await searcher.search(query=query, files=files, top_k=1)

    # Process the results
    if results:
        print(f"Found {len(results)} result(s):")
        for result in results:
            print(f"  - Path: {result.path}")
            print(f"    Line: {result.line_number + 1}")  # +1 for 1-based indexing
            print(f"    Distance: {result.distance:.4f}")
    else:
        print("No results found.")
    
    # Clean up the dummy file
    p.unlink()

if __name__ == "__main__":
    asyncio.run(main())
```

## CLI Help

```
$ parse --help
Usage: parse [OPTIONS] FILES...

  A CLI tool for parsing documents using various backends

Arguments:
  FILES...  [required]

Options:
  -c, --parse-config TEXT  Path to the config file. Defaults to
                           ~/.semtools/parse_config.json
  -b, --backend TEXT       The backend type to use for parsing. Defaults to
                           `llama-parse`  [default: llama-parse]
  -v, --verbose            Verbose output while parsing
  --help                   Show this message and exit.
```

```
$ search --help
Usage: search [OPTIONS] QUERY [FILES]...

  A CLI tool for fast semantic keyword search

Arguments:
  QUERY  [required]
  [FILES]...

Options:
  -n, --n-lines INTEGER   How many lines before/after to return as context
                          [default: 3]
  --top-k INTEGER         The top-k files or texts to return (ignored if
                          max_distance is set)  [default: 3]
  -m, --max-distance FLOAT
                          Return all results with distance below this
                          threshold (0.0+)
  -i, --ignore-case       Perform case-insensitive search (default is false)
  --help                  Show this message and exit.
```

```
$ workspace --help
Usage: workspace [OPTIONS] COMMAND [ARGS]...

  Manage semtools workspaces

Options:
  --help  Show this message and exit.

Commands:
  delete  Permanently delete a workspace
  prune   Remove stale or missing files from store
  status  Show active workspace and basic stats
  use     Use or create a workspace (prints export command to run)
```

## Configuration

The `parse` tool requires a LlamaParse API key. It can be configured in two ways:

1.  **Environment Variable (Recommended)**:
    ```bash
    export LLAMA_CLOUD_API_KEY="your_api_key_here"
    ```

2.  **Configuration File**:
    Create a file at `~/.semtools/parse_config.json`. The tool will load this file if it exists. See `src/semtools/parse/config.py` for all options.

## Qualitative Benchmark

`SemTools` includes a qualitative benchmark to evaluate the retrieval performance of the `search` command against a curated dataset of arXiv research papers.

The benchmark uses a powerful LLM (Google's Gemini) as an "Oracle" to generate complex questions and ground truth answers from a set of source documents. It then executes `search` for each question and asks the Oracle to synthesize a new answer using *only* the search results. A final Markdown report is generated comparing the ground truth answer, the search-augmented answer, and retrieval metrics (Precision/Recall).

### Running the Benchmark

1.  **Get the Source Code**: The benchmark scripts are part of the development repository and not included in the PyPI package. Clone the repository to get the necessary files:
    ```bash
    git clone https://github.com/your-repo/semtools-py.git
    cd semtools-py
    ```
2.  **Install Dependencies**: Ensure you have the development dependencies installed:
    ```bash
    pip install -e ".[dev]"
    ```
3.  **Set API Key**: Set your Gemini API key:
    ```bash
    export GEMINI_API_KEY="your_gemini_api_key"
    ```
4.  **Download Data**: Download the benchmark dataset:
    ```bash
    python benchmarks/arxiv/download_arxiv_files.py
    ```
5.  **Run**: Run the benchmark:
    ```bash
    python benchmarks/arxiv/benchmark.py --mode workspace
    ```
    A report file (`benchmark_qualitative_report_workspace.md`) will be created in the `benchmarks/arxiv` directory.

## License

This project is licensed under the MIT License.

## Acknowledgments

- [LlamaParse](https://cloud.llamaindex.ai) for the powerful document parsing API.
- [model2vec](https://github.com/johann-petrak/model2vec-py) for the fast, high-quality local embedding generation.
- [LanceDB](https://lancedb.com/) for the efficient and scalable vector database engine.
- [minishlab/potion-multilingual-128M](https://huggingface.co/minishlab/potion-multilingual-128M) for the excellent open-source embedding model.
