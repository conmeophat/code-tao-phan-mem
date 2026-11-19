"""Application configuration loaded from environment variables."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Mapping
import os


_ALLOWED_LOG_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}


@dataclass(frozen=True, slots=True)
class AppConfig:
    """Small, validated configuration object for an application."""

    app_name: str = "My Python App"
    environment: str = "development"
    log_level: str = "INFO"
    data_dir: Path = Path("data")

    def __post_init__(self) -> None:
        if not self.app_name.strip():
            raise ValueError("app_name must not be empty")
        if not self.environment.strip():
            raise ValueError("environment must not be empty")

        normalized_level = self.log_level.strip().upper()
        if normalized_level not in _ALLOWED_LOG_LEVELS:
            allowed = ", ".join(sorted(_ALLOWED_LOG_LEVELS))
            raise ValueError(f"log_level must be one of: {allowed}")
        object.__setattr__(self, "log_level", normalized_level)
        object.__setattr__(self, "data_dir", Path(self.data_dir).expanduser())

    @classmethod
    def from_env(cls, environ: Mapping[str, str] | None = None) -> "AppConfig":
        """Build configuration from APP_* environment variables.

        Passing a mapping makes this method easy to test without changing
        the real process environment.
        """
        source = os.environ if environ is None else environ
        return cls(
            app_name=source.get("APP_NAME", "My Python App"),
            environment=source.get("APP_ENV", "development"),
            log_level=source.get("APP_LOG_LEVEL", "INFO"),
            data_dir=Path(source.get("APP_DATA_DIR", "data")),
        )
