Exceptions
==========

Exception classes for error handling.

.. currentmodule:: django_api_orm.exceptions

Base Exception
--------------

.. autoclass:: APIException
   :members:
   :undoc-members:
   :show-inheritance:

Validation Exceptions
---------------------

.. autoclass:: ValidationException
   :members:
   :undoc-members:
   :show-inheritance:

Query Exceptions
----------------

.. autoclass:: DoesNotExist
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: MultipleObjectsReturned
   :members:
   :undoc-members:
   :show-inheritance:

HTTP Exceptions
---------------

.. autoclass:: HTTPStatusError
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: AuthenticationError
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: RateLimitError
   :members:
   :undoc-members:
   :show-inheritance:

Connection Exceptions
---------------------

.. autoclass:: ConnectionError
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: TimeoutError
   :members:
   :undoc-members:
   :show-inheritance:

Exception Hierarchy
-------------------

.. code-block:: text

   APIException
   ├── ValidationException
   ├── DoesNotExist
   ├── MultipleObjectsReturned
   ├── ConnectionError
   ├── TimeoutError
   ├── AuthenticationError
   ├── RateLimitError
   └── HTTPStatusError

Example Usage
-------------

Basic Exception Handling
^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from django_api_orm.exceptions import DoesNotExist, MultipleObjectsReturned

   try:
       user = User.objects.get(id=1)
   except DoesNotExist:
       print("User not found")
   except MultipleObjectsReturned:
       print("Multiple users found")

HTTP Error Handling
^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from django_api_orm.exceptions import (
       AuthenticationError,
       RateLimitError,
       HTTPStatusError
   )

   try:
       user = User.objects.get(id=1)
   except AuthenticationError:
       print("Please log in")
   except RateLimitError:
       print("Rate limit exceeded")
   except HTTPStatusError as e:
       print(f"HTTP error: {e}")

Connection Error Handling
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from django_api_orm.exceptions import ConnectionError, TimeoutError

   try:
       user = User.objects.get(id=1)
   except ConnectionError:
       print("Failed to connect to API")
   except TimeoutError:
       print("Request timed out")

Generic Error Handling
^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from django_api_orm.exceptions import APIException

   try:
       user = User.objects.get(id=1)
   except APIException as e:
       print(f"API error: {e}")

See Also
--------

- :doc:`../user-guide/exceptions` for detailed exception handling documentation
