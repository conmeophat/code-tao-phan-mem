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
from universal_framework.project_generator import (
    SUPPORTED_PROJECT_TYPES,
    create_project,
)

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
    "SUPPORTED_PROJECT_TYPES",
    "create_project",
]

__version__ = "0.2.0"
