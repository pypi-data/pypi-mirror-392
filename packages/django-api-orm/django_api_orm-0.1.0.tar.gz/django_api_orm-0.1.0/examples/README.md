# Django API ORM Examples

This folder contains examples and a development test server for the django-api-orm library.

## Files

- **basic_usage.py** - Synchronous usage examples
- **async_usage.py** - Asynchronous usage examples
- **test_server.py** - FastAPI development server for testing
- **test_with_server.py** - Comprehensive sync tests using the test server
- **test_with_server_async.py** - Comprehensive async tests using the test server

## Quick Start

### 1. Install Development Dependencies

```bash
# Using uv (recommended)
uv sync --all-extras

# Or using pip
pip install -e ".[dev,async]"
```

### 2. Start the Test Server

```bash
# From the project root
uvicorn examples.test_server:app --reload

# Or specify host and port
uvicorn examples.test_server:app --host 0.0.0.0 --port 8700 --reload
```

The server will start at `http://localhost:8700` with:
- Interactive API docs at `http://localhost:8700/docs`
- ReDoc documentation at `http://localhost:8700/redoc`
- User endpoint at `http://localhost:8700/api/v1/users/`
- Post endpoint at `http://localhost:8700/api/v1/posts/`

### 3. Run Test Scripts

In a separate terminal:

```bash
# Run synchronous tests
python examples/test_with_server.py

# Run asynchronous tests
python examples/test_with_server_async.py
```

## Test Server Features

The test server (`test_server.py`) provides a fully functional REST API for testing all django-api-orm features:

### Endpoints

#### Users (`/api/v1/users/`)
- `GET /api/v1/users/` - List users with filtering, ordering, and pagination
- `GET /api/v1/users/{id}` - Get a single user
- `POST /api/v1/users/` - Create a new user
- `PUT /api/v1/users/{id}` - Update a user (full)
- `PATCH /api/v1/users/{id}` - Partial update a user
- `DELETE /api/v1/users/{id}` - Delete a user
- `POST /api/v1/users/bulk/` - Bulk create users

#### Posts (`/api/v1/posts/`)
- `GET /api/v1/posts/` - List posts with filtering, ordering, and pagination
- `GET /api/v1/posts/{id}` - Get a single post
- `POST /api/v1/posts/` - Create a new post
- `PUT /api/v1/posts/{id}` - Update a post (full)
- `PATCH /api/v1/posts/{id}` - Partial update a post
- `DELETE /api/v1/posts/{id}` - Delete a post

#### Utility
- `POST /api/v1/reset/` - Reset database to initial state

### Query Parameters

All list endpoints support:
- **Filtering**: `?active=true`, `?published=false`, `?user_id=1`
- **Ordering**: `?ordering=name` or `?ordering=-id` (prefix with `-` for descending)
- **Pagination**: `?limit=10&offset=20`

### Initial Test Data

The server starts with sample data:
- 4 test users (3 active, 1 inactive)
- 4 test posts (3 published, 1 draft)

## Features Tested

The test scripts demonstrate all major django-api-orm features:

### QuerySet Operations
- `all()` - Get all objects
- `filter(**kwargs)` - Filter by fields
- `exclude(**kwargs)` - Exclude by fields
- `get(**kwargs)` - Get a single object
- `first()` / `last()` - Get first/last object
- `exists()` - Check if objects exist
- `count()` - Count objects
- `order_by(*fields)` - Order results
- Slicing: `[start:end]` - Pagination

### Manager Operations
- `create(**kwargs)` - Create a new object
- `bulk_create(data_list)` - Bulk create objects
- `get_or_create(**kwargs)` - Get or create an object
- `update_or_create(**kwargs)` - Update or create an object

### Model Operations
- `save()` - Save changes
- `save(update_fields=[...])` - Partial update
- `delete()` - Delete object
- `refresh_from_api()` - Refresh from server
- `to_dict()` - Convert to dictionary

### Async Operations
- Async iteration: `async for obj in Model.objects.all()`
- Awaitable operations: `await Model.objects.get(id=1)`
- Concurrent operations: `asyncio.gather(...)`

## API Examples

### Using the Test Server with curl

```bash
# List all users
curl http://localhost:8700/api/v1/users/

# Get user by ID
curl http://localhost:8700/api/v1/users/1

# Create a new user
curl -X POST http://localhost:8700/api/v1/users/ \
  -H "Content-Type: application/json" \
  -d '{"name":"Test User","email":"test@example.com","active":true}'

# Filter active users
curl http://localhost:8700/api/v1/users/?active=true

# Order by name descending
curl http://localhost:8700/api/v1/users/?ordering=-name

# Pagination
curl http://localhost:8700/api/v1/users/?limit=2&offset=1

# Update user
curl -X PATCH http://localhost:8700/api/v1/users/1 \
  -H "Content-Type: application/json" \
  -d '{"email":"updated@example.com"}'

# Delete user
curl -X DELETE http://localhost:8700/api/v1/users/1

# Reset database
curl -X POST http://localhost:8700/api/v1/reset/
```

### Using with Python Requests

```python
import requests

# List users
response = requests.get("http://localhost:8700/api/v1/users/")
users = response.json()

# Create user
response = requests.post(
    "http://localhost:8700/api/v1/users/",
    json={"name": "New User", "email": "new@example.com"}
)
user = response.json()

# Filter and order
response = requests.get(
    "http://localhost:8700/api/v1/users/",
    params={"active": "true", "ordering": "-id", "limit": 5}
)
users = response.json()
```

## Development Notes

### In-Memory Storage

The test server uses in-memory dictionaries for storage, which means:
- Data is reset when the server restarts
- No database setup required
- Fast and simple for testing
- Use `POST /api/v1/reset/` to reset data without restarting

### Development-Only Dependencies

FastAPI and uvicorn are only installed when using the `dev` extras:
```bash
pip install -e ".[dev]"
```

These dependencies are **not** required for production use of django-api-orm.

### Extending the Test Server

You can easily extend the test server to test additional features:

1. Add new models by creating schemas and endpoints
2. Add custom query parameters for advanced filtering
3. Add authentication/authorization testing
4. Add rate limiting or caching examples

## Troubleshooting

### Port Already in Use

If port 8700 is already in use:
```bash
uvicorn examples.test_server:app --port 8701 --reload
```

Then update the test scripts to use `http://localhost:8701`.

### Import Errors

Make sure you've installed the package and dependencies:
```bash
uv sync --all-extras
# or
pip install -e ".[dev,async]"
```

### Connection Refused

Make sure the test server is running before executing the test scripts.

## Next Steps

- Try modifying the test scripts to explore different query patterns
- Use the interactive API docs at `/docs` to experiment with the API
- Create your own models and test them with the library
- Check out the main documentation for advanced features
