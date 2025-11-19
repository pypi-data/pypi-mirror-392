from collections.abc import Sized
from pathlib import Path

from rich.console import Console
from rich.markup import escape

console = Console()

ICON_OK = ":heavy_check_mark:"
ICON_SKIP = ":x:"
STYLE_PATH = "bold cyan"
STYLE_OK = "green"
STYLE_SKIP = "yellow"
STYLE_DIM = "dim"


def print_included(path: Path) -> None:
    console.print(f"{ICON_OK} {escape(path.as_posix())} — file included")


def print_summary(included: Sized) -> None:
    included_count = len(included)
    console.rule("[b]Summary")
    console.print(f"{ICON_OK} [bold {STYLE_OK}]Included:[/] {included_count}")
