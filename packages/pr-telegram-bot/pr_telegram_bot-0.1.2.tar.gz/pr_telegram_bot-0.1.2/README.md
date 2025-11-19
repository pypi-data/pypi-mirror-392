# PR Telegram Bot

A modern Python framework for building Telegram bots with a state-based architecture. Built on top of `pyTelegramBotAPI` with async support, Pydantic models, and clean state management.

## Features

- 🎯 **State-based Architecture**: Organize bot logic into clean, maintainable states
- 🔄 **Async/Await Support**: Built for modern asynchronous Python
- 📝 **Type Safety**: Full type hints with Pydantic models
- 🎨 **Flexible Filters**: Expressive filter system for message handling
- 🗄️ **Database Abstraction**: Simple interface for user data persistence
- 🌐 **Global Handlers**: Define handlers that work across all states
- 🔌 **Easy Integration**: Drop-in replacement for pyTelegramBotAPI

## Installation

Using `uv` (recommended):

```bash
uv add pr-telegram-bot
```

Using `pip`:

```bash
pip install pr-telegram-bot
```

## Quick Start

```python
import asyncio
from pr_telegram_bot.client import PRTeleBotClient
from pr_telegram_bot.db_service import InMemoryUserDBService
from pr_telegram_bot.state import State, StateGroup, handler
from pr_telegram_bot.filters import F
from pr_telegram_bot.models import User

# Define a global state for commands available everywhere
class GlobalState(State):
    is_global = True

    @staticmethod
    @handler(F.text == "/start")
    async def send_start_message(bot, chat_id, update, user, data):
        await bot.send_message(chat_id=chat_id, text="Welcome! 👋")
        await bot.db_service.update_user(user_id=user.id, state="MainMenu")

# Create a state group
state_group = StateGroup()

# Define application states
@state_group.register
class MainMenu(State):
    @staticmethod
    @handler(F.content_type == "text")
    async def handle_text(bot, chat_id, update, user, data):
        await bot.send_message(chat_id=chat_id, text=f"You said: {update.text}")

# Initialize bot
db_service = InMemoryUserDBService()
bot = PRTeleBotClient(db_service=db_service, token="YOUR_BOT_TOKEN")

# Register states
bot.register_state(GlobalState)
bot.include(state_group)

# Start polling
asyncio.run(bot.polling())
```

## Core Concepts

### States

States represent different conversation contexts in your bot. Each state can have multiple handlers:

```python
@state_group.register
class OrderProcess(State):
    @staticmethod
    @handler(F.text == "/cancel")
    async def cancel_order(bot, chat_id, update, user, data):
        await bot.send_message(chat_id, "Order cancelled")
        await bot.db_service.update_user(user_id=user.id, state="MainMenu")

    @staticmethod
    @handler(F.content_type == "text")
    async def process_input(bot, chat_id, update, user, data):
        # Process order details
        pass
```

### Filters

Use the `F` object to create expressive filters:

```python
# Text matching
@handler(F.text == "/help")
@handler(F.text.startswith("/"))

# Content type
@handler(F.content_type == "photo")
@handler(F.content_type == "document")

# Update type
@handler(F.update_type == "message")
@handler(F.update_type == "callback_query")

# Commands
@handler(F.command == "start")

# Callback data
@handler(F.callback_data == "button_clicked")

# Combine filters
@handler(F.content_type == "text" & F.text.startswith("/"))
```

### User Model

The `User` model tracks user state and data:

```python
class User(BaseModel):
    id: int | None
    first_name: str
    last_name: str | None = None
    username: str | None = None
    language_code: str | None = None
    photo_url: str | None = None
    state: str = "Start"  # Current state
    data: dict[str, Any] = {}  # Persistent data
```

### Database Service

Implement your own database service or use the built-in in-memory one:

```python
from pr_telegram_bot.db_service import UserDBService

class MongoUserDBService(UserDBService):
    async def create_user(self, user: User) -> User:
        # Your implementation
        pass

    async def get_user(self, user_id: int) -> User | None:
        # Your implementation
        pass

    async def update_user(self, user_id: int, **update_data) -> User:
        # Your implementation
        pass
```

### Global Handlers

Global handlers work across all states (useful for commands like `/help`, `/cancel`):

```python
class GlobalState(State):
    is_global = True

    @staticmethod
    @handler(F.text == "/help")
    async def show_help(bot, chat_id, update, user, data):
        await bot.send_message(chat_id, "Help message")
```

## Advanced Usage

### State Groups

Organize related states into groups:

```python
# states/shopping.py
shopping_states = StateGroup()

@shopping_states.register
class BrowseCatalog(State):
    # handlers...

@shopping_states.register
class ViewCart(State):
    # handlers...

# main.py
from states.shopping import shopping_states

bot.include(shopping_states)
```

### Handler Priority

Handlers are executed in the order they're defined. The first matching handler stops execution:

```python
class MyState(State):
    @staticmethod
    @handler(F.text == "/special")
    async def handle_special(bot, chat_id, update, user, data):
        # Handles /special first
        pass

    @staticmethod
    @handler(F.content_type == "text")
    async def handle_any_text(bot, chat_id, update, user, data):
        # Handles any other text
        pass
```

### State Transitions

Change user state to control conversation flow:

```python
# Move to next state
await bot.db_service.update_user(
    user_id=user.id,
    state="NextState",
    data={"key": "value"}
)
```

## Project Structure Example

```
my_bot/
├── main.py
├── states/
│   ├── __init__.py
│   ├── global_handlers.py
│   ├── onboarding.py
│   └── main_menu.py
├── db_service.py
└── requirements.txt
```

## Development

### Requirements

- Python >= 3.13
- aiohttp >= 3.13.2
- pydantic >= 2.12.4
- pymongo >= 4.15.4
- pytelegrambotapi >= 4.29.1

### Development Setup

```bash
# Clone repository
git clone https://github.com/yourusername/pr-telegram-bot.git
cd pr-telegram-bot

# Install with dev dependencies
uv sync --dev

# Run tests
uv run pytest

# Run linter
uv run ruff check

# Format code
uv run ruff format
```

### Code Quality

The project uses:
- **Ruff** for linting and formatting
- **MyPy** for type checking
- **Pytest** for testing
- **Pre-commit** hooks for automated checks

## API Reference

### PRTeleBotClient

Main bot client class extending `AsyncTeleBot`.

**Methods:**
- `register_state(state_class)` - Register a single state
- `include(state_group)` - Include all states from a StateGroup

### State

Base class for defining bot states.

**Attributes:**
- `is_global` - Boolean flag for global handlers

### StateGroup

Container for organizing related states.

**Methods:**
- `register(state_class)` - Decorator to register a state

### Filters (F)

Filter expressions for message matching:
- `F.text` - Match message text
- `F.command` - Match bot commands
- `F.content_type` - Match content type
- `F.update_type` - Match update type
- `F.callback_data` - Match callback query data

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Run pre-commit checks
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Author

**Petro Romaniuk**
- Email: pr@email.com

## Changelog

### v0.1.1
- Initial release
- State-based architecture
- Filter system
- Database abstraction
- Global handlers support
