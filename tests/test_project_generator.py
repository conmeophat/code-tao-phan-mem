"""Tests for safe project generation."""

import ast
from pathlib import Path
import tempfile
import tomllib
import unittest

from universal_framework.project_generator import create_project


class ProjectGeneratorTests(unittest.TestCase):
    def test_creates_cli_project_structure(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            project_dir = create_project("MyFirstApp", temporary_directory, "cli")

            self.assertTrue((project_dir / "pyproject.toml").is_file())
            self.assertTrue((project_dir / "README.md").is_file())
            self.assertTrue((project_dir / "src" / "myfirstapp" / "main.py").is_file())
            self.assertTrue((project_dir / "src" / "myfirstapp" / "__main__.py").is_file())
            self.assertTrue((project_dir / "tests" / "test_smoke.py").is_file())
            self.assertEqual(project_dir.parent, Path(temporary_directory).resolve())

    def test_normalizes_hyphens_for_python_package(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            project_dir = create_project("Sales-Manager", temporary_directory)
            self.assertTrue(
                (project_dir / "src" / "sales_manager" / "__init__.py").is_file()
            )
            generated_main = (
                project_dir / "src" / "sales_manager" / "main.py"
            ).read_text(encoding="utf-8")
            self.assertIn("Sales Manager", generated_main)

    def test_supports_web_and_desktop_templates(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            web_dir = create_project("WebDemo", temporary_directory, "web")
            desktop_dir = create_project("DesktopDemo", temporary_directory, "desktop")

            web_main = (web_dir / "src" / "webdemo" / "main.py").read_text(
                encoding="utf-8"
            )
            desktop_main = (
                desktop_dir / "src" / "desktopdemo" / "main.py"
            ).read_text(encoding="utf-8")
            self.assertIn("ThreadingHTTPServer", web_main)
            self.assertIn("tkinter", desktop_main)

    def test_all_generated_python_files_parse(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            for project_type in ("cli", "web", "desktop"):
                project_dir = create_project(
                    f"Parse{project_type.title()}",
                    temporary_directory,
                    project_type,
                )
                for source_file in project_dir.rglob("*.py"):
                    with self.subTest(project_type=project_type, file=source_file):
                        ast.parse(source_file.read_text(encoding="utf-8"))

    def test_generated_pyproject_has_console_entry_point(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            project_dir = create_project("Sales-Manager", temporary_directory)
            config = tomllib.loads(
                (project_dir / "pyproject.toml").read_text(encoding="utf-8")
            )
            self.assertEqual(
                config["project"]["scripts"]["sales-manager"],
                "sales_manager.main:main",
            )

    def test_rejects_path_traversal_and_invalid_names(self) -> None:
        invalid_names = ("../escape", "two words", "", "_hidden", "bad/name")
        with tempfile.TemporaryDirectory() as temporary_directory:
            for name in invalid_names:
                with self.subTest(name=name):
                    with self.assertRaises(ValueError):
                        create_project(name, temporary_directory)

            self.assertEqual(list(Path(temporary_directory).iterdir()), [])

    def test_rejects_unknown_project_type(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            with self.assertRaises(ValueError):
                create_project("UnknownApp", temporary_directory, "mobile")
            with self.assertRaises(ValueError):
                create_project("UnknownApp", temporary_directory, None)  # type: ignore[arg-type]

    def test_never_overwrites_existing_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            existing = Path(temporary_directory) / "existing"
            existing.mkdir()
            marker = existing / "keep.txt"
            marker.write_text("keep me", encoding="utf-8")

            with self.assertRaises(FileExistsError):
                create_project("existing", temporary_directory)

            self.assertEqual(marker.read_text(encoding="utf-8"), "keep me")


if __name__ == "__main__":
    unittest.main()
