"""Tests for module registration and application lifecycle."""

import unittest

from universal_framework import (
    AppConfig,
    Application,
    AppNotStartedError,
    DuplicateModuleError,
    FrameworkModuleNotFoundError,
    ModuleDefinition,
    ModuleExecutionError,
    ModuleRegistry,
)


class ModuleRegistryTests(unittest.TestCase):
    def test_registers_and_finds_module(self) -> None:
        registry = ModuleRegistry()
        module = ModuleDefinition(name="sample", handler=lambda app: "ok")
        registry.register(module)
        self.assertIs(registry.get("sample"), module)
        self.assertEqual(registry.all(), (module,))

    def test_rejects_duplicate_names(self) -> None:
        registry = ModuleRegistry()
        module = ModuleDefinition(name="sample", handler=lambda app: None)
        registry.register(module)
        with self.assertRaises(DuplicateModuleError):
            registry.register(module)

    def test_missing_module_raises_clear_error(self) -> None:
        with self.assertRaises(FrameworkModuleNotFoundError):
            ModuleRegistry().get("missing")


class ApplicationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.app = Application(
            AppConfig(app_name="Test App", environment="testing"),
        )

    def tearDown(self) -> None:
        if self.app.is_started:
            self.app.close()

    def test_module_requires_started_application(self) -> None:
        self.app.register_module(ModuleDefinition(name="sample", handler=lambda app: "ok"))
        with self.assertRaises(AppNotStartedError):
            self.app.run_module("sample")

    def test_runs_module_and_returns_result(self) -> None:
        self.app.register_module(ModuleDefinition(name="sample", handler=lambda app: 42))
        self.app.start()
        self.assertEqual(self.app.run_module("sample"), 42)

    def test_wraps_handler_failure(self) -> None:
        def fail(app: Application) -> None:
            raise RuntimeError("expected failure")

        self.app.register_module(ModuleDefinition(name="broken", handler=fail))
        self.app.start()
        with self.assertRaises(ModuleExecutionError):
            self.app.run_module("broken")

    def test_setup_and_teardown_order(self) -> None:
        events: list[str] = []
        self.app.register_module(
            ModuleDefinition(
                name="first",
                handler=lambda app: None,
                setup=lambda app: events.append("setup-first"),
                teardown=lambda app: events.append("close-first"),
            )
        )
        self.app.register_module(
            ModuleDefinition(
                name="second",
                handler=lambda app: None,
                setup=lambda app: events.append("setup-second"),
                teardown=lambda app: events.append("close-second"),
            )
        )

        self.app.start()
        self.app.close()
        self.assertEqual(
            events,
            ["setup-first", "setup-second", "close-second", "close-first"],
        )


if __name__ == "__main__":
    unittest.main()
