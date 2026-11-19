"""Reusable foundations for Python applications."""

from universal_framework.app import Application
from universal_framework.config import AppConfig
from universal_framework.errors import (
    AppNotStartedError,
    DuplicateModuleError,
    FrameworkError,
    FrameworkModuleNotFoundError,
    ModuleExecutionError,
    ModuleLifecycleError,
)
from universal_framework.modules import ModuleDefinition, ModuleRegistry

__all__ = [
    "Application",
    "AppConfig",
    "AppNotStartedError",
    "DuplicateModuleError",
    "FrameworkError",
    "FrameworkModuleNotFoundError",
    "ModuleDefinition",
    "ModuleExecutionError",
    "ModuleLifecycleError",
    "ModuleRegistry",
]

__version__ = "0.1.0"
