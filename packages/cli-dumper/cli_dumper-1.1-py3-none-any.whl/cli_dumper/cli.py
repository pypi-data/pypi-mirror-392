from pathlib import Path
from typing import Annotated

import typer

from cli_dumper.core import find_targets, process_targets
from cli_dumper.display import console, print_summary

app = typer.Typer(
    help="A CLI tool that merges multiple files into a single text file",
    add_completion=False,
)


@app.command()
def dumper(
    extensions: Annotated[list[str], typer.Argument(help="Extensions to include")],
    ignored_dirs: Annotated[
        list[str],
        typer.Option(
            "--ignored-dirs",
            "-id",
            help="Folders to ignore",
            show_default="[]",
            default_factory=list,
        ),
    ],
    ignored_files: Annotated[
        list[str],
        typer.Option(
            "--ignored-files",
            "-if",
            help="Files to ignore",
            show_default="[]",
            default_factory=list,
        ),
    ],
) -> None:
    root = Path(".").resolve()
    output = root / "project_dump.txt"

    console.rule(root.as_posix())
    included_files = find_targets(extensions, ignored_dirs, ignored_files, root)
    process_targets(included_files, root, output)
    print_summary(included_files)
