Models
======

Models in **django-api-orm** are the primary way to interact with REST API resources. They provide a Django ORM-like interface for working with external APIs.

Defining Models
---------------

Basic Model Definition
^^^^^^^^^^^^^^^^^^^^^^

A model requires a Pydantic schema class and an API endpoint:

.. code-block:: python

   from pydantic import BaseModel
   from django_api_orm import APIModel

   class UserSchema(BaseModel):
       id: int | None = None
       name: str
       email: str
       active: bool = True

   class User(APIModel):
       _schema_class = UserSchema
       _endpoint = "/api/v1/users/"

Required Attributes
^^^^^^^^^^^^^^^^^^^

Every model must define:

- ``_schema_class``: A Pydantic BaseModel subclass that defines the data structure
- ``_endpoint``: The API endpoint path (relative to the base URL)

Optional Attributes
^^^^^^^^^^^^^^^^^^^

You can also define:

- ``_id_field``: The name of the ID field (default: ``"id"``)
- Custom methods and properties

Model Registration
------------------

Before using a model, you must register it with a client:

.. code-block:: python

   from django_api_orm import ServiceClient, register_models

   with ServiceClient(base_url="https://api.example.com") as client:
       register_models(client, User)

       # Now User.objects is available

Multiple Model Registration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can register multiple models at once:

.. code-block:: python

   register_models(client, User, Post, Comment)

Model Instances
---------------

Creating Instances
^^^^^^^^^^^^^^^^^^

There are several ways to create model instances:

.. code-block:: python

   # Using Manager.create()
   user = User.objects.create(name="Alice", email="alice@example.com")

   # Using the constructor and save()
   user = User(name="Alice", email="alice@example.com", _client=client)
   user.save()

   # Using Manager.get_or_create()
   user, created = User.objects.get_or_create(
       email="alice@example.com",
       defaults={"name": "Alice"}
   )

Accessing Attributes
^^^^^^^^^^^^^^^^^^^^^

Model instances behave like Pydantic models:

.. code-block:: python

   user = User.objects.get(id=1)

   # Access attributes
   print(user.name)
   print(user.email)

   # Set attributes
   user.name = "Alice Updated"
   user.email = "alice.updated@example.com"

Instance Methods
----------------

save()
^^^^^^

Save the instance to the API:

.. code-block:: python

   user = User.objects.get(id=1)
   user.name = "New Name"
   user.save()

Partial updates are supported:

.. code-block:: python

   user.email = "newemail@example.com"
   user.save(update_fields=["email"])

delete()
^^^^^^^^

Delete the instance from the API:

.. code-block:: python

   user = User.objects.get(id=1)
   user.delete()

refresh_from_api()
^^^^^^^^^^^^^^^^^^

Refresh the instance with the latest data from the API:

.. code-block:: python

   user = User.objects.get(id=1)
   # ... some time passes ...
   user.refresh_from_api()  # Get latest data

to_dict()
^^^^^^^^^

Convert the instance to a dictionary:

.. code-block:: python

   user = User.objects.get(id=1)
   data = user.to_dict()
   # {"id": 1, "name": "Alice", "email": "alice@example.com", "active": True}

   # Exclude unset fields
   data = user.to_dict(exclude_unset=True)

Class Methods
-------------

from_api()
^^^^^^^^^^

Create an instance from API response data:

.. code-block:: python

   data = {"id": 1, "name": "Alice", "email": "alice@example.com"}
   user = User.from_api(data, client=client)

get_schema_class()
^^^^^^^^^^^^^^^^^^

Get the Pydantic schema class:

.. code-block:: python

   schema_class = User.get_schema_class()
   # Returns UserSchema

Model Validation
----------------

All data is validated using Pydantic before being sent to the API:

.. code-block:: python

   from pydantic import EmailStr, Field

   class UserSchema(BaseModel):
       id: int | None = None
       name: str = Field(..., min_length=1, max_length=100)
       email: EmailStr
       age: int = Field(..., ge=0, le=150)

   class User(APIModel):
       _schema_class = UserSchema
       _endpoint = "/api/v1/users/"

   # This will raise a validation error
   try:
       user = User.objects.create(name="", email="invalid", age=200)
   except ValidationError as e:
       print(e)

Async Models
------------

For async operations, use ``AsyncAPIModel``:

.. code-block:: python

   from django_api_orm import AsyncAPIModel, AsyncServiceClient, register_async_models

   class User(AsyncAPIModel):
       _schema_class = UserSchema
       _endpoint = "/api/v1/users/"

   async with AsyncServiceClient(base_url="https://api.example.com") as client:
       register_async_models(client, User)

       # Await async operations
       user = await User.objects.create(name="Alice", email="alice@example.com")
       await user.save()
       await user.delete()

See :doc:`async` for more details on async usage.

Custom Model Behavior
---------------------

You can add custom methods and properties to your models:

.. code-block:: python

   class User(APIModel):
       _schema_class = UserSchema
       _endpoint = "/api/v1/users/"

       def is_admin(self) -> bool:
           """Check if user is an admin."""
           return self.role == "admin"

       @property
       def full_name(self) -> str:
           """Get user's full name."""
           return f"{self.first_name} {self.last_name}"

       def deactivate(self) -> None:
           """Deactivate this user."""
           self.active = False
           self.save(update_fields=["active"])

   # Usage
   user = User.objects.get(id=1)
   if user.is_admin():
       print(f"Admin: {user.full_name}")
   user.deactivate()

Best Practices
--------------

1. **Use descriptive schema names**: ``UserSchema``, ``PostSchema``, etc.
2. **Define optional fields correctly**: Use ``field: type | None = None`` for optional fields
3. **Use update_fields for partial updates**: More efficient and prevents overwriting unchanged data
4. **Handle validation errors**: Always wrap create/save operations in try/except blocks
5. **Refresh when needed**: Use ``refresh_from_api()`` when data might be stale
6. **Custom methods for business logic**: Keep API interaction logic in the model

Next Steps
----------

- Learn about :doc:`querysets` for querying data
- Explore :doc:`managers` for creating and managing instances
- See :doc:`exceptions` for error handling
