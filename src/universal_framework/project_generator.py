"""Generate ready-to-run starter projects safely."""

from __future__ import annotations

import json
import keyword
from pathlib import Path
import re
import shutil


SUPPORTED_PROJECT_TYPES = ("cli", "web", "desktop")
SUPPORTED_DATABASES = ("none", "sqlite")
_NAME_PATTERN = re.compile(r"[A-Za-z][A-Za-z0-9_-]{0,49}")
_WINDOWS_RESERVED_NAMES = {
    "con", "prn", "aux", "nul", "conin$", "conout$",
    *(f"com{number}" for number in range(1, 10)),
    *(f"lpt{number}" for number in range(1, 10)),
}


def _normalise_name(name: str) -> tuple[str, str]:
    """Return (directory_name, importable_package_name)."""
    if not isinstance(name, str) or not _NAME_PATTERN.fullmatch(name):
        raise ValueError(
            "Project name must start with a letter and contain only "
            "English letters, numbers, '_' or '-' (maximum 50 characters)."
        )

    directory_name = name.lower()
    package_name = directory_name.replace("-", "_")
    if not package_name.isidentifier() or keyword.iskeyword(package_name):
        raise ValueError(
            f"Project name '{name}' becomes an invalid Python package name."
        )
    if directory_name.casefold() in _WINDOWS_RESERVED_NAMES:
        raise ValueError(
            f"Project name '{name}' is reserved by Windows and cannot be used as a folder."
        )
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


_SQLITE_STORAGE_TEMPLATE = '''"""Small JSON key-value storage backed by SQLite.

This starter is intended for a single application process. For concurrent
multi-process workloads, design and test a more specific persistence layer.
"""

from __future__ import annotations

import json
from pathlib import Path
import sqlite3
from typing import Any


class SQLiteStore:
    """Persist JSON-compatible values under string keys."""

    def __init__(self, database_path: str | Path = "data/app.db") -> None:
        raw_path = str(database_path)
        if raw_path != ":memory:":
            path = Path(raw_path).expanduser()
            path.parent.mkdir(parents=True, exist_ok=True)
            raw_path = str(path)

        self._connection = sqlite3.connect(raw_path)
        self._closed = False
        self._connection.execute(
            """
            CREATE TABLE IF NOT EXISTS kv_store (
                key TEXT PRIMARY KEY,
                value_json TEXT NOT NULL
            )
            """
        )
        self._connection.commit()

    def _ensure_open(self) -> None:
        if self._closed:
            raise RuntimeError("SQLiteStore is already closed")

    @staticmethod
    def _validate_key(key: str) -> None:
        if not isinstance(key, str) or not key.strip():
            raise ValueError("key must be a non-empty string")

    def set(self, key: str, value: Any) -> None:
        """Insert or replace a JSON-compatible value."""
        self._ensure_open()
        self._validate_key(key)
        serialized = json.dumps(value, ensure_ascii=False, allow_nan=False)
        with self._connection:
            self._connection.execute(
                """
                INSERT INTO kv_store (key, value_json)
                VALUES (?, ?)
                ON CONFLICT(key) DO UPDATE SET value_json = excluded.value_json
                """,
                (key, serialized),
            )

    def get(self, key: str, default: Any = None) -> Any:
        """Read a value, returning default when the key does not exist."""
        self._ensure_open()
        self._validate_key(key)
        row = self._connection.execute(
            "SELECT value_json FROM kv_store WHERE key = ?", (key,)
        ).fetchone()
        return default if row is None else json.loads(row[0])

    def delete(self, key: str) -> bool:
        """Delete a key and report whether a row was removed."""
        self._ensure_open()
        self._validate_key(key)
        with self._connection:
            cursor = self._connection.execute(
                "DELETE FROM kv_store WHERE key = ?", (key,)
            )
        return cursor.rowcount > 0

    def keys(self) -> tuple[str, ...]:
        """Return all stored keys in sorted order."""
        self._ensure_open()
        rows = self._connection.execute(
            "SELECT key FROM kv_store ORDER BY key"
        ).fetchall()
        return tuple(row[0] for row in rows)

    def close(self) -> None:
        """Close the connection. Repeated calls are safe."""
        if not self._closed:
            self._connection.close()
            self._closed = True

    def __enter__(self) -> "SQLiteStore":
        self._ensure_open()
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> bool:
        self.close()
        return False
'''


def create_project(
    name: str,
    destination: str | Path = ".",
    project_type: str = "cli",
    *,
    database: str = "none",
    description: str | None = None,
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

    if not isinstance(database, str) or database.strip().lower() not in SUPPORTED_DATABASES:
        allowed = ", ".join(SUPPORTED_DATABASES)
        raise ValueError(f"database must be one of: {allowed}")
    normalized_database = database.strip().lower()

    if description is None:
        project_description = f"A {normalized_type} Python application"
    elif not isinstance(description, str) or not description.strip():
        raise ValueError("description must be a non-empty, single-line string")
    else:
        project_description = description.strip()
    if len(project_description) > 200 or "\n" in project_description or "\r" in project_description:
        raise ValueError("description must be a single line of at most 200 characters")

    parent = Path(destination).expanduser().resolve()
    parent.mkdir(parents=True, exist_ok=True)
    project_dir = parent / directory_name
    project_dir.mkdir()

    project_title = name.replace("_", " ").replace("-", " ").title()
    distribution_name = directory_name.replace("_", "-")
    description_toml = json.dumps(project_description, ensure_ascii=False)
    files: dict[str, str] = {
        f"src/{package_name}/__init__.py": (
            '"""Application package."""' + chr(10) * 2
            + '__version__ = "0.1.0"' + chr(10)
        ),
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
name = "{distribution_name}"
version = "0.1.0"
description = {description_toml}
requires-python = ">=3.11"
dependencies = []

[project.scripts]
{distribution_name} = "{package_name}.main:main"

[tool.setuptools]
package-dir = {{ "" = "src" }}

[tool.setuptools.packages.find]
where = ["src"]
''',
        "README.md": f'''# {project_title}

{project_description}

Generated by Universal Python Software Framework.

## Requirements

- Python 3.11 or newer
- SQLite storage uses Python's standard library and needs no separate database server.
{"" if normalized_type != "desktop" else "- Tkinter must be available in your Python installation."}

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

{"## SQLite storage" + chr(10) + chr(10) + "The optional SQLiteStore stores JSON-compatible values by key:" + chr(10) + chr(10) + "~~~python" + chr(10) + f"from {package_name}.storage import SQLiteStore" + chr(10) * 2 + 'with SQLiteStore("data/app.db") as store:' + chr(10) + '    store.set("settings", {"language": "vi"})' + chr(10) + '    settings = store.get("settings", default={})' + chr(10) + '    print(settings)' + chr(10) + "~~~" + chr(10) if normalized_database == "sqlite" else ""}

This is a starter scaffold. Add and test your own business features before production use.
''',
        ".gitignore": """__pycache__/
*.py[cod]
.venv/
venv/
.env
*.log
.pytest_cache/
build/
dist/
*.egg-info/
data/
""",
    }

    if normalized_database == "sqlite":
        files[f"src/{package_name}/storage.py"] = _SQLITE_STORAGE_TEMPLATE
        files["tests/test_storage.py"] = f'''"""Tests for the generated SQLite storage module."""

import unittest

from {package_name}.storage import SQLiteStore


class SQLiteStoreTests(unittest.TestCase):
    def test_round_trip_unicode_json_and_delete(self) -> None:
        with SQLiteStore(":memory:") as store:
            value = {{"language": "Tiếng Việt", "items": [1, 2, 3]}}
            store.set("settings", value)
            self.assertEqual(store.get("settings"), value)
            self.assertEqual(store.keys(), ("settings",))
            self.assertTrue(store.delete("settings"))
            self.assertFalse(store.delete("settings"))
            self.assertEqual(store.get("settings", default={{}}), {{}})


if __name__ == "__main__":
    unittest.main()
'''

    try:
        (project_dir / "src" / package_name).mkdir(parents=True)
        (project_dir / "tests").mkdir(parents=True)
        for relative_path, file_content in files.items():
            file_path = project_dir / relative_path
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(file_content, encoding="utf-8")
    except Exception:
        shutil.rmtree(project_dir, ignore_errors=True)
        raise

    return project_dir
