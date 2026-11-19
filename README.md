# Universal Python Software Framework

A reusable foundation and project generator for building different kinds of Python applications.

> The framework creates safe, structured starter projects and reusable infrastructure. It does not automatically invent every feature or guarantee that every possible application will work without further development. Each real-world feature still needs clear requirements, implementation, integration, and tests.

## Version 0.2.0

### Included

- **Application core:** predictable startup, module execution, and shutdown.
- **Module registry:** register independent features by unique names.
- **Configuration:** validated settings from environment variables.
- **Logging and error handling:** consistent diagnostics and framework exceptions.
- **Project generator:** create CLI, web, and desktop starter projects.
- **Command-line interface:** generate a new project with one command.
- **Safety checks:** validate names, reject path traversal, and never overwrite an existing project.
- **Automated tests:** unit tests run in GitHub Actions across supported Python versions.

The framework core uses the Python standard library and supports Python 3.11 or newer. The web starter uses Python's built-in HTTP server. The desktop starter uses Tkinter, which must be available in the Python installation.

## Install the framework on Windows

Open PowerShell in the cloned repository folder:

~~~powershell
py -m venv .venv
./.venv/Scripts/python.exe -m pip install --upgrade pip
./.venv/Scripts/python.exe -m pip install -e ".[dev]"
~~~

## Create a new application

The command format is:

~~~powershell
py -m universal_framework create --name PROJECT_NAME --type PROJECT_TYPE --destination PARENT_FOLDER
~~~

Supported project types:

| Type | Starter application | Dependencies |
|---|---|---|
| cli | Command-line application | Python standard library |
| web | Local web server and starter HTML page | Python standard library |
| desktop | Basic desktop window | Tkinter |

For example, create a command-line inventory program:

~~~powershell
py -m universal_framework create --name QuanLyKho --type cli --destination .
~~~

This creates a new folder named quanlykho. Then run:

~~~powershell
cd quanlykho
py -m venv .venv
./.venv/Scripts/python.exe -m pip install -e .
./.venv/Scripts/python.exe -m quanlykho
./.venv/Scripts/python.exe -m unittest discover -s tests -v
~~~

To create a web starter instead:

~~~powershell
py -m universal_framework create --name WebsiteDemo --type web --destination .
~~~

Open the generated project, install it, and run its module. The starter server listens on 127.0.0.1:8000, so it is intended for local development, not direct public production hosting.

To create a desktop starter:

~~~powershell
py -m universal_framework create --name DesktopDemo --type desktop --destination .
~~~

## Use the framework core in Python

Register an independent feature module:

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

## Configuration

The framework reads these optional environment variables:

| Variable | Default | Purpose |
|---|---|---|
| APP_NAME | My Python App | Display name |
| APP_ENV | development | Environment label |
| APP_LOG_LEVEL | INFO | DEBUG, INFO, WARNING, ERROR, or CRITICAL |
| APP_DATA_DIR | data | Path reserved for application data |

PowerShell example:

~~~powershell
$env:APP_NAME = "Inventory Manager"
$env:APP_ENV = "development"
$env:APP_LOG_LEVEL = "DEBUG"
py your_app.py
~~~

## Tests and quality checks

Run the framework test suite:

~~~powershell
py -m unittest discover -s tests -v
~~~

Or use pytest after installing the development extra:

~~~powershell
py -m pytest
~~~

GitHub Actions runs the unit tests on pushes and pull requests using Python 3.11, 3.12, 3.13, and 3.14.

## Design principles

1. Keep business logic separate from UI and infrastructure.
2. Validate user input at system boundaries.
3. Never overwrite existing project files without explicit, safe support.
4. Log useful diagnostic information without logging secrets.
5. Keep optional integrations optional.
6. Test modules independently and integrations together.
7. Never advertise a feature as production-ready until it has been tested in its target environment.

## Roadmap

- [x] Initialize repository and define project direction
- [x] Implement application lifecycle and configuration
- [x] Implement module registry, errors, and logging
- [x] Add example application and unit tests
- [x] Add continuous integration test workflow
- [x] Add project generator for CLI, web, and desktop starters
- [x] Add command-line interface
- [ ] Add richer web UI adapters (for example, FastAPI)
- [ ] Add richer desktop UI adapters
- [ ] Add database and API adapters
- [ ] Add security helpers and integration testing guidance
- [ ] Add interactive project wizard and feature templates

## License

No open-source license has been selected yet. Until a license is added, all rights are reserved by the repository owner.
