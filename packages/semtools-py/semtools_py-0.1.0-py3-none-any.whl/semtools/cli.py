import asyncio
import sys
import click

from .config import APP_HOME_DIR, APP_HOME_DIR_NAME
from .parse import LlamaParseBackend
from .parse.enums import ParseBackendType
from .search import Searcher
from .search.presenter import SearchResultFormatter
from .workspace import Workspace, WorkspaceError


@click.command(help="A CLI tool for parsing documents using various backends")
@click.option(
    "-c",
    "--parse-config",
    "config_path",
    type=click.Path(),
    default=str(APP_HOME_DIR / "parse_config.json"),
    help=f"Path to the config file. Defaults to ~/{APP_HOME_DIR_NAME}/parse_config.json",
)
@click.option(
    "-b",
    "--backend",
    default=ParseBackendType.LLAMA_PARSE,
    help="The backend type to use for parsing. Defaults to `llama-parse`",
)
@click.option("-v", "--verbose", is_flag=True, help="Verbose output while parsing")
@click.argument("files", nargs=-1, type=click.Path(exists=True), required=True)
def parse(config_path, backend, verbose, files):
    if backend != ParseBackendType.LLAMA_PARSE:
        click.echo(f"Error: Unknown backend '{backend}'. Supported backends: {ParseBackendType.LLAMA_PARSE.value}", err=True)
        sys.exit(1)

    parser = LlamaParseBackend(config_path, verbose=verbose)

    results = asyncio.run(parser.parse(list(files)))

    for result_path in results:
        click.echo(result_path)


@click.command(help="A CLI tool for fast semantic keyword search")
@click.argument("query")
@click.argument("files", nargs=-1, type=click.Path(exists=True))
@click.option(
    "-n", "--n-lines", default=3, help="How many lines before/after to return as context"
)
@click.option(
    "--top-k", default=3, help="The top-k files or texts to return (ignored if max_distance is set)"
)
@click.option(
    "-m", "--max-distance", type=float, help="Return all results with distance below this threshold (0.0+)"
)
@click.option(
    "-i", "--ignore-case", is_flag=True, help="Perform case-insensitive search (default is false)"
)
def search(query, files, n_lines, top_k, max_distance, ignore_case):
    files = list(files)

    searcher = Searcher()
    try:
        results = asyncio.run(
            searcher.search(query, files, top_k, max_distance, ignore_case))
    except (ValueError, WorkspaceError) as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

    if not results:
        click.echo(f"No results found")
        return

    is_tty = sys.stdout.isatty()
    formatter = SearchResultFormatter(n_lines, is_tty)
    formatted_results = formatter.format_results(results)

    for res in formatted_results:
        click.echo(res.header)
        for i, line in enumerate(res.lines):
            if i == res.highlighted_line_index:
                # The line is already pre-formatted with its number.
                click.echo(click.style(line, bg="yellow", fg="black"))
            else:
                click.echo(line)
        click.echo()


@click.group(help="Manage semtools workspaces")
def workspace():
    pass


@workspace.command("use", help="Use or create a workspace (prints export command to run)")
@click.argument("name")
def use_workspace(name):
    try:
        asyncio.run(Workspace.create_or_use(name))
        click.echo(f"Workspace '{name}' configured.")
        click.echo("To activate it, run:")
        click.echo(f"  export SEMTOOLS_WORKSPACE={name}")
        click.echo()
        click.echo("Or add this to your shell profile (.bashrc, .zshrc, etc.)")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@workspace.command("delete", help="Permanently delete a workspace")
@click.argument("name")
def delete_workspace(name):
    """Deletes a workspace and all its associated data."""
    if not click.confirm(
        f"Are you sure you want to permanently delete the workspace '{name}'? This cannot be undone."
    ):
        click.echo("Deletion aborted.")
        return

    try:
        asyncio.run(Workspace.delete(name))
        click.echo(f"Workspace '{name}' has been deleted.")
        click.echo(f"If you had 'export SEMTOOLS_WORKSPACE={name}' in your shell, you should remove it.")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@workspace.command("status", help="Show active workspace and basic stats")
def status_workspace():
    try:
        ws, stats = asyncio.run(Workspace.get_active_workspace_with_stats())

        click.echo(f"Active workspace: {ws.config.name}")
        click.echo(f"Root: {ws.config.root_dir}")

        click.echo(f"Documents: {stats.total_documents}")
        if stats.has_index:
            index_info = stats.index_type or "Unknown"
            click.echo(f"Index: Yes ({index_info})")
        else:
            click.echo("Index: No")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@workspace.command("prune", help="Remove stale or missing files from store")
def prune_workspace():
    try:
        missing_paths = asyncio.run(Workspace.prune_active_workspace())

        if not missing_paths:
            click.echo("No stale documents found. Workspace is clean.")
            return

        click.echo(f"Found {len(missing_paths)} stale documents:")
        for path in missing_paths:
            click.echo(f"  - {path}")

        click.echo(f"Removed {len(missing_paths)} stale documents from workspace.")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
