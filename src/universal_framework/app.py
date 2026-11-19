"""Application lifecycle and module execution."""

from __future__ import annotations

import logging
from typing import Any

from universal_framework.config import AppConfig
from universal_framework.errors import (
    AppNotStartedError,
    ModuleExecutionError,
    ModuleLifecycleError,
)
from universal_framework.logging_config import configure_logging
from universal_framework.modules import ModuleDefinition, ModuleRegistry


class Application:
    """Coordinates configuration, logging, and registered feature modules.

    Feature-specific business logic belongs in modules, not in this class.
    """

    def __init__(
        self,
        config: AppConfig | None = None,
        *,
        registry: ModuleRegistry | None = None,
        logger: logging.Logger | None = None,
    ) -> None:
        self.config = config or AppConfig.from_env()
        self.registry = registry or ModuleRegistry()
        self.logger = logger or configure_logging(self.config.log_level)
        self._started = False
        self._started_modules: list[ModuleDefinition] = []

    @property
    def is_started(self) -> bool:
        return self._started

    def register_module(self, module: ModuleDefinition) -> None:
        if self._started:
            raise ModuleLifecycleError("Modules cannot be registered after the app starts")
        self.registry.register(module)

    def start(self) -> None:
        """Run setup hooks for enabled modules, rolling back on failure."""
        if self._started:
            return

        started: list[ModuleDefinition] = []
        try:
            for module in self.registry.all(enabled_only=True):
                if module.setup is not None:
                    module.setup(self)
                started.append(module)
        except Exception as exc:
            for module in reversed(started):
                if module.teardown is not None:
                    try:
                        module.teardown(self)
                    except Exception:
                        self.logger.exception("Rollback failed for module '%s'", module.name)
            raise ModuleLifecycleError(
                f"Application startup failed while setting up module '{module.name}'"
            ) from exc

        self._started_modules = started
        self._started = True
        self.logger.info("%s started in %s mode", self.config.app_name, self.config.environment)

    def run_module(self, name: str) -> Any:
        """Execute one enabled module and return its result."""
        if not self._started:
            raise AppNotStartedError("Call app.start() before running modules")

        module = self.registry.get(name)
        if not module.enabled:
            raise ModuleLifecycleError(f"Module is disabled: {name}")

        try:
            return module.handler(self)
        except Exception as exc:
            self.logger.exception("Module '%s' failed", name)
            raise ModuleExecutionError(f"Module execution failed: {name}") from exc

    def close(self) -> None:
        """Run teardown hooks in reverse order and attempt every cleanup."""
        if not self._started:
            return

        failures: list[tuple[str, Exception]] = []
        for module in reversed(self._started_modules):
            if module.teardown is None:
                continue
            try:
                module.teardown(self)
            except Exception as exc:
                failures.append((module.name, exc))
                self.logger.exception("Teardown failed for module '%s'", module.name)

        self._started_modules.clear()
        self._started = False
        self.logger.info("%s stopped", self.config.app_name)

        if failures:
            names = ", ".join(name for name, _ in failures)
            raise ModuleLifecycleError(f"Teardown failed for module(s): {names}") from failures[0][1]

    def __enter__(self) -> "Application":
        self.start()
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> bool:
        self.close()
        return False
