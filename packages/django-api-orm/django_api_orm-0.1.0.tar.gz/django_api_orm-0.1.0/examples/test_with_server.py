"""Test script for django-api-orm with the local test server - Insurance Domain.

This script demonstrates all features of django-api-orm using the local FastAPI test server
with insurance models (PolicyHolder, Policy, Claim).

Make sure the test server is running first:
    uvicorn examples.test_server:app --host 127.0.0.1 --port 8700 --reload

Then run this script:
    uv run python examples/test_with_server.py
"""

from datetime import date

from pydantic import BaseModel, EmailStr

from django_api_orm import APIModel, ServiceClient, register_models


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


# Define API models
class PolicyHolder(APIModel):
    """PolicyHolder model for /api/v1/policyholders/ endpoint."""

    _schema_class = PolicyHolderSchema
    _endpoint = "/api/v1/policyholders/"


class Policy(APIModel):
    """Policy model for /api/v1/policies/ endpoint."""

    _schema_class = PolicySchema
    _endpoint = "/api/v1/policies/"


class Claim(APIModel):
    """Claim model for /api/v1/claims/ endpoint."""

    _schema_class = ClaimSchema
    _endpoint = "/api/v1/claims/"


def main() -> None:
    """Main example function testing all django-api-orm features with insurance models."""
    print("=" * 80)
    print("django-api-orm Feature Test - Insurance Domain")
    print("=" * 80)

    # Create client (pointing to local test server)
    with ServiceClient(base_url="http://localhost:8700") as client:
        # Register models with client
        register_models(client, PolicyHolder, Policy, Claim)

        # 1. Query all policyholders
        print("\n1. Query all policyholders (PolicyHolder.objects.all()):")
        print("-" * 80)
        policyholders = PolicyHolder.objects.all()
        for ph in policyholders:
            print(
                f"  - {ph.first_name} {ph.last_name} ({ph.email}) "
                f"[{ph.address.city}, {ph.address.state}] Active: {ph.active}"
            )

        # 2. Filter active policyholders
        print("\n2. Filter active policyholders (PolicyHolder.objects.filter(active=True)):")
        print("-" * 80)
        active_policyholders = PolicyHolder.objects.filter(active=True)
        for ph in active_policyholders:
            print(f"  - {ph.first_name} {ph.last_name}")

        # 3. Filter by nested field (state)
        print("\n3. Filter by nested field - state (PolicyHolder.objects.filter(state='IL')):")
        print("-" * 80)
        il_policyholders = PolicyHolder.objects.filter(state="IL")
        for ph in il_policyholders:
            print(f"  - {ph.first_name} {ph.last_name} in {ph.address.city}, {ph.address.state}")

        # 4. Get a single policyholder
        print("\n4. Get policyholder by ID (PolicyHolder.objects.get(id=1)):")
        print("-" * 80)
        try:
            ph = PolicyHolder.objects.get(id=1)
            print(f"  Found: {ph.first_name} {ph.last_name}")
            print(f"  Address: {ph.address.street}, {ph.address.city}")
        except Exception as e:
            print(f"  Error: {e}")

        # 5. Create a new policyholder with nested address
        print("\n5. Create new policyholder with nested address:")
        print("-" * 80)
        try:
            new_address = AddressSchema(
                street="999 Test Blvd",
                city="Testville",
                state="CA",
                zip_code="90210",
                country="USA",
            )
            new_ph = PolicyHolder.objects.create(
                first_name="Sarah",
                last_name="Connor",
                email=f"sarah.connor+{id(client)}@example.com",
                phone="555-9999",
                date_of_birth=date(1965, 11, 13),
                address=new_address,
                active=True,
            )
            print(f"  Created: {new_ph.first_name} {new_ph.last_name} (ID: {new_ph.id})")
            print(f"  Address: {new_ph.address.city}, {new_ph.address.state}")
        except Exception as e:
            print(f"  Error: {e}")

        # 6. Query all policies
        print("\n6. Query all policies (Policy.objects.all()):")
        print("-" * 80)
        policies = Policy.objects.all()
        for policy in policies:
            print(
                f"  - {policy.policy_number} ({policy.policy_type}) "
                f"- PolicyHolder ID: {policy.policyholder_id} "
                f"- Premium: ${policy.premium_amount:,.2f}"
            )

        # 7. Filter policies by type
        print("\n7. Filter auto policies (Policy.objects.filter(policy_type='auto')):")
        print("-" * 80)
        auto_policies = Policy.objects.filter(policy_type="auto")
        for policy in auto_policies:
            print(f"  - {policy.policy_number} - Coverage: ${policy.coverage_amount:,.2f}")

        # 8. Filter policies by policyholder (relationship)
        print("\n8. Filter policies by policyholder ID (Policy.objects.filter(policyholder_id=1)):")
        print("-" * 80)
        ph1_policies = Policy.objects.filter(policyholder_id=1)
        for policy in ph1_policies:
            print(f"  - {policy.policy_number} ({policy.policy_type})")

        # 9. Create a new policy
        print("\n9. Create new policy:")
        print("-" * 80)
        try:
            new_policy = Policy.objects.create(
                policy_number=f"HEALTH-2024-{id(client)}",
                policyholder_id=1,
                policy_type="health",
                premium_amount=800.00,
                coverage_amount=50000.00,
                start_date=date(2024, 1, 1),
                end_date=date(2024, 12, 31),
                status="active",
            )
            print(f"  Created: {new_policy.policy_number}")
            print(f"  Type: {new_policy.policy_type}, Premium: ${new_policy.premium_amount:,.2f}")
        except Exception as e:
            print(f"  Error: {e}")

        # 10. Query all claims
        print("\n10. Query all claims (Claim.objects.all()):")
        print("-" * 80)
        claims = Claim.objects.all()
        for claim in claims:
            print(
                f"  - {claim.claim_number} (Policy ID: {claim.policy_id}) "
                f"- Amount: ${claim.claim_amount:,.2f} - Status: {claim.status}"
            )

        # 11. Filter claims by status
        print("\n11. Filter approved claims (Claim.objects.filter(status='approved')):")
        print("-" * 80)
        approved_claims = Claim.objects.filter(status="approved")
        for claim in approved_claims:
            print(
                f"  - {claim.claim_number} - Claim: ${claim.claim_amount:,.2f}, "
                f"Approved: ${claim.approved_amount:,.2f}"
            )

        # 12. Filter claims by policy (relationship)
        print("\n12. Filter claims by policy ID (Claim.objects.filter(policy_id=1)):")
        print("-" * 80)
        policy1_claims = Claim.objects.filter(policy_id=1)
        for claim in policy1_claims:
            print(f"  - {claim.claim_number}: {claim.description}")

        # 13. Create a new claim
        print("\n13. Create new claim:")
        print("-" * 80)
        try:
            new_claim = Claim.objects.create(
                claim_number=f"CLM-2024-{id(client)}",
                policy_id=1,
                claim_date=date(2024, 6, 15),
                incident_date=date(2024, 6, 10),
                claim_amount=2500.00,
                approved_amount=None,
                status="pending",
                description="Test claim from script",
            )
            print(f"  Created: {new_claim.claim_number}")
            print(f"  Amount: ${new_claim.claim_amount:,.2f}, Status: {new_claim.status}")
        except Exception as e:
            print(f"  Error: {e}")

        # 14. Update operations
        print("\n14. Update claim status to approved:")
        print("-" * 80)
        new_claim.status = "approved"
        new_claim.approved_amount = 2500.00
        new_claim.save(update_fields=["status", "approved_amount"])
        print(f"  Updated {new_claim.claim_number} to {new_claim.status}")
        print(f"  Approved amount: ${new_claim.approved_amount:,.2f}")

        # 15. Ordering
        print("\n15. Order policies by premium (descending):")
        print("-" * 80)
        ordered_policies = Policy.objects.order_by("-premium_amount")[:3]
        for policy in ordered_policies:
            print(f"  - {policy.policy_number}: ${policy.premium_amount:,.2f}")

        # 16. Count operations
        print("\n16. Count operations:")
        print("-" * 80)
        total_policyholders = PolicyHolder.objects.count()
        active_policyholders_count = PolicyHolder.objects.filter(active=True).count()
        total_policies = Policy.objects.count()
        active_policies = Policy.objects.filter(status="active").count()
        total_claims = Claim.objects.count()
        pending_claims = Claim.objects.filter(status="pending").count()
        print(f"  Total PolicyHolders: {total_policyholders} (Active: {active_policyholders_count})")
        print(f"  Total Policies: {total_policies} (Active: {active_policies})")
        print(f"  Total Claims: {total_claims} (Pending: {pending_claims})")

        # 17. Exists check
        print("\n17. Exists check:")
        print("-" * 80)
        has_life_policies = Policy.objects.filter(policy_type="life").exists()
        has_health_policies = Policy.objects.filter(policy_type="health").exists()
        print(f"  Has life policies: {has_life_policies}")
        print(f"  Has health policies: {has_health_policies}")

        # 18. Values and values_list
        print("\n18. Value extraction:")
        print("-" * 80)
        policy_numbers = Policy.objects.values_list("policy_number", flat=True)
        print(f"  Policy numbers: {policy_numbers[:3]}...")

        claim_data = Claim.objects.values("claim_number", "status")
        print(f"  Claim data (first 2): {claim_data[:2]}")

        # 19. Get or create
        print("\n19. Get or create policyholder:")
        print("-" * 80)
        test_address = AddressSchema(
            street="123 Test St", city="Boston", state="MA", zip_code="02101", country="USA"
        )
        ph, created = PolicyHolder.objects.get_or_create(
            email="test.user@example.com",
            defaults={
                "first_name": "Test",
                "last_name": "User",
                "phone": "555-0000",
                "date_of_birth": date(1990, 1, 1),
                "address": test_address,
                "active": True,
            },
        )
        print(f"  {'Created' if created else 'Found'}: {ph.first_name} {ph.last_name} (ID: {ph.id})")

        # 20. Chained filtering
        print("\n20. Complex chained filtering:")
        print("-" * 80)
        active_auto_policies = (
            Policy.objects.filter(status="active").filter(policy_type="auto").order_by("-premium_amount")
        )
        print(f"  Found {active_auto_policies.count()} active auto policies:")
        for policy in active_auto_policies:
            print(f"  - {policy.policy_number}: ${policy.premium_amount:,.2f}")

        # 21. Refresh from API
        print("\n21. Refresh policyholder from API:")
        print("-" * 80)
        print(f"  Before refresh: {ph.first_name} {ph.last_name}")
        ph.refresh_from_api()
        print(f"  After refresh: {ph.first_name} {ph.last_name}")

        # 22. Delete operations
        print("\n22. Delete operations:")
        print("-" * 80)
        print(f"  Deleting claim {new_claim.id}...")
        new_claim.delete()
        print("  Claim deleted successfully")

        # 23. Slicing
        print("\n23. Slicing - get 2nd and 3rd policyholders:")
        print("-" * 80)
        sliced_phs = PolicyHolder.objects.order_by("id")[1:3]
        for ph in sliced_phs:
            print(f"  - {ph.first_name} {ph.last_name} (ID: {ph.id})")

        # 24. First and last
        print("\n24. First and last operations:")
        print("-" * 80)
        first_policy = Policy.objects.order_by("start_date").first()
        last_policy = Policy.objects.order_by("start_date").last()
        if first_policy and last_policy:
            print(f"  First policy by start date: {first_policy.policy_number} ({first_policy.start_date})")
            print(f"  Last policy by start date: {last_policy.policy_number} ({last_policy.start_date})")

        # 25. Final summary
        print("\n25. Final summary:")
        print("-" * 80)
        final_ph_count = PolicyHolder.objects.count()
        final_policy_count = Policy.objects.count()
        final_claim_count = Claim.objects.count()
        total_premium = sum(
            p.premium_amount for p in Policy.objects.filter(status="active")
        )
        print(f"  Total PolicyHolders: {final_ph_count}")
        print(f"  Total Policies: {final_policy_count}")
        print(f"  Total Claims: {final_claim_count}")
        print(f"  Total Active Premium Revenue: ${total_premium:,.2f}")

    print("\n" + "=" * 80)
    print("All tests completed successfully!")
    print("=" * 80)


if __name__ == "__main__":
    main()
