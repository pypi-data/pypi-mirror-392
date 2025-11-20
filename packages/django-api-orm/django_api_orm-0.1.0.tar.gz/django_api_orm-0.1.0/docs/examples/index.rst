Examples
========

This section provides practical examples of using **django-api-orm** in various scenarios.

Basic CRUD Operations
---------------------

Complete example of Create, Read, Update, Delete operations:

.. code-block:: python

   from pydantic import BaseModel, EmailStr
   from django_api_orm import APIModel, ServiceClient, register_models

   # Define schema
   class UserSchema(BaseModel):
       id: int | None = None
       name: str
       email: EmailStr
       active: bool = True
       role: str = "user"

   # Define model
   class User(APIModel):
       _schema_class = UserSchema
       _endpoint = "/api/v1/users/"

   # Use the model
   with ServiceClient(
       base_url="https://api.example.com",
       auth_token="your-token-here"
   ) as client:
       register_models(client, User)

       # CREATE
       user = User.objects.create(
           name="Alice Smith",
           email="alice@example.com",
           role="admin"
       )
       print(f"Created user {user.id}: {user.name}")

       # READ
       user = User.objects.get(id=user.id)
       print(f"Retrieved user: {user.name}")

       # List all users
       all_users = list(User.objects.all())
       print(f"Total users: {len(all_users)}")

       # Filter users
       active_users = list(User.objects.filter(active=True))
       print(f"Active users: {len(active_users)}")

       # UPDATE
       user.email = "alice.updated@example.com"
       user.save(update_fields=["email"])
       print(f"Updated user email: {user.email}")

       # DELETE
       user.delete()
       print("User deleted")

Async CRUD Operations
---------------------

Async version with concurrent operations:

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
           http2=True
       ) as client:
           register_async_models(client, User)

           # CREATE - concurrent creation
           users = await asyncio.gather(
               User.objects.create(name="Alice", email="alice@example.com"),
               User.objects.create(name="Bob", email="bob@example.com"),
               User.objects.create(name="Charlie", email="charlie@example.com")
           )
           print(f"Created {len(users)} users concurrently")

           # READ - concurrent retrieval
           retrieved_users = await asyncio.gather(
               User.objects.get(id=users[0].id),
               User.objects.get(id=users[1].id),
               User.objects.get(id=users[2].id)
           )
           print(f"Retrieved {len(retrieved_users)} users concurrently")

           # UPDATE - concurrent updates
           for user in users:
               user.active = True
           await asyncio.gather(*[user.save() for user in users])
           print("Updated all users concurrently")

           # DELETE - concurrent deletion
           await asyncio.gather(*[user.delete() for user in users])
           print("Deleted all users concurrently")

   asyncio.run(main())

Pagination
----------

Paginating through large result sets:

.. code-block:: python

   def paginate_users(page_size=20):
       """Paginate through all users."""
       page = 1
       while True:
           offset = (page - 1) * page_size
           users = list(User.objects.all()[offset:offset + page_size])

           if not users:
               break

           print(f"\nPage {page}:")
           for user in users:
               print(f"  {user.id}: {user.name}")

           page += 1

   # Usage
   with ServiceClient(base_url="https://api.example.com") as client:
       register_models(client, User)
       paginate_users(page_size=10)

Search and Filter
-----------------

Advanced filtering and search:

.. code-block:: python

   with ServiceClient(base_url="https://api.example.com") as client:
       register_models(client, User)

       # Find active admin users
       active_admins = User.objects.filter(active=True, role="admin")

       # Exclude banned users
       valid_users = User.objects.exclude(status="banned")

       # Combine filters
       users = (User.objects
                .filter(active=True)
                .exclude(role="guest")
                .order_by("-created_at"))

       # Get count
       admin_count = User.objects.filter(role="admin").count()
       print(f"Total admins: {admin_count}")

       # Check existence
       has_admins = User.objects.filter(role="admin").exists()
       if has_admins:
           print("Admin users exist")

       # Get first/last
       newest_user = User.objects.order_by("-created_at").first()
       oldest_user = User.objects.order_by("created_at").first()

Batch Operations
----------------

Processing records in batches:

.. code-block:: python

   # Synchronous batch processing
   def process_users_in_batches(batch_size=100):
       """Process users in batches."""
       offset = 0

       while True:
           batch = list(User.objects.all()[offset:offset + batch_size])

           if not batch:
               break

           # Process batch
           for user in batch:
               # Do something with user
               print(f"Processing {user.name}")

           offset += batch_size

   # Async batch processing with concurrency
   async def process_users_async(batch_size=100, concurrent=10):
       """Process users in batches with concurrency."""
       offset = 0

       while True:
           batch = []
           async for user in User.objects.all()[offset:offset + batch_size]:
               batch.append(user)

           if not batch:
               break

           # Process batch concurrently
           await asyncio.gather(*[process_user(user) for user in batch])

           offset += batch_size

   async def process_user(user):
       """Process a single user."""
       # Do something async with user
       await asyncio.sleep(0.1)

Error Handling
--------------

Comprehensive error handling:

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

   def safe_get_user(user_id):
       """Safely get a user with comprehensive error handling."""
       try:
           return User.objects.get(id=user_id)

       except DoesNotExist:
           logger.warning(f"User {user_id} not found")
           return None

       except UnauthorizedError:
           logger.error("Authentication failed - please log in")
           raise

       except ForbiddenError:
           logger.error(f"Access denied to user {user_id}")
           raise

       except TooManyRequestsError as e:
           logger.warning(f"Rate limited. Retry after {e.retry_after}s")
           raise

       except APIServerError as e:
           logger.error(f"Server error: {e.status_code}")
           return None

       except APITimeoutError:
           logger.error(f"Request timed out for user {user_id}")
           return None

       except APIConnectionError as e:
           logger.error(f"Connection failed: {e.message}")
           return None

Custom Managers
---------------

Creating custom managers for common queries:

.. code-block:: python

   from django_api_orm import Manager, APIModel

   class UserManager(Manager):
       """Custom manager with convenience methods."""

       def active(self):
           """Get active users."""
           return self.filter(active=True)

       def inactive(self):
           """Get inactive users."""
           return self.filter(active=False)

       def admins(self):
           """Get admin users."""
           return self.filter(role="admin")

       def users(self):
           """Get regular users."""
           return self.filter(role="user")

       def active_admins(self):
           """Get active admin users."""
           return self.active().admins()

       def create_admin(self, **kwargs):
           """Create an admin user."""
           kwargs["role"] = "admin"
           return self.create(**kwargs)

   class User(APIModel):
       _schema_class = UserSchema
       _endpoint = "/api/v1/users/"
       objects = UserManager()

   # Usage
   with ServiceClient(base_url="https://api.example.com") as client:
       register_models(client, User)

       # Use custom manager methods
       active_users = User.objects.active()
       admins = User.objects.admins()
       active_admins = User.objects.active_admins()

       # Create admin
       admin = User.objects.create_admin(
           name="Admin User",
           email="admin@example.com"
       )

Multiple Related Models
-----------------------

Working with multiple related models:

.. code-block:: python

   from pydantic import BaseModel

   # Define schemas
   class UserSchema(BaseModel):
       id: int | None = None
       name: str
       email: str

   class PostSchema(BaseModel):
       id: int | None = None
       user_id: int
       title: str
       content: str
       published: bool = False

   class CommentSchema(BaseModel):
       id: int | None = None
       post_id: int
       user_id: int
       text: str

   # Define models
   class User(APIModel):
       _schema_class = UserSchema
       _endpoint = "/api/v1/users/"

   class Post(APIModel):
       _schema_class = PostSchema
       _endpoint = "/api/v1/posts/"

   class Comment(APIModel):
       _schema_class = CommentSchema
       _endpoint = "/api/v1/comments/"

   # Usage
   with ServiceClient(base_url="https://api.example.com") as client:
       register_models(client, User, Post, Comment)

       # Create user
       user = User.objects.create(name="Alice", email="alice@example.com")

       # Create posts for user
       post1 = Post.objects.create(
           user_id=user.id,
           title="First Post",
           content="Hello World",
           published=True
       )

       post2 = Post.objects.create(
           user_id=user.id,
           title="Second Post",
           content="More content",
           published=False
       )

       # Create comments
       comment = Comment.objects.create(
           post_id=post1.id,
           user_id=user.id,
           text="Great post!"
       )

       # Query related data
       user_posts = Post.objects.filter(user_id=user.id)
       published_posts = Post.objects.filter(user_id=user.id, published=True)
       post_comments = Comment.objects.filter(post_id=post1.id)

Testing with Mock APIs
----------------------

Testing your code with mock APIs using respx:

.. code-block:: python

   import respx
   import httpx
   from django_api_orm import ServiceClient, APIModel, register_models

   @respx.mock
   def test_user_creation():
       """Test creating a user."""
       # Mock the API response
       respx.post("https://api.example.com/api/v1/users/").mock(
           return_value=httpx.Response(
               201,
               json={"id": 1, "name": "Alice", "email": "alice@example.com"}
           )
       )

       with ServiceClient(base_url="https://api.example.com") as client:
           register_models(client, User)

           user = User.objects.create(name="Alice", email="alice@example.com")

           assert user.id == 1
           assert user.name == "Alice"
           assert user.email == "alice@example.com"

FastAPI Integration
-------------------

Integrating with FastAPI:

.. code-block:: python

   from fastapi import FastAPI, Depends, HTTPException
   from django_api_orm import AsyncServiceClient, AsyncAPIModel, register_async_models

   app = FastAPI()

   class User(AsyncAPIModel):
       _schema_class = UserSchema
       _endpoint = "/api/v1/users/"

   async def get_client():
       """Dependency to provide async client."""
       async with AsyncServiceClient(
           base_url="https://api.example.com",
           auth_token="your-token-here"
       ) as client:
           register_async_models(client, User)
           yield client

   @app.get("/users/{user_id}")
   async def get_user(user_id: int, client = Depends(get_client)):
       """Get a user by ID."""
       try:
           user = await User.objects.get(id=user_id)
           return user.to_dict()
       except User.DoesNotExist:
           raise HTTPException(status_code=404, detail="User not found")

   @app.get("/users/")
   async def list_users(active: bool = True, client = Depends(get_client)):
       """List users."""
       users = []
       async for user in User.objects.filter(active=active):
           users.append(user.to_dict())
       return users

   @app.post("/users/")
   async def create_user(
       name: str,
       email: str,
       client = Depends(get_client)
   ):
       """Create a user."""
       user = await User.objects.create(name=name, email=email)
       return user.to_dict()

See Also
--------

- :doc:`../quickstart` for basic usage
- :doc:`../user-guide/models` for model documentation
- :doc:`../user-guide/async` for async patterns
