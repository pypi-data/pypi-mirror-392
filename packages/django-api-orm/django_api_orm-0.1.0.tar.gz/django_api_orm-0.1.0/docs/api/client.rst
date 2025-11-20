ServiceClient
=============

The ``ServiceClient`` provides synchronous HTTP client functionality for interacting with REST APIs.

.. currentmodule:: django_api_orm.client

.. autoclass:: ServiceClient
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__, __enter__, __exit__

Example Usage
-------------

Basic Client
^^^^^^^^^^^^

.. code-block:: python

   from django_api_orm import ServiceClient

   # Create a client
   client = ServiceClient(
       base_url="https://api.example.com",
       auth_token="your-token-here"
   )

   # Use as context manager (recommended)
   with ServiceClient(base_url="https://api.example.com") as client:
       # Client automatically closed on exit
       pass

Configuration Options
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   client = ServiceClient(
       base_url="https://api.example.com",
       auth_token="your-token-here",
       timeout=30.0,  # Request timeout in seconds
       max_retries=3,  # Number of retries for failed requests
       retry_delay=1.0,  # Delay between retries in seconds
       max_connections=100,  # Maximum number of connections
       max_keepalive_connections=20,  # Maximum keep-alive connections
       headers={"X-Custom-Header": "value"}  # Additional headers
   )

Making Requests
^^^^^^^^^^^^^^^

.. code-block:: python

   with ServiceClient(base_url="https://api.example.com") as client:
       # GET request
       response = client.get("/users/", params={"active": True})

       # POST request
       response = client.post("/users/", data={"name": "Alice"})

       # PUT request
       response = client.put("/users/1/", data={"name": "Alice Updated"})

       # PATCH request
       response = client.patch("/users/1/", data={"email": "new@example.com"})

       # DELETE request
       response = client.delete("/users/1/")

Response Object
^^^^^^^^^^^^^^^

All request methods return a ``Response`` object:

.. code-block:: python

   response = client.get("/users/1/")

   # Access response data
   print(response.status_code)  # HTTP status code
   print(response.data)  # Parsed JSON data (dict or list)
   print(response.headers)  # Response headers

See Also
--------

- :class:`~django_api_orm.async_client.AsyncServiceClient` for async operations
- :doc:`../user-guide/models` for using the client with models
