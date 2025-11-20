"""Integration tests for async ORM functionality (AsyncQuerySet, AsyncManager, AsyncAPIModel)."""

import httpx
import pytest
import respx
from pydantic import BaseModel

from django_api_orm import (
    APIException,
    AsyncAPIModel,
    AsyncManager,
    AsyncServiceClient,
    DoesNotExist,
    MultipleObjectsReturned,
    register_async_models,
)


class UserSchema(BaseModel):
    """Test schema for User."""

    id: int | None = None  # Make id optional for creation
    name: str
    email: str
    active: bool = True


class User(AsyncAPIModel):
    """Test async User model."""

    _schema_class = UserSchema
    _endpoint = "/api/v1/users/"


class TestAsyncAPIModelBasics:
    """Test basic AsyncAPIModel functionality."""

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


class TestAsyncQuerySetFiltering:
    """Test AsyncQuerySet filtering methods."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_filter_basic(self) -> None:
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

        async with AsyncServiceClient(base_url="https://api.example.com") as client:
            register_async_models(client, User)

            users = []
            async for user in User.objects.filter(active=True):
                users.append(user)

            assert len(users) == 1
            assert users[0].name == "Alice"

    @pytest.mark.asyncio
    @respx.mock
    async def test_filter_chaining(self) -> None:
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

        async with AsyncServiceClient(base_url="https://api.example.com") as client:
            register_async_models(client, User)

            users = []
            async for user in User.objects.filter(active=True).filter(name="Alice"):
                users.append(user)

            assert len(users) == 1

    @pytest.mark.asyncio
    @respx.mock
    async def test_all(self) -> None:
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

        async with AsyncServiceClient(base_url="https://api.example.com") as client:
            register_async_models(client, User)

            users = []
            async for user in User.objects.all():
                users.append(user)

            assert len(users) == 2
            assert users[0].name == "Alice"
            assert users[1].name == "Bob"


class TestAsyncQuerySetRetrieval:
    """Test AsyncQuerySet retrieval methods."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_success(self) -> None:
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

        async with AsyncServiceClient(base_url="https://api.example.com") as client:
            register_async_models(client, User)

            user = await User.objects.get(id=1)
            assert user.name == "Alice"

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_does_not_exist(self) -> None:
        """Test get() raises DoesNotExist when not found."""
        respx.get("https://api.example.com/api/v1/users/", params={"id": 999, "limit": 2}).mock(
            return_value=httpx.Response(200, json={"results": []})
        )

        async with AsyncServiceClient(base_url="https://api.example.com") as client:
            register_async_models(client, User)

            with pytest.raises(DoesNotExist):
                await User.objects.get(id=999)

    @pytest.mark.asyncio
    @respx.mock
    async def test_first(self) -> None:
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

        async with AsyncServiceClient(base_url="https://api.example.com") as client:
            register_async_models(client, User)

            user = await User.objects.first()
            assert user is not None
            assert user.name == "Alice"

    @pytest.mark.asyncio
    @respx.mock
    async def test_first_empty(self) -> None:
        """Test first() returns None when empty."""
        respx.get("https://api.example.com/api/v1/users/", params={"limit": 1}).mock(
            return_value=httpx.Response(200, json={"results": []})
        )

        async with AsyncServiceClient(base_url="https://api.example.com") as client:
            register_async_models(client, User)

            user = await User.objects.first()
            assert user is None

    @pytest.mark.asyncio
    @respx.mock
    async def test_exists_true(self) -> None:
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

        async with AsyncServiceClient(base_url="https://api.example.com") as client:
            register_async_models(client, User)

            exists = await User.objects.exists()
            assert exists is True

    @pytest.mark.asyncio
    @respx.mock
    async def test_exists_false(self) -> None:
        """Test exists() returns False when no results."""
        respx.get("https://api.example.com/api/v1/users/", params={"limit": 1}).mock(
            return_value=httpx.Response(200, json={"results": []})
        )

        async with AsyncServiceClient(base_url="https://api.example.com") as client:
            register_async_models(client, User)

            exists = await User.objects.exists()
            assert exists is False

    @pytest.mark.asyncio
    @respx.mock
    async def test_alen(self) -> None:
        """Test async length method."""
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

        async with AsyncServiceClient(base_url="https://api.example.com") as client:
            register_async_models(client, User)

            qs = User.objects.all()
            count = await qs.alen()
            assert count == 2


class TestAsyncManagerCreation:
    """Test AsyncManager creation methods."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_create(self) -> None:
        """Test creating a new object."""
        respx.post("https://api.example.com/api/v1/users/").mock(
            return_value=httpx.Response(
                201,
                json={"id": 1, "name": "Alice", "email": "alice@example.com", "active": True},
            )
        )

        async with AsyncServiceClient(base_url="https://api.example.com") as client:
            register_async_models(client, User)

            user = await User.objects.create(name="Alice", email="alice@example.com")
            assert user.id == 1
            assert user.name == "Alice"

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_or_create_get(self) -> None:
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

        async with AsyncServiceClient(base_url="https://api.example.com") as client:
            register_async_models(client, User)

            user, created = await User.objects.get_or_create(
                email="alice@example.com", defaults={"name": "Alice"}
            )
            assert created is False
            assert user.name == "Alice"

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_or_create_create(self) -> None:
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

        async with AsyncServiceClient(base_url="https://api.example.com") as client:
            register_async_models(client, User)

            user, created = await User.objects.get_or_create(
                email="bob@example.com", defaults={"name": "Bob"}
            )
            assert created is True
            assert user.name == "Bob"

    @pytest.mark.asyncio
    @respx.mock
    async def test_values(self) -> None:
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

        async with AsyncServiceClient(base_url="https://api.example.com") as client:
            register_async_models(client, User)

            values = await User.objects.all().values("id", "name")
            assert len(values) == 2
            assert values[0] == {"id": 1, "name": "Alice"}
            assert values[1] == {"id": 2, "name": "Bob"}

    @pytest.mark.asyncio
    @respx.mock
    async def test_values_list(self) -> None:
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

        async with AsyncServiceClient(base_url="https://api.example.com") as client:
            register_async_models(client, User)

            values = await User.objects.all().values_list("id", flat=True)
            assert values == [1, 2]


class TestRegisterAsyncModels:
    """Test async model registration."""

    @pytest.mark.asyncio
    async def test_register_async_models(self) -> None:
        """Test registering models with async client."""
        client = AsyncServiceClient(base_url="https://api.example.com")
        register_async_models(client, User)

        assert hasattr(User, "objects")
        assert isinstance(User.objects, AsyncManager)
        await client.close()


class TestAsyncIteration:
    """Test async iteration features."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_for_loop(self) -> None:
        """Test async for loop iteration."""
        respx.get("https://api.example.com/api/v1/users/").mock(
            return_value=httpx.Response(
                200,
                json={
                    "results": [
                        {"id": 1, "name": "Alice", "email": "alice@example.com", "active": True},
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

        async with AsyncServiceClient(base_url="https://api.example.com") as client:
            register_async_models(client, User)

            names = []
            async for user in User.objects.all():
                names.append(user.name)

            assert names == ["Alice", "Bob", "Charlie"]


class TestAsyncQuerySetAdvanced:
    """Test advanced async QuerySet methods."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_exclude(self) -> None:
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

        async with AsyncServiceClient(base_url="https://api.example.com") as client:
            register_async_models(client, User)

            users = []
            async for user in User.objects.exclude(active=True):
                users.append(user)
            assert len(users) == 1
            assert users[0].name == "Bob"

    @pytest.mark.asyncio
    @respx.mock
    async def test_order_by(self) -> None:
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

        async with AsyncServiceClient(base_url="https://api.example.com") as client:
            register_async_models(client, User)

            users = []
            async for user in User.objects.order_by("-name"):
                users.append(user)
            assert len(users) == 2
            assert users[0].name == "Bob"

    @pytest.mark.asyncio
    @respx.mock
    async def test_last(self) -> None:
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

        async with AsyncServiceClient(base_url="https://api.example.com") as client:
            register_async_models(client, User)

            user = await User.objects.last()
            assert user is not None
            assert user.name == "Bob"

    @pytest.mark.asyncio
    @respx.mock
    async def test_last_empty(self) -> None:
        """Test last() returns None when empty."""
        respx.get("https://api.example.com/api/v1/users/").mock(
            return_value=httpx.Response(200, json={"results": []})
        )

        async with AsyncServiceClient(base_url="https://api.example.com") as client:
            register_async_models(client, User)

            user = await User.objects.last()
            assert user is None

    @pytest.mark.asyncio
    @respx.mock
    async def test_count(self) -> None:
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

        async with AsyncServiceClient(base_url="https://api.example.com") as client:
            register_async_models(client, User)

            count = await User.objects.count()
            assert count == 10

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_multiple_objects_returned(self) -> None:
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

        async with AsyncServiceClient(base_url="https://api.example.com") as client:
            register_async_models(client, User)

            with pytest.raises(MultipleObjectsReturned):
                await User.objects.get(name="Alice")


class TestAsyncManagerAdvanced:
    """Test advanced async Manager methods."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_update_or_create_update(self) -> None:
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

        async with AsyncServiceClient(base_url="https://api.example.com") as client:
            register_async_models(client, User)

            user, created = await User.objects.update_or_create(
                email="alice@example.com", defaults={"name": "Alice Updated"}
            )
            assert created is False
            assert user.name == "Alice Updated"

    @pytest.mark.asyncio
    @respx.mock
    async def test_update_or_create_create(self) -> None:
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

        async with AsyncServiceClient(base_url="https://api.example.com") as client:
            register_async_models(client, User)

            user, created = await User.objects.update_or_create(
                email="charlie@example.com", defaults={"name": "Charlie"}
            )
            assert created is True
            assert user.name == "Charlie"

    @pytest.mark.asyncio
    @respx.mock
    async def test_bulk_create(self) -> None:
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

        async with AsyncServiceClient(base_url="https://api.example.com") as client:
            register_async_models(client, User)

            users_data = [
                {"name": "Alice", "email": "alice@example.com"},
                {"name": "Bob", "email": "bob@example.com"},
            ]
            users = await User.objects.bulk_create(users_data)
            assert len(users) == 2
            assert users[0].name == "Alice"
            assert users[1].name == "Bob"


class TestAsyncAPIModelOperations:
    """Test async APIModel instance operations."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_save_create(self) -> None:
        """Test save() creates new object when no id."""
        respx.post("https://api.example.com/api/v1/users/").mock(
            return_value=httpx.Response(
                201,
                json={"id": 1, "name": "Alice", "email": "alice@example.com", "active": True},
            )
        )

        async with AsyncServiceClient(base_url="https://api.example.com") as client:
            register_async_models(client, User)

            user = User(name="Alice", email="alice@example.com", _client=client)
            await user.save()
            assert user.id == 1

    @pytest.mark.asyncio
    @respx.mock
    async def test_save_update(self) -> None:
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

        async with AsyncServiceClient(base_url="https://api.example.com") as client:
            user = User(id=1, name="Alice Updated", email="alice@example.com", _client=client)
            await user.save()
            assert user.name == "Alice Updated"

    @pytest.mark.asyncio
    @respx.mock
    async def test_save_with_update_fields(self) -> None:
        """Test save() with update_fields parameter."""
        respx.patch("https://api.example.com/api/v1/users/1/").mock(
            return_value=httpx.Response(
                200,
                json={"id": 1, "name": "Alice", "email": "alice.new@example.com", "active": True},
            )
        )

        async with AsyncServiceClient(base_url="https://api.example.com") as client:
            user = User(id=1, name="Alice", email="alice.new@example.com", _client=client)
            await user.save(update_fields=["email"])
            assert user.email == "alice.new@example.com"

    @pytest.mark.asyncio
    async def test_save_without_client_raises(self) -> None:
        """Test save() raises APIException when no client."""
        user = User(name="Alice", email="alice@example.com")
        with pytest.raises(APIException, match="Cannot save.*no client"):
            await user.save()

    @pytest.mark.asyncio
    @respx.mock
    async def test_delete(self) -> None:
        """Test delete() method."""
        respx.delete("https://api.example.com/api/v1/users/1/").mock(
            return_value=httpx.Response(204)
        )

        async with AsyncServiceClient(base_url="https://api.example.com") as client:
            user = User(id=1, name="Alice", email="alice@example.com", _client=client)
            await user.delete()

    @pytest.mark.asyncio
    async def test_delete_without_client_raises(self) -> None:
        """Test delete() raises APIException when no client."""
        user = User(id=1, name="Alice", email="alice@example.com")
        with pytest.raises(APIException, match="Cannot delete"):
            await user.delete()

    @pytest.mark.asyncio
    async def test_delete_without_id_raises(self) -> None:
        """Test delete() raises APIException when no id."""
        async with AsyncServiceClient(base_url="https://api.example.com") as client:
            user = User(name="Alice", email="alice@example.com", _client=client)
            with pytest.raises(APIException, match="Cannot delete"):
                await user.delete()

    @pytest.mark.asyncio
    @respx.mock
    async def test_refresh_from_api(self) -> None:
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

        async with AsyncServiceClient(base_url="https://api.example.com") as client:
            user = User(id=1, name="Alice", email="alice@example.com", _client=client)
            await user.refresh_from_api()
            assert user.name == "Alice Updated"
            assert user.active is False

    @pytest.mark.asyncio
    async def test_refresh_without_client_raises(self) -> None:
        """Test refresh_from_api() raises APIException when no client."""
        user = User(id=1, name="Alice", email="alice@example.com")
        with pytest.raises(APIException, match="Cannot refresh"):
            await user.refresh_from_api()

    @pytest.mark.asyncio
    async def test_refresh_without_id_raises(self) -> None:
        """Test refresh_from_api() raises APIException when no id."""
        async with AsyncServiceClient(base_url="https://api.example.com") as client:
            user = User(name="Alice", email="alice@example.com", _client=client)
            with pytest.raises(APIException, match="Cannot refresh"):
                await user.refresh_from_api()
