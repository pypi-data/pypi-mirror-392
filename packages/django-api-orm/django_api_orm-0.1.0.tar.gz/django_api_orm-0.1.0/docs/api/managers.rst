Managers
========

Manager classes provide the interface for creating and managing model instances.

Synchronous Managers
--------------------

.. currentmodule:: django_api_orm.base

.. autoclass:: Manager
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__

Example Usage
^^^^^^^^^^^^^

.. code-block:: python

   from django_api_orm import APIModel

   class User(APIModel):
       _schema_class = UserSchema
       _endpoint = "/api/v1/users/"

   # Access manager
   manager = User.objects

   # Create instance
   user = User.objects.create(name="Alice", email="alice@example.com")

   # Get instance
   user = User.objects.get(id=1)

   # Filter instances
   active_users = User.objects.filter(active=True)

   # Get or create
   user, created = User.objects.get_or_create(
       email="alice@example.com",
       defaults={"name": "Alice"}
   )

   # Update or create
   user, created = User.objects.update_or_create(
       email="alice@example.com",
       defaults={"name": "Alice Updated"}
   )

   # Bulk create
   users = User.objects.bulk_create([
       {"name": "Bob", "email": "bob@example.com"},
       {"name": "Charlie", "email": "charlie@example.com"}
   ])

Asynchronous Managers
---------------------

.. currentmodule:: django_api_orm.async_base

.. autoclass:: AsyncManager
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__

Example Usage
^^^^^^^^^^^^^

.. code-block:: python

   from django_api_orm import AsyncAPIModel

   class User(AsyncAPIModel):
       _schema_class = UserSchema
       _endpoint = "/api/v1/users/"

   # Access manager
   manager = User.objects

   # Create instance (await needed)
   user = await User.objects.create(name="Alice", email="alice@example.com")

   # Get instance (await needed)
   user = await User.objects.get(id=1)

   # Filter instances (no await needed for QuerySet)
   active_users = User.objects.filter(active=True)

   # Get or create (await needed)
   user, created = await User.objects.get_or_create(
       email="alice@example.com",
       defaults={"name": "Alice"}
   )

   # Update or create (await needed)
   user, created = await User.objects.update_or_create(
       email="alice@example.com",
       defaults={"name": "Alice Updated"}
   )

   # Bulk create (await needed)
   users = await User.objects.bulk_create([
       {"name": "Bob", "email": "bob@example.com"},
       {"name": "Charlie", "email": "charlie@example.com"}
   ])

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

   class User(APIModel):
       _schema_class = UserSchema
       _endpoint = "/api/v1/users/"
       objects = UserManager()

   # Usage
   active_users = User.objects.active()
   admins = User.objects.admins()

See Also
--------

- :doc:`../user-guide/managers` for detailed manager documentation
- :doc:`querysets` for querying data
- :doc:`models` for working with instances
