#!/bin/bash
# Convenience script to run the test server and tests

set -e

echo "============================================"
echo "django-api-orm Test Server & Tests"
echo "============================================"
echo ""

# Check if server is already running
if curl -s http://localhost:8700 > /dev/null 2>&1; then
    echo "✓ Test server is already running at http://localhost:8700"
    echo ""
else
    echo "✗ Test server is not running"
    echo ""
    echo "Please start the server in a separate terminal:"
    echo "  uvicorn examples.test_server:app --host 127.0.0.1 --port 8700 --reload"
    echo ""
    echo "Then run this script again, or run the tests directly:"
    echo "  python examples/test_with_server.py"
    echo "  python examples/test_with_server_async.py"
    exit 1
fi

# Run sync tests
echo "Running synchronous tests..."
echo "--------------------------------------------"
python examples/test_with_server.py
echo ""

# Run async tests
echo "Running asynchronous tests..."
echo "--------------------------------------------"
python examples/test_with_server_async.py
echo ""

echo "============================================"
echo "All tests completed!"
echo "============================================"
