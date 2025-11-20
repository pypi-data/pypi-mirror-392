"""Main CLI entry point for lf."""

import sys

import typer

app = typer.Typer(
    name="lf",
    help="loopflow - arrange LLMs to code in harmony",
    no_args_is_help=True,
)

from lf.cp.cli import app as cp_app

@app.command()
def cp(ctx: typer.Context):
    """Arrange codebase context for LLM interactions (alias for lfcp).

    This command is an alias that invokes lfcp with the same arguments.
    All arguments after 'cp' are passed directly to lfcp.
    """
    # Import here to avoid circular dependencies
    # Get all remaining arguments from sys.argv
    # Find the index of 'cp' and pass everything after it
    try:
        cp_index = sys.argv.index('cp')
        remaining_args = sys.argv[cp_index + 1:]
    except ValueError:
        remaining_args = []

    # Invoke the clip app with remaining arguments
    cp_app(remaining_args, standalone_mode=False)


if __name__ == "__main__":
    app()
