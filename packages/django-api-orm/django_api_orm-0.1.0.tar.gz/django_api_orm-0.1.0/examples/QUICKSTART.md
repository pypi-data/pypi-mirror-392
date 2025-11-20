# Quick Start Guide - Test Server

Get up and running with the django-api-orm test server in 3 simple steps!

## Step 1: Install Dependencies

```bash
uv sync --all-extras
```

## Step 2: Start the Test Server

```bash
uvicorn examples.test_server:app --host 127.0.0.1 --port 8700 --reload
```

The server will start at `http://localhost:8700`

**Try it out:**
- Open `http://localhost:8700/docs` in your browser to see the interactive API documentation
- The server comes pre-loaded with test users and posts

## Step 3: Run the Test Scripts

Open a **new terminal** (keep the server running) and run:

```bash
# Test synchronous features
uv run python examples/test_with_server.py

# Test asynchronous features
uv run python examples/test_with_server_async.py
```

## What You'll See

The test scripts will demonstrate:
- ✓ Querying and filtering data
- ✓ Creating, updating, and deleting records
- ✓ Ordering and pagination
- ✓ Django ORM-like chaining
- ✓ Async/await patterns
- ✓ And much more!

## Example Output

```
================================================================================
django-api-orm Feature Test
================================================================================

1. Query all users (User.objects.all()):
--------------------------------------------------------------------------------
  - John Doe (john@example.com) [Active: True]
  - Jane Smith (jane@example.com) [Active: True]
  - Bob Wilson (bob@example.com) [Active: False]
  - Alice Johnson (alice@example.com) [Active: True]

2. Filter active users (User.objects.filter(active=True)):
--------------------------------------------------------------------------------
  - John Doe
  - Jane Smith
  - Alice Johnson

...
```

## Next Steps

- Modify `test_with_server.py` to try different queries
- Check out `examples/README.md` for detailed documentation
- Explore the API at `http://localhost:8700/docs`
- Try the API with curl or Postman

## Troubleshooting

**Port 8700 already in use?**
```bash
uvicorn examples.test_server:app --port 8701 --reload
```
Then update the test scripts to use `http://localhost:8701`.

**Connection refused error?**
Make sure the test server is running in a separate terminal before running the test scripts.

## Manual Testing with curl

```bash
# List all users
curl http://localhost:8700/api/v1/users/

# Get a specific user
curl http://localhost:8700/api/v1/users/1

# Create a new user
curl -X POST http://localhost:8700/api/v1/users/ \
  -H "Content-Type: application/json" \
  -d '{"name":"Test User","email":"test@example.com","active":true}'

# Filter active users
curl http://localhost:8700/api/v1/users/?active=true

# Reset the database
curl -X POST http://localhost:8700/api/v1/reset/
```

Happy testing! 🚀
