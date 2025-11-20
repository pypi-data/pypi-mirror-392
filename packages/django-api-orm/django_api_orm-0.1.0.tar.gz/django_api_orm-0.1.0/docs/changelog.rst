Changelog
=========

All notable changes to this project will be documented in this file.

The format is based on `Keep a Changelog <https://keepachangelog.com/en/1.1.0/>`_,
and this project adheres to `Semantic Versioning <https://semver.org/spec/v2.0.0.html>`_.

For the complete changelog, see the `CHANGELOG.md file <https://github.com/mrb101/django-api-orm/blob/main/CHANGELOG.md>`_ in the repository.

Unreleased
----------

See `unreleased changes <https://github.com/mrb101/django-api-orm/blob/main/CHANGELOG.md#unreleased>`_ for planned features.

0.1.0 - Initial Release
-----------------------

Released: 2025-01-XX

Added
^^^^^

- Django ORM-like interface for external REST APIs
- Full synchronous and asynchronous support with httpx
- Pydantic 2.0 integration for data validation and serialization
- Complete QuerySet implementation (filter, exclude, order_by, slicing, etc.)
- Manager implementation with create, get_or_create, update_or_create, bulk_create
- APIModel base class for defining API resources
- Comprehensive exception system mirroring Django's exceptions
- HTTP/2 support for async client
- Connection pooling and automatic retries
- Type-safe with full mypy strict mode compliance
- 91% test coverage with 152 comprehensive tests
- CI/CD with GitHub Actions
- Complete documentation with Sphinx and Read the Docs

See the `complete changelog <https://github.com/mrb101/django-api-orm/blob/main/CHANGELOG.md>`_ for detailed version history.
