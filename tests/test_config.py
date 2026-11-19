"""Tests for application configuration."""

import unittest
from pathlib import Path

from universal_framework.config import AppConfig


class AppConfigTests(unittest.TestCase):
    def test_defaults_are_valid(self) -> None:
        config = AppConfig()
        self.assertEqual(config.log_level, "INFO")
        self.assertEqual(config.data_dir, Path("data"))

    def test_reads_environment_mapping(self) -> None:
        config = AppConfig.from_env(
            {
                "APP_NAME": "Test Tool",
                "APP_ENV": "testing",
                "APP_LOG_LEVEL": "debug",
                "APP_DATA_DIR": "~/test-data",
            }
        )
        self.assertEqual(config.app_name, "Test Tool")
        self.assertEqual(config.environment, "testing")
        self.assertEqual(config.log_level, "DEBUG")
        self.assertEqual(config.data_dir, Path("~/test-data").expanduser())

    def test_rejects_unknown_log_level(self) -> None:
        with self.assertRaises(ValueError):
            AppConfig(log_level="LOUD")


if __name__ == "__main__":
    unittest.main()
