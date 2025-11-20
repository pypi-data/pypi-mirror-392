"""CLI entry point for launching the Esprit Textual application."""

import argparse
from importlib.metadata import version
from pathlib import Path
from typing import Optional

from .app import SpreadsheetApp


def main(argv: Optional[list[str]] = None) -> None:
    """Entry point for esprit CLI."""
    parser = argparse.ArgumentParser(
        description="Structured table editor for terminal",
    )

    parser.add_argument(
        "--version",
        action="store_true",
        help="Display the esprit version and exit",
    )
    parser.add_argument(
        "file",
        nargs="?",
        help="Path to a JSON table file to open on startup",
    )
    args = parser.parse_args(argv)

    if args.version:
        print(f"{parser.prog} v{version('esprit')}")
        return

    start_file = Path(args.file).expanduser() if args.file else None
    app = SpreadsheetApp(start_file=start_file)
    app.run()


if __name__ == "__main__":
    main()
