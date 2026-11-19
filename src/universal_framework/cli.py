"""Command-line interface for the framework project generator."""

from __future__ import annotations

import argparse
from collections.abc import Sequence

from universal_framework.project_generator import (
    SUPPORTED_PROJECT_TYPES,
    create_project,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ufs",
        description="Create a ready-to-extend Python application project.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    create_parser = subparsers.add_parser(
        "create",
        help="Generate a new application project.",
    )
    create_parser.add_argument("--name", required=True, help="Project name")
    create_parser.add_argument(
        "--type",
        dest="project_type",
        choices=SUPPORTED_PROJECT_TYPES,
        default="cli",
        help="Starter type: cli, web, or desktop (default: cli)",
    )
    create_parser.add_argument(
        "--destination",
        default=".",
        help="Parent folder for the new project (default: current directory)",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "create":
        try:
            project_dir = create_project(
                name=args.name,
                destination=args.destination,
                project_type=args.project_type,
            )
        except (ValueError, FileExistsError, OSError) as exc:
            parser.error(str(exc))
        print(f"Project created: {project_dir}")
        print("Next: open the folder, create a virtual environment, and install it.")
        return 0

    parser.error("Unknown command")
    return 2
