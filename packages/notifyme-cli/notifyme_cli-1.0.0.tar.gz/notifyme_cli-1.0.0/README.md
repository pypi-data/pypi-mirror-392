# notifyme-cli

[![CI](https://github.com/judeosbert/notifyme-cli/workflows/CI/badge.svg)](https://github.com/judeosbert/notifyme-cli/actions)
[![PyPI version](https://badge.fury.io/py/notifyme-cli.svg)](https://badge.fury.io/py/notifyme-cli)
[![Python versions](https://img.shields.io/pypi/pyversions/notifyme-cli.svg)](https://pypi.org/project/notifyme-cli/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![codecov](https://codecov.io/gh/judeosbert/notifyme-cli/branch/main/graph/badge.svg)](https://codecov.io/gh/judeosbert/notifyme-cli)

A command-line tool that sends Telegram notifications when long-running commands complete. Never miss when your builds, tests, or data processing jobs finish!

## ✨ Features

- 🔔 Get notified via Telegram when commands finish
- ⏱️ Shows command duration and exit status
- 📝 Add custom messages to notifications
- 🛠️ Easy setup with interactive configuration
- 🎯 Works with any command-line program
- 💾 Secure local configuration storage

## 📦 Installation

### From PyPI (Recommended)
```bash
pip install notifyme-cli
```

### From Source
```bash
git clone https://github.com/judeosbert/notifyme-cli.git
cd notifyme-cli
pip install -e .
```

### Development Installation
```bash
git clone https://github.com/judeosbert/notifyme-cli.git
cd notifyme-cli
pip install -e ".[dev]"
```

## Setup

### 1. Create a Telegram Bot

1. Open Telegram and message [@BotFather](https://t.me/botfather)
2. Send `/newbot` and follow the instructions
3. Save the bot token you receive

### 2. Get Your Chat ID

1. Message [@userinfobot](https://t.me/userinfobot) on Telegram
2. It will reply with your user information including your chat ID
3. Save the chat ID (it's a number like `123456789`)

### 3. Configure notify-me

Run the setup command and enter your bot token and chat ID:

```bash
notifyme setup
```

The setup will test the connection and confirm everything works.

## 📱 Usage

### Basic Usage (Recommended)

Run commands and then notify when complete:
```bash
# Send default "Task complete" message
python train_model.py && notifyme

# Send custom message
make build && notifyme -m "Build finished"

# Chain multiple commands
npm test && npm build && notifyme -m "CI pipeline complete"
```

### Direct Message Sending

Send a message directly:
```bash
notifyme                                    # Send "Task complete"
notifyme -m "Hello from the command line!"  # Send custom message
```

### Command Wrapper (Alternative)

Execute commands with notification wrapper:
```bash
notifyme --exec python train_model.py
notifyme --exec -m "Training complete!" python train_model.py
```

### Test Configuration

Test your setup:
```bash
notifyme test
```

## Command Examples

```bash
# Long-running build with notification (recommended)
docker build -t myapp . && notifyme -m "Docker build complete"

# Database backup with notification
pg_dump mydatabase > backup.sql && notifyme -m "Backup finished"

# Machine learning training
python train.py --epochs 100 && notifyme -m "Model training done"

# Run tests and get notified
pytest tests/ && notifyme

# Complex pipeline
bash ./process_data.sh && notifyme -m "Data processing complete"

# Using the wrapper (alternative method)
notifyme --exec pytest tests/
notifyme --exec -m "Training complete!" python train.py
```

## Configuration

Configuration is stored in `~/.notify-me/config.json`. The file contains:

```json
{
  "bot_token": "your-bot-token-here",
  "chat_id": "your-chat-id-here"
}
```

## Security

- Your bot token and chat ID are stored locally on your machine
- No data is sent to external servers except Telegram's API
- Configuration file has restricted permissions (600)

## Notification Format

Notifications include:
- ✅/❌ Success or failure status
- Command that was executed
- Execution time
- Timestamp
- Custom message (if provided)
- Exit code (if command failed)

Example notification:
```
✅ Command completed successfully

Message: Training finished!

Command: python train_model.py
Duration: 2.3 hours
Time: 2024-11-17 14:30:22
```

## Troubleshooting

### "Bot not configured" Error
Run `notifyme setup` to configure your bot token and chat ID.

### "Connection error" or timeout
- Check your internet connection
- Verify your bot token is correct
- Make sure your bot hasn't been deleted

### "Telegram API error"
- Verify your chat ID is correct
- Make sure you've sent at least one message to your bot
- Check that your bot token is valid

### Permission errors
The configuration directory `~/.notify-me/` should be writable by your user.

## Development

### Running Tests
```bash
python -m pytest tests/
```

### Installing for Development
```bash
pip install -e ".[dev]"
```

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if needed
5. Submit a pull request

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Quick Start for Contributors

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes and add tests
4. Run tests: `make test`
5. Submit a pull request

## 📝 Changelog

See [CHANGELOG.md](CHANGELOG.md) for a detailed history of changes.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⭐ Support

If you find this project helpful, please consider:
- Giving it a star on GitHub ⭐
- Reporting bugs or requesting features through [issues](https://github.com/judeosbert/notifyme-cli/issues)
- Contributing to the codebase
- Sharing it with others who might find it useful

## 🤖 **Built with AI**

This project was created with the assistance of AI (GitHub Copilot) to demonstrate modern Python development practices and open-source project structure. The AI helped with:

- Code architecture and implementation
- Comprehensive documentation and examples  
- GitHub workflows and community templates
- Testing and quality assurance setup
- Open-source best practices

## 🔗 Links

- [PyPI Package](https://pypi.org/project/notifyme-cli/)
- [GitHub Repository](https://github.com/judeosbert/notifyme-cli)
- [Documentation](https://github.com/judeosbert/notifyme-cli#readme)
- [Issue Tracker](https://github.com/judeosbert/notifyme-cli/issues)
- [Discussions](https://github.com/judeosbert/notifyme-cli/discussions)