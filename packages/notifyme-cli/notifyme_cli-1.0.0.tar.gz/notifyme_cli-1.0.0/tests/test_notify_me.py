"""
Tests for notify-me package.
"""

import unittest
import tempfile
import json
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

from notify_me.config import Config
from notify_me.notifier import NotifyMe


class TestConfig(unittest.TestCase):
    """Test cases for Config class."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_dir = Path(self.temp_dir) / ".notify-me"
        self.config_file = self.config_dir / "config.json"

    @patch.object(Path, "home")
    def test_config_creation(self, mock_home):
        """Test config file creation."""
        mock_home.return_value = Path(self.temp_dir)
        config = Config()

        self.assertTrue(self.config_dir.exists())
        self.assertTrue(isinstance(config._config, dict))

    @patch.object(Path, "home")
    def test_config_set_get(self, mock_home):
        """Test setting and getting config values."""
        mock_home.return_value = Path(self.temp_dir)
        config = Config()

        config.set("test_key", "test_value")
        self.assertEqual(config.get("test_key"), "test_value")
        self.assertTrue(self.config_file.exists())

    @patch.object(Path, "home")
    def test_config_is_configured(self, mock_home):
        """Test configuration validation."""
        mock_home.return_value = Path(self.temp_dir)
        config = Config()

        self.assertFalse(config.is_configured())

        config.set("bot_token", "test_token")
        config.set("chat_id", "test_chat_id")

        self.assertTrue(config.is_configured())


class TestNotifyMe(unittest.TestCase):
    """Test cases for NotifyMe class."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_dir = Path(self.temp_dir) / ".notify-me"

    @patch.object(Path, "home")
    def test_notifier_creation(self, mock_home):
        """Test NotifyMe instance creation."""
        mock_home.return_value = Path(self.temp_dir)
        notifier = NotifyMe()

        self.assertIsInstance(notifier.config, Config)
        self.assertIn("api.telegram.org", notifier.telegram_api_url)

    def test_format_duration(self):
        """Test duration formatting."""
        notifier = NotifyMe()

        # Test seconds
        self.assertEqual(notifier._format_duration(30.5), "30.5 seconds")

        # Test minutes
        self.assertEqual(notifier._format_duration(120), "2.0 minutes")

        # Test hours
        self.assertEqual(notifier._format_duration(3661), "1.0 hours")

    def test_format_command_completion_message(self):
        """Test command completion message formatting."""
        notifier = NotifyMe()

        message = notifier.format_command_completion_message("python test.py", 0, 30.5, "Test completed")

        self.assertIn("✅", message)
        self.assertIn("python test.py", message)
        self.assertIn("30.5 seconds", message)
        self.assertIn("Test completed", message)

        # Test failed command
        message = notifier.format_command_completion_message("python test.py", 1, 30.5)

        self.assertIn("❌", message)
        self.assertIn("exit code: 1", message)


if __name__ == "__main__":
    unittest.main()
