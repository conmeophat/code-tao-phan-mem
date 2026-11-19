"""Custom exceptions raised by the framework."""


class FrameworkError(Exception):
    """Base class for framework-specific errors."""


class DuplicateModuleError(FrameworkError):
    """Raised when a module name is already registered."""


class FrameworkModuleNotFoundError(FrameworkError):
    """Raised when a requested module does not exist."""


class AppNotStartedError(FrameworkError):
    """Raised when a module is run before the application starts."""


class ModuleExecutionError(FrameworkError):
    """Raised when a module handler fails."""


class ModuleLifecycleError(FrameworkError):
    """Raised when module setup or teardown fails."""
