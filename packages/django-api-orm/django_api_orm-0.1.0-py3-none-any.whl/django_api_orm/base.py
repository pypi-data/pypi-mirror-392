"""Synchronous base classes for APIModel, QuerySet, and Manager."""

from collections.abc import Iterator
from typing import Any, Generic, TypeVar, Union

from pydantic import BaseModel

from .client import ServiceClient
from .exceptions import DoesNotExist, MultipleObjectsReturned

T = TypeVar("T", bound="APIModel")


class QuerySet(Generic[T]):
    """Django-like QuerySet for filtering and retrieving API resources.

    Provides lazy evaluation with result caching and chainable filter methods.

    Example:
        >>> queryset = Policy.objects.filter(status='active')
        >>> queryset = queryset.order_by('-created_at')
        >>> for policy in queryset:  # Executes query here
        ...     print(policy.policy_number)
    """

    def __init__(self, model_class: type[T], manager: "Manager[T]") -> None:
        """Initialize QuerySet.

        Args:
            model_class: The model class this QuerySet represents
            manager: The manager that created this QuerySet
        """
        self.model_class = model_class
        self.manager = manager

        # Query parameters
        self._filters: dict[str, Any] = {}
        self._excludes: dict[str, Any] = {}
        self._order_by_fields: list[str] = []
        self._limit: int | None = None
        self._offset: int | None = None

        # Result caching
        self._result_cache: list[T] | None = None
        self._fetched = False

    def _clone(self) -> "QuerySet[T]":
        """Create a copy of this QuerySet for chaining.

        Returns:
            A new QuerySet with the same parameters
        """
        qs = QuerySet(self.model_class, self.manager)
        qs._filters = self._filters.copy()
        qs._excludes = self._excludes.copy()
        qs._order_by_fields = self._order_by_fields.copy()
        qs._limit = self._limit
        qs._offset = self._offset
        return qs

    def _build_params(self) -> dict[str, Any]:
        """Build query parameters for the API request.

        Returns:
            Dictionary of query parameters
        """
        params: dict[str, Any] = {}

        # Add filters
        params.update(self._filters)

        # Add excludes (if API supports it)
        for key, value in self._excludes.items():
            params[f"exclude_{key}"] = value

        # Add ordering
        if self._order_by_fields:
            params["ordering"] = ",".join(self._order_by_fields)

        # Add pagination
        if self._limit is not None:
            params["limit"] = self._limit
        if self._offset is not None:
            params["offset"] = self._offset

        return params

    def _fetch(self) -> None:
        """Execute the query and cache results."""
        if self._fetched:
            return

        params = self._build_params()
        response = self.manager.client.get(self.manager.get_endpoint(), params=params)

        # Parse response data
        data = response.data

        # Handle paginated responses (Django REST framework style)
        if isinstance(data, dict) and "results" in data:
            results = data["results"]
        elif isinstance(data, list):
            results = data
        else:
            results = [data]

        # Convert to model instances
        self._result_cache = [
            self.model_class.from_api(item, client=self.manager.client)  # type: ignore[misc]
            for item in results
        ]
        self._fetched = True

    # Filtering methods

    def filter(self, **kwargs: Any) -> "QuerySet[T]":
        """Filter QuerySet by given parameters.

        Args:
            **kwargs: Field lookups (e.g., status='active', id=123)

        Returns:
            New QuerySet with filters applied

        Example:
            >>> Policy.objects.filter(status='active', premium_amount__gte=1000)
        """
        qs = self._clone()
        qs._filters.update(kwargs)
        return qs

    def exclude(self, **kwargs: Any) -> "QuerySet[T]":
        """Exclude results matching given parameters.

        Args:
            **kwargs: Field lookups to exclude

        Returns:
            New QuerySet with exclusions applied

        Example:
            >>> Policy.objects.exclude(status='cancelled')
        """
        qs = self._clone()
        qs._excludes.update(kwargs)
        return qs

    def all(self) -> "QuerySet[T]":
        """Return a copy of this QuerySet.

        Returns:
            New QuerySet (clone)
        """
        return self._clone()

    # Ordering methods

    def order_by(self, *fields: str) -> "QuerySet[T]":
        """Order results by given fields.

        Args:
            *fields: Field names (prefix with '-' for descending)

        Returns:
            New QuerySet with ordering applied

        Example:
            >>> Policy.objects.order_by('-created_at', 'policy_number')
        """
        qs = self._clone()
        qs._order_by_fields = list(fields)
        return qs

    # Slicing and limiting methods

    def first(self) -> T | None:
        """Get the first result or None.

        Returns:
            First model instance or None

        Example:
            >>> policy = Policy.objects.filter(status='active').first()
        """
        qs = self._clone()
        qs._limit = 1
        qs._fetch()
        return qs._result_cache[0] if qs._result_cache else None

    def last(self) -> T | None:
        """Get the last result or None.

        Returns:
            Last model instance or None
        """
        qs = self._clone()
        # If ordering specified, reverse it and get first
        if qs._order_by_fields:
            qs._order_by_fields = [
                f[1:] if f.startswith("-") else f"-{f}" for f in qs._order_by_fields
            ]
            qs._limit = 1
        # If no ordering, need to fetch all and get last
        qs._fetch()
        return qs._result_cache[-1] if qs._result_cache else None

    def __getitem__(self, key: int | slice) -> Union[T, "QuerySet[T]"]:
        """Support slicing and indexing.

        Args:
            key: Integer index or slice

        Returns:
            Model instance (for int) or QuerySet (for slice)

        Example:
            >>> policies = Policy.objects.all()
            >>> first = policies[0]  # Get first
            >>> subset = policies[10:20]  # Get slice
        """
        if isinstance(key, int):
            # Get single item by index
            qs = self._clone()
            qs._offset = key
            qs._limit = 1
            qs._fetch()
            if not qs._result_cache:
                raise IndexError("QuerySet index out of range")
            return qs._result_cache[0]

        elif isinstance(key, slice):
            # Get slice
            qs = self._clone()
            if key.start is not None:
                qs._offset = key.start
            if key.stop is not None:
                if key.start is not None:
                    qs._limit = key.stop - key.start
                else:
                    qs._limit = key.stop
            return qs

        else:
            raise TypeError("QuerySet indices must be integers or slices")

    # Retrieval methods

    def get(self, **kwargs: Any) -> T:
        """Get a single object matching the criteria.

        Args:
            **kwargs: Field lookups

        Returns:
            Single model instance

        Raises:
            DoesNotExist: If no results found
            MultipleObjectsReturned: If multiple results found

        Example:
            >>> policy = Policy.objects.get(id=123)
        """
        qs = self.filter(**kwargs)
        qs._limit = 2  # Fetch 2 to detect multiple
        qs._fetch()

        if not qs._result_cache:
            raise DoesNotExist(f"{self.model_class.__name__} matching query does not exist")

        if len(qs._result_cache) > 1:
            raise MultipleObjectsReturned(
                f"get() returned more than one {self.model_class.__name__}"
            )

        return qs._result_cache[0]

    def exists(self) -> bool:
        """Check if any results exist.

        Returns:
            True if results exist, False otherwise

        Example:
            >>> if Policy.objects.filter(status='active').exists():
            ...     print("Active policies found")
        """
        qs = self._clone()
        qs._limit = 1
        qs._fetch()
        return bool(qs._result_cache)

    def count(self) -> int:
        """Get count of results.

        Returns:
            Number of results

        Example:
            >>> count = Policy.objects.filter(status='active').count()
        """
        # Try to get count from API without fetching all results
        params = self._build_params()
        params["count_only"] = "true"

        try:
            response = self.manager.client.get(self.manager.get_endpoint(), params=params)
            # Try to get count from response
            if isinstance(response.data, dict):
                if "count" in response.data:
                    return int(response.data["count"])
                elif "total" in response.data:
                    return int(response.data["total"])
        except Exception:
            pass

        # Fallback: fetch and count
        self._fetch()
        return len(self._result_cache) if self._result_cache else 0

    # Iteration support

    def __iter__(self) -> Iterator[T]:
        """Make QuerySet iterable.

        Returns:
            Iterator over model instances

        Example:
            >>> for policy in Policy.objects.filter(status='active'):
            ...     print(policy.policy_number)
        """
        self._fetch()
        return iter(self._result_cache or [])

    def __len__(self) -> int:
        """Get length of results.

        Returns:
            Number of cached results
        """
        self._fetch()
        return len(self._result_cache) if self._result_cache else 0

    # Value extraction methods

    def values(self, *fields: str) -> list[dict[str, Any]]:
        """Return list of dictionaries instead of model instances.

        Args:
            *fields: Field names to include (all if not specified)

        Returns:
            List of dictionaries

        Example:
            >>> policies = Policy.objects.values('id', 'policy_number')
            >>> # [{'id': 1, 'policy_number': 'POL-001'}, ...]
        """
        self._fetch()
        if not self._result_cache:
            return []

        results = []
        for obj in self._result_cache:
            data = obj.to_dict()
            if fields:
                data = {k: v for k, v in data.items() if k in fields}
            results.append(data)

        return results

    def values_list(self, *fields: str, flat: bool = False) -> list[Any]:
        """Return list of tuples instead of model instances.

        Args:
            *fields: Field names to include
            flat: If True and one field, return flat list

        Returns:
            List of tuples (or flat list if flat=True)

        Example:
            >>> ids = Policy.objects.values_list('id', flat=True)
            >>> # [1, 2, 3, ...]
            >>> pairs = Policy.objects.values_list('id', 'policy_number')
            >>> # [(1, 'POL-001'), (2, 'POL-002'), ...]
        """
        self._fetch()
        if not self._result_cache:
            return []

        if flat and len(fields) != 1:
            raise ValueError("'flat' is only valid when one field is specified")

        results = []
        for obj in self._result_cache:
            data = obj.to_dict()
            if flat:
                results.append(data.get(fields[0]))
            else:
                values = tuple(data.get(field) for field in fields)
                results.append(values)

        return results

    def __repr__(self) -> str:
        """String representation of QuerySet."""
        if self._result_cache is not None:
            return f"<QuerySet {list(self._result_cache)}>"
        return f"<QuerySet for {self.model_class.__name__}>"


class Manager(Generic[T]):
    """Django-like Manager for model querying.

    Handles creation and retrieval of model instances.

    Example:
        >>> class Policy(APIModel):
        ...     objects = Manager()
        >>> policies = Policy.objects.filter(status='active')
    """

    def __init__(self, model_class: type[T], client: ServiceClient) -> None:
        """Initialize Manager.

        Args:
            model_class: The model class this manager handles
            client: HTTP client for API requests
        """
        self.model_class = model_class
        self.client = client

    def get_endpoint(self) -> str:
        """Get the API endpoint for this model.

        Returns:
            API endpoint path
        """
        return self.model_class.get_endpoint()

    # Query methods (delegate to QuerySet)

    def all(self) -> QuerySet[T]:
        """Get all objects.

        Returns:
            QuerySet of all objects

        Example:
            >>> all_policies = Policy.objects.all()
        """
        return QuerySet(self.model_class, self)

    def filter(self, **kwargs: Any) -> QuerySet[T]:
        """Filter objects by criteria.

        Args:
            **kwargs: Filter parameters

        Returns:
            Filtered QuerySet

        Example:
            >>> active_policies = Policy.objects.filter(status='active')
        """
        return self.all().filter(**kwargs)

    def exclude(self, **kwargs: Any) -> QuerySet[T]:
        """Exclude objects matching criteria.

        Args:
            **kwargs: Exclusion parameters

        Returns:
            Filtered QuerySet
        """
        return self.all().exclude(**kwargs)

    def get(self, **kwargs: Any) -> T:
        """Get a single object.

        Args:
            **kwargs: Lookup parameters

        Returns:
            Single model instance

        Raises:
            DoesNotExist: If not found
            MultipleObjectsReturned: If multiple found

        Example:
            >>> policy = Policy.objects.get(id=123)
        """
        return self.all().get(**kwargs)

    def order_by(self, *fields: str) -> QuerySet[T]:
        """Order results by given fields.

        Args:
            *fields: Field names to order by (prefix with '-' for descending)

        Returns:
            Ordered QuerySet

        Example:
            >>> policies = Policy.objects.order_by('-created_at')
        """
        return self.all().order_by(*fields)

    def first(self) -> T | None:
        """Get the first object or None.

        Returns:
            First model instance or None

        Example:
            >>> policy = Policy.objects.first()
        """
        return self.all().first()

    def last(self) -> T | None:
        """Get the last object or None.

        Returns:
            Last model instance or None

        Example:
            >>> policy = Policy.objects.last()
        """
        return self.all().last()

    def exists(self) -> bool:
        """Check if any objects exist.

        Returns:
            True if results exist, False otherwise

        Example:
            >>> has_policies = Policy.objects.filter(status='active').exists()
        """
        return self.all().exists()

    def values(self, *fields: str) -> list[dict[str, Any]]:
        """Return list of dictionaries instead of model instances.

        Args:
            *fields: Field names to include (all if not specified)

        Returns:
            List of dictionaries

        Example:
            >>> policies = Policy.objects.values('id', 'policy_number')
        """
        return self.all().values(*fields)

    def values_list(self, *fields: str, flat: bool = False) -> list[Any]:
        """Return list of tuples instead of model instances.

        Args:
            *fields: Field names to include
            flat: If True and one field, return flat list

        Returns:
            List of tuples (or flat list if flat=True)

        Example:
            >>> ids = Policy.objects.values_list('id', flat=True)
        """
        return self.all().values_list(*fields, flat=flat)

    def count(self) -> int:
        """Count the number of objects.

        Returns:
            Number of objects

        Example:
            >>> total = Policy.objects.count()
        """
        return self.all().count()

    # Creation methods

    def create(self, **kwargs: Any) -> T:
        """Create a new object in the API.

        Args:
            **kwargs: Field values

        Returns:
            Created model instance

        Example:
            >>> policy = Policy.objects.create(
            ...     policy_number='POL-001',
            ...     premium_amount=1500.00
            ... )
        """
        # Validate with Pydantic schema
        schema_class = self.model_class.get_schema_class()
        validated_data = schema_class(**kwargs)
        data = validated_data.model_dump(mode="json", exclude_unset=True)

        # Make API request
        response = self.client.post(self.get_endpoint(), data=data)

        # Return model instance
        return self.model_class.from_api(response.data, client=self.client)  # type: ignore[return-value]

    def get_or_create(
        self, defaults: dict[str, Any] | None = None, **kwargs: Any
    ) -> tuple[T, bool]:
        """Get an existing object or create a new one.

        Args:
            defaults: Values to use when creating
            **kwargs: Lookup parameters

        Returns:
            Tuple of (object, created) where created is a boolean

        Example:
            >>> policy, created = Policy.objects.get_or_create(
            ...     policy_number='POL-001',
            ...     defaults={'premium_amount': 1500.00}
            ... )
        """
        try:
            obj = self.get(**kwargs)
            return obj, False
        except DoesNotExist:
            create_data = kwargs.copy()
            if defaults:
                create_data.update(defaults)
            obj = self.create(**create_data)
            return obj, True

    def update_or_create(
        self, defaults: dict[str, Any] | None = None, **kwargs: Any
    ) -> tuple[T, bool]:
        """Update an existing object or create a new one.

        Args:
            defaults: Values to update/create with
            **kwargs: Lookup parameters

        Returns:
            Tuple of (object, created) where created is a boolean

        Example:
            >>> policy, created = Policy.objects.update_or_create(
            ...     policy_number='POL-001',
            ...     defaults={'premium_amount': 2000.00}
            ... )
        """
        try:
            obj = self.get(**kwargs)
            # Update object
            if defaults:
                for key, value in defaults.items():
                    setattr(obj, key, value)
                obj.save(update_fields=list(defaults.keys()))
            return obj, False
        except DoesNotExist:
            create_data = kwargs.copy()
            if defaults:
                create_data.update(defaults)
            obj = self.create(**create_data)
            return obj, True

    def bulk_create(self, objs: list[dict[str, Any]]) -> list[T]:
        """Create multiple objects in bulk.

        Args:
            objs: List of dictionaries with object data

        Returns:
            List of created model instances

        Example:
            >>> policies = Policy.objects.bulk_create([
            ...     {'policy_number': 'POL-001', 'premium_amount': 1500},
            ...     {'policy_number': 'POL-002', 'premium_amount': 2000},
            ... ])
        """
        created_objects = []
        for obj_data in objs:
            obj = self.create(**obj_data)
            created_objects.append(obj)
        return created_objects


class APIModel:
    """Base class for API models.

    Provides Django ORM-like interface for working with API resources.
    Must be subclassed with _schema_class and _endpoint defined.

    Example:
        >>> class PolicySchema(BaseModel):
        ...     id: int
        ...     policy_number: str
        ...     premium_amount: float
        >>>
        >>> class Policy(APIModel):
        ...     _schema_class = PolicySchema
        ...     _endpoint = "/api/v1/policies/"
        >>>
        >>> # Register with client
        >>> Policy.objects = Manager(Policy, client)
    """

    # Class attributes (to be overridden in subclasses)
    _schema_class: type[BaseModel]
    _endpoint: str
    objects: Manager["APIModel"]

    def __init__(self, **kwargs: Any) -> None:
        """Initialize model instance.

        Args:
            **kwargs: Field values or _pydantic_instance
        """
        # Check if we received a pydantic instance
        if "_pydantic_instance" in kwargs:
            self._pydantic_instance: BaseModel = kwargs["_pydantic_instance"]
            self._client: ServiceClient | None = kwargs.get("_client")
        else:
            # Validate and create pydantic instance
            schema_class = self.get_schema_class()
            self._pydantic_instance = schema_class(**kwargs)
            self._client = kwargs.get("_client")

        # Set attributes from pydantic instance (preserving nested Pydantic models)
        for key in self._pydantic_instance.model_fields.keys():
            object.__setattr__(self, key, getattr(self._pydantic_instance, key))

    def __setattr__(self, name: str, value: Any) -> None:
        """Set attribute and update internal pydantic instance.

        Args:
            name: Attribute name
            value: Attribute value
        """
        # Set the attribute normally
        object.__setattr__(self, name, value)

        # If it's a model field and we have a pydantic instance, update it
        if (
            name not in ("_pydantic_instance", "_client")
            and hasattr(self, "_pydantic_instance")
            and name in self._pydantic_instance.model_fields
        ):
            # Get current data and update with new value
            current_data = self._pydantic_instance.model_dump()
            current_data[name] = value
            # Recreate pydantic instance with updated data
            schema_class = self.get_schema_class()
            self._pydantic_instance = schema_class(**current_data)

    @classmethod
    def get_endpoint(cls) -> str:
        """Get the API endpoint for this model.

        Returns:
            API endpoint path
        """
        return cls._endpoint

    @classmethod
    def get_schema_class(cls) -> type[BaseModel]:
        """Get the Pydantic schema class for this model.

        Returns:
            Pydantic BaseModel class
        """
        return cls._schema_class

    @classmethod
    def from_api(cls, data: dict[str, Any], client: ServiceClient | None = None) -> "APIModel":
        """Create model instance from API response data.

        Args:
            data: API response data
            client: HTTP client

        Returns:
            Model instance
        """
        schema_class = cls.get_schema_class()
        pydantic_instance = schema_class(**data)
        return cls(_pydantic_instance=pydantic_instance, _client=client)

    def to_dict(self, exclude_unset: bool = False, exclude_none: bool = False) -> dict[str, Any]:
        """Convert model to dictionary.

        Args:
            exclude_unset: Exclude fields that weren't explicitly set
            exclude_none: Exclude fields with None values

        Returns:
            Dictionary representation
        """
        return self._pydantic_instance.model_dump(
            mode="json", exclude_unset=exclude_unset, exclude_none=exclude_none
        )

    def model_dump(self, **kwargs: Any) -> dict[str, Any]:
        """Alias for to_dict for Pydantic compatibility.

        Args:
            **kwargs: Arguments to pass to model_dump

        Returns:
            Dictionary representation
        """
        return self._pydantic_instance.model_dump(**kwargs)

    def save(self, update_fields: list[str] | None = None) -> None:
        """Save this instance to the API.

        Creates or updates based on whether the object has an ID.

        Args:
            update_fields: List of fields to update (None = all fields)

        Raises:
            APIException: If client is not set

        Example:
            >>> policy = Policy(policy_number='POL-001', premium_amount=1500)
            >>> policy.save()  # Creates new
            >>> policy.premium_amount = 2000
            >>> policy.save(update_fields=['premium_amount'])  # Updates
        """
        from .exceptions import APIException

        if not self._client:
            raise APIException("Cannot save: no client configured for this instance")

        # Get data to send
        data = self.to_dict(exclude_unset=True)
        schema_class = self.get_schema_class()

        # Filter by update_fields if specified
        if update_fields:
            data = {k: v for k, v in data.items() if k in update_fields}
            # Skip validation for partial updates - API will validate
        else:
            # Validate full data
            schema_class(**data)

        # Determine if update or create
        if hasattr(self, "id") and self.id:
            # Update existing
            endpoint = f"{self.get_endpoint()}{self.id}/"
            response = self._client.patch(endpoint, data=data)
        else:
            # Create new
            response = self._client.post(self.get_endpoint(), data=data)

        # Update instance with response data
        pydantic_instance = schema_class(**response.data)
        self._pydantic_instance = pydantic_instance

        # Update attributes (preserving nested Pydantic models)
        for key in pydantic_instance.model_fields.keys():
            object.__setattr__(self, key, getattr(pydantic_instance, key))

    def delete(self) -> None:
        """Delete this instance from the API.

        Raises:
            APIException: If client is not set or object has no ID

        Example:
            >>> policy = Policy.objects.get(id=123)
            >>> policy.delete()
        """
        from .exceptions import APIException

        if not self._client:
            raise APIException("Cannot delete: no client configured")

        if not hasattr(self, "id") or not self.id:
            raise APIException("Cannot delete: object has no id")

        endpoint = f"{self.get_endpoint()}{self.id}/"
        self._client.delete(endpoint)

    def refresh_from_api(self) -> None:
        """Refresh this instance's data from the API.

        Raises:
            APIException: If client is not set or object has no ID

        Example:
            >>> policy = Policy.objects.get(id=123)
            >>> # ... time passes, data may have changed ...
            >>> policy.refresh_from_api()  # Reload from API
        """
        from .exceptions import APIException

        if not self._client:
            raise APIException("Cannot refresh: no client configured")

        if not hasattr(self, "id") or not self.id:
            raise APIException("Cannot refresh: object has no id")

        endpoint = f"{self.get_endpoint()}{self.id}/"
        response = self._client.get(endpoint)

        # Update instance with fresh data
        schema_class = self.get_schema_class()
        pydantic_instance = schema_class(**response.data)
        self._pydantic_instance = pydantic_instance

        # Update attributes (preserving nested Pydantic models)
        for key in pydantic_instance.model_fields.keys():
            object.__setattr__(self, key, getattr(pydantic_instance, key))

    def __repr__(self) -> str:
        """String representation."""
        return f"<{self.__class__.__name__}: {self._pydantic_instance}>"

    def __str__(self) -> str:
        """Human-readable string."""
        return repr(self)


def register_models(client: ServiceClient, *model_classes: type[APIModel]) -> None:
    """Register model classes with a sync client.

    This assigns a Manager instance to each model's 'objects' attribute.

    Args:
        client: ServiceClient instance
        *model_classes: Model classes to register

    Example:
        >>> client = ServiceClient(base_url="https://api.example.com")
        >>> register_models(client, Policy, Claim, Broker)
        >>> policies = Policy.objects.filter(status='active')
    """
    for model_class in model_classes:
        model_class.objects = Manager(model_class, client)
