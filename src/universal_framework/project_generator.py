"""Generate ready-to-run starter projects safely."""

from __future__ import annotations

from pathlib import Path
import re
import shutil


SUPPORTED_PROJECT_TYPES = ("cli", "web", "desktop")
_NAME_PATTERN = re.compile(r"[A-Za-z][A-Za-z0-9_-]{0,49}")


def _normalise_name(name: str) -> tuple[str, str]:
    """Return (directory_name, importable_package_name)."""
    if not isinstance(name, str) or not _NAME_PATTERN.fullmatch(name):
        raise ValueError(
            "Project name must start with a letter and contain only "
            "English letters, numbers, '_' or '-' (maximum 50 characters)."
        )

    directory_name = name.lower()
    package_name = directory_name.replace("-", "_")
    return directory_name, package_name


def _main_template(project_title: str, project_type: str) -> str:
    if project_type == "cli":
        return '''"""Command-line entry point for {title}."""

import argparse


def main() -> int:
    parser = argparse.ArgumentParser(description="{title}")
    parser.add_argument("--name", default="World", help="Name to greet")
    args = parser.parse_args()
    print(f"Hello, {{args.name}}! Welcome to {title}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''.format(title=project_title)

    if project_type == "web":
        return '''"""A small standard-library web server for {title}."""

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        body = (
            "<!doctype html><html lang='en'><meta charset='utf-8'>"
            "<title>{title}</title><body><h1>{title}</h1>"
            "<p>Your application is running.</p></body></html>"
        ).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main() -> int:
    server = ThreadingHTTPServer(("127.0.0.1", 8000), RequestHandler)
    print("Open http://127.0.0.1:8000 in your browser. Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\\nStopping server...")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''.format(title=project_title)

    return '''"""A small Tkinter desktop window for {title}."""

import tkinter as tk


def main() -> int:
    window = tk.Tk()
    window.title("{title}")
    window.geometry("480x240")

    heading = tk.Label(window, text="{title}", font=("Segoe UI", 18, "bold"))
    heading.pack(pady=(45, 12))

    message = tk.Label(window, text="Your desktop application is ready to extend.")
    message.pack(pady=8)

    close_button = tk.Button(window, text="Close", command=window.destroy)
    close_button.pack(pady=16)

    window.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''.format(title=project_title)


def create_project(
    name: str,
    destination: str | Path = ".",
    project_type: str = "cli",
) -> Path:
    """Create a starter project and return its absolute directory path.

    destination is the parent folder in which the project directory will
    be created. Existing project directories are never overwritten.
    """
    directory_name, package_name = _normalise_name(name)
    if not isinstance(project_type, str):
        raise ValueError("project_type must be one of: cli, web, desktop")
    normalized_type = project_type.strip().lower()
    if normalized_type not in SUPPORTED_PROJECT_TYPES:
        allowed = ", ".join(SUPPORTED_PROJECT_TYPES)
        raise ValueError(f"Unsupported project type '{project_type}'. Choose: {allowed}")

    parent = Path(destination).expanduser().resolve()
    parent.mkdir(parents=True, exist_ok=True)
    project_dir = parent / directory_name

    # mkdir() is the atomic no-overwrite operation. Do not delete the target
    # unless this process successfully created the directory itself.
    project_dir.mkdir()

    project_title = name.replace("_", " ").replace("-", " ").title()
    files: dict[str, str] = {
        f"src/{package_name}/__init__.py": '"""Application package."""\\n\\n__version__ = "0.1.0"\\n',
        f"src/{package_name}/__main__.py": f'''"""Run {project_title} as a Python module."""

from {package_name}.main import main


if __name__ == "__main__":
    raise SystemExit(main())
''',
        f"src/{package_name}/main.py": _main_template(project_title, normalized_type),
        "tests/test_smoke.py": f'''"""Basic import test for {project_title}."""

import unittest

import {package_name}


class ProjectSmokeTests(unittest.TestCase):
    def test_package_has_version(self) -> None:
        self.assertEqual({package_name}.__version__, "0.1.0")


if __name__ == "__main__":
    unittest.main()
''',
        "pyproject.toml": f'''[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[project]
name = "{directory_name.replace("_", "-")}"
version = "0.1.0"
description = "A {normalized_type} Python application"
requires-python = ">=3.11"
dependencies = []

[project.scripts]
{directory_name.replace("_", "-")} = "{package_name}.main:main"

[tool.setuptools]
package-dir = {{ "" = "src" }}

[tool.setuptools.packages.find]
where = ["src"]
''',
        "README.md": f'''# {project_title}

Starter project generated by Universal Python Software Framework.

## Requirements

- Python 3.11 or newer

## Setup (Windows PowerShell)

~~~powershell
py -m venv .venv
./.venv/Scripts/python.exe -m pip install -e .
~~~

## Run

~~~powershell
py -m {package_name}
~~~

## Test

~~~powershell
py -m unittest discover -s tests -v
~~~

This is a starter scaffold. Add and test your own business features before using it in production.
''',
        ".gitignore": "__pycache__/\\n*.py[cod]\\n.venv/\\nvenv/\\n.env\\n*.log\\n.pytest_cache/\\nbuild/\\ndist/\\n*.egg-info/\\n",
    }

    try:
        (project_dir / "src" / package_name).mkdir(parents=True)
        (project_dir / "tests").mkdir(parents=True)
        for relative_path, file_content in files.items():
            file_path = project_dir / relative_path
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(file_content, encoding="utf-8", newline="\\n")
    except Exception:
        shutil.rmtree(project_dir, ignore_errors=True)
        raise

    return project_dir
