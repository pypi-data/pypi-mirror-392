"""Basic usage example for django-api-orm.

This example demonstrates how to use the library to interact with a REST API
in a Django ORM-like way.
"""

from pydantic import BaseModel

from django_api_orm import APIModel, Manager, ServiceClient, register_models


# Step 1: Define your Pydantic schemas
class UserSchema(BaseModel):
    """Schema for User model."""

    id: int
    name: str
    email: str
    active: bool = True


class PostSchema(BaseModel):
    """Schema for Post model."""

    id: int
    title: str
    content: str
    user_id: int
    published: bool = False


# Step 2: Define your API models
class User(APIModel):
    """User model for /api/v1/users/ endpoint."""

    _schema_class = UserSchema
    _endpoint = "/api/v1/users/"


class Post(APIModel):
    """Post model for /api/v1/posts/ endpoint."""

    _schema_class = PostSchema
    _endpoint = "/api/v1/posts/"


# Step 3: Use the models
def main() -> None:
    """Main example function."""
    # Create client
    with ServiceClient(
        base_url="https://api.example.com", auth_token="your-token-here"
    ) as client:
        # Register models with client
        register_models(client, User, Post)

        # Query all users
        print("All users:")
        users = User.objects.all()
        for user in users:
            print(f"  - {user.name} ({user.email})")

        # Filter users
        print("\nActive users:")
        active_users = User.objects.filter(active=True)
        for user in active_users:
            print(f"  - {user.name}")

        # Get a single user
        print("\nGet user by ID:")
        try:
            user = User.objects.get(id=1)
            print(f"  Found: {user.name}")
        except Exception as e:
            print(f"  Error: {e}")

        # Create a new user
        print("\nCreate new user:")
        new_user = User.objects.create(name="Alice Smith", email="alice@example.com", active=True)
        print(f"  Created: {new_user.name} (ID: {new_user.id})")

        # Update a user
        print("\nUpdate user:")
        new_user.email = "alice.smith@example.com"
        new_user.save(update_fields=["email"])
        print(f"  Updated email to: {new_user.email}")

        # Chain filters
        print("\nChained filters:")
        posts = Post.objects.filter(published=True).filter(user_id=1).order_by("-id")[:5]
        for post in posts:
            print(f"  - {post.title}")

        # Get first/last
        print("\nFirst and last:")
        first_user = User.objects.order_by("id").first()
        last_user = User.objects.order_by("id").last()
        if first_user and last_user:
            print(f"  First: {first_user.name}")
            print(f"  Last: {last_user.name}")

        # Count
        print("\nCounts:")
        total_users = User.objects.count()
        active_count = User.objects.filter(active=True).count()
        print(f"  Total users: {total_users}")
        print(f"  Active users: {active_count}")

        # Exists check
        print("\nExists check:")
        has_active = User.objects.filter(active=True).exists()
        print(f"  Has active users: {has_active}")

        # Values and values_list
        print("\nValue extraction:")
        user_emails = User.objects.values_list("email", flat=True)
        print(f"  Emails: {user_emails}")

        user_data = User.objects.values("id", "name")
        print(f"  User data: {user_data}")

        # Get or create
        print("\nGet or create:")
        user, created = User.objects.get_or_create(
            email="bob@example.com", defaults={"name": "Bob Jones", "active": True}
        )
        print(f"  {'Created' if created else 'Found'}: {user.name}")

        # Refresh from API
        print("\nRefresh from API:")
        user.refresh_from_api()
        print(f"  Refreshed: {user.name}")

        # Delete
        print("\nDelete user:")
        user.delete()
        print("  User deleted")


if __name__ == "__main__":
    main()
