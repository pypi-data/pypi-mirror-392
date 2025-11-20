Quick Start
===========

This guide will walk you through the basics of using **django-api-orm** to interact with REST APIs using a Django ORM-like interface.

Define Your Schema
------------------

First, define your data schema using Pydantic:

.. code-block:: python

   from pydantic import BaseModel

   class UserSchema(BaseModel):
       id: int | None = None  # Optional for creation
       name: str
       email: str
       active: bool = True
       role: str = "user"

Define Your Model
-----------------

Create an API model that uses your schema:

.. code-block:: python

   from django_api_orm import APIModel

   class User(APIModel):
       _schema_class = UserSchema
       _endpoint = "/api/v1/users/"

Synchronous Usage
-----------------

Create a Client
^^^^^^^^^^^^^^^

Create a service client and register your models:

.. code-block:: python

   from django_api_orm import ServiceClient, register_models

   with ServiceClient(
       base_url="https://api.example.com",
       auth_token="your-token-here"
   ) as client:
       register_models(client, User)

       # Your API calls go here

Query Data
^^^^^^^^^^

Use familiar Django ORM methods to query data:

.. code-block:: python

   # Get all users
   all_users = User.objects.all()
   for user in all_users:
       print(f"{user.name} - {user.email}")

   # Filter users
   active_users = User.objects.filter(active=True)
   admin_users = User.objects.filter(role="admin")

   # Chain filters
   active_admins = User.objects.filter(active=True).filter(role="admin")

   # Exclude users
   non_admins = User.objects.exclude(role="admin")

   # Get a single user
   user = User.objects.get(id=1)

   # Get first or last
   first_user = User.objects.first()
   last_user = User.objects.last()

   # Check existence
   has_users = User.objects.exists()

   # Count users
   user_count = User.objects.count()

Create Data
^^^^^^^^^^^

Create new records:

.. code-block:: python

   # Create a single user
   new_user = User.objects.create(
       name="Alice Smith",
       email="alice@example.com",
       role="admin"
   )

   # Create multiple users at once
   users = User.objects.bulk_create([
       {"name": "Bob Jones", "email": "bob@example.com"},
       {"name": "Charlie Brown", "email": "charlie@example.com"}
   ])

   # Get or create
   user, created = User.objects.get_or_create(
       email="alice@example.com",
       defaults={"name": "Alice Smith", "role": "admin"}
   )

Update Data
^^^^^^^^^^^

Update existing records:

.. code-block:: python

   # Update specific fields
   user = User.objects.get(id=1)
   user.email = "newemail@example.com"
   user.save(update_fields=["email"])

   # Update all fields
   user.name = "Alice Johnson"
   user.email = "alice.johnson@example.com"
   user.save()

   # Update or create
   user, created = User.objects.update_or_create(
       email="alice@example.com",
       defaults={"name": "Alice Updated", "role": "admin"}
   )

Delete Data
^^^^^^^^^^^

Delete records:

.. code-block:: python

   user = User.objects.get(id=1)
   user.delete()

Asynchronous Usage
------------------

For async operations, use the async versions of the classes:

.. code-block:: python

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
           results = await asyncio.gather(
               User.objects.filter(active=True).count(),
               User.objects.filter(role="admin").count()
           )
           active_count, admin_count = results

   asyncio.run(main())

Advanced Queries
----------------

Order Results
^^^^^^^^^^^^^

.. code-block:: python

   # Order by a single field
   users = User.objects.order_by("name")

   # Order by multiple fields
   users = User.objects.order_by("role", "-created_at")

   # Descending order
   users = User.objects.order_by("-email")

Slice Results
^^^^^^^^^^^^^

.. code-block:: python

   # Get first 10 users
   users = User.objects.all()[:10]

   # Get users 10-20
   users = User.objects.all()[10:20]

   # Get a specific user by index
   user = User.objects.all()[0]

Extract Values
^^^^^^^^^^^^^^

.. code-block:: python

   # Get list of dictionaries
   user_data = User.objects.all().values("id", "name", "email")
   # [{"id": 1, "name": "Alice", "email": "alice@example.com"}, ...]

   # Get flat list of values
   user_ids = User.objects.all().values_list("id", flat=True)
   # [1, 2, 3, 4, 5]

   # Get list of tuples
   user_pairs = User.objects.all().values_list("id", "name")
   # [(1, "Alice"), (2, "Bob"), ...]

Error Handling
--------------

The library provides Django-like exceptions:

.. code-block:: python

   from django_api_orm.exceptions import DoesNotExist, MultipleObjectsReturned

   try:
       user = User.objects.get(email="nonexistent@example.com")
   except DoesNotExist:
       print("User not found")

   try:
       user = User.objects.get(role="admin")  # Multiple admins exist
   except MultipleObjectsReturned:
       print("Multiple users found")

See :doc:`user-guide/exceptions` for more details on exception handling.

Next Steps
----------

- Learn more about :doc:`user-guide/models`
- Explore :doc:`user-guide/querysets` in depth
- Understand :doc:`user-guide/managers`
- Master :doc:`user-guide/async` patterns
- Check out :doc:`examples/index` for more use cases
