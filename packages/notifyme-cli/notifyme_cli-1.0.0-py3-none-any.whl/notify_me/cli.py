"""
Command-line interface for notify-me.
"""

import argparse
import subprocess
import sys
import time
from typing import List, Optional
from .config import Config
from .notifier import NotifyMe


def setup_bot():
    """Interactive setup for Telegram bot configuration."""
    print("🔧 Setting up notifyme with Telegram bot")
    print("=" * 50)

    config = Config()

    print("\n📝 You'll need:")
    print("1. A Telegram bot token (create one with @BotFather)")
    print("2. Your chat ID (send a message to @userinfobot)")
    print("\nFor detailed instructions, visit: https://core.telegram.org/bots#3-how-do-i-create-a-bot")

    # Get bot token
    print("\n🤖 Enter your Telegram bot token:")
    bot_token = input("Token: ").strip()

    if not bot_token:
        print("❌ Bot token is required!")
        return False

    # Get chat ID
    print("\n💬 Enter your chat ID:")
    chat_id = input("Chat ID: ").strip()

    if not chat_id:
        print("❌ Chat ID is required!")
        return False

    # Save configuration
    config.set("bot_token", bot_token)
    config.set("chat_id", chat_id)

    # Test the configuration
    print("\n🔍 Testing connection...")
    notifier = NotifyMe(config)

    if notifier.test_connection():
        print("✅ Setup completed successfully!")
        print(f"Configuration saved to: {config.config_file}")
        return True
    else:
        print("❌ Setup failed. Please check your bot token and chat ID.")
        return False


def run_command_with_notification(command: List[str], message: Optional[str] = None) -> int:
    """
    Run a command and send a notification when it completes.

    Args:
        command: Command to execute as a list of strings
        message: Optional custom message to include in notification

    Returns:
        int: Exit code of the command
    """
    config = Config()
    notifier = NotifyMe(config)

    if not config.is_configured():
        print("❌ Bot not configured. Run 'notifyme setup' first.")
        return 1

    command_str = " ".join(command)
    print(f"🚀 Running command: {command_str}")

    start_time = time.time()

    try:
        # Run the command
        result = subprocess.run(command, capture_output=False)
        exit_code = result.returncode
    except KeyboardInterrupt:
        print("\n⚠️ Command interrupted by user")
        exit_code = 130  # Standard exit code for Ctrl+C
    except FileNotFoundError:
        print(f"❌ Command not found: {command[0]}")
        exit_code = 127
    except Exception as e:
        print(f"❌ Error executing command: {e}")
        exit_code = 1

    end_time = time.time()
    execution_time = end_time - start_time

    # Send notification
    notification_message = notifier.format_command_completion_message(command_str, exit_code, execution_time, message)

    notifier.send_notification(notification_message)

    return exit_code


def send_simple_message(message: str) -> bool:
    """
    Send a simple message via Telegram.

    Args:
        message: Message to send

    Returns:
        bool: True if successful, False otherwise
    """
    config = Config()
    notifier = NotifyMe(config)

    if not config.is_configured():
        print("❌ Bot not configured. Run 'notifyme setup' first.")
        return False

    return notifier.send_notification(message)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Send Telegram notifications",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  notifyme setup                          # Set up Telegram bot
  notifyme                                # Send default "Task complete" message
  notifyme -m "Build finished"            # Send custom message
  python train.py && notifyme             # Run command then notify
  make build && notifyme -m "Build done"  # Run command then notify with message
  notifyme test                          # Test the current configuration
  notifyme --exec python train.py        # Run command with notification wrapper
        """,
    )

    parser.add_argument("--version", action="version", version="notifyme-cli 1.0.0")

    # Main execution arguments
    parser.add_argument("-m", "--message", type=str, help='Custom message to send (default: "Task complete")')

    parser.add_argument("--exec", action="store_true", help="Execute command with notification wrapper (old behavior)")

    parser.add_argument("cmd", nargs="*", help="Command to execute when using --exec, or special commands (setup/test)")

    args = parser.parse_args()

    # Handle special commands
    if args.cmd and len(args.cmd) == 1:
        if args.cmd[0] == "setup":
            success = setup_bot()
            sys.exit(0 if success else 1)
        elif args.cmd[0] == "test":
            config = Config()
            if not config.is_configured():
                print("❌ Bot not configured. Run 'notifyme setup' first.")
                sys.exit(1)

            notifier = NotifyMe(config)
            success = notifier.test_connection()
            sys.exit(0 if success else 1)

    # Handle command execution with wrapper (old behavior)
    if args.exec:
        if not args.cmd:
            print("❌ Command is required when using --exec")
            sys.exit(1)

        exit_code = run_command_with_notification(args.cmd, args.message)
        sys.exit(exit_code)

    # Handle command execution with wrapper if cmd is provided and not special
    elif args.cmd:
        # Check if it's not a special command
        if len(args.cmd) > 1 or (len(args.cmd) == 1 and args.cmd[0] not in ["setup", "test"]):
            exit_code = run_command_with_notification(args.cmd, args.message)
            sys.exit(exit_code)

    # Default behavior: send a simple notification message
    message = args.message or "Task complete"
    success = send_simple_message(message)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
