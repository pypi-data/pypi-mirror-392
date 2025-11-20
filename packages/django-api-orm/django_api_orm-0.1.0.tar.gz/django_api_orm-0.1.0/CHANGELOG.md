# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Nested Pydantic schema support** - Full support for nested Pydantic models with dot notation access
- **FastAPI test server** - Comprehensive test server in `examples/` folder for development and testing
- **Insurance domain example** - Complete insurance domain implementation with PolicyHolder, Policy, and Claim models
- **Test scripts** - Comprehensive sync and async test scripts demonstrating all features
- **Manager delegation methods** - Added `values()` and `values_list()` methods to Manager classes for convenience
- **AsyncQuerySet slicing** - Added `__getitem__` support for slicing async querysets
- **Documentation** - Added extensive documentation for nested schemas and insurance domain examples

### Fixed
- **Nested schema preservation** - Fixed bug where nested Pydantic models were being converted to dictionaries
- **Attribute syncing** - Implemented custom `__setattr__` to sync attribute changes with internal Pydantic instance
- **JSON serialization** - Added `mode='json'` to `model_dump()` calls for proper date serialization
- **Manager methods** - Fixed missing `values()` and `values_list()` delegation methods on Manager classes

### Planned
- Advanced caching layer
- Streaming support for large responses
- Related field support (select_related, prefetch_related)
- Query optimization and request batching
- GraphQL support
- Additional authentication methods
- Rate limiting helpers
- Response pagination helpers
- Video tutorials
- Performance benchmarks

## [0.1.0] - 2025-01-XX

### Added
- Django ORM-like interface for external REST APIs
- Full synchronous and asynchronous support
- `ServiceClient` for synchronous HTTP requests with httpx
- `AsyncServiceClient` for asynchronous HTTP requests with httpx
- HTTP/2 support for async client
- Connection pooling and automatic retries
- Type-safe Pydantic 2.0 validation throughout
- `QuerySet` class with lazy evaluation for synchronous operations
- `AsyncQuerySet` class with async iteration support
- `Manager` class for model querying and creation (synchronous)
- `AsyncManager` class with async methods
- `APIModel` base class with CRUD operations (synchronous)
- `AsyncAPIModel` base class with async CRUD operations
- Model registration functions: `register_models()` and `register_async_models()`
- Query methods: `filter()`, `exclude()`, `all()`, `order_by()`, `get()`, `first()`, `last()`, `exists()`, `count()`
- Value extraction methods: `values()`, `values_list()`
- QuerySet slicing support with `__getitem__`
- Manager creation methods: `create()`, `bulk_create()`, `get_or_create()`, `update_or_create()`
- Model instance methods: `save()`, `delete()`, `refresh_from_api()`, `to_dict()`
- Partial update support with `save(update_fields=[])`
- Async iteration support with `async for` loops
- Concurrent operations support with `asyncio.gather()`
- Exception hierarchy: `APIException`, `ValidationException`, `DoesNotExist`, `MultipleObjectsReturned`, `ConnectionError`, `TimeoutError`, `AuthenticationError`, `RateLimitError`, `HTTPStatusError`
- Comprehensive test suite with 152 tests
- 91% test coverage
- Full type safety with mypy strict mode
- CI/CD pipeline with GitHub Actions (Python 3.10, 3.11, 3.12)
- Pre-commit hooks configuration
- Ruff linting and formatting
- Complete documentation with examples
- Sync and async usage examples in `examples/` directory
- `py.typed` marker for PEP 561 compliance
- Development tools configuration (pytest, mypy, ruff, black)

### Changed
- N/A (initial release)

### Deprecated
- N/A (initial release)

### Removed
- N/A (initial release)

### Fixed
- N/A (initial release)

### Security
- N/A (initial release)

---

[unreleased]: https://github.com/mrb101/django-api-orm/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/mrb101/django-api-orm/releases/tag/v0.1.0
