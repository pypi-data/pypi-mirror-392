Utilities
=========

Utility functions and helpers.

.. currentmodule:: django_api_orm.utils

Query Parameters
----------------

.. autofunction:: build_query_params

Example Usage
^^^^^^^^^^^^^

.. code-block:: python

   from django_api_orm.utils import build_query_params

   # Build query parameters
   params = build_query_params(
       active=True,
       role="admin",
       limit=10,
       offset=0
   )
   # {"active": "true", "role": "admin", "limit": "10", "offset": "0"}

   # None values are excluded
   params = build_query_params(
       active=True,
       role=None,
       limit=10
   )
   # {"active": "true", "limit": "10"}

Dictionary Operations
---------------------

.. autofunction:: merge_dicts

Example Usage
^^^^^^^^^^^^^

.. code-block:: python

   from django_api_orm.utils import merge_dicts

   # Merge multiple dictionaries
   dict1 = {"a": 1, "b": 2}
   dict2 = {"b": 3, "c": 4}
   dict3 = {"c": 5, "d": 6}

   merged = merge_dicts(dict1, dict2, dict3)
   # {"a": 1, "b": 3, "c": 5, "d": 6}

   # Later values override earlier ones
   merged = merge_dicts({"a": 1}, {"a": 2}, {"a": 3})
   # {"a": 3}

List Operations
---------------

.. autofunction:: chunk_list

Example Usage
^^^^^^^^^^^^^

.. code-block:: python

   from django_api_orm.utils import chunk_list

   # Chunk a list into smaller lists
   items = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
   chunks = chunk_list(items, chunk_size=3)
   # [[1, 2, 3], [4, 5, 6], [7, 8, 9], [10]]

   # Process in batches
   for batch in chunk_list(user_ids, chunk_size=100):
       # Process batch of up to 100 user IDs
       pass

See Also
--------

- Source code in ``src/django_api_orm/utils.py``
