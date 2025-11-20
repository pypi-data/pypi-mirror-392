Installation
============

Requirements
------------

**django-api-orm** requires Python 3.10 or higher. It has the following core dependencies:

- `pydantic <https://docs.pydantic.dev/>`_ >= 2.0.0 for data validation and serialization
- `httpx <https://www.python-httpx.org/>`_ >= 0.27.0 for HTTP client functionality

Basic Installation
------------------

Install using pip:

.. code-block:: bash

   pip install django-api-orm

Or using `uv <https://github.com/astral-sh/uv>`_ (recommended):

.. code-block:: bash

   uv add django-api-orm

With Async and HTTP/2 Support
------------------------------

For async support with HTTP/2 capabilities:

.. code-block:: bash

   pip install django-api-orm[async]

Or with uv:

.. code-block:: bash

   uv add "django-api-orm[async]"

Development Installation
------------------------

To install with development dependencies (for contributing):

.. code-block:: bash

   pip install django-api-orm[dev]

Or with uv:

.. code-block:: bash

   uv add "django-api-orm[dev]"

This includes:

- pytest and pytest plugins for testing
- mypy for type checking
- ruff for linting and formatting
- coverage tools

Installing from Source
----------------------

To install from the GitHub repository:

.. code-block:: bash

   git clone https://github.com/mrb101/django-api-orm.git
   cd django-api-orm
   pip install -e .

Or with uv:

.. code-block:: bash

   git clone https://github.com/mrb101/django-api-orm.git
   cd django-api-orm
   uv sync

Verifying Installation
----------------------

You can verify the installation by importing the package:

.. code-block:: python

   import django_api_orm
   print(django_api_orm.__version__)

Or check that the main classes are available:

.. code-block:: python

   from django_api_orm import (
       APIModel,
       AsyncAPIModel,
       ServiceClient,
       AsyncServiceClient,
       register_models,
       register_async_models,
   )

Next Steps
----------

Once installed, proceed to the :doc:`quickstart` guide to learn how to use **django-api-orm**.
