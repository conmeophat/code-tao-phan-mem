"""Tests for safe project generation and the interactive CLI."""

import ast
from pathlib import Path
import os
import subprocess
import sys
import tempfile
import tomllib
import unittest

from universal_framework.cli import main as framework_cli
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
                    database="sqlite",
                )
                for source_file in project_dir.rglob("*.py"):
                    with self.subTest(project_type=project_type, file=source_file):
                        ast.parse(source_file.read_text(encoding="utf-8"))

    def test_generated_cli_project_runs_end_to_end(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            project_dir = create_project("Sales-Manager", temporary_directory)
            package_root = str(project_dir / "src")
            environment = os.environ.copy()
            environment["PYTHONPATH"] = package_root + os.pathsep + environment.get(
                "PYTHONPATH", ""
            )

            completed = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "sales_manager",
                    "--name",
                    "Ada",
                ],
                cwd=project_dir,
                env=environment,
                capture_output=True,
                text=True,
                check=True,
                timeout=15,
            )
            self.assertIn("Hello, Ada! Welcome to Sales Manager.", completed.stdout)

    def test_generated_sqlite_feature_round_trips_values(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            project_dir = create_project(
                "StorageDemo",
                temporary_directory,
                database="sqlite",
            )
            package_root = str(project_dir / "src")
            environment = os.environ.copy()
            environment["PYTHONPATH"] = package_root + os.pathsep + environment.get(
                "PYTHONPATH", ""
            )
            program = (
                "from storagedemo.storage import SQLiteStore\n"
                "with SQLiteStore(':memory:') as store:\n"
                "    store.set('settings', {'language': 'Tiếng Việt'})\n"
                "    assert store.get('settings') == {'language': 'Tiếng Việt'}\n"
                "    assert store.keys() == ('settings',)\n"
                "    assert store.delete('settings') is True\n"
                "    assert store.delete('settings') is False\n"
            )
            subprocess.run(
                [sys.executable, "-c", program],
                cwd=project_dir,
                env=environment,
                capture_output=True,
                text=True,
                check=True,
                timeout=15,
            )
            self.assertTrue(
                (project_dir / "src" / "storagedemo" / "storage.py").is_file()
            )
            self.assertTrue((project_dir / "tests" / "test_storage.py").is_file())

    def test_framework_cli_creates_project(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            output: list[str] = []
            exit_code = framework_cli(
                [
                    "create",
                    "--name",
                    "CreatedByCli",
                    "--type",
                    "cli",
                    "--database",
                    "sqlite",
                    "--destination",
                    temporary_directory,
                    "--description",
                    "An inventory demo",
                ],
                output_fn=output.append,
            )

            self.assertEqual(exit_code, 0)
            generated = Path(temporary_directory) / "createdbycli"
            self.assertTrue(generated.is_dir())
            self.assertTrue((generated / "src" / "createdbycli" / "storage.py").is_file())
            self.assertIn("Project created:", output[0])
            project_config = tomllib.loads(
                (generated / "pyproject.toml").read_text(encoding="utf-8")
            )
            self.assertEqual(
                project_config["project"]["description"],
                "An inventory demo",
            )

    def test_interactive_wizard_collects_settings(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            answers = iter(
                [
                    "WizardApp",
                    "cli",
                    "sqlite",
                    temporary_directory,
                    "A wizard-generated example",
                ]
            )
            output: list[str] = []
            result = framework_cli(
                ["wizard"],
                input_fn=lambda prompt: next(answers),
                output_fn=output.append,
            )
            generated = Path(temporary_directory) / "wizardapp"

            self.assertEqual(result, 0)
            self.assertTrue((generated / "src" / "wizardapp" / "storage.py").is_file())
            self.assertTrue(any("WIZARD" in line for line in output))

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

    def test_rejects_path_traversal_invalid_and_reserved_names(self) -> None:
        invalid_names = (
            "../escape",
            "two words",
            "",
            "_hidden",
            "bad/name",
            "Class",
            "def",
            "CON",
            "nul",
            "COM1",
        )
        with tempfile.TemporaryDirectory() as temporary_directory:
            for name in invalid_names:
                with self.subTest(name=name):
                    with self.assertRaises(ValueError):
                        create_project(name, temporary_directory)

            self.assertEqual(list(Path(temporary_directory).iterdir()), [])

    def test_rejects_unknown_project_type_or_database(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            with self.assertRaises(ValueError):
                create_project("UnknownType", temporary_directory, "mobile")
            with self.assertRaises(ValueError):
                create_project("UnknownType", temporary_directory, None)  # type: ignore[arg-type]
            with self.assertRaises(ValueError):
                create_project("UnknownDatabase", temporary_directory, database="nosql")

    def test_rejects_invalid_description(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            with self.assertRaises(ValueError):
                create_project("BadDescription", temporary_directory, description="  ")
            with self.assertRaises(ValueError):
                create_project(
                    "BadDescription",
                    temporary_directory,
                    description="line 1\nline 2",
                )

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
