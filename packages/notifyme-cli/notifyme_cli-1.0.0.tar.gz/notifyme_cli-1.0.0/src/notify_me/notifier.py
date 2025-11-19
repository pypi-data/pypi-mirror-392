"""
Core notification functionality for notify-me.
"""

import requests
import time
from typing import Optional
from .config import Config


class NotifyMe:
    """Main class for sending Telegram notifications."""

    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.telegram_api_url = "https://api.telegram.org/bot{token}/sendMessage"

    def send_notification(self, message: str, parse_mode: str = "Markdown") -> bool:
        """
        Send a notification via Telegram webhook.

        Args:
            message: The message to send
            parse_mode: Parse mode for Telegram (Markdown or HTML)

        Returns:
            bool: True if successful, False otherwise
        """
        if not self.config.is_configured():
            print("❌ Bot not configured. Run 'notify-me setup' first.")
            return False

        url = self.telegram_api_url.format(token=self.config.bot_token)

        payload = {"chat_id": self.config.chat_id, "text": message, "parse_mode": parse_mode}

        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()

            if response.json().get("ok"):
                print("✅ Notification sent successfully!")
                return True
            else:
                error_description = response.json().get("description", "Unknown error")
                print(f"❌ Telegram API error: {error_description}")
                return False

        except requests.exceptions.Timeout:
            print("❌ Request timed out. Check your internet connection.")
            return False
        except requests.exceptions.ConnectionError:
            print("❌ Connection error. Check your internet connection.")
            return False
        except requests.exceptions.HTTPError as e:
            print(f"❌ HTTP error: {e}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return False

    def test_connection(self) -> bool:
        """
        Test the connection to Telegram API.

        Returns:
            bool: True if connection is successful, False otherwise
        """
        if not self.config.is_configured():
            return False

        test_message = "🔔 notify-me test message - connection successful!"
        return self.send_notification(test_message)

    def format_command_completion_message(
        self, command: str, exit_code: int, execution_time: float, custom_message: str = None
    ) -> str:
        """
        Format a message for command completion notification.

        Args:
            command: The command that was executed
            exit_code: Exit code of the command
            execution_time: Time taken for execution in seconds
            custom_message: Custom message to include

        Returns:
            str: Formatted message
        """
        status_emoji = "✅" if exit_code == 0 else "❌"
        status_text = "completed successfully" if exit_code == 0 else f"failed (exit code: {exit_code})"

        duration = self._format_duration(execution_time)

        message_parts = [
            f"{status_emoji} *Command {status_text}*",
            f"",
            f"*Command:* `{command}`",
            f"*Duration:* {duration}",
            f"*Time:* {time.strftime('%Y-%m-%d %H:%M:%S')}",
        ]

        if custom_message:
            message_parts.insert(1, f"*Message:* {custom_message}")
            message_parts.insert(2, "")

        return "\n".join(message_parts)

    def _format_duration(self, seconds: float) -> str:
        """Format duration in a human-readable way."""
        if seconds < 60:
            return f"{seconds:.1f} seconds"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f} minutes"
        else:
            hours = seconds / 3600
            return f"{hours:.1f} hours"
