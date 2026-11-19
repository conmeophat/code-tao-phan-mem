# Universal Python Software Framework

A reusable, beginner-friendly foundation for building different kinds of Python applications.

> This project provides reusable infrastructure, not a magical generator for every possible app. Each product feature still needs its own requirements, implementation, and tests. No software can honestly guarantee zero bugs or 100% success in every environment.

## Goals

- Keep application startup and configuration consistent.
- Load features as independent modules.
- Provide shared logging and error handling.
- Keep business logic separate from the user interface.
- Make automated tests and documentation part of the default workflow.
- Start small and grow into CLI, desktop, web, automation, or data applications.

## Current status

**Milestone 0 – repository initialized.** The first implementation will provide a lightweight Python core that uses only the standard library. Optional UI, database, API, and AI integrations will be added as separate adapters so the core does not require every dependency.

## Planned structure

```text
universal_python_framework/
├── framework/
│   ├── app.py              # Application lifecycle
│   ├── config.py           # Environment-based settings
│   ├── errors.py           # Framework exceptions
│   ├── logging_config.py   # Central logging
│   └── modules.py          # Feature/module registry
├── examples/
│   └── hello_app.py        # Minimal example application
├── tests/
│   ├── test_config.py
│   └── test_modules.py
├── .gitignore
├── pyproject.toml
└── README.md
```

## Requirements

- Python 3.11 or newer
- No third-party dependency is required for the core

## Quick start

The exact commands and API will be documented after the initial core implementation is committed.

## Development principles

1. Explicit behavior is better than hidden magic.
2. Validate inputs at system boundaries.
3. Fail visibly and log enough context to diagnose problems.
4. Keep optional integrations optional.
5. Test the core and each adapter independently.
6. Never claim a feature works until it has been tested in the target environment.

## Roadmap

- [x] Initialize repository and define project direction
- [ ] Implement application lifecycle and configuration
- [ ] Implement module registry and error/logging infrastructure
- [ ] Add example application and unit tests
- [ ] Add CI checks
- [ ] Add optional adapters (CLI, desktop, web, database, API)
- [ ] Add template generator for new projects

## License

License has not yet been selected. Until one is added, all rights are reserved by the repository owner.
