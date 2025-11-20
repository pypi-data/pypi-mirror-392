QuerySets
=========

QuerySet classes provide the interface for querying and filtering data.

Synchronous QuerySets
---------------------

.. currentmodule:: django_api_orm.base

.. autoclass:: QuerySet
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__, __iter__, __getitem__

Example Usage
^^^^^^^^^^^^^

.. code-block:: python

   from django_api_orm import APIModel

   class User(APIModel):
       _schema_class = UserSchema
       _endpoint = "/api/v1/users/"

   # Get QuerySet via manager
   queryset = User.objects.all()

   # Filter
   active_users = User.objects.filter(active=True)

   # Chain filters
   admin_users = User.objects.filter(active=True).filter(role="admin")

   # Order
   ordered_users = User.objects.order_by("-created_at")

   # Slice
   first_ten = User.objects.all()[:10]

   # Iterate
   for user in User.objects.filter(active=True):
       print(user.name)

Asynchronous QuerySets
----------------------

.. currentmodule:: django_api_orm.async_base

.. autoclass:: AsyncQuerySet
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__, __aiter__, __getitem__

Example Usage
^^^^^^^^^^^^^

.. code-block:: python

   from django_api_orm import AsyncAPIModel

   class User(AsyncAPIModel):
       _schema_class = UserSchema
       _endpoint = "/api/v1/users/"

   # Get QuerySet via manager
   queryset = User.objects.all()

   # Filter (returns QuerySet, no await needed)
   active_users = User.objects.filter(active=True)

   # Chain filters
   admin_users = User.objects.filter(active=True).filter(role="admin")

   # Order
   ordered_users = User.objects.order_by("-created_at")

   # Slice
   first_ten = User.objects.all()[:10]

   # Iterate (await needed)
   async for user in User.objects.filter(active=True):
       print(user.name)

   # Get single (await needed)
   user = await User.objects.get(id=1)

   # Count (await needed)
   count = await User.objects.count()

See Also
--------

- :doc:`../user-guide/querysets` for detailed QuerySet documentation
- :doc:`managers` for creating QuerySets
- :doc:`models` for working with results
