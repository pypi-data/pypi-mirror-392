AsyncServiceClient
==================

The ``AsyncServiceClient`` provides asynchronous HTTP client functionality for interacting with REST APIs.

.. currentmodule:: django_api_orm.async_client

.. autoclass:: AsyncServiceClient
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__, __aenter__, __aexit__

Example Usage
-------------

Basic Client
^^^^^^^^^^^^

.. code-block:: python

   from django_api_orm import AsyncServiceClient

   # Create a client
   client = AsyncServiceClient(
       base_url="https://api.example.com",
       auth_token="your-token-here"
   )

   # Use as async context manager (recommended)
   async with AsyncServiceClient(base_url="https://api.example.com") as client:
       # Client automatically closed on exit
       pass

Configuration Options
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   client = AsyncServiceClient(
       base_url="https://api.example.com",
       auth_token="your-token-here",
       timeout=30.0,  # Request timeout in seconds
       max_retries=3,  # Number of retries for failed requests
       retry_delay=1.0,  # Delay between retries in seconds
       http2=True,  # Enable HTTP/2 support
       max_connections=100,  # Maximum number of connections
       max_keepalive_connections=20,  # Maximum keep-alive connections
       headers={"X-Custom-Header": "value"}  # Additional headers
   )

Making Requests
^^^^^^^^^^^^^^^

.. code-block:: python

   async with AsyncServiceClient(base_url="https://api.example.com") as client:
       # GET request
       response = await client.get("/users/", params={"active": True})

       # POST request
       response = await client.post("/users/", data={"name": "Alice"})

       # PUT request
       response = await client.put("/users/1/", data={"name": "Alice Updated"})

       # PATCH request
       response = await client.patch("/users/1/", data={"email": "new@example.com"})

       # DELETE request
       response = await client.delete("/users/1/")

HTTP/2 Support
^^^^^^^^^^^^^^

Enable HTTP/2 for better performance:

.. code-block:: python

   async with AsyncServiceClient(
       base_url="https://api.example.com",
       http2=True  # Requires httpx[http2]
   ) as client:
       # Requests use HTTP/2 when supported by server
       response = await client.get("/users/")

Concurrent Requests
^^^^^^^^^^^^^^^^^^^

Make multiple requests concurrently:

.. code-block:: python

   import asyncio

   async with AsyncServiceClient(base_url="https://api.example.com") as client:
       # Concurrent requests
       responses = await asyncio.gather(
           client.get("/users/1/"),
           client.get("/users/2/"),
           client.get("/users/3/")
       )

       # Process responses
       for response in responses:
           print(response.data)

Response Object
^^^^^^^^^^^^^^^

All request methods return a ``Response`` object:

.. code-block:: python

   response = await client.get("/users/1/")

   # Access response data
   print(response.status_code)  # HTTP status code
   print(response.data)  # Parsed JSON data (dict or list)
   print(response.headers)  # Response headers

See Also
--------

- :class:`~django_api_orm.client.ServiceClient` for sync operations
- :doc:`../user-guide/async` for async patterns and examples
- :doc:`../user-guide/models` for using the client with models
