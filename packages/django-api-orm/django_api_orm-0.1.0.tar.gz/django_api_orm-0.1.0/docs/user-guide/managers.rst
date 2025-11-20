Managers
========

Managers provide the primary interface for database-table operations in **django-api-orm**. Every model has a ``objects`` manager that provides methods for creating, retrieving, and managing instances.

Accessing Managers
------------------

The default manager is available as ``objects`` on your model:

.. code-block:: python

   # Access the manager
   User.objects

   # Manager is only available after model registration
   from django_api_orm import ServiceClient, register_models

   with ServiceClient(base_url="https://api.example.com") as client:
       register_models(client, User)
       # Now User.objects is available

Manager Methods
---------------

QuerySet Methods
^^^^^^^^^^^^^^^^

All QuerySet methods are available on the manager:

.. code-block:: python

   # These are equivalent
   User.objects.filter(active=True)
   User.objects.all().filter(active=True)

   # Manager methods return QuerySets
   queryset = User.objects.filter(active=True)
   admin_queryset = queryset.filter(role="admin")

See :doc:`querysets` for complete QuerySet documentation.

Creation Methods
----------------

create()
^^^^^^^^

Create and save a new instance:

.. code-block:: python

   user = User.objects.create(
       name="Alice Smith",
       email="alice@example.com",
       active=True
   )

   # Equivalent to:
   user = User(name="Alice Smith", email="alice@example.com", active=True, _client=client)
   user.save()

This method:

1. Validates the data using Pydantic
2. Makes a POST request to the API
3. Returns the created instance with API-assigned fields (like ``id``)

bulk_create()
^^^^^^^^^^^^^

Create multiple instances at once:

.. code-block:: python

   users = User.objects.bulk_create([
       {"name": "Alice", "email": "alice@example.com"},
       {"name": "Bob", "email": "bob@example.com"},
       {"name": "Charlie", "email": "charlie@example.com"}
   ])

   # Returns a list of created instances
   for user in users:
       print(f"Created user {user.id}: {user.name}")

Note: This makes individual POST requests for each instance (no bulk endpoint is assumed).

get_or_create()
^^^^^^^^^^^^^^^

Get an existing instance or create a new one:

.. code-block:: python

   user, created = User.objects.get_or_create(
       email="alice@example.com",
       defaults={"name": "Alice Smith", "role": "user"}
   )

   if created:
       print(f"Created new user: {user.name}")
   else:
       print(f"Found existing user: {user.name}")

The first argument(s) are used for the lookup, and ``defaults`` provides additional fields for creation.

update_or_create()
^^^^^^^^^^^^^^^^^^

Update an existing instance or create a new one:

.. code-block:: python

   user, created = User.objects.update_or_create(
       email="alice@example.com",
       defaults={"name": "Alice Updated", "role": "admin"}
   )

   if created:
       print(f"Created new user: {user.name}")
   else:
       print(f"Updated existing user: {user.name}")

This method:

1. Tries to get an instance matching the lookup fields
2. If found, updates it with the ``defaults`` fields
3. If not found, creates a new instance with all fields

Retrieval Methods
-----------------

all()
^^^^^

Get all instances:

.. code-block:: python

   all_users = User.objects.all()

Returns a QuerySet that can be further filtered:

.. code-block:: python

   active_users = User.objects.all().filter(active=True)

filter()
^^^^^^^^

Filter instances by field values:

.. code-block:: python

   active_users = User.objects.filter(active=True)
   admins = User.objects.filter(role="admin")

   # Multiple filters (AND logic)
   active_admins = User.objects.filter(active=True, role="admin")

exclude()
^^^^^^^^^

Exclude instances by field values:

.. code-block:: python

   non_admins = User.objects.exclude(role="admin")
   active_non_guests = User.objects.filter(active=True).exclude(role="guest")

get()
^^^^^

Get a single instance:

.. code-block:: python

   from django_api_orm.exceptions import DoesNotExist, MultipleObjectsReturned

   try:
       user = User.objects.get(id=1)
   except DoesNotExist:
       print("User not found")
   except MultipleObjectsReturned:
       print("Multiple users found")

first()
^^^^^^^

Get the first instance or None:

.. code-block:: python

   first_user = User.objects.first()
   if first_user:
       print(f"First user: {first_user.name}")

   # With ordering
   newest_user = User.objects.order_by("-created_at").first()

last()
^^^^^^

Get the last instance or None:

.. code-block:: python

   last_user = User.objects.last()
   if last_user:
       print(f"Last user: {last_user.name}")

   # With ordering
   oldest_user = User.objects.order_by("created_at").last()

Utility Methods
---------------

count()
^^^^^^^

Get the count of instances:

.. code-block:: python

   total_users = User.objects.count()
   active_users = User.objects.filter(active=True).count()

   print(f"{active_users} out of {total_users} users are active")

exists()
^^^^^^^^

Check if any instances exist:

.. code-block:: python

   has_users = User.objects.exists()
   has_admins = User.objects.filter(role="admin").exists()

   if not has_admins:
       print("No admin users found!")

Ordering Methods
----------------

order_by()
^^^^^^^^^^

Order instances by one or more fields:

.. code-block:: python

   # Ascending order
   users = User.objects.order_by("name")

   # Descending order
   users = User.objects.order_by("-created_at")

   # Multiple fields
   users = User.objects.order_by("role", "-name")

Async Managers
--------------

Async managers work the same way but require ``await`` for operations that return instances or data:

.. code-block:: python

   from django_api_orm import AsyncAPIModel, AsyncServiceClient, register_async_models

   class User(AsyncAPIModel):
       _schema_class = UserSchema
       _endpoint = "/api/v1/users/"

   async with AsyncServiceClient(base_url="https://api.example.com") as client:
       register_async_models(client, User)

       # Await creation
       user = await User.objects.create(name="Alice", email="alice@example.com")

       # Await retrieval
       user = await User.objects.get(id=1)
       first_user = await User.objects.first()

       # Await get_or_create
       user, created = await User.objects.get_or_create(
           email="alice@example.com",
           defaults={"name": "Alice"}
       )

       # QuerySet methods don't need await until evaluation
       queryset = User.objects.filter(active=True)  # No await
       async for user in queryset:  # Await during iteration
           print(user.name)

       # Await count/exists
       count = await User.objects.count()
       exists = await User.objects.exists()

See :doc:`async` for complete async documentation.

Custom Managers
---------------

You can create custom managers to encapsulate common queries:

.. code-block:: python

   from django_api_orm import Manager, APIModel

   class UserManager(Manager):
       """Custom manager for User model."""

       def active(self):
           """Get only active users."""
           return self.filter(active=True)

       def admins(self):
           """Get only admin users."""
           return self.filter(role="admin")

       def active_admins(self):
           """Get active admin users."""
           return self.active().admins()

   class User(APIModel):
       _schema_class = UserSchema
       _endpoint = "/api/v1/users/"

       # Override the default manager
       objects = UserManager()

   # Usage
   active_users = User.objects.active()
   admins = User.objects.admins()
   active_admins = User.objects.active_admins()

Best Practices
--------------

1. **Use create() over manual instantiation**: More concise and handles client injection
2. **Use get_or_create() for idempotency**: Prevents duplicate creation
3. **Use exists() instead of count() > 0**: More efficient for existence checks
4. **Chain filters for readability**: ``User.objects.filter(active=True).filter(role="admin")``
5. **Use custom managers for common queries**: Encapsulate business logic
6. **Remember async/await**: Don't forget to await async manager methods

Common Patterns
---------------

Pagination
^^^^^^^^^^

.. code-block:: python

   page_size = 20
   page = 1

   # Get page 1 (offset 0, limit 20)
   users = User.objects.all()[(page - 1) * page_size:page * page_size]

Conditional Creation
^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   # Only create if doesn't exist
   if not User.objects.filter(email="alice@example.com").exists():
       User.objects.create(name="Alice", email="alice@example.com")

   # Or use get_or_create
   user, created = User.objects.get_or_create(
       email="alice@example.com",
       defaults={"name": "Alice"}
   )

Batch Processing
^^^^^^^^^^^^^^^^

.. code-block:: python

   # Create multiple users
   users_data = [
       {"name": "Alice", "email": "alice@example.com"},
       {"name": "Bob", "email": "bob@example.com"},
       {"name": "Charlie", "email": "charlie@example.com"}
   ]
   users = User.objects.bulk_create(users_data)

   # Process in batches
   batch_size = 100
   offset = 0
   while True:
       batch = User.objects.all()[offset:offset + batch_size]
       if not batch:
           break
       for user in batch:
           # Process user
           pass
       offset += batch_size

Finding or Creating Defaults
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   # Find admin or create a default one
   admin, created = User.objects.get_or_create(
       role="admin",
       defaults={
           "name": "Default Admin",
           "email": "admin@example.com",
           "active": True
       }
   )

Examples
--------

.. code-block:: python

   # Create a user
   user = User.objects.create(
       name="Alice Smith",
       email="alice@example.com",
       role="admin"
   )

   # Get or create pattern
   user, created = User.objects.get_or_create(
       email="bob@example.com",
       defaults={"name": "Bob Jones", "role": "user"}
   )

   # Update or create pattern
   user, created = User.objects.update_or_create(
       email="charlie@example.com",
       defaults={"name": "Charlie Brown", "role": "user", "active": True}
   )

   # Bulk creation
   users = User.objects.bulk_create([
       {"name": f"User {i}", "email": f"user{i}@example.com"}
       for i in range(10)
   ])

   # Common queries via manager
   active_count = User.objects.filter(active=True).count()
   has_admins = User.objects.filter(role="admin").exists()
   newest_user = User.objects.order_by("-created_at").first()

Next Steps
----------

- Learn about :doc:`querysets` for advanced querying
- See :doc:`models` for working with instances
- Explore :doc:`async` for async manager usage
