Contributing
============

We welcome contributions to **django-api-orm**! This guide will help you get started.

Getting Started
---------------

Development Setup
^^^^^^^^^^^^^^^^^

1. Fork the repository on GitHub
2. Clone your fork locally:

.. code-block:: bash

   git clone https://github.com/mrb101/django-api-orm.git
   cd django-api-orm

3. Install dependencies using uv:

.. code-block:: bash

   # Install uv if you haven't already
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # Install dependencies
   uv sync --all-extras

4. Install pre-commit hooks:

.. code-block:: bash

   uv run pre-commit install

Running Tests
-------------

Run the test suite:

.. code-block:: bash

   # Run all tests
   uv run pytest

   # Run with coverage
   uv run pytest --cov=src/django_api_orm --cov-report=term-missing

   # Run specific test file
   uv run pytest tests/test_orm_integration.py

   # Run specific test
   uv run pytest tests/test_orm_integration.py::TestQuerySet::test_filter

Code Quality
------------

Type Checking
^^^^^^^^^^^^^

Run mypy for type checking:

.. code-block:: bash

   uv run mypy src/

All code must pass strict type checking with mypy.

Linting
^^^^^^^

Run ruff for linting:

.. code-block:: bash

   # Check for issues
   uv run ruff check src/ tests/

   # Auto-fix issues
   uv run ruff check --fix src/ tests/

Formatting
^^^^^^^^^^

Format code with ruff:

.. code-block:: bash

   uv run ruff format src/ tests/

Pre-commit Hooks
^^^^^^^^^^^^^^^^

Pre-commit hooks will automatically run when you commit:

.. code-block:: bash

   git add .
   git commit -m "Your commit message"

To run manually:

.. code-block:: bash

   uv run pre-commit run --all-files

Making Changes
--------------

Creating a Feature Branch
^^^^^^^^^^^^^^^^^^^^^^^^^

Create a branch for your changes:

.. code-block:: bash

   git checkout -b feature/amazing-feature

Use descriptive branch names:

- ``feature/add-caching`` for new features
- ``fix/timeout-error`` for bug fixes
- ``docs/update-quickstart`` for documentation
- ``refactor/simplify-queryset`` for refactoring

Writing Code
^^^^^^^^^^^^

Follow these guidelines:

1. **Type hints**: All functions must have type hints
2. **Docstrings**: Use Google-style docstrings for all public APIs
3. **Tests**: Add tests for new functionality
4. **Coverage**: Maintain or improve test coverage
5. **Style**: Follow PEP 8 and the existing code style

Example of well-documented code:

.. code-block:: python

   def build_query_params(**kwargs: Any) -> dict[str, str]:
       """Build query parameters dictionary from keyword arguments.

       Converts all values to strings and filters out None values.

       Args:
           **kwargs: Arbitrary keyword arguments to convert to query params.

       Returns:
           Dictionary with string keys and values, None values excluded.

       Example:
           >>> build_query_params(active=True, limit=10, offset=None)
           {'active': 'true', 'limit': '10'}
       """
       return {
           key: str(value).lower() if isinstance(value, bool) else str(value)
           for key, value in kwargs.items()
           if value is not None
       }

Writing Tests
^^^^^^^^^^^^^

Add tests for all new functionality:

.. code-block:: python

   import pytest
   import respx
   import httpx
   from django_api_orm import ServiceClient, APIModel, register_models

   class TestUser:
       """Tests for User model."""

       @respx.mock
       def test_create_user(self) -> None:
           """Test creating a user."""
           # Mock API response
           respx.post("https://api.example.com/api/v1/users/").mock(
               return_value=httpx.Response(
                   201,
                   json={"id": 1, "name": "Alice", "email": "alice@example.com"}
               )
           )

           with ServiceClient(base_url="https://api.example.com") as client:
               register_models(client, User)

               user = User.objects.create(
                   name="Alice",
                   email="alice@example.com"
               )

               assert user.id == 1
               assert user.name == "Alice"
               assert user.email == "alice@example.com"

Committing Changes
^^^^^^^^^^^^^^^^^^

Write clear, descriptive commit messages:

.. code-block:: bash

   git add src/django_api_orm/new_feature.py tests/test_new_feature.py
   git commit -m "Add caching support for QuerySets

   - Implement QuerySet result caching
   - Add cache invalidation on create/update/delete
   - Add tests for cache behavior
   - Update documentation"

Submitting Changes
------------------

Creating a Pull Request
^^^^^^^^^^^^^^^^^^^^^^^

1. Push your branch to GitHub:

.. code-block:: bash

   git push origin feature/amazing-feature

2. Go to the repository on GitHub
3. Click "New Pull Request"
4. Select your branch
5. Fill in the PR template with:

   - Description of changes
   - Related issue numbers
   - Test coverage
   - Breaking changes (if any)

Pull Request Checklist
^^^^^^^^^^^^^^^^^^^^^^

Before submitting, ensure:

- [ ] All tests pass (``uv run pytest``)
- [ ] Type checking passes (``uv run mypy src/``)
- [ ] Linting passes (``uv run ruff check src/ tests/``)
- [ ] Code is formatted (``uv run ruff format src/ tests/``)
- [ ] New tests added for new functionality
- [ ] Documentation updated if needed
- [ ] CHANGELOG.md updated
- [ ] Commit messages are clear and descriptive

Code Review Process
^^^^^^^^^^^^^^^^^^^

1. Maintainers will review your PR
2. Address any feedback or requested changes
3. Once approved, your PR will be merged
4. Your contribution will be included in the next release

Development Guidelines
----------------------

Architecture
^^^^^^^^^^^^

The library is organized into:

- ``client.py``: Synchronous HTTP client
- ``async_client.py``: Asynchronous HTTP client
- ``base.py``: APIModel, QuerySet, Manager (sync)
- ``async_base.py``: AsyncAPIModel, AsyncQuerySet, AsyncManager
- ``exceptions.py``: Exception hierarchy
- ``utils.py``: Helper functions
- ``typing.py``: Type hints and protocols

Design Principles
^^^^^^^^^^^^^^^^^

1. **Django-like API**: Mirror Django ORM patterns where possible
2. **Type safety**: Full type hints and mypy compatibility
3. **Async support**: Complete async/await support
4. **HTTP client agnostic**: Use httpx for both sync and async
5. **Pydantic validation**: Leverage Pydantic for data validation
6. **Test coverage**: Maintain high test coverage (>90%)

Adding New Features
^^^^^^^^^^^^^^^^^^^

When adding new features:

1. **Discuss first**: Open an issue to discuss the feature
2. **Start small**: Implement the minimal viable version
3. **Add tests**: Comprehensive tests for all code paths
4. **Document**: Update documentation and examples
5. **Type safe**: Full type hints and mypy compliance
6. **Backward compatible**: Avoid breaking changes when possible

Reporting Issues
----------------

Bug Reports
^^^^^^^^^^^

When reporting bugs, include:

1. **Description**: Clear description of the bug
2. **Steps to reproduce**: Minimal code example
3. **Expected behavior**: What should happen
4. **Actual behavior**: What actually happens
5. **Environment**:

   - Python version
   - django-api-orm version
   - Operating system

Example:

.. code-block:: markdown

   **Description**
   QuerySet.count() returns incorrect value when filtering

   **Steps to Reproduce**
   ```python
   users = User.objects.filter(active=True)
   count = users.count()  # Returns 5 instead of 3
   ```

   **Expected**: count should be 3
   **Actual**: count is 5

   **Environment**
   - Python 3.12
   - django-api-orm 0.1.0
   - macOS 14

Feature Requests
^^^^^^^^^^^^^^^^

When requesting features, include:

1. **Use case**: Why is this feature needed?
2. **Proposed solution**: How should it work?
3. **Alternatives**: Other approaches considered
4. **Examples**: Code examples showing usage

Questions
^^^^^^^^^

For questions:

1. Check existing documentation
2. Search existing issues
3. Open a discussion on GitHub Discussions

Documentation
-------------

Building Documentation
^^^^^^^^^^^^^^^^^^^^^^

Build the documentation locally:

.. code-block:: bash

   cd docs
   uv run sphinx-build -b html . _build/html

   # Or use make (if available)
   make html

View the docs:

.. code-block:: bash

   open _build/html/index.html  # macOS
   xdg-open _build/html/index.html  # Linux

Documentation Style
^^^^^^^^^^^^^^^^^^^

- Use reStructuredText (.rst) format
- Include code examples for all features
- Keep examples concise and focused
- Use proper Sphinx directives (``.. code-block::``, ``.. autoclass::``, etc.)
- Cross-reference related documentation

Community
---------

Getting Help
^^^^^^^^^^^^

- **Issues**: https://github.com/mrb101/django-api-orm/issues
- **Discussions**: https://github.com/mrb101/django-api-orm/discussions
- **Documentation**: https://django-api-orm.readthedocs.io

Code of Conduct
^^^^^^^^^^^^^^^

Please be respectful and constructive in all interactions. We aim to maintain a welcoming and inclusive community.

License
-------

By contributing, you agree that your contributions will be licensed under the MIT License.

Acknowledgments
---------------

Thank you for contributing to **django-api-orm**! Your contributions help make this project better for everyone.

See Also
--------

- :doc:`changelog` for recent changes
- :doc:`quickstart` to get started using the library
- :doc:`installation` for installation instructions
