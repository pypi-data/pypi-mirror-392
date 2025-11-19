# textmine - Retro Terminal Chat Client

```
 _____ _______  _______ __  __ _____ _   _ ______ 
|_   _|__   __||__   __|  \/  |_   _| \ | |  ____|
  | |    | |      | |  | \  / | | | |  \| | |__   
  | |    | |      | |  | |\/| | | | | . ` |  __|  
 _| |_   | |      | |  | |  | |_| |_| |\  | |____ 
|_____|  |_|      |_|  |_|  |_|_____|_| \_|______|
```

Authentic 1980s terminal-based chat experience. Connect to textmine.net and chat with friends using this retro VT100-style interface.

## Features

- 🖥️ **Retro Terminal UI** - Phosphor green monochrome CRT aesthetic
- 💬 **Real-time Chat** - WebSocket-powered instant messaging
- 🔍 **User Search** - Find and connect with other users
- 👤 **User Profiles** - View stats and bios
- 🔐 **Secure Authentication** - Session-based login with token storage

## Installation

```bash
pip install textmine-cli
```

**Now available on PyPI!** Install with a single command and start chatting.

## Quick Start

### 1. Login or Register

```bash
# Login to existing account
textmine login

# Register new account (requires invite code)
textmine register
```

### 2. Start Chatting

```bash
# Search for users
textmine search alice

# Open chat with a user
textmine chat alice

# View user profile
textmine profile bob
```

### 3. Commands Available in Chat

- Type your message and press Enter to send
- `/exit` or `/quit` - Leave chat
- `/clear` - Clear screen
- `/profile` - View other user's profile
- `/help` - Show help

## Configuration

The CLI stores session tokens securely using your system's keyring. Server URL defaults to `https://textmine.net` but can be configured:

```bash
export TEXTMINE_SERVER=http://localhost:5000
```

## Development

```bash
# Clone repository
git clone https://github.com/textmine/textmine-cli
cd textmine-cli

# Install in editable mode
pip install -e .

# Run CLI
textmine --help
```

## Requirements

- Python 3.8+
- Internet connection
- Terminal with 256-color support (recommended)

## License

MIT License - See LICENSE file for details

## Links

- Website: https://textmine.net
- GitHub: https://github.com/textmine/textmine-cli
- Report Issues: https://github.com/textmine/textmine-cli/issues
