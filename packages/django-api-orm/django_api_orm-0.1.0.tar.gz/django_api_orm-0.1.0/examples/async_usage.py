"""Async usage example for django-api-orm.

This example demonstrates how to use the async interface to interact with a REST API
in a Django ORM-like way with async/await.
"""

import asyncio

from pydantic import BaseModel

from django_api_orm import AsyncAPIModel, AsyncServiceClient, register_async_models


# Step 1: Define your Pydantic schemas
class UserSchema(BaseModel):
    """Schema for User model."""

    id: int | None = None  # Optional for creation
    name: str
    email: str
    active: bool = True


class PostSchema(BaseModel):
    """Schema for Post model."""

    id: int | None = None  # Optional for creation
    title: str
    content: str
    user_id: int
    published: bool = False


# Step 2: Define your async API models
class User(AsyncAPIModel):
    """User model for /api/v1/users/ endpoint."""

    _schema_class = UserSchema
    _endpoint = "/api/v1/users/"


class Post(AsyncAPIModel):
    """Post model for /api/v1/posts/ endpoint."""

    _schema_class = PostSchema
    _endpoint = "/api/v1/posts/"


# Step 3: Use the models with async/await
async def main() -> None:
    """Main async example function."""
    # Create async client
    async with AsyncServiceClient(
        base_url="https://api.example.com",
        auth_token="your-token-here",
        http2=True,  # Enable HTTP/2 for better performance
    ) as client:
        # Register models with async client
        register_async_models(client, User, Post)

        # Async iteration over all users
        print("All users:")
        async for user in User.objects.all():
            print(f"  - {user.name} ({user.email})")

        # Filter users with async for
        print("\nActive users:")
        async for user in User.objects.filter(active=True):
            print(f"  - {user.name}")

        # Get a single user (await)
        print("\nGet user by ID:")
        try:
            user = await User.objects.get(id=1)
            print(f"  Found: {user.name}")
        except Exception as e:
            print(f"  Error: {e}")

        # Create a new user (await)
        print("\nCreate new user:")
        new_user = await User.objects.create(
            name="Alice Smith", email="alice@example.com", active=True
        )
        print(f"  Created: {new_user.name} (ID: {new_user.id})")

        # Update a user (await)
        print("\nUpdate user:")
        new_user.email = "alice.smith@example.com"
        await new_user.save(update_fields=["email"])
        print(f"  Updated email to: {new_user.email}")

        # Chain filters
        print("\nChained filters:")
        posts_qs = Post.objects.filter(published=True).filter(user_id=1).order_by("-id")
        async for post in posts_qs:
            print(f"  - {post.title}")

        # Get first/last (await)
        print("\nFirst and last:")
        first_user = await User.objects.order_by("id").first()
        last_user = await User.objects.order_by("id").last()
        if first_user and last_user:
            print(f"  First: {first_user.name}")
            print(f"  Last: {last_user.name}")

        # Count (await)
        print("\nCounts:")
        total_users = await User.objects.count()
        active_count = await User.objects.filter(active=True).count()
        print(f"  Total users: {total_users}")
        print(f"  Active users: {active_count}")

        # Exists check (await)
        print("\nExists check:")
        has_active = await User.objects.filter(active=True).exists()
        print(f"  Has active users: {has_active}")

        # Values and values_list (await)
        print("\nValue extraction:")
        user_emails = await User.objects.all().values_list("email", flat=True)
        print(f"  Emails: {user_emails}")

        user_data = await User.objects.all().values("id", "name")
        print(f"  User data: {user_data}")

        # Get or create (await)
        print("\nGet or create:")
        user, created = await User.objects.get_or_create(
            email="bob@example.com", defaults={"name": "Bob Jones", "active": True}
        )
        print(f"  {'Created' if created else 'Found'}: {user.name}")

        # Refresh from API (await)
        print("\nRefresh from API:")
        await user.refresh_from_api()
        print(f"  Refreshed: {user.name}")

        # Delete (await)
        print("\nDelete user:")
        await user.delete()
        print("  User deleted")

        # Concurrent operations
        print("\nConcurrent operations:")
        users_task = User.objects.filter(active=True).count()
        posts_task = Post.objects.filter(published=True).count()

        # Run both queries concurrently
        user_count, post_count = await asyncio.gather(users_task, posts_task)
        print(f"  Active users: {user_count}")
        print(f"  Published posts: {post_count}")


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
