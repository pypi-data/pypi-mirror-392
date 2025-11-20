Exceptions
==========

**django-api-orm** provides a comprehensive exception hierarchy similar to Django's ORM exceptions, making error handling familiar and predictable.

Exception Hierarchy
-------------------

All exceptions inherit from ``APIException``:

.. code-block:: text

   APIException
   ├── ValidationError (from Pydantic)
   ├── DoesNotExist
   ├── MultipleObjectsReturned
   ├── APIConnectionError
   ├── APITimeoutError
   ├── APIHTTPError
   │   ├── APIClientError (4xx)
   │   │   ├── BadRequestError (400)
   │   │   ├── UnauthorizedError (401)
   │   │   ├── ForbiddenError (403)
   │   │   ├── NotFoundError (404)
   │   │   └── TooManyRequestsError (429)
   │   └── APIServerError (5xx)
   │       ├── InternalServerError (500)
   │       ├── BadGatewayError (502)
   │       ├── ServiceUnavailableError (503)
   │       └── GatewayTimeoutError (504)
   └── ConfigurationError

Common Exceptions
-----------------

DoesNotExist
^^^^^^^^^^^^

Raised when a query returns no results when exactly one was expected:

.. code-block:: python

   from django_api_orm.exceptions import DoesNotExist

   try:
       user = User.objects.get(id=999)
   except DoesNotExist:
       print("User not found")

   # Or catch model-specific exception
   try:
       user = User.objects.get(id=999)
   except User.DoesNotExist:
       print("User not found")

Common scenarios:

- ``Model.objects.get()`` with no matching record
- API returns 404 for a specific resource

MultipleObjectsReturned
^^^^^^^^^^^^^^^^^^^^^^^^

Raised when a query returns multiple results when exactly one was expected:

.. code-block:: python

   from django_api_orm.exceptions import MultipleObjectsReturned

   try:
       # Multiple users with role="admin" exist
       user = User.objects.get(role="admin")
   except MultipleObjectsReturned:
       print("Multiple users found, expected one")

   # Or catch model-specific exception
   try:
       user = User.objects.get(role="admin")
   except User.MultipleObjectsReturned:
       print("Multiple users found")

Common scenarios:

- ``Model.objects.get()`` with multiple matching records
- API returns a list when a single item was expected

ValidationError
^^^^^^^^^^^^^^^

Raised when data validation fails (from Pydantic):

.. code-block:: python

   from pydantic import ValidationError

   try:
       user = User.objects.create(
           name="",  # Empty name
           email="invalid-email",  # Invalid email
           age=-5  # Invalid age
       )
   except ValidationError as e:
       print(f"Validation failed: {e}")
       for error in e.errors():
           print(f"  {error['loc']}: {error['msg']}")

Common scenarios:

- Invalid field values during creation
- Missing required fields
- Type mismatches
- Failed Pydantic validators

HTTP Exceptions
---------------

APIHTTPError
^^^^^^^^^^^^

Base class for all HTTP-related errors:

.. code-block:: python

   from django_api_orm.exceptions import APIHTTPError

   try:
       user = User.objects.get(id=1)
   except APIHTTPError as e:
       print(f"HTTP error: {e.status_code} - {e.message}")

Client Errors (4xx)
^^^^^^^^^^^^^^^^^^^

**BadRequestError (400)**: Invalid request data

.. code-block:: python

   from django_api_orm.exceptions import BadRequestError

   try:
       user = User.objects.create(name="Alice", email="alice@example.com")
   except BadRequestError as e:
       print(f"Bad request: {e.message}")

**UnauthorizedError (401)**: Authentication required or failed

.. code-block:: python

   from django_api_orm.exceptions import UnauthorizedError

   try:
       user = User.objects.get(id=1)
   except UnauthorizedError:
       print("Authentication required or token expired")

**ForbiddenError (403)**: Authenticated but not authorized

.. code-block:: python

   from django_api_orm.exceptions import ForbiddenError

   try:
       user.delete()
   except ForbiddenError:
       print("You don't have permission to delete this user")

**NotFoundError (404)**: Resource not found

.. code-block:: python

   from django_api_orm.exceptions import NotFoundError

   try:
       user = User.objects.get(id=999)
   except NotFoundError:
       print("User not found")

**TooManyRequestsError (429)**: Rate limit exceeded

.. code-block:: python

   from django_api_orm.exceptions import TooManyRequestsError

   try:
       users = User.objects.all()
   except TooManyRequestsError as e:
       print(f"Rate limit exceeded. Retry after: {e.retry_after}")

Server Errors (5xx)
^^^^^^^^^^^^^^^^^^^

**InternalServerError (500)**: Server error

.. code-block:: python

   from django_api_orm.exceptions import InternalServerError

   try:
       user = User.objects.create(name="Alice", email="alice@example.com")
   except InternalServerError:
       print("Server encountered an error")

**BadGatewayError (502)**: Bad gateway

.. code-block:: python

   from django_api_orm.exceptions import BadGatewayError

   try:
       users = User.objects.all()
   except BadGatewayError:
       print("Gateway error - upstream server issue")

**ServiceUnavailableError (503)**: Service unavailable

.. code-block:: python

   from django_api_orm.exceptions import ServiceUnavailableError

   try:
       users = User.objects.all()
   except ServiceUnavailableError as e:
       print(f"Service unavailable. Retry after: {e.retry_after}")

**GatewayTimeoutError (504)**: Gateway timeout

.. code-block:: python

   from django_api_orm.exceptions import GatewayTimeoutError

   try:
       users = User.objects.all()
   except GatewayTimeoutError:
       print("Gateway timeout - upstream server too slow")

Connection Exceptions
---------------------

APIConnectionError
^^^^^^^^^^^^^^^^^^

Raised when a connection to the API cannot be established:

.. code-block:: python

   from django_api_orm.exceptions import APIConnectionError

   try:
       user = User.objects.get(id=1)
   except APIConnectionError as e:
       print(f"Connection failed: {e.message}")

Common scenarios:

- Network is down
- Invalid base URL
- DNS resolution failed
- SSL/TLS errors

APITimeoutError
^^^^^^^^^^^^^^^

Raised when a request times out:

.. code-block:: python

   from django_api_orm.exceptions import APITimeoutError

   try:
       user = User.objects.get(id=1)
   except APITimeoutError as e:
       print(f"Request timed out after {e.timeout} seconds")

Common scenarios:

- API is slow to respond
- Large response taking too long
- Network latency issues

Configuration Exceptions
------------------------

ConfigurationError
^^^^^^^^^^^^^^^^^^

Raised when there's a configuration issue:

.. code-block:: python

   from django_api_orm.exceptions import ConfigurationError

   try:
       # Model not registered with client
       user = User.objects.get(id=1)
   except ConfigurationError as e:
       print(f"Configuration error: {e.message}")

Common scenarios:

- Model not registered with a client
- Invalid endpoint configuration
- Missing required configuration

Error Handling Patterns
-----------------------

Specific Exception Handling
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Handle specific exceptions for fine-grained control:

.. code-block:: python

   from django_api_orm.exceptions import (
       DoesNotExist,
       UnauthorizedError,
       NotFoundError,
       APIServerError
   )

   try:
       user = User.objects.get(id=user_id)
   except DoesNotExist:
       print("User not found")
   except UnauthorizedError:
       print("Please log in")
   except NotFoundError:
       print("API endpoint not found")
   except APIServerError:
       print("Server error, try again later")

Generic Exception Handling
^^^^^^^^^^^^^^^^^^^^^^^^^^

Catch all API exceptions with ``APIException``:

.. code-block:: python

   from django_api_orm.exceptions import APIException

   try:
       user = User.objects.get(id=user_id)
   except APIException as e:
       print(f"API error: {e}")
       # Log error, notify admin, etc.

HTTP Status Code Handling
^^^^^^^^^^^^^^^^^^^^^^^^^^

Handle errors by HTTP status code:

.. code-block:: python

   from django_api_orm.exceptions import APIHTTPError, APIClientError, APIServerError

   try:
       user = User.objects.get(id=user_id)
   except APIClientError as e:
       # 4xx errors - client issue
       if e.status_code == 401:
           print("Please log in")
       elif e.status_code == 403:
           print("Permission denied")
       elif e.status_code == 404:
           print("Not found")
       else:
           print(f"Client error: {e.status_code}")
   except APIServerError as e:
       # 5xx errors - server issue
       print(f"Server error: {e.status_code}")

Retry Logic
^^^^^^^^^^^

Implement retry logic for transient errors:

.. code-block:: python

   import time
   from django_api_orm.exceptions import (
       APIServerError,
       APITimeoutError,
       TooManyRequestsError
   )

   max_retries = 3
   retry_delay = 1  # seconds

   for attempt in range(max_retries):
       try:
           user = User.objects.get(id=user_id)
           break
       except (APIServerError, APITimeoutError) as e:
           if attempt < max_retries - 1:
               time.sleep(retry_delay * (attempt + 1))
               continue
           raise
       except TooManyRequestsError as e:
           if attempt < max_retries - 1 and e.retry_after:
               time.sleep(e.retry_after)
               continue
           raise

Fallback Values
^^^^^^^^^^^^^^^

Provide fallback values when resources don't exist:

.. code-block:: python

   from django_api_orm.exceptions import DoesNotExist

   try:
       user = User.objects.get(email=email)
   except DoesNotExist:
       # Create a default user
       user = User.objects.create(
           email=email,
           name="New User",
           active=False
       )

   # Or use get_or_create
   user, created = User.objects.get_or_create(
       email=email,
       defaults={"name": "New User", "active": False}
   )

Logging Errors
^^^^^^^^^^^^^^

Log errors for debugging and monitoring:

.. code-block:: python

   import logging
   from django_api_orm.exceptions import APIException

   logger = logging.getLogger(__name__)

   try:
       user = User.objects.get(id=user_id)
   except APIException as e:
       logger.error(
           f"API error getting user {user_id}: {e}",
           exc_info=True,
           extra={
               "user_id": user_id,
               "exception_type": type(e).__name__,
           }
       )
       raise

Async Exception Handling
-------------------------

Exception handling in async code works the same way:

.. code-block:: python

   from django_api_orm.exceptions import DoesNotExist, APIHTTPError

   try:
       user = await User.objects.get(id=user_id)
   except DoesNotExist:
       print("User not found")
   except APIHTTPError as e:
       print(f"HTTP error: {e.status_code}")

Best Practices
--------------

1. **Be specific**: Catch specific exceptions when possible
2. **Log errors**: Always log unexpected errors for debugging
3. **Provide context**: Include relevant information in error messages
4. **Handle validation**: Validate data before sending to API
5. **Implement retries**: Retry transient errors (5xx, timeouts)
6. **Respect rate limits**: Honor ``retry_after`` headers
7. **Use fallbacks**: Provide sensible defaults when appropriate
8. **Don't catch too broadly**: Only catch exceptions you can handle

Exception Attributes
--------------------

All exceptions have useful attributes:

.. code-block:: python

   from django_api_orm.exceptions import APIHTTPError

   try:
       user = User.objects.get(id=user_id)
   except APIHTTPError as e:
       print(f"Status code: {e.status_code}")
       print(f"Message: {e.message}")
       print(f"Response: {e.response}")

   from django_api_orm.exceptions import TooManyRequestsError

   try:
       users = User.objects.all()
   except TooManyRequestsError as e:
       print(f"Retry after: {e.retry_after} seconds")

Complete Example
----------------

.. code-block:: python

   import logging
   from django_api_orm.exceptions import (
       DoesNotExist,
       MultipleObjectsReturned,
       ValidationError,
       UnauthorizedError,
       ForbiddenError,
       NotFoundError,
       TooManyRequestsError,
       APIServerError,
       APITimeoutError,
       APIConnectionError,
   )

   logger = logging.getLogger(__name__)

   def get_user_safely(user_id: int):
       """Get a user with comprehensive error handling."""
       try:
           return User.objects.get(id=user_id)

       except DoesNotExist:
           logger.warning(f"User {user_id} not found")
           return None

       except UnauthorizedError:
           logger.error("Authentication failed")
           raise  # Re-raise to caller

       except ForbiddenError:
           logger.error(f"Access denied to user {user_id}")
           raise

       except NotFoundError:
           logger.error("API endpoint not found")
           return None

       except TooManyRequestsError as e:
           logger.warning(f"Rate limited. Retry after {e.retry_after}s")
           raise

       except APIServerError as e:
           logger.error(f"Server error: {e.status_code} - {e.message}")
           return None

       except APITimeoutError:
           logger.error(f"Request timed out for user {user_id}")
           return None

       except APIConnectionError as e:
           logger.error(f"Connection failed: {e.message}")
           return None

       except Exception as e:
           logger.exception(f"Unexpected error getting user {user_id}")
           raise

Next Steps
----------

- See :doc:`models` for model usage
- Learn about :doc:`querysets` for querying
- Explore :doc:`async` for async exception handling
