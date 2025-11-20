"""Integration tests for ORM functionality (QuerySet, Manager, APIModel)."""

import httpx
import pytest
import respx
from pydantic import BaseModel

from django_api_orm import (
    APIException,
    APIModel,
    DoesNotExist,
    Manager,
    MultipleObjectsReturned,
    ServiceClient,
    register_models,
)


class UserSchema(BaseModel):
    """Test schema for User."""

    id: int | None = None  # Make id optional for creation
    name: str
    email: str
    active: bool = True


class User(APIModel):
    """Test User model."""

    _schema_class = UserSchema
    _endpoint = "/api/v1/users/"


class TestAPIModelBasics:
    """Test basic APIModel functionality."""

    def test_model_initialization(self) -> None:
        """Test creating a model instance."""
        user = User(id=1, name="John Doe", email="john@example.com")
        assert user.id == 1
        assert user.name == "John Doe"
        assert user.email == "john@example.com"
        assert user.active is True

    def test_model_to_dict(self) -> None:
        """Test converting model to dictionary."""
        user = User(id=1, name="John Doe", email="john@example.com")
        data = user.to_dict()
        assert data == {
            "id": 1,
            "name": "John Doe",
            "email": "john@example.com",
            "active": True,
        }

    def test_model_from_api(self) -> None:
        """Test creating model from API data."""
        data = {"id": 1, "name": "John Doe", "email": "john@example.com", "active": False}
        user = User.from_api(data)
        assert user.id == 1
        assert user.name == "John Doe"
        assert user.active is False


class TestQuerySetFiltering:
    """Test QuerySet filtering methods."""

    @respx.mock
    def test_filter_basic(self) -> None:
        """Test basic filtering."""
        respx.get("https://api.example.com/api/v1/users/", params={"active": True}).mock(
            return_value=httpx.Response(
                200,
                json={
                    "results": [
                        {"id": 1, "name": "Alice", "email": "alice@example.com", "active": True}
                    ]
                },
            )
        )

        with ServiceClient(base_url="https://api.example.com") as client:
            register_models(client, User)

            users = list(User.objects.filter(active=True))
            assert len(users) == 1
            assert users[0].name == "Alice"

    @respx.mock
    def test_filter_chaining(self) -> None:
        """Test chaining multiple filters."""
        respx.get(
            "https://api.example.com/api/v1/users/",
            params={"active": True, "name": "Alice"},
        ).mock(
            return_value=httpx.Response(
                200,
                json={
                    "results": [
                        {"id": 1, "name": "Alice", "email": "alice@example.com", "active": True}
                    ]
                },
            )
        )

        with ServiceClient(base_url="https://api.example.com") as client:
            register_models(client, User)

            users = list(User.objects.filter(active=True).filter(name="Alice"))
            assert len(users) == 1

    @respx.mock
    def test_all(self) -> None:
        """Test getting all objects."""
        respx.get("https://api.example.com/api/v1/users/").mock(
            return_value=httpx.Response(
                200,
                json={
                    "results": [
                        {"id": 1, "name": "Alice", "email": "alice@example.com", "active": True},
                        {"id": 2, "name": "Bob", "email": "bob@example.com", "active": True},
                    ]
                },
            )
        )

        with ServiceClient(base_url="https://api.example.com") as client:
            register_models(client, User)

            users = list(User.objects.all())
            assert len(users) == 2
            assert users[0].name == "Alice"
            assert users[1].name == "Bob"


class TestQuerySetRetrieval:
    """Test QuerySet retrieval methods."""

    @respx.mock
    def test_get_success(self) -> None:
        """Test get() with single result."""
        respx.get("https://api.example.com/api/v1/users/", params={"id": 1, "limit": 2}).mock(
            return_value=httpx.Response(
                200,
                json={
                    "results": [
                        {"id": 1, "name": "Alice", "email": "alice@example.com", "active": True}
                    ]
                },
            )
        )

        with ServiceClient(base_url="https://api.example.com") as client:
            register_models(client, User)

            user = User.objects.get(id=1)
            assert user.name == "Alice"

    @respx.mock
    def test_get_does_not_exist(self) -> None:
        """Test get() raises DoesNotExist when not found."""
        respx.get("https://api.example.com/api/v1/users/", params={"id": 999, "limit": 2}).mock(
            return_value=httpx.Response(200, json={"results": []})
        )

        with ServiceClient(base_url="https://api.example.com") as client:
            register_models(client, User)

            with pytest.raises(DoesNotExist):
                User.objects.get(id=999)

    @respx.mock
    def test_first(self) -> None:
        """Test first() method."""
        respx.get("https://api.example.com/api/v1/users/", params={"limit": 1}).mock(
            return_value=httpx.Response(
                200,
                json={
                    "results": [
                        {"id": 1, "name": "Alice", "email": "alice@example.com", "active": True}
                    ]
                },
            )
        )

        with ServiceClient(base_url="https://api.example.com") as client:
            register_models(client, User)

            user = User.objects.first()
            assert user is not None
            assert user.name == "Alice"

    @respx.mock
    def test_first_empty(self) -> None:
        """Test first() returns None when empty."""
        respx.get("https://api.example.com/api/v1/users/", params={"limit": 1}).mock(
            return_value=httpx.Response(200, json={"results": []})
        )

        with ServiceClient(base_url="https://api.example.com") as client:
            register_models(client, User)

            user = User.objects.first()
            assert user is None

    @respx.mock
    def test_exists_true(self) -> None:
        """Test exists() returns True when results exist."""
        respx.get("https://api.example.com/api/v1/users/", params={"limit": 1}).mock(
            return_value=httpx.Response(
                200,
                json={
                    "results": [
                        {"id": 1, "name": "Alice", "email": "alice@example.com", "active": True}
                    ]
                },
            )
        )

        with ServiceClient(base_url="https://api.example.com") as client:
            register_models(client, User)

            exists = User.objects.exists()
            assert exists is True

    @respx.mock
    def test_exists_false(self) -> None:
        """Test exists() returns False when no results."""
        respx.get("https://api.example.com/api/v1/users/", params={"limit": 1}).mock(
            return_value=httpx.Response(200, json={"results": []})
        )

        with ServiceClient(base_url="https://api.example.com") as client:
            register_models(client, User)

            exists = User.objects.exists()
            assert exists is False


class TestManagerCreation:
    """Test Manager creation methods."""

    @respx.mock
    def test_create(self) -> None:
        """Test creating a new object."""
        respx.post("https://api.example.com/api/v1/users/").mock(
            return_value=httpx.Response(
                201,
                json={"id": 1, "name": "Alice", "email": "alice@example.com", "active": True},
            )
        )

        with ServiceClient(base_url="https://api.example.com") as client:
            register_models(client, User)

            user = User.objects.create(name="Alice", email="alice@example.com")
            assert user.id == 1
            assert user.name == "Alice"

    @respx.mock
    def test_get_or_create_get(self) -> None:
        """Test get_or_create when object exists."""
        respx.get(
            "https://api.example.com/api/v1/users/",
            params={"email": "alice@example.com", "limit": 2},
        ).mock(
            return_value=httpx.Response(
                200,
                json={
                    "results": [
                        {"id": 1, "name": "Alice", "email": "alice@example.com", "active": True}
                    ]
                },
            )
        )

        with ServiceClient(base_url="https://api.example.com") as client:
            register_models(client, User)

            user, created = User.objects.get_or_create(
                email="alice@example.com", defaults={"name": "Alice"}
            )
            assert created is False
            assert user.name == "Alice"

    @respx.mock
    def test_get_or_create_create(self) -> None:
        """Test get_or_create when object doesn't exist."""
        respx.get(
            "https://api.example.com/api/v1/users/",
            params={"email": "bob@example.com", "limit": 2},
        ).mock(return_value=httpx.Response(200, json={"results": []}))

        respx.post("https://api.example.com/api/v1/users/").mock(
            return_value=httpx.Response(
                201, json={"id": 2, "name": "Bob", "email": "bob@example.com", "active": True}
            )
        )

        with ServiceClient(base_url="https://api.example.com") as client:
            register_models(client, User)

            user, created = User.objects.get_or_create(
                email="bob@example.com", defaults={"name": "Bob"}
            )
            assert created is True
            assert user.name == "Bob"


class TestRegisterModels:
    """Test model registration."""

    def test_register_models(self) -> None:
        """Test registering models with client."""
        client = ServiceClient(base_url="https://api.example.com")
        register_models(client, User)

        assert hasattr(User, "objects")
        assert isinstance(User.objects, Manager)
        client.close()


class TestQuerySetAdvanced:
    """Test advanced QuerySet methods."""

    @respx.mock
    def test_exclude(self) -> None:
        """Test exclude() method."""
        respx.get("https://api.example.com/api/v1/users/", params={"exclude_active": True}).mock(
            return_value=httpx.Response(
                200,
                json={
                    "results": [
                        {"id": 2, "name": "Bob", "email": "bob@example.com", "active": False}
                    ]
                },
            )
        )

        with ServiceClient(base_url="https://api.example.com") as client:
            register_models(client, User)

            users = list(User.objects.exclude(active=True))
            assert len(users) == 1
            assert users[0].name == "Bob"

    @respx.mock
    def test_order_by(self) -> None:
        """Test order_by() method."""
        respx.get("https://api.example.com/api/v1/users/", params={"ordering": "-name"}).mock(
            return_value=httpx.Response(
                200,
                json={
                    "results": [
                        {"id": 2, "name": "Bob", "email": "bob@example.com", "active": True},
                        {"id": 1, "name": "Alice", "email": "alice@example.com", "active": True},
                    ]
                },
            )
        )

        with ServiceClient(base_url="https://api.example.com") as client:
            register_models(client, User)

            users = list(User.objects.order_by("-name"))
            assert len(users) == 2
            assert users[0].name == "Bob"

    @respx.mock
    def test_last(self) -> None:
        """Test last() method."""
        respx.get("https://api.example.com/api/v1/users/").mock(
            return_value=httpx.Response(
                200,
                json={
                    "results": [
                        {"id": 1, "name": "Alice", "email": "alice@example.com", "active": True},
                        {"id": 2, "name": "Bob", "email": "bob@example.com", "active": True},
                    ]
                },
            )
        )

        with ServiceClient(base_url="https://api.example.com") as client:
            register_models(client, User)

            user = User.objects.last()
            assert user is not None
            assert user.name == "Bob"

    @respx.mock
    def test_last_empty(self) -> None:
        """Test last() returns None when empty."""
        respx.get("https://api.example.com/api/v1/users/").mock(
            return_value=httpx.Response(200, json={"results": []})
        )

        with ServiceClient(base_url="https://api.example.com") as client:
            register_models(client, User)

            user = User.objects.last()
            assert user is None

    @respx.mock
    def test_count(self) -> None:
        """Test count() method."""
        respx.get("https://api.example.com/api/v1/users/").mock(
            return_value=httpx.Response(
                200,
                json={
                    "count": 10,
                    "results": [],
                },
            )
        )

        with ServiceClient(base_url="https://api.example.com") as client:
            register_models(client, User)

            count = User.objects.count()
            assert count == 10

    @respx.mock
    def test_get_multiple_objects_returned(self) -> None:
        """Test get() raises MultipleObjectsReturned when multiple results."""
        respx.get(
            "https://api.example.com/api/v1/users/", params={"name": "Alice", "limit": 2}
        ).mock(
            return_value=httpx.Response(
                200,
                json={
                    "results": [
                        {"id": 1, "name": "Alice", "email": "alice1@example.com", "active": True},
                        {"id": 2, "name": "Alice", "email": "alice2@example.com", "active": True},
                    ]
                },
            )
        )

        with ServiceClient(base_url="https://api.example.com") as client:
            register_models(client, User)

            with pytest.raises(MultipleObjectsReturned):
                User.objects.get(name="Alice")

    @respx.mock
    def test_values(self) -> None:
        """Test values() method."""
        respx.get("https://api.example.com/api/v1/users/").mock(
            return_value=httpx.Response(
                200,
                json={
                    "results": [
                        {"id": 1, "name": "Alice", "email": "alice@example.com", "active": True},
                        {"id": 2, "name": "Bob", "email": "bob@example.com", "active": True},
                    ]
                },
            )
        )

        with ServiceClient(base_url="https://api.example.com") as client:
            register_models(client, User)

            values = User.objects.all().values("id", "name")
            assert len(values) == 2
            assert values[0] == {"id": 1, "name": "Alice"}
            assert values[1] == {"id": 2, "name": "Bob"}

    @respx.mock
    def test_values_list(self) -> None:
        """Test values_list() method."""
        respx.get("https://api.example.com/api/v1/users/").mock(
            return_value=httpx.Response(
                200,
                json={
                    "results": [
                        {"id": 1, "name": "Alice", "email": "alice@example.com", "active": True},
                        {"id": 2, "name": "Bob", "email": "bob@example.com", "active": True},
                    ]
                },
            )
        )

        with ServiceClient(base_url="https://api.example.com") as client:
            register_models(client, User)

            values = User.objects.all().values_list("id", flat=True)
            assert values == [1, 2]

    @respx.mock
    def test_len(self) -> None:
        """Test __len__() method."""
        respx.get("https://api.example.com/api/v1/users/").mock(
            return_value=httpx.Response(
                200,
                json={
                    "results": [
                        {"id": 1, "name": "Alice", "email": "alice@example.com", "active": True},
                        {"id": 2, "name": "Bob", "email": "bob@example.com", "active": True},
                    ]
                },
            )
        )

        with ServiceClient(base_url="https://api.example.com") as client:
            register_models(client, User)

            qs = User.objects.all()
            assert len(qs) == 2

    @respx.mock
    def test_getitem_index(self) -> None:
        """Test __getitem__() with index."""
        respx.get("https://api.example.com/api/v1/users/").mock(
            return_value=httpx.Response(
                200,
                json={
                    "results": [
                        {"id": 1, "name": "Alice", "email": "alice@example.com", "active": True},
                        {"id": 2, "name": "Bob", "email": "bob@example.com", "active": True},
                    ]
                },
            )
        )

        with ServiceClient(base_url="https://api.example.com") as client:
            register_models(client, User)

            user = User.objects.all()[0]
            assert user.name == "Alice"

    @respx.mock
    def test_getitem_slice(self) -> None:
        """Test __getitem__() with slice."""
        respx.get("https://api.example.com/api/v1/users/", params={"offset": 1, "limit": 2}).mock(
            return_value=httpx.Response(
                200,
                json={
                    "results": [
                        {"id": 2, "name": "Bob", "email": "bob@example.com", "active": True},
                        {
                            "id": 3,
                            "name": "Charlie",
                            "email": "charlie@example.com",
                            "active": True,
                        },
                    ]
                },
            )
        )

        with ServiceClient(base_url="https://api.example.com") as client:
            register_models(client, User)

            users = User.objects.all()[1:3]
            user_list = list(users)
            assert len(user_list) == 2
            assert user_list[0].name == "Bob"


class TestManagerAdvanced:
    """Test advanced Manager methods."""

    @respx.mock
    def test_update_or_create_update(self) -> None:
        """Test update_or_create when object exists."""
        respx.get(
            "https://api.example.com/api/v1/users/",
            params={"email": "alice@example.com", "limit": 2},
        ).mock(
            return_value=httpx.Response(
                200,
                json={
                    "results": [
                        {"id": 1, "name": "Alice", "email": "alice@example.com", "active": True}
                    ]
                },
            )
        )

        respx.patch("https://api.example.com/api/v1/users/1/").mock(
            return_value=httpx.Response(
                200,
                json={
                    "id": 1,
                    "name": "Alice Updated",
                    "email": "alice@example.com",
                    "active": True,
                },
            )
        )

        with ServiceClient(base_url="https://api.example.com") as client:
            register_models(client, User)

            user, created = User.objects.update_or_create(
                email="alice@example.com", defaults={"name": "Alice Updated"}
            )
            assert created is False
            assert user.name == "Alice Updated"

    @respx.mock
    def test_update_or_create_create(self) -> None:
        """Test update_or_create when object doesn't exist."""
        respx.get(
            "https://api.example.com/api/v1/users/",
            params={"email": "charlie@example.com", "limit": 2},
        ).mock(return_value=httpx.Response(200, json={"results": []}))

        respx.post("https://api.example.com/api/v1/users/").mock(
            return_value=httpx.Response(
                201,
                json={"id": 3, "name": "Charlie", "email": "charlie@example.com", "active": True},
            )
        )

        with ServiceClient(base_url="https://api.example.com") as client:
            register_models(client, User)

            user, created = User.objects.update_or_create(
                email="charlie@example.com", defaults={"name": "Charlie"}
            )
            assert created is True
            assert user.name == "Charlie"

    @respx.mock
    def test_bulk_create(self) -> None:
        """Test bulk_create() method."""
        # bulk_create calls create() for each object, so mock individual POSTs
        respx.post("https://api.example.com/api/v1/users/").mock(
            side_effect=[
                httpx.Response(
                    201,
                    json={"id": 1, "name": "Alice", "email": "alice@example.com", "active": True},
                ),
                httpx.Response(
                    201,
                    json={"id": 2, "name": "Bob", "email": "bob@example.com", "active": True},
                ),
            ]
        )

        with ServiceClient(base_url="https://api.example.com") as client:
            register_models(client, User)

            users_data = [
                {"name": "Alice", "email": "alice@example.com"},
                {"name": "Bob", "email": "bob@example.com"},
            ]
            users = User.objects.bulk_create(users_data)
            assert len(users) == 2
            assert users[0].name == "Alice"
            assert users[1].name == "Bob"


class TestAPIModelOperations:
    """Test APIModel instance operations."""

    @respx.mock
    def test_save_create(self) -> None:
        """Test save() creates new object when no id."""
        respx.post("https://api.example.com/api/v1/users/").mock(
            return_value=httpx.Response(
                201,
                json={"id": 1, "name": "Alice", "email": "alice@example.com", "active": True},
            )
        )

        with ServiceClient(base_url="https://api.example.com") as client:
            register_models(client, User)

            user = User(name="Alice", email="alice@example.com", _client=client)
            user.save()
            assert user.id == 1

    @respx.mock
    def test_save_update(self) -> None:
        """Test save() updates existing object when has id."""
        respx.patch("https://api.example.com/api/v1/users/1/").mock(
            return_value=httpx.Response(
                200,
                json={
                    "id": 1,
                    "name": "Alice Updated",
                    "email": "alice@example.com",
                    "active": True,
                },
            )
        )

        with ServiceClient(base_url="https://api.example.com") as client:
            user = User(id=1, name="Alice Updated", email="alice@example.com", _client=client)
            user.save()
            assert user.name == "Alice Updated"

    @respx.mock
    def test_save_with_update_fields(self) -> None:
        """Test save() with update_fields parameter."""
        respx.patch("https://api.example.com/api/v1/users/1/").mock(
            return_value=httpx.Response(
                200,
                json={"id": 1, "name": "Alice", "email": "alice.new@example.com", "active": True},
            )
        )

        with ServiceClient(base_url="https://api.example.com") as client:
            user = User(id=1, name="Alice", email="alice.new@example.com", _client=client)
            user.save(update_fields=["email"])
            assert user.email == "alice.new@example.com"

    def test_save_without_client_raises(self) -> None:
        """Test save() raises APIException when no client."""
        user = User(name="Alice", email="alice@example.com")
        with pytest.raises(APIException, match="Cannot save.*no client"):
            user.save()

    @respx.mock
    def test_delete(self) -> None:
        """Test delete() method."""
        respx.delete("https://api.example.com/api/v1/users/1/").mock(
            return_value=httpx.Response(204)
        )

        with ServiceClient(base_url="https://api.example.com") as client:
            user = User(id=1, name="Alice", email="alice@example.com", _client=client)
            user.delete()

    def test_delete_without_client_raises(self) -> None:
        """Test delete() raises APIException when no client."""
        user = User(id=1, name="Alice", email="alice@example.com")
        with pytest.raises(APIException, match="Cannot delete"):
            user.delete()

    def test_delete_without_id_raises(self) -> None:
        """Test delete() raises APIException when no id."""
        with ServiceClient(base_url="https://api.example.com") as client:
            user = User(name="Alice", email="alice@example.com", _client=client)
            with pytest.raises(APIException, match="Cannot delete"):
                user.delete()

    @respx.mock
    def test_refresh_from_api(self) -> None:
        """Test refresh_from_api() method."""
        respx.get("https://api.example.com/api/v1/users/1/").mock(
            return_value=httpx.Response(
                200,
                json={
                    "id": 1,
                    "name": "Alice Updated",
                    "email": "alice@example.com",
                    "active": False,
                },
            )
        )

        with ServiceClient(base_url="https://api.example.com") as client:
            user = User(id=1, name="Alice", email="alice@example.com", _client=client)
            user.refresh_from_api()
            assert user.name == "Alice Updated"
            assert user.active is False

    def test_refresh_without_client_raises(self) -> None:
        """Test refresh_from_api() raises APIException when no client."""
        user = User(id=1, name="Alice", email="alice@example.com")
        with pytest.raises(APIException, match="Cannot refresh"):
            user.refresh_from_api()

    def test_refresh_without_id_raises(self) -> None:
        """Test refresh_from_api() raises APIException when no id."""
        with ServiceClient(base_url="https://api.example.com") as client:
            user = User(name="Alice", email="alice@example.com", _client=client)
            with pytest.raises(APIException, match="Cannot refresh"):
                user.refresh_from_api()
