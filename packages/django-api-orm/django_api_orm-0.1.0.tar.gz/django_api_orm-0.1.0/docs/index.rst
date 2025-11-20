django-api-orm Documentation
=============================

.. image:: https://github.com/mrb101/django-api-orm/workflows/Tests/badge.svg
   :target: https://github.com/mrb101/django-api-orm/actions
   :alt: Tests

.. image:: https://codecov.io/gh/tigerlab/django-api-orm/branch/main/graph/badge.svg
   :target: https://codecov.io/gh/tigerlab/django-api-orm
   :alt: Coverage

.. image:: https://img.shields.io/badge/python-3.10%2B-blue.svg
   :target: https://www.python.org/downloads/
   :alt: Python Version

.. image:: https://img.shields.io/badge/license-MIT-green.svg
   :target: https://github.com/mrb101/django-api-orm/blob/main/LICENSE
   :alt: License

A Django ORM-like interface for external REST APIs with Pydantic validation and httpx.

**django-api-orm** provides a familiar Django ORM interface for interacting with REST APIs,
making it easy to work with external services using the same patterns you already know.

Key Features
------------

* **Sync and Async Support** - Use synchronous or asynchronous clients based on your needs
* **Type Safety** - Full type hints and Pydantic validation throughout
* **Django-like API** - Familiar ``filter()``, ``exclude()``, ``get()``, ``first()``, ``last()``, etc.
* **HTTP/2 Support** - Optional HTTP/2 for better performance (async only)
* **Connection Pooling** - Built-in connection pooling with httpx
* **Lazy Evaluation** - QuerySets only execute when needed
* **Full CRUD** - Complete create, read, update, delete operations
* **91% Test Coverage** - 152 comprehensive tests

Quick Example
-------------

.. code-block:: python

   from pydantic import BaseModel
   from django_api_orm import APIModel, ServiceClient, register_models

   # Define your schema
   class UserSchema(BaseModel):
       id: int | None = None
       name: str
       email: str
       active: bool = True

   # Define your model
   class User(APIModel):
       _schema_class = UserSchema
       _endpoint = "/api/v1/users/"

   # Use it!
   with ServiceClient(base_url="https://api.example.com") as client:
       register_models(client, User)

       # Django-like queries
       users = User.objects.filter(active=True)
       for user in users:
           print(f"{user.name} - {user.email}")

       # CRUD operations
       user = User.objects.get(id=1)
       user.email = "newemail@example.com"
       user.save()

Documentation Contents
----------------------

.. toctree::
   :maxdepth: 2
   :caption: Getting Started

   installation
   quickstart
   examples/index

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   user-guide/models
   user-guide/querysets
   user-guide/managers
   user-guide/async
   user-guide/exceptions

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api/client
   api/async_client
   api/models
   api/querysets
   api/managers
   api/exceptions
   api/utils

.. toctree::
   :maxdepth: 1
   :caption: Development

   contributing
   changelog

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
