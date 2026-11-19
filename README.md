# Universal Python Software Framework

A reusable, beginner-friendly foundation for building different kinds of Python applications with Python.

> This framework supplies reusable infrastructure; it does not automatically invent every feature. Each product still needs clear requirements, feature-specific code, integration, and tests. No software can honestly guarantee zero bugs or 100% success in every environment.

## What is included in version 0.1.0

- **Application lifecycle:** start, run, and close an application predictably.
- **Module registry:** register independent features by unique names.
- **Configuration:** read and validate common settings from environment variables.
- **Logging:** one consistent console logging setup without duplicate handlers.
- **Error types:** distinguish configuration, lifecycle, and feature execution errors.
- **Example and tests:** a small example plus standard-library unit tests.

The core has no mandatory third-party runtime dependencies and supports Python 3.11 or newer.

## Project structure

```text
.
├── src/
│   └── universal_framework/
│       ├── __init__.py
│       ├── app.py
│       ├── config.py
│       ├── errors.py
│       ├── logging_config.py
│       └── modules.py
├── examples/
│   └── hello_app.py
├── tests/
│   ├── test_config.py
│   └── test_modules.py
├── .github/
│   └── workflows/
│       └── tests.yml
├── pyproject.toml
└── README.md
```

## Quick start on Windows PowerShell

Run these commands from the repository folder:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe examples\hello_app.py
```

Expected example output includes a greeting similar to:

```text
Hello from My First App!
```

## Add a feature module

A feature is represented by a `ModuleDefinition`. Its `handler` receives the running `Application` and can return a result.

```python
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
```

A module may also define optional `setup(app)` and `teardown(app)` functions for opening and closing resources. Setup runs in registration order; teardown runs in reverse order.

## Configuration

The framework reads these optional environment variables:

| Variable | Default | Purpose |
|---|---|---|
| `APP_NAME` | `My Python App` | Display name |
| `APP_ENV` | `development` | Environment label |
| `APP_LOG_LEVEL` | `INFO` | DEBUG, INFO, WARNING, ERROR, or CRITICAL |
| `APP_DATA_DIR` | `data` | Path reserved for application data |

PowerShell example:

```powershell
$env:APP_NAME = "Inventory Manager"
$env:APP_ENV = "development"
$env:APP_LOG_LEVEL = "DEBUG"
py your_app.py
```

## Development and quality checks

Run the built-in tests:

```powershell
py -m unittest discover -s tests -v
```

Run pytest when the development extra is installed:

```powershell
py -m pytest
```

GitHub Actions runs the test suite on pushes and pull requests.

## Design principles

1. Keep business logic separate from UI and infrastructure.
2. Prefer explicit configuration over hidden behavior.
3. Validate inputs at boundaries.
4. Log useful diagnostic information without logging secrets.
5. Keep optional integrations optional.
6. Test modules independently and test integrations together.
7. Never advertise a feature as working until it has been exercised in its target environment.

## Roadmap

- [x] Initialize repository and define project direction
- [x] Implement application lifecycle and configuration
- [x] Implement module registry, errors, and logging
- [x] Add example application and unit tests
- [x] Add continuous integration test workflow
- [ ] Add project template generator
- [ ] Add optional CLI and desktop UI adapters
- [ ] Add optional web UI adapter
- [ ] Add database and API adapters
- [ ] Add security helpers and integration testing guidance

## License

No open-source license has been selected yet. Until a license is added, all rights are reserved by the repository owner.
