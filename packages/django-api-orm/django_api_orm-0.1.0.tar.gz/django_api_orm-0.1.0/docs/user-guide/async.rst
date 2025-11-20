Async Support
=============

**django-api-orm** provides full async/await support for modern asynchronous Python applications. The async API mirrors the synchronous API, making it easy to switch between the two.

Why Async?
----------

Async operations are beneficial when:

1. **Making many API calls**: Concurrent requests improve performance
2. **Building async applications**: Integration with FastAPI, aiohttp, etc.
3. **Handling I/O-bound operations**: Better resource utilization
4. **HTTP/2 support**: Multiplexing multiple requests over a single connection

Async vs Sync
-------------

**Synchronous** (blocking):

.. code-block:: python

   from django_api_orm import APIModel, ServiceClient

   class User(APIModel):
       _schema_class = UserSchema
       _endpoint = "/api/v1/users/"

   with ServiceClient(base_url="https://api.example.com") as client:
       register_models(client, User)
       user = User.objects.get(id=1)  # Blocks until complete

**Asynchronous** (non-blocking):

.. code-block:: python

   from django_api_orm import AsyncAPIModel, AsyncServiceClient

   class User(AsyncAPIModel):
       _schema_class = UserSchema
       _endpoint = "/api/v1/users/"

   async with AsyncServiceClient(base_url="https://api.example.com") as client:
       register_async_models(client, User)
       user = await User.objects.get(id=1)  # Non-blocking, awaitable

Async Client
------------

The ``AsyncServiceClient`` provides async HTTP operations using httpx:

.. code-block:: python

   from django_api_orm import AsyncServiceClient

   async with AsyncServiceClient(
       base_url="https://api.example.com",
       auth_token="your-token-here",
       timeout=30.0,
       http2=True,  # Enable HTTP/2
       max_connections=100,
       max_keepalive_connections=20
   ) as client:
       # Use the client

HTTP/2 Support
^^^^^^^^^^^^^^

Enable HTTP/2 for better performance:

.. code-block:: python

   async with AsyncServiceClient(
       base_url="https://api.example.com",
       http2=True  # Requires httpx[http2]
   ) as client:
       # HTTP/2 provides:
       # - Request/response multiplexing
       # - Header compression
       # - Server push
       # - Better performance for multiple requests

Async Models
------------

Define async models using ``AsyncAPIModel``:

.. code-block:: python

   from pydantic import BaseModel
   from django_api_orm import AsyncAPIModel

   class UserSchema(BaseModel):
       id: int | None = None
       name: str
       email: str

   class User(AsyncAPIModel):
       _schema_class = UserSchema
       _endpoint = "/api/v1/users/"

   class Post(AsyncAPIModel):
       _schema_class = PostSchema
       _endpoint = "/api/v1/posts/"

Model Registration
^^^^^^^^^^^^^^^^^^

Register async models with an async client:

.. code-block:: python

   from django_api_orm import register_async_models

   async with AsyncServiceClient(base_url="https://api.example.com") as client:
       register_async_models(client, User, Post)

Async Operations
----------------

Creating Instances
^^^^^^^^^^^^^^^^^^

.. code-block:: python

   # await create()
   user = await User.objects.create(
       name="Alice Smith",
       email="alice@example.com"
   )

   # await get_or_create()
   user, created = await User.objects.get_or_create(
       email="alice@example.com",
       defaults={"name": "Alice Smith"}
   )

   # await update_or_create()
   user, created = await User.objects.update_or_create(
       email="alice@example.com",
       defaults={"name": "Alice Updated"}
   )

   # await bulk_create()
   users = await User.objects.bulk_create([
       {"name": "Bob", "email": "bob@example.com"},
       {"name": "Charlie", "email": "charlie@example.com"}
   ])

Retrieving Instances
^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   # await get()
   user = await User.objects.get(id=1)

   # await first()
   first_user = await User.objects.first()

   # await last()
   last_user = await User.objects.last()

   # await count()
   user_count = await User.objects.count()

   # await exists()
   has_users = await User.objects.exists()

Updating Instances
^^^^^^^^^^^^^^^^^^

.. code-block:: python

   user = await User.objects.get(id=1)
   user.name = "New Name"
   await user.save()

   # Partial update
   user.email = "newemail@example.com"
   await user.save(update_fields=["email"])

Deleting Instances
^^^^^^^^^^^^^^^^^^

.. code-block:: python

   user = await User.objects.get(id=1)
   await user.delete()

Refreshing Instances
^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   user = await User.objects.get(id=1)
   # ... some time passes ...
   await user.refresh_from_api()

Async QuerySets
---------------

Async Iteration
^^^^^^^^^^^^^^^

Use ``async for`` to iterate over QuerySets:

.. code-block:: python

   # Async iteration
   async for user in User.objects.filter(active=True):
       print(f"{user.name} - {user.email}")

   # Process all users
   async for user in User.objects.all():
       await process_user(user)

Converting to List
^^^^^^^^^^^^^^^^^^

.. code-block:: python

   # Await to get list
   users = await User.objects.filter(active=True)._fetch()

   # Or iterate to build list
   users = []
   async for user in User.objects.all():
       users.append(user)

   # Or use list comprehension (not async)
   users = [user async for user in User.objects.all()]

Value Extraction
^^^^^^^^^^^^^^^^

.. code-block:: python

   # await values()
   user_data = await User.objects.all().values("id", "name")

   # await values_list()
   user_ids = await User.objects.all().values_list("id", flat=True)

Concurrent Operations
---------------------

Using asyncio.gather()
^^^^^^^^^^^^^^^^^^^^^^

Run multiple operations concurrently:

.. code-block:: python

   import asyncio

   # Fetch multiple users concurrently
   user1, user2, user3 = await asyncio.gather(
       User.objects.get(id=1),
       User.objects.get(id=2),
       User.objects.get(id=3)
   )

   # Get counts from multiple models
   user_count, post_count, comment_count = await asyncio.gather(
       User.objects.count(),
       Post.objects.count(),
       Comment.objects.count()
   )

   # Create multiple instances concurrently
   users = await asyncio.gather(
       User.objects.create(name="Alice", email="alice@example.com"),
       User.objects.create(name="Bob", email="bob@example.com"),
       User.objects.create(name="Charlie", email="charlie@example.com")
   )

Using asyncio.create_task()
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Create tasks for background execution:

.. code-block:: python

   # Create tasks
   task1 = asyncio.create_task(User.objects.get(id=1))
   task2 = asyncio.create_task(Post.objects.filter(published=True).count())

   # Do other work...

   # Wait for tasks to complete
   user = await task1
   post_count = await task2

Batch Processing
^^^^^^^^^^^^^^^^

Process records in batches concurrently:

.. code-block:: python

   async def process_user(user):
       """Process a single user."""
       # Do something with the user
       await asyncio.sleep(0.1)  # Simulate work

   # Get users in batches
   batch_size = 10
   offset = 0

   while True:
       users = []
       async for user in User.objects.all()[offset:offset + batch_size]:
           users.append(user)

       if not users:
           break

       # Process batch concurrently
       await asyncio.gather(*[process_user(user) for user in users])

       offset += batch_size

Error Handling
--------------

Exception handling works the same as sync:

.. code-block:: python

   from django_api_orm.exceptions import DoesNotExist, MultipleObjectsReturned

   try:
       user = await User.objects.get(email="nonexistent@example.com")
   except DoesNotExist:
       print("User not found")

   try:
       user = await User.objects.get(role="admin")
   except MultipleObjectsReturned:
       print("Multiple admins found")

Complete Example
----------------

.. code-block:: python

   import asyncio
   from pydantic import BaseModel
   from django_api_orm import AsyncAPIModel, AsyncServiceClient, register_async_models

   class UserSchema(BaseModel):
       id: int | None = None
       name: str
       email: str
       active: bool = True

   class User(AsyncAPIModel):
       _schema_class = UserSchema
       _endpoint = "/api/v1/users/"

   async def main():
       async with AsyncServiceClient(
           base_url="https://api.example.com",
           auth_token="your-token-here",
           http2=True
       ) as client:
           register_async_models(client, User)

           # Create users concurrently
           users = await asyncio.gather(
               User.objects.create(name="Alice", email="alice@example.com"),
               User.objects.create(name="Bob", email="bob@example.com"),
               User.objects.create(name="Charlie", email="charlie@example.com")
           )
           print(f"Created {len(users)} users")

           # Query users
           print("\nActive users:")
           async for user in User.objects.filter(active=True):
               print(f"  {user.name} - {user.email}")

           # Get counts concurrently
           total, active = await asyncio.gather(
               User.objects.count(),
               User.objects.filter(active=True).count()
           )
           print(f"\nTotal users: {total}, Active: {active}")

           # Update user
           user = await User.objects.get(id=users[0].id)
           user.email = "alice.updated@example.com"
           await user.save(update_fields=["email"])
           print(f"\nUpdated {user.name}'s email")

           # Delete user
           await user.delete()
           print(f"Deleted {user.name}")

   if __name__ == "__main__":
       asyncio.run(main())

Integration Examples
--------------------

FastAPI Integration
^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from fastapi import FastAPI, Depends
   from django_api_orm import AsyncServiceClient, register_async_models

   app = FastAPI()

   async def get_client():
       """Dependency to provide async client."""
       async with AsyncServiceClient(
           base_url="https://api.example.com",
           auth_token="your-token-here"
       ) as client:
           register_async_models(client, User)
           yield client

   @app.get("/users/{user_id}")
   async def get_user(user_id: int, client: AsyncServiceClient = Depends(get_client)):
       user = await User.objects.get(id=user_id)
       return user.to_dict()

   @app.get("/users/")
   async def list_users(active: bool = True):
       users = []
       async for user in User.objects.filter(active=active):
           users.append(user.to_dict())
       return users

aiohttp Integration
^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from aiohttp import web
   from django_api_orm import AsyncServiceClient, register_async_models

   async def handle_get_user(request):
       user_id = int(request.match_info['user_id'])
       client = request.app['client']

       user = await User.objects.get(id=user_id)
       return web.json_response(user.to_dict())

   async def on_startup(app):
       app['client'] = AsyncServiceClient(base_url="https://api.example.com")
       await app['client'].__aenter__()
       register_async_models(app['client'], User)

   async def on_cleanup(app):
       await app['client'].__aexit__(None, None, None)

   app = web.Application()
   app.router.add_get('/users/{user_id}', handle_get_user)
   app.on_startup.append(on_startup)
   app.on_cleanup.append(on_cleanup)

   web.run_app(app)

Best Practices
--------------

1. **Use HTTP/2 when possible**: Better performance for multiple requests
2. **Batch operations with asyncio.gather()**: Maximize concurrency
3. **Don't forget await**: All async operations must be awaited
4. **Use async for for iteration**: Proper async iteration over QuerySets
5. **Handle exceptions properly**: Same exception types as sync
6. **Close clients properly**: Use ``async with`` for proper cleanup
7. **Configure connection limits**: Set appropriate max_connections for your use case
8. **Use tasks for background work**: Create tasks with asyncio.create_task()

Performance Tips
----------------

1. **Concurrent requests**: Use asyncio.gather() for independent operations
2. **Connection pooling**: Async client maintains a connection pool
3. **HTTP/2 multiplexing**: Multiple requests over single connection
4. **Batch processing**: Process records in batches with concurrent operations
5. **Limit concurrency**: Don't overwhelm the API with too many concurrent requests

Common Pitfalls
---------------

1. **Forgetting await**: ``user = User.objects.get(id=1)`` won't work (need ``await``)
2. **Using sync in async**: Don't use ``APIModel`` in async code (use ``AsyncAPIModel``)
3. **Not using async for**: Regular ``for`` won't work with async iterators
4. **Not closing client**: Always use ``async with`` or manually close
5. **Too much concurrency**: Respect API rate limits

Next Steps
----------

- See :doc:`models` for model details
- Learn about :doc:`querysets` for querying
- Explore :doc:`managers` for creation and management
- Check :doc:`exceptions` for error handling
