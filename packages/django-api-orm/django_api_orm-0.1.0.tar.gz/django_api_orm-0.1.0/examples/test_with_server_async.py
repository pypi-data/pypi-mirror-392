"""Async test script for django-api-orm with the local test server - Insurance Domain.

This script demonstrates all async features of django-api-orm using the local FastAPI test server
with insurance models (PolicyHolder, Policy, Claim).

Make sure the test server is running first:
    uvicorn examples.test_server:app --host 127.0.0.1 --port 8700 --reload

Then run this script:
    uv run python examples/test_with_server_async.py
"""

import asyncio
from datetime import date

from pydantic import BaseModel, EmailStr

from django_api_orm import AsyncAPIModel, AsyncServiceClient, register_async_models


# Define nested schemas
class AddressSchema(BaseModel):
    """Nested address schema."""

    street: str
    city: str
    state: str
    zip_code: str
    country: str = "USA"


# Define main schemas (matching test_server.py)
class PolicyHolderSchema(BaseModel):
    """Schema for PolicyHolder model with nested address."""

    id: int | None = None
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    date_of_birth: date
    address: AddressSchema
    active: bool = True


class PolicySchema(BaseModel):
    """Schema for Policy model."""

    id: int | None = None
    policy_number: str
    policyholder_id: int
    policy_type: str
    premium_amount: float
    coverage_amount: float
    start_date: date
    end_date: date
    status: str = "active"


class ClaimSchema(BaseModel):
    """Schema for Claim model."""

    id: int | None = None
    claim_number: str
    policy_id: int
    claim_date: date
    incident_date: date
    claim_amount: float
    approved_amount: float | None = None
    status: str = "pending"
    description: str


# Define async API models
class PolicyHolder(AsyncAPIModel):
    """PolicyHolder model for /api/v1/policyholders/ endpoint."""

    _schema_class = PolicyHolderSchema
    _endpoint = "/api/v1/policyholders/"


class Policy(AsyncAPIModel):
    """Policy model for /api/v1/policies/ endpoint."""

    _schema_class = PolicySchema
    _endpoint = "/api/v1/policies/"


class Claim(AsyncAPIModel):
    """Claim model for /api/v1/claims/ endpoint."""

    _schema_class = ClaimSchema
    _endpoint = "/api/v1/claims/"


async def main() -> None:
    """Main async example function testing all django-api-orm features with insurance models."""
    print("=" * 80)
    print("django-api-orm Async Feature Test - Insurance Domain")
    print("=" * 80)

    # Create async client (pointing to local test server)
    async with AsyncServiceClient(
        base_url="http://localhost:8700",
        http2=True,  # Enable HTTP/2 for better performance
    ) as client:
        # Register models with client
        register_async_models(client, PolicyHolder, Policy, Claim)

        # 1. Async iteration over all policyholders
        print("\n1. Async iteration over all policyholders:")
        print("-" * 80)
        async for ph in PolicyHolder.objects.all():
            print(
                f"  - {ph.first_name} {ph.last_name} ({ph.email}) "
                f"[{ph.address.city}, {ph.address.state}] Active: {ph.active}"
            )

        # 2. Filter active policyholders
        print("\n2. Filter active policyholders (async for):")
        print("-" * 80)
        async for ph in PolicyHolder.objects.filter(active=True):
            print(f"  - {ph.first_name} {ph.last_name}")

        # 3. Filter by nested field
        print("\n3. Filter by nested field - state (async for):")
        print("-" * 80)
        async for ph in PolicyHolder.objects.filter(state="IL"):
            print(f"  - {ph.first_name} {ph.last_name} in {ph.address.city}, {ph.address.state}")

        # 4. Get a single policyholder (await)
        print("\n4. Get policyholder by ID (await PolicyHolder.objects.get(id=1)):")
        print("-" * 80)
        try:
            ph = await PolicyHolder.objects.get(id=1)
            print(f"  Found: {ph.first_name} {ph.last_name}")
            print(f"  Address: {ph.address.street}, {ph.address.city}")
        except Exception as e:
            print(f"  Error: {e}")

        # 5. Create a new policyholder with nested address (await)
        print("\n5. Create new policyholder with nested address (await):")
        print("-" * 80)
        try:
            new_address = AddressSchema(
                street="888 Async Ave",
                city="Asyncville",
                state="TX",
                zip_code="75001",
                country="USA",
            )
            new_ph = await PolicyHolder.objects.create(
                first_name="Kyle",
                last_name="Reese",
                email=f"kyle.reese+{id(client)}@example.com",
                phone="555-8888",
                date_of_birth=date(1975, 6, 22),
                address=new_address,
                active=True,
            )
            print(f"  Created: {new_ph.first_name} {new_ph.last_name} (ID: {new_ph.id})")
            print(f"  Address: {new_ph.address.city}, {new_ph.address.state}")
        except Exception as e:
            print(f"  Error: {e}")

        # 6. Async iteration over policies
        print("\n6. Async iteration over all policies:")
        print("-" * 80)
        async for policy in Policy.objects.all():
            print(
                f"  - {policy.policy_number} ({policy.policy_type}) "
                f"- PolicyHolder ID: {policy.policyholder_id} "
                f"- Premium: ${policy.premium_amount:,.2f}"
            )

        # 7. Filter policies by type (async for)
        print("\n7. Filter auto policies (async for):")
        print("-" * 80)
        async for policy in Policy.objects.filter(policy_type="auto"):
            print(f"  - {policy.policy_number} - Coverage: ${policy.coverage_amount:,.2f}")

        # 8. Filter policies by policyholder (relationship)
        print("\n8. Filter policies by policyholder ID (async for):")
        print("-" * 80)
        async for policy in Policy.objects.filter(policyholder_id=1):
            print(f"  - {policy.policy_number} ({policy.policy_type})")

        # 9. Create a new policy (await)
        print("\n9. Create new policy (await):")
        print("-" * 80)
        try:
            new_policy = await Policy.objects.create(
                policy_number=f"DENTAL-2024-{id(client)}",
                policyholder_id=1,
                policy_type="health",
                premium_amount=600.00,
                coverage_amount=25000.00,
                start_date=date(2024, 1, 1),
                end_date=date(2024, 12, 31),
                status="active",
            )
            print(f"  Created: {new_policy.policy_number}")
            print(f"  Type: {new_policy.policy_type}, Premium: ${new_policy.premium_amount:,.2f}")
        except Exception as e:
            print(f"  Error: {e}")

        # 10. Async iteration over claims
        print("\n10. Async iteration over all claims:")
        print("-" * 80)
        async for claim in Claim.objects.all():
            print(
                f"  - {claim.claim_number} (Policy ID: {claim.policy_id}) "
                f"- Amount: ${claim.claim_amount:,.2f} - Status: {claim.status}"
            )

        # 11. Filter claims by status (async for)
        print("\n11. Filter approved claims (async for):")
        print("-" * 80)
        async for claim in Claim.objects.filter(status="approved"):
            print(
                f"  - {claim.claim_number} - Claim: ${claim.claim_amount:,.2f}, "
                f"Approved: ${claim.approved_amount:,.2f}"
            )

        # 12. Filter claims by policy (relationship)
        print("\n12. Filter claims by policy ID (async for):")
        print("-" * 80)
        async for claim in Claim.objects.filter(policy_id=1):
            print(f"  - {claim.claim_number}: {claim.description}")

        # 13. Create a new claim (await)
        print("\n13. Create new claim (await):")
        print("-" * 80)
        try:
            new_claim = await Claim.objects.create(
                claim_number=f"CLM-ASYNC-{id(client)}",
                policy_id=1,
                claim_date=date(2024, 7, 20),
                incident_date=date(2024, 7, 15),
                claim_amount=3500.00,
                approved_amount=None,
                status="pending",
                description="Async test claim from script",
            )
            print(f"  Created: {new_claim.claim_number}")
            print(f"  Amount: ${new_claim.claim_amount:,.2f}, Status: {new_claim.status}")
        except Exception as e:
            print(f"  Error: {e}")

        # 14. Update operations (await)
        print("\n14. Update claim status to approved (await):")
        print("-" * 80)
        new_claim.status = "approved"
        new_claim.approved_amount = 3500.00
        await new_claim.save(update_fields=["status", "approved_amount"])
        print(f"  Updated {new_claim.claim_number} to {new_claim.status}")
        print(f"  Approved amount: ${new_claim.approved_amount:,.2f}")

        # 15. Ordering with slicing (async for)
        print("\n15. Order policies by premium (descending, top 3):")
        print("-" * 80)
        count = 0
        async for policy in Policy.objects.order_by("-premium_amount"):
            print(f"  - {policy.policy_number}: ${policy.premium_amount:,.2f}")
            count += 1
            if count >= 3:
                break

        # 16. Count operations (await)
        print("\n16. Count operations (await):")
        print("-" * 80)
        total_policyholders = await PolicyHolder.objects.count()
        active_policyholders_count = await PolicyHolder.objects.filter(active=True).count()
        total_policies = await Policy.objects.count()
        active_policies = await Policy.objects.filter(status="active").count()
        total_claims = await Claim.objects.count()
        pending_claims = await Claim.objects.filter(status="pending").count()
        print(f"  Total PolicyHolders: {total_policyholders} (Active: {active_policyholders_count})")
        print(f"  Total Policies: {total_policies} (Active: {active_policies})")
        print(f"  Total Claims: {total_claims} (Pending: {pending_claims})")

        # 17. Exists check (await)
        print("\n17. Exists check (await):")
        print("-" * 80)
        has_life_policies = await Policy.objects.filter(policy_type="life").exists()
        has_health_policies = await Policy.objects.filter(policy_type="health").exists()
        print(f"  Has life policies: {has_life_policies}")
        print(f"  Has health policies: {has_health_policies}")

        # 18. Values and values_list (await)
        print("\n18. Value extraction (await):")
        print("-" * 80)
        policy_numbers = await Policy.objects.all().values_list("policy_number", flat=True)
        print(f"  Policy numbers (first 3): {policy_numbers[:3]}")

        claim_data = await Claim.objects.all().values("claim_number", "status")
        print(f"  Claim data (first 2): {claim_data[:2]}")

        # 19. Get or create (await)
        print("\n19. Get or create policyholder (await):")
        print("-" * 80)
        test_address = AddressSchema(
            street="456 Test Ave", city="Seattle", state="WA", zip_code="98101", country="USA"
        )
        ph, created = await PolicyHolder.objects.get_or_create(
            email="async.test@example.com",
            defaults={
                "first_name": "Async",
                "last_name": "Tester",
                "phone": "555-1111",
                "date_of_birth": date(1992, 5, 15),
                "address": test_address,
                "active": True,
            },
        )
        print(f"  {'Created' if created else 'Found'}: {ph.first_name} {ph.last_name} (ID: {ph.id})")

        # 20. Chained filtering with async for
        print("\n20. Complex chained filtering (async for):")
        print("-" * 80)
        active_auto_qs = (
            Policy.objects.filter(status="active")
            .filter(policy_type="auto")
            .order_by("-premium_amount")
        )
        count = await active_auto_qs.count()
        print(f"  Found {count} active auto policies:")
        async for policy in active_auto_qs:
            print(f"  - {policy.policy_number}: ${policy.premium_amount:,.2f}")

        # 21. Concurrent operations with asyncio.gather
        print("\n21. Concurrent operations with asyncio.gather:")
        print("-" * 80)
        print("  Running multiple queries concurrently...")

        # Create tasks
        active_ph_count_task = PolicyHolder.objects.filter(active=True).count()
        active_policies_task = Policy.objects.filter(status="active").count()
        pending_claims_task = Claim.objects.filter(status="pending").count()
        all_auto_policies_task = Policy.objects.filter(policy_type="auto").count()

        # Run concurrently
        active_ph, active_pol, pending_cl, auto_pol = await asyncio.gather(
            active_ph_count_task,
            active_policies_task,
            pending_claims_task,
            all_auto_policies_task,
        )

        print(f"  Active policyholders: {active_ph}")
        print(f"  Active policies: {active_pol}")
        print(f"  Pending claims: {pending_cl}")
        print(f"  Auto policies: {auto_pol}")

        # 22. Refresh from API (await)
        print("\n22. Refresh policyholder from API (await):")
        print("-" * 80)
        print(f"  Before refresh: {ph.first_name} {ph.last_name}")
        await ph.refresh_from_api()
        print(f"  After refresh: {ph.first_name} {ph.last_name}")

        # 23. First and last (await)
        print("\n23. First and last operations (await):")
        print("-" * 80)
        first_policy = await Policy.objects.order_by("start_date").first()
        last_policy = await Policy.objects.order_by("start_date").last()
        if first_policy and last_policy:
            print(
                f"  First policy by start date: {first_policy.policy_number} "
                f"({first_policy.start_date})"
            )
            print(
                f"  Last policy by start date: {last_policy.policy_number} "
                f"({last_policy.start_date})"
            )

        # 24. Async iteration with slicing
        print("\n24. Async iteration with slicing [1:3]:")
        print("-" * 80)
        async for ph in PolicyHolder.objects.order_by("id")[1:3]:
            print(f"  - {ph.first_name} {ph.last_name} (ID: {ph.id})")

        # 25. Delete operations (await)
        print("\n25. Delete operations (await):")
        print("-" * 80)
        print(f"  Deleting claim {new_claim.id}...")
        await new_claim.delete()
        print("  Claim deleted successfully")

        # 26. Final summary with concurrent aggregation
        print("\n26. Final summary with concurrent aggregation:")
        print("-" * 80)

        # Get counts concurrently
        final_ph_count_task = PolicyHolder.objects.count()
        final_policy_count_task = Policy.objects.count()
        final_claim_count_task = Claim.objects.count()

        final_ph, final_pol, final_cl = await asyncio.gather(
            final_ph_count_task,
            final_policy_count_task,
            final_claim_count_task,
        )

        # Calculate total premium (fetching all policies)
        all_active_policies = []
        async for p in Policy.objects.filter(status="active"):
            all_active_policies.append(p)
        total_premium = sum(p.premium_amount for p in all_active_policies)

        print(f"  Total PolicyHolders: {final_ph}")
        print(f"  Total Policies: {final_pol}")
        print(f"  Total Claims: {final_cl}")
        print(f"  Total Active Premium Revenue: ${total_premium:,.2f}")

    print("\n" + "=" * 80)
    print("All async tests completed successfully!")
    print("=" * 80)


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
