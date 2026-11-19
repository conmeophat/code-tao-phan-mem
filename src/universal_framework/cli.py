"""Command-line interface for the framework project generator."""

from __future__ import annotations

import argparse
from collections.abc import Callable, Sequence

from universal_framework.project_generator import (
    SUPPORTED_DATABASES,
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
    create_parser.add_argument(
        "--database",
        choices=SUPPORTED_DATABASES,
        default="none",
        help="Optional storage pack: none or sqlite (default: none)",
    )
    create_parser.add_argument(
        "--description",
        default=None,
        help="One-line project description (maximum 200 characters)",
    )

    subparsers.add_parser(
        "wizard",
        help="Answer a few questions to create a new project.",
    )
    return parser


def _create_from_values(
    parser: argparse.ArgumentParser,
    *,
    name: str,
    project_type: str,
    destination: str,
    database: str,
    description: str | None,
    output_fn: Callable[[str], None],
) -> int:
    try:
        project_dir = create_project(
            name=name,
            destination=destination,
            project_type=project_type,
            database=database,
            description=description,
        )
    except (ValueError, FileExistsError, OSError) as exc:
        parser.error(str(exc))

    output_fn(f"Project created: {project_dir}")
    output_fn("Next: open the folder, create a virtual environment, and install it.")
    return 0


def main(
    argv: Sequence[str] | None = None,
    *,
    input_fn: Callable[[str], str] | None = None,
    output_fn: Callable[[str], None] = print,
) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "create":
        return _create_from_values(
            parser,
            name=args.name,
            project_type=args.project_type,
            destination=args.destination,
            database=args.database,
            description=args.description,
            output_fn=output_fn,
        )

    if args.command == "wizard":
        ask = input if input_fn is None else input_fn
        output_fn("=== UNIVERSAL PYTHON PROJECT WIZARD ===")
        name = ask("Tên dự án (ví dụ: QuanLyKho): ").strip()
        project_type = ask("Loại phần mềm [cli/web/desktop] (mặc định cli): ").strip() or "cli"
        database = ask("Lưu trữ dữ liệu [none/sqlite] (mặc định none): ").strip() or "none"
        destination = ask("Thư mục chứa dự án (mặc định thư mục hiện tại): ").strip() or "."
        description = ask("Mô tả ngắn (có thể để trống): ").strip() or None

        return _create_from_values(
            parser,
            name=name,
            project_type=project_type,
            destination=destination,
            database=database,
            description=description,
            output_fn=output_fn,
        )

    parser.error("Unknown command")
    return 2
