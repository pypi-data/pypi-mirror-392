QuerySets
=========

QuerySets provide a Django-like interface for querying and filtering data from REST APIs. They support method chaining, lazy evaluation, and most of the familiar Django QuerySet methods.

Basic Concepts
--------------

Lazy Evaluation
^^^^^^^^^^^^^^^

QuerySets are lazy - they don't execute the API request until you actually need the data:

.. code-block:: python

   # This doesn't hit the API yet
   queryset = User.objects.filter(active=True)

   # This triggers the API request
   for user in queryset:
       print(user.name)

   # These also trigger requests
   users = list(queryset)
   count = queryset.count()
   exists = queryset.exists()

Method Chaining
^^^^^^^^^^^^^^^

QuerySet methods return new QuerySets, allowing you to chain operations:

.. code-block:: python

   queryset = (User.objects
               .filter(active=True)
               .exclude(role="banned")
               .order_by("-created_at")
               .filter(age__gte=18))

Filtering Methods
-----------------

filter()
^^^^^^^^

Filter results based on field values:

.. code-block:: python

   # Single filter
   active_users = User.objects.filter(active=True)

   # Multiple filters (AND logic)
   admin_users = User.objects.filter(active=True, role="admin")

   # Chain filters
   users = User.objects.filter(active=True).filter(role="admin")

exclude()
^^^^^^^^^

Exclude results based on field values:

.. code-block:: python

   # Exclude banned users
   users = User.objects.exclude(status="banned")

   # Combine with filter
   users = User.objects.filter(active=True).exclude(role="guest")

Ordering Methods
----------------

order_by()
^^^^^^^^^^

Order results by one or more fields:

.. code-block:: python

   # Ascending order
   users = User.objects.order_by("name")

   # Descending order (prefix with -)
   users = User.objects.order_by("-created_at")

   # Multiple fields
   users = User.objects.order_by("role", "-name")

Retrieval Methods
-----------------

all()
^^^^^

Get all records (returns a QuerySet):

.. code-block:: python

   all_users = User.objects.all()
   for user in all_users:
       print(user.name)

get()
^^^^^

Get a single record. Raises ``DoesNotExist`` if not found or ``MultipleObjectsReturned`` if multiple records match:

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

Get the first record or ``None`` if no records exist:

.. code-block:: python

   first_user = User.objects.order_by("created_at").first()
   if first_user:
       print(f"First user: {first_user.name}")

last()
^^^^^^

Get the last record or ``None`` if no records exist:

.. code-block:: python

   last_user = User.objects.order_by("created_at").last()
   if last_user:
       print(f"Last user: {last_user.name}")

Slicing and Indexing
--------------------

Slice Notation
^^^^^^^^^^^^^^

Use Python slice notation to limit and offset results:

.. code-block:: python

   # First 10 users
   users = User.objects.all()[:10]

   # Users 10-20 (offset 10, limit 10)
   users = User.objects.all()[10:20]

   # First 5 active users
   users = User.objects.filter(active=True)[:5]

Index Access
^^^^^^^^^^^^

Access a specific record by index:

.. code-block:: python

   # Get the first user (index 0)
   first_user = User.objects.all()[0]

   # Get the tenth user (index 9)
   tenth_user = User.objects.all()[9]

Note: Negative indexing is not supported.

Counting and Existence
----------------------

count()
^^^^^^^

Get the count of records matching the query:

.. code-block:: python

   total_users = User.objects.all().count()
   active_users = User.objects.filter(active=True).count()
   print(f"{active_users} out of {total_users} users are active")

exists()
^^^^^^^^

Check if any records match the query:

.. code-block:: python

   has_admins = User.objects.filter(role="admin").exists()
   if has_admins:
       print("Admin users exist")

Value Extraction
----------------

values()
^^^^^^^^

Get a list of dictionaries with only specified fields:

.. code-block:: python

   # Get specific fields
   user_data = User.objects.all().values("id", "name", "email")
   # [{"id": 1, "name": "Alice", "email": "alice@example.com"}, ...]

   # With filtering
   active_emails = User.objects.filter(active=True).values("email")
   # [{"email": "alice@example.com"}, {"email": "bob@example.com"}, ...]

values_list()
^^^^^^^^^^^^^

Get a list of tuples with only specified fields:

.. code-block:: python

   # Get tuples
   user_pairs = User.objects.all().values_list("id", "name")
   # [(1, "Alice"), (2, "Bob"), (3, "Charlie")]

   # Get flat list of single field
   user_ids = User.objects.all().values_list("id", flat=True)
   # [1, 2, 3, 4, 5]

   user_emails = User.objects.filter(active=True).values_list("email", flat=True)
   # ["alice@example.com", "bob@example.com", "charlie@example.com"]

Iteration
---------

Synchronous Iteration
^^^^^^^^^^^^^^^^^^^^^

QuerySets are iterable:

.. code-block:: python

   for user in User.objects.filter(active=True):
       print(f"{user.name} - {user.email}")

You can also convert to a list:

.. code-block:: python

   users = list(User.objects.all())

Asynchronous Iteration
^^^^^^^^^^^^^^^^^^^^^^^

For async QuerySets, use ``async for``:

.. code-block:: python

   async for user in User.objects.filter(active=True):
       print(f"{user.name} - {user.email}")

See :doc:`async` for more details.

QuerySet Evaluation
-------------------

A QuerySet is evaluated (triggers an API request) when:

1. **Iterating**: ``for user in queryset:``
2. **Converting to list**: ``list(queryset)``
3. **Slicing**: ``queryset[:10]``
4. **Indexing**: ``queryset[0]``
5. **Calling count()**: ``queryset.count()``
6. **Calling exists()**: ``queryset.exists()``
7. **Calling get()**: ``queryset.get(id=1)``
8. **Calling first()**: ``queryset.first()``
9. **Calling last()**: ``queryset.last()``
10. **Calling values()**: ``queryset.values("id", "name")``
11. **Calling values_list()**: ``queryset.values_list("id", flat=True)``

Caching
-------

Once evaluated, QuerySet results are cached:

.. code-block:: python

   queryset = User.objects.filter(active=True)

   # First iteration - hits the API
   for user in queryset:
       print(user.name)

   # Second iteration - uses cached results
   for user in queryset:
       print(user.email)

To force a new API request, create a new QuerySet:

.. code-block:: python

   # New query, will hit the API again
   fresh_queryset = User.objects.filter(active=True)

Complex Queries
---------------

Combining Filters
^^^^^^^^^^^^^^^^^

.. code-block:: python

   # AND logic - all conditions must match
   users = (User.objects
            .filter(active=True)
            .filter(role="admin")
            .exclude(status="banned"))

With Ordering
^^^^^^^^^^^^^

.. code-block:: python

   # Get the 5 most recently created active users
   recent_users = (User.objects
                   .filter(active=True)
                   .order_by("-created_at")
                   [:5])

With Value Extraction
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   # Get emails of all active admins
   admin_emails = (User.objects
                   .filter(active=True, role="admin")
                   .values_list("email", flat=True))

Limitations
-----------

Unlike Django ORM, **django-api-orm** QuerySets have some limitations:

1. **No complex lookups**: No ``__gte``, ``__contains``, etc. (depends on API support)
2. **No joins**: No ``select_related()`` or ``prefetch_related()`` (future feature)
3. **Limited aggregation**: Only ``count()`` is supported
4. **API-dependent filtering**: Filtering depends on what the API supports

These limitations exist because the library works with REST APIs that may have varying capabilities.

Best Practices
--------------

1. **Chain filters**: Use method chaining for readable queries
2. **Be specific**: Filter as much as possible to reduce data transfer
3. **Use slicing**: Limit results when you don't need all records
4. **Cache aware**: Remember that QuerySets cache results after evaluation
5. **Use exists() for checks**: More efficient than ``count() > 0``
6. **Extract values when possible**: Use ``values()`` or ``values_list()`` if you don't need full objects

Examples
--------

Real-world usage patterns:

.. code-block:: python

   # Get the 10 most recent active users
   recent_active = (User.objects
                    .filter(active=True)
                    .order_by("-created_at")
                    [:10])

   # Check if any admins exist
   has_admins = User.objects.filter(role="admin").exists()

   # Get all active user emails
   active_emails = (User.objects
                    .filter(active=True)
                    .values_list("email", flat=True))

   # Count users by status
   active_count = User.objects.filter(active=True).count()
   inactive_count = User.objects.filter(active=False).count()

   # Get first admin or None
   first_admin = User.objects.filter(role="admin").first()

Next Steps
----------

- Learn about :doc:`managers` for creating and managing instances
- See :doc:`models` for working with model instances
- Explore :doc:`async` for async QuerySet usage
