# Universal Python Software Framework

A reusable foundation, interactive wizard, and project generator for building Python applications.

> The framework creates structured starter projects and reusable infrastructure. It does not automatically invent every feature or guarantee that every possible application will work without further development. Each real-world feature still needs clear requirements, implementation, integration, and tests.

## Version 0.3.0

### Included

- Application core, module registry, configuration, logging, and error handling.
- Project generator for CLI, web, and desktop starter projects.
- Interactive wizard: answer prompts instead of remembering command-line flags.
- Optional SQLite pack: persistent JSON key-value storage using Python's standard library.
- Safety checks: reject invalid Python package names, Windows reserved folder names, path traversal, and attempts to overwrite existing projects.
- Automated tests: generator, wizard, and SQLite behavior run in GitHub Actions.

The framework supports Python 3.11 or newer. The web starter uses Python's built-in HTTP server and binds to localhost only. The desktop starter uses Tkinter, which must be available in the Python installation.

## Install the framework on Windows

Open PowerShell in the cloned repository folder:

~~~powershell
py -m venv .venv
./.venv/Scripts/python.exe -m pip install --upgrade pip
./.venv/Scripts/python.exe -m pip install -e ".[dev]"
~~~

## Option 1: Interactive wizard

Run:

~~~powershell
py -m universal_framework wizard
~~~

The wizard asks for the project name, application type, storage option, destination folder, and a short description.

## Option 2: One command

~~~powershell
py -m universal_framework create --name PROJECT_NAME --type PROJECT_TYPE --database DATABASE --destination PARENT_FOLDER
~~~

| Option | Values | Default |
|---|---|---|
| --name | English letters, numbers, underscore and hyphen; must start with a letter | Required |
| --type | cli, web, desktop | cli |
| --database | none, sqlite | none |
| --destination | Parent folder path | Current folder |
| --description | One-line description, up to 200 characters | Generated automatically |

Example: generate an inventory CLI with SQLite storage:

~~~powershell
py -m universal_framework create --name QuanLyKho --type cli --database sqlite --destination . --description "Inventory management starter"
~~~

Then run:

~~~powershell
cd quanlykho
py -m venv .venv
./.venv/Scripts/python.exe -m pip install -e .
./.venv/Scripts/python.exe -m quanlykho
./.venv/Scripts/python.exe -m unittest discover -s tests -v
~~~

## Generated application types

| Type | Starter | Dependencies |
|---|---|---|
| CLI | Argument-based command-line app | Python standard library |
| Web | Local HTTP server and starter HTML page | Python standard library |
| Desktop | Basic Tkinter window | Tkinter |

The generated web starter is for local development, not production hosting. A production web service needs additional security, deployment, and operational configuration.

## Optional SQLite storage

When created with the SQLite option, the project includes a storage module and tests. Example:

~~~python
from quanlykho.storage import SQLiteStore

with SQLiteStore("data/app.db") as store:
    store.set("settings", {"language": "vi", "currency": "VND"})
    settings = store.get("settings", default={})
    print(settings)
~~~

This starter stores JSON-compatible values by key. It is intended for a simple, single-process application, not a complete ORM or a substitute for designing the application's data model.

## Use the framework core in Python

~~~python
from universal_framework import Application, AppConfig, ModuleDefinition


def calculate_total(app: Application) -> int:
    price = 120
    quantity = 3
    return price * quantity


app = Application(AppConfig(app_name="Sales Tool"))
app.register_module(
    ModuleDefinition(name="calculate_total", handler=calculate_total)
)

with app:
    result = app.run_module("calculate_total")
    print(result)  # 360
~~~

Modules may define optional setup and teardown functions for acquiring and releasing resources. Setup runs in registration order; teardown runs in reverse order.

## Tests and quality checks

Run:

~~~powershell
py -m unittest discover -s tests -v
~~~

Or use pytest after installing the development extra:

~~~powershell
py -m pytest
~~~

GitHub Actions runs the suite on pushes and pull requests using Python 3.11, 3.12, 3.13, and 3.14.

## Roadmap

- [x] Application core, module registry, configuration, logging, and errors
- [x] CLI, web, and desktop starter generation
- [x] Interactive project wizard
- [x] Optional SQLite key-value storage pack
- [x] Safety checks and automated tests
- [ ] Richer web UI adapters
- [ ] Richer desktop UI adapters
- [ ] Database migrations and app-specific data model templates
- [ ] API client/server templates
- [ ] Feature specification that scaffolds selected modules

## License

No open-source license has been selected yet. Until a license is added, all rights are reserved by the repository owner.
