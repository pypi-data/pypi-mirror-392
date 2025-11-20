Models
======

Model classes provide the interface for working with API resources.

Synchronous Models
------------------

.. currentmodule:: django_api_orm.base

.. autoclass:: APIModel
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__

Model Registration
^^^^^^^^^^^^^^^^^^

.. autofunction:: django_api_orm.register_models

Example Usage
^^^^^^^^^^^^^

.. code-block:: python

   from pydantic import BaseModel
   from django_api_orm import APIModel, ServiceClient, register_models

   class UserSchema(BaseModel):
       id: int | None = None
       name: str
       email: str

   class User(APIModel):
       _schema_class = UserSchema
       _endpoint = "/api/v1/users/"

   with ServiceClient(base_url="https://api.example.com") as client:
       register_models(client, User)

       # Create instance
       user = User.objects.create(name="Alice", email="alice@example.com")

       # Save instance
       user.name = "Alice Updated"
       user.save()

       # Delete instance
       user.delete()

Asynchronous Models
-------------------

.. currentmodule:: django_api_orm.async_base

.. autoclass:: AsyncAPIModel
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__

Model Registration
^^^^^^^^^^^^^^^^^^

.. autofunction:: django_api_orm.register_async_models

Example Usage
^^^^^^^^^^^^^

.. code-block:: python

   from django_api_orm import AsyncAPIModel, AsyncServiceClient, register_async_models

   class User(AsyncAPIModel):
       _schema_class = UserSchema
       _endpoint = "/api/v1/users/"

   async with AsyncServiceClient(base_url="https://api.example.com") as client:
       register_async_models(client, User)

       # Create instance
       user = await User.objects.create(name="Alice", email="alice@example.com")

       # Save instance
       user.name = "Alice Updated"
       await user.save()

       # Delete instance
       await user.delete()

See Also
--------

- :doc:`../user-guide/models` for detailed model documentation
- :doc:`querysets` for querying data
- :doc:`managers` for creating and managing instances
