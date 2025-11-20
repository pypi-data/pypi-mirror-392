# django-api-orm

[![Tests](https://github.com/mrb101/django-api-orm/workflows/Tests/badge.svg)](https://github.com/mrb101/django-api-orm/actions)
[![Coverage](https://codecov.io/gh/mrb101/django-api-orm/branch/main/graph/badge.svg)](https://codecov.io/gh/mrb101/django-api-orm)
[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](https://github.com/mrb101/django-api-orm/blob/main/LICENSE)

A Django ORM-like interface for external REST APIs with Pydantic validation and httpx.

## Overview

`django-api-orm` provides a familiar Django ORM interface for interacting with REST APIs, making it easy to work with external services using the same patterns you already know. Built with modern Python features:

- **Pydantic 2.0** for robust data validation and serialization
- **httpx** for modern HTTP client support (both sync and async)
- **Full type safety** with comprehensive type hints
- **Django-like API** for intuitive, familiar usage
- **91% test coverage** with 152 comprehensive tests

## Features

- **Sync and Async Support** - Use synchronous or asynchronous clients based on your needs
- **Type Safety** - Full type hints and Pydantic validation throughout
- **Nested Schemas** - Full support for nested Pydantic models with dot notation access
- **Django-like QuerySet API** - Familiar filter(), exclude(), get(), first(), last(), etc.
- **HTTP/2 Support** - Optional HTTP/2 for better performance (async only)
- **Connection Pooling** - Built-in connection pooling with httpx
- **Automatic Retries** - Configurable retry logic for failed requests
- **Lazy Evaluation** - QuerySets only execute when needed
- **Chainable Queries** - Build complex queries with method chaining
- **CRUD Operations** - Full create, read, update, delete support
- **Concurrent Operations** - Easy async/await with asyncio.gather()
- **Test Server Included** - FastAPI test server with insurance domain for development and testing

## Installation

```bash
# Basic installation
pip install django-api-orm

# With async and HTTP/2 support
pip install django-api-orm[async]

# Development installation
pip install django-api-orm[dev]
```

Using uv (recommended):

```bash
uv add django-api-orm
# or with async support
uv add "django-api-orm[async]"
```

## Quick Start

### Define Your Models

```python
from pydantic import BaseModel
from django_api_orm import APIModel, ServiceClient, register_models

# Define your Pydantic schema
class UserSchema(BaseModel):
    id: int | None = None  # Optional for creation
    name: str
    email: str
    active: bool = True

# Define your API model
class User(APIModel):
    _schema_class = UserSchema
    _endpoint = "/api/v1/users/"
```

### Synchronous Usage

```python
# Create a client and register models
with ServiceClient(
    base_url="https://api.example.com",
    auth_token="your-token-here"
) as client:
    register_models(client, User)

    # Query users (Django-like!)
    active_users = User.objects.filter(active=True)
    for user in active_users:
        print(f"{user.name} - {user.email}")

    # Get a single user
    user = User.objects.get(id=1)

    # Create a new user
    new_user = User.objects.create(
        name="Alice Smith",
        email="alice@example.com"
    )

    # Update a user
    user.email = "newemail@example.com"
    user.save(update_fields=["email"])

    # Delete a user
    user.delete()

    # Chain queries
    recent_active = (User.objects
                     .filter(active=True)
                     .order_by("-created_at")
                     .first())

    # Get or create
    user, created = User.objects.get_or_create(
        email="bob@example.com",
        defaults={"name": "Bob Jones"}
    )
```

### Asynchronous Usage

```python
import asyncio
from django_api_orm import AsyncAPIModel, AsyncServiceClient, register_async_models

class User(AsyncAPIModel):
    _schema_class = UserSchema
    _endpoint = "/api/v1/users/"

async def main():
    async with AsyncServiceClient(
        base_url="https://api.example.com",
        auth_token="your-token-here",
        http2=True  # Enable HTTP/2
    ) as client:
        register_async_models(client, User)

        # Async iteration
        async for user in User.objects.filter(active=True):
            print(f"{user.name} - {user.email}")

        # Async retrieval
        user = await User.objects.get(id=1)

        # Async creation
        new_user = await User.objects.create(
            name="Charlie Brown",
            email="charlie@example.com"
        )

        # Async update
        user.email = "updated@example.com"
        await user.save()

        # Concurrent operations
        users_count, posts_count = await asyncio.gather(
            User.objects.filter(active=True).count(),
            Post.objects.filter(published=True).count()
        )

asyncio.run(main())
```

## Nested Schemas

django-api-orm fully supports nested Pydantic models with dot notation access:

```python
from pydantic import BaseModel, EmailStr
from datetime import date

# Define nested schema
class AddressSchema(BaseModel):
    street: str
    city: str
    state: str
    zip_code: str
    country: str = "USA"

# Use in parent schema
class PolicyHolderSchema(BaseModel):
    id: int | None = None
    first_name: str
    last_name: str
    email: EmailStr
    date_of_birth: date
    address: AddressSchema  # Nested schema
    active: bool = True

class PolicyHolder(APIModel):
    _schema_class = PolicyHolderSchema
    _endpoint = "/api/v1/policyholders/"

# Access nested fields with dot notation
with ServiceClient(base_url="https://api.example.com") as client:
    register_models(client, PolicyHolder)

    # Create with nested data
    address = AddressSchema(
        street="123 Main St",
        city="Chicago",
        state="IL",
        zip_code="60601"
    )

    holder = PolicyHolder.objects.create(
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        date_of_birth=date(1980, 1, 1),
        address=address,  # Nested schema
        active=True
    )

    # Access nested fields
    print(holder.address.city)      # "Chicago"
    print(holder.address.state)     # "IL"
    print(holder.address.zip_code)  # "60601"

    # Update nested fields
    holder.address.street = "456 Oak Ave"
    holder.save()
```

See [examples/INSURANCE_DOMAIN.md](examples/INSURANCE_DOMAIN.md) for a complete insurance domain example with nested schemas.

## Test Server

django-api-orm includes a comprehensive FastAPI test server for development and testing. The test server implements a complete insurance domain API with PolicyHolder, Policy, and Claim models.

### Starting the Test Server

```bash
# Install development dependencies
uv sync --all-extras

# Start the server
uvicorn examples.test_server:app --host 127.0.0.1 --port 8700 --reload
```

The server will be available at `http://localhost:8700` with interactive API docs at `http://localhost:8700/docs`.

### Running Test Scripts

```bash
# Run synchronous test script
uv run python examples/test_with_server.py

# Run asynchronous test script
uv run python examples/test_with_server_async.py
```

The test scripts demonstrate all features including:
- Creating, reading, updating, and deleting records
- Filtering and querying with nested schemas
- Relationship-based filtering
- Concurrent async operations
- And much more!

See [examples/README.md](examples/README.md) for complete test server documentation.

## Advanced Features

### Query Methods

```python
# Filtering
User.objects.filter(active=True, role="admin")
User.objects.exclude(status="banned")

# Ordering
User.objects.order_by("-created_at")
User.objects.order_by("name", "-email")

# Slicing
User.objects.all()[10:20]  # Offset and limit
User.objects.all()[0]  # Get first by index

# Retrieval
User.objects.get(id=123)  # Get single (raises DoesNotExist)
User.objects.first()  # Get first or None
User.objects.last()  # Get last or None
User.objects.exists()  # Check if any exist
User.objects.count()  # Get count

# Value extraction
User.objects.all().values("id", "name")  # List of dicts
User.objects.all().values_list("id", flat=True)  # Flat list
```

### Manager Methods

```python
# Creation
User.objects.create(name="Alice", email="alice@example.com")
User.objects.bulk_create([
    {"name": "Bob", "email": "bob@example.com"},
    {"name": "Charlie", "email": "charlie@example.com"}
])

# Get or create
user, created = User.objects.get_or_create(
    email="alice@example.com",
    defaults={"name": "Alice"}
)

# Update or create
user, created = User.objects.update_or_create(
    email="alice@example.com",
    defaults={"name": "Alice Updated"}
)
```

### Model Methods

```python
# Create
user = User(name="Alice", email="alice@example.com", _client=client)
user.save()

# Update
user.email = "newemail@example.com"
user.save()  # Updates all fields
user.save(update_fields=["email"])  # Partial update

# Refresh
user.refresh_from_api()  # Re-fetch from API

# Delete
user.delete()

# Convert to dict
data = user.to_dict()
data = user.to_dict(exclude_unset=True)
```

## Testing

The library has comprehensive test coverage (91%):

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src/django_api_orm

# Run specific tests
uv run pytest tests/test_orm_integration.py
uv run pytest tests/test_async_orm_integration.py
```

## Type Checking and Linting

```bash
# Type checking with mypy
uv run mypy src/

# Linting with ruff
uv run ruff check src/ tests/

# Auto-fix linting issues
uv run ruff check --fix src/ tests/

# Format code
uv run ruff format src/ tests/
```

## Project Status

**Version:** 0.1.0 (Beta)

**Test Coverage:** 91% (152 tests)

### Implemented Features

- [x] Complete exception system
- [x] Synchronous HTTP client (ServiceClient)
- [x] Asynchronous HTTP client (AsyncServiceClient)
- [x] QuerySet implementation (sync and async)
- [x] Manager implementation (sync and async)
- [x] APIModel base class (sync and async)
- [x] Model registration system
- [x] Nested Pydantic schema support with dot notation
- [x] Manager delegation methods (values, values_list)
- [x] AsyncQuerySet slicing support
- [x] Comprehensive test suite (152 tests, 91% coverage)
- [x] FastAPI test server with insurance domain examples
- [x] Full type safety with mypy
- [x] CI/CD with GitHub Actions
- [x] Connection pooling and retries
- [x] HTTP/2 support (async)

### Roadmap

- [ ] Advanced caching layer
- [ ] Streaming support for large responses
- [ ] Related field support (select_related, prefetch_related)
- [ ] Query optimization and request batching
- [ ] More example projects
- [ ] Performance benchmarks

## Why httpx over requests?

We chose httpx for several important reasons:

1. **Native async/sync support** - Single codebase for both patterns
2. **HTTP/2 support** - Better performance with multiplexing
3. **Better connection pooling** - Optimized and built-in
4. **Modern API** - Cleaner, more Pythonic interface
5. **Active development** - Better maintained with more features
6. **Type hints** - Better IDE support and type safety
7. **Better timeout control** - More granular timeout configuration

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/mrb101/django-api-orm.git
cd django-api-orm

# Install dependencies
uv sync --all-extras

# Run tests
uv run pytest

# Type checking
uv run mypy src/

# Linting
uv run ruff check src/ tests/
```

### Project Structure

```
src/django_api_orm/
├── __init__.py          # Public API exports
├── py.typed             # PEP 561 type marker
├── exceptions.py        # Custom exceptions
├── client.py            # Sync HTTP client (httpx)
├── async_client.py      # Async HTTP client (httpx)
├── base.py              # APIModel, QuerySet, Manager
├── async_base.py        # Async versions
├── utils.py             # Helper functions
└── typing.py            # Type hints and protocols

tests/
├── test_exceptions.py          # Exception tests
├── test_client.py              # Sync client tests
├── test_async_client.py        # Async client tests
├── test_orm_integration.py     # Sync ORM tests
├── test_async_orm_integration.py  # Async ORM tests
└── test_utils.py               # Utility tests

examples/
├── basic_usage.py              # Basic sync example
├── async_usage.py              # Basic async example
├── test_server.py              # FastAPI test server (insurance domain)
├── test_with_server.py         # Comprehensive sync test script
├── test_with_server_async.py   # Comprehensive async test script
├── README.md                   # Test server documentation
├── INSURANCE_DOMAIN.md         # Insurance domain guide
└── QUICKSTART.md               # Quick start guide
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for your changes
5. Ensure tests pass (`uv run pytest`)
6. Ensure type checking passes (`uv run mypy src/`)
7. Ensure linting passes (`uv run ruff check src/ tests/`)
8. Commit your changes (`git commit -m 'Add amazing feature'`)
9. Push to the branch (`git push origin feature/amazing-feature`)
10. Open a Pull Request

## License

MIT License - see LICENSE file for details.

## Credits

Created by Bassel J. Hamadeh at TigerLab.

Inspired by Django ORM, Pydantic, and httpx.

## Support

- **Issues**: https://github.com/mrb101/django-api-orm/issues
- **Discussions**: https://github.com/mrb101/django-api-orm/discussions
- **Documentation**: https://django-api-orm.readthedocs.io/en/latest/

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for detailed version history.

### Recent Updates

- **Nested Pydantic schema support** - Full support for nested models with dot notation access
- **FastAPI test server** - Comprehensive insurance domain test server for development
- **Enhanced Manager methods** - Added values() and values_list() delegation methods
- **Bug fixes** - Fixed nested schema preservation, attribute syncing, and JSON serialization

### 0.1.0 (Beta)

- Initial release with full sync and async support
- Complete QuerySet, Manager, and APIModel implementations
- 91% test coverage with 152 tests
- Full type safety with mypy
- CI/CD with GitHub Actions
