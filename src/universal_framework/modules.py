"""Registration and lookup of independent application modules."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable

from universal_framework.errors import DuplicateModuleError, FrameworkModuleNotFoundError

if TYPE_CHECKING:
    from universal_framework.app import Application

ModuleHandler = Callable[["Application"], Any]
LifecycleHandler = Callable[["Application"], None]


@dataclass(frozen=True, slots=True)
class ModuleDefinition:
    """A named feature that can be attached to an Application."""

    name: str
    handler: ModuleHandler
    setup: LifecycleHandler | None = None
    teardown: LifecycleHandler | None = None
    enabled: bool = True

    def __post_init__(self) -> None:
        if not self.name or not self.name.strip():
            raise ValueError("Module name must not be empty")
        if not callable(self.handler):
            raise TypeError("Module handler must be callable")


class ModuleRegistry:
    """Stores modules by unique name and preserves registration order."""

    def __init__(self) -> None:
        self._modules: dict[str, ModuleDefinition] = {}

    def register(self, module: ModuleDefinition) -> None:
        if module.name in self._modules:
            raise DuplicateModuleError(f"Module already registered: {module.name}")
        self._modules[module.name] = module

    def unregister(self, name: str) -> ModuleDefinition:
        try:
            return self._modules.pop(name)
        except KeyError as exc:
            raise FrameworkModuleNotFoundError(f"Module not found: {name}") from exc

    def get(self, name: str) -> ModuleDefinition:
        try:
            return self._modules[name]
        except KeyError as exc:
            raise FrameworkModuleNotFoundError(f"Module not found: {name}") from exc

    def all(self, *, enabled_only: bool = False) -> tuple[ModuleDefinition, ...]:
        modules = tuple(self._modules.values())
        if enabled_only:
            return tuple(module for module in modules if module.enabled)
        return modules

    def __len__(self) -> int:
        return len(self._modules)
