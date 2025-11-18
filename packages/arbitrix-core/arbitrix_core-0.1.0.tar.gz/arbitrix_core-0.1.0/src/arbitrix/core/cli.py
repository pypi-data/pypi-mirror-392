from __future__ import annotations

import argparse
import sys

from arbitrix._version import __version__


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="arbitrix-core",
        description="Utility helpers for working with the Arbitrix open-core toolkit.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"arbitrix-core {__version__}",
    )
    parser.add_argument(
        "--about",
        action="store_true",
        help="Print a short summary of the available core modules.",
    )
    parser.add_argument(
        "--docs",
        action="store_true",
        help="Print a link to the local documentation entry point.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.about:
        print(
            "Arbitrix Core exposes the backtesting engine, strategy base classes, "
            "cost models, and technical indicators required for local research."
        )
    if args.docs:
        print("Documentation: https://github.com/your-org/arbitrix/tree/main/docs")
    if not (args.about or args.docs):
        parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
