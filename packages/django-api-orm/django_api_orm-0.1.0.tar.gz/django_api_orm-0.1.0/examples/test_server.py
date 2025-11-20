"""FastAPI test server for django-api-orm - Insurance Domain.

This is a development-only server that provides REST API endpoints
to test all features of the django-api-orm library using an insurance context.

Run with: uvicorn examples.test_server:app --host 127.0.0.1 --port 8700 --reload
"""

from datetime import date, datetime
from typing import Any

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, EmailStr, Field

# In-memory storage
policyholders_db: dict[int, dict[str, Any]] = {}
policies_db: dict[int, dict[str, Any]] = {}
claims_db: dict[int, dict[str, Any]] = {}
policyholder_id_counter = 1
policy_id_counter = 1
claim_id_counter = 1


# Schemas
class AddressSchema(BaseModel):
    """Nested address schema."""

    street: str
    city: str
    state: str
    zip_code: str
    country: str = "USA"


class PolicyHolderSchema(BaseModel):
    """PolicyHolder schema with nested address."""

    id: int | None = None
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    date_of_birth: date
    address: AddressSchema
    active: bool = True


class PolicySchema(BaseModel):
    """Policy schema."""

    id: int | None = None
    policy_number: str
    policyholder_id: int
    policy_type: str  # "auto", "home", "life", "health"
    premium_amount: float
    coverage_amount: float
    start_date: date
    end_date: date
    status: str = "active"  # "active", "expired", "cancelled"


class ClaimSchema(BaseModel):
    """Claim schema."""

    id: int | None = None
    claim_number: str
    policy_id: int
    claim_date: date
    incident_date: date
    claim_amount: float
    approved_amount: float | None = None
    status: str = "pending"  # "pending", "approved", "denied", "paid"
    description: str


# Create/Update schemas
class PolicyHolderCreateSchema(BaseModel):
    """Schema for creating a policyholder."""

    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    date_of_birth: date
    address: AddressSchema
    active: bool = True


class PolicyHolderUpdateSchema(BaseModel):
    """Schema for updating a policyholder."""

    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    date_of_birth: date | None = None
    address: AddressSchema | None = None
    active: bool | None = None


class PolicyCreateSchema(BaseModel):
    """Schema for creating a policy."""

    policy_number: str
    policyholder_id: int
    policy_type: str
    premium_amount: float
    coverage_amount: float
    start_date: date
    end_date: date
    status: str = "active"


class PolicyUpdateSchema(BaseModel):
    """Schema for updating a policy."""

    policy_number: str | None = None
    policyholder_id: int | None = None
    policy_type: str | None = None
    premium_amount: float | None = None
    coverage_amount: float | None = None
    start_date: date | None = None
    end_date: date | None = None
    status: str | None = None


class ClaimCreateSchema(BaseModel):
    """Schema for creating a claim."""

    claim_number: str
    policy_id: int
    claim_date: date
    incident_date: date
    claim_amount: float
    approved_amount: float | None = None
    status: str = "pending"
    description: str


class ClaimUpdateSchema(BaseModel):
    """Schema for updating a claim."""

    claim_number: str | None = None
    policy_id: int | None = None
    claim_date: date | None = None
    incident_date: date | None = None
    claim_amount: float | None = None
    approved_amount: float | None = None
    status: str | None = None
    description: str | None = None


# Initialize FastAPI app
app = FastAPI(
    title="django-api-orm Test Server - Insurance Domain",
    description="Development server for testing django-api-orm features with insurance models",
    version="0.1.0",
)


@app.on_event("startup")
async def startup_event() -> None:
    """Initialize with some test data."""
    global policyholder_id_counter, policy_id_counter, claim_id_counter
    global policyholders_db, policies_db, claims_db

    # Add test policyholders
    test_policyholders = [
        {
            "first_name": "John",
            "last_name": "Smith",
            "email": "john.smith@example.com",
            "phone": "555-0101",
            "date_of_birth": date(1980, 5, 15),
            "address": {
                "street": "123 Main St",
                "city": "Springfield",
                "state": "IL",
                "zip_code": "62701",
                "country": "USA",
            },
            "active": True,
        },
        {
            "first_name": "Jane",
            "last_name": "Doe",
            "email": "jane.doe@example.com",
            "phone": "555-0102",
            "date_of_birth": date(1985, 8, 22),
            "address": {
                "street": "456 Oak Ave",
                "city": "Chicago",
                "state": "IL",
                "zip_code": "60601",
                "country": "USA",
            },
            "active": True,
        },
        {
            "first_name": "Bob",
            "last_name": "Johnson",
            "email": "bob.johnson@example.com",
            "phone": "555-0103",
            "date_of_birth": date(1975, 3, 10),
            "address": {
                "street": "789 Pine Rd",
                "city": "Naperville",
                "state": "IL",
                "zip_code": "60540",
                "country": "USA",
            },
            "active": False,
        },
    ]

    for ph_data in test_policyholders:
        policyholders_db[policyholder_id_counter] = {**ph_data, "id": policyholder_id_counter}
        policyholder_id_counter += 1

    # Add test policies
    test_policies = [
        {
            "policy_number": "AUTO-2024-001",
            "policyholder_id": 1,
            "policy_type": "auto",
            "premium_amount": 1200.00,
            "coverage_amount": 100000.00,
            "start_date": date(2024, 1, 1),
            "end_date": date(2024, 12, 31),
            "status": "active",
        },
        {
            "policy_number": "HOME-2024-001",
            "policyholder_id": 1,
            "policy_type": "home",
            "premium_amount": 1500.00,
            "coverage_amount": 300000.00,
            "start_date": date(2024, 1, 1),
            "end_date": date(2024, 12, 31),
            "status": "active",
        },
        {
            "policy_number": "AUTO-2024-002",
            "policyholder_id": 2,
            "policy_type": "auto",
            "premium_amount": 1100.00,
            "coverage_amount": 100000.00,
            "start_date": date(2024, 2, 1),
            "end_date": date(2025, 1, 31),
            "status": "active",
        },
        {
            "policy_number": "LIFE-2023-001",
            "policyholder_id": 2,
            "policy_type": "life",
            "premium_amount": 500.00,
            "coverage_amount": 500000.00,
            "start_date": date(2023, 1, 1),
            "end_date": date(2033, 12, 31),
            "status": "active",
        },
    ]

    for policy_data in test_policies:
        policies_db[policy_id_counter] = {**policy_data, "id": policy_id_counter}
        policy_id_counter += 1

    # Add test claims
    test_claims = [
        {
            "claim_number": "CLM-2024-001",
            "policy_id": 1,
            "claim_date": date(2024, 3, 15),
            "incident_date": date(2024, 3, 10),
            "claim_amount": 5000.00,
            "approved_amount": 4500.00,
            "status": "approved",
            "description": "Minor collision damage to front bumper",
        },
        {
            "claim_number": "CLM-2024-002",
            "policy_id": 2,
            "claim_date": date(2024, 4, 20),
            "incident_date": date(2024, 4, 18),
            "claim_amount": 15000.00,
            "approved_amount": None,
            "status": "pending",
            "description": "Water damage from roof leak",
        },
        {
            "claim_number": "CLM-2024-003",
            "policy_id": 3,
            "claim_date": date(2024, 5, 5),
            "incident_date": date(2024, 5, 3),
            "claim_amount": 3000.00,
            "approved_amount": 3000.00,
            "status": "paid",
            "description": "Windshield replacement",
        },
    ]

    for claim_data in test_claims:
        claims_db[claim_id_counter] = {**claim_data, "id": claim_id_counter}
        claim_id_counter += 1


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint with API info."""
    return {
        "message": "django-api-orm Test Server - Insurance Domain",
        "policyholders_endpoint": "/api/v1/policyholders/",
        "policies_endpoint": "/api/v1/policies/",
        "claims_endpoint": "/api/v1/claims/",
        "docs": "/docs",
    }


# PolicyHolder endpoints
@app.get("/api/v1/policyholders/", response_model=list[PolicyHolderSchema])
async def list_policyholders(
    id: int | None = None,
    active: bool | None = None,
    first_name: str | None = None,
    last_name: str | None = None,
    email: str | None = None,
    state: str | None = None,
    ordering: str | None = Query(None, description="Comma-separated fields, prefix with - for desc"),
    limit: int | None = Query(None, ge=1),
    offset: int | None = Query(None, ge=0),
) -> list[PolicyHolderSchema]:
    """List policyholders with filtering, ordering, and pagination."""
    results = list(policyholders_db.values())

    # Apply filters
    if id is not None:
        results = [ph for ph in results if ph["id"] == id]
    if active is not None:
        results = [ph for ph in results if ph["active"] == active]
    if first_name is not None:
        results = [ph for ph in results if ph["first_name"] == first_name]
    if last_name is not None:
        results = [ph for ph in results if ph["last_name"] == last_name]
    if email is not None:
        results = [ph for ph in results if ph["email"] == email]
    if state is not None:
        results = [ph for ph in results if ph["address"]["state"] == state]

    # Apply ordering
    if ordering:
        for field in reversed(ordering.split(",")):
            field = field.strip()
            reverse = field.startswith("-")
            field_name = field[1:] if reverse else field
            if field_name in ["id", "first_name", "last_name", "email", "active"]:
                results.sort(key=lambda x: x.get(field_name, ""), reverse=reverse)

    # Apply pagination
    if offset is not None:
        results = results[offset:]
    if limit is not None:
        results = results[:limit]

    return [PolicyHolderSchema(**ph) for ph in results]


@app.get("/api/v1/policyholders/{policyholder_id}", response_model=PolicyHolderSchema)
async def get_policyholder(policyholder_id: int) -> PolicyHolderSchema:
    """Get a single policyholder by ID."""
    if policyholder_id not in policyholders_db:
        raise HTTPException(status_code=404, detail="PolicyHolder not found")
    return PolicyHolderSchema(**policyholders_db[policyholder_id])


@app.post("/api/v1/policyholders/", response_model=PolicyHolderSchema, status_code=201)
async def create_policyholder(policyholder: PolicyHolderCreateSchema) -> PolicyHolderSchema:
    """Create a new policyholder."""
    global policyholder_id_counter

    # Check for duplicate email
    for existing_ph in policyholders_db.values():
        if existing_ph["email"] == policyholder.email:
            raise HTTPException(status_code=400, detail="Email already exists")

    ph_data = policyholder.model_dump()
    ph_data["id"] = policyholder_id_counter
    policyholders_db[policyholder_id_counter] = ph_data
    policyholder_id_counter += 1

    return PolicyHolderSchema(**ph_data)


@app.put("/api/v1/policyholders/{policyholder_id}", response_model=PolicyHolderSchema)
async def update_policyholder(
    policyholder_id: int, policyholder: PolicyHolderUpdateSchema
) -> PolicyHolderSchema:
    """Update a policyholder."""
    if policyholder_id not in policyholders_db:
        raise HTTPException(status_code=404, detail="PolicyHolder not found")

    update_data = policyholder.model_dump(exclude_unset=True)
    policyholders_db[policyholder_id].update(update_data)

    return PolicyHolderSchema(**policyholders_db[policyholder_id])


@app.patch("/api/v1/policyholders/{policyholder_id}", response_model=PolicyHolderSchema)
async def partial_update_policyholder(
    policyholder_id: int, policyholder: PolicyHolderUpdateSchema
) -> PolicyHolderSchema:
    """Partially update a policyholder."""
    if policyholder_id not in policyholders_db:
        raise HTTPException(status_code=404, detail="PolicyHolder not found")

    update_data = policyholder.model_dump(exclude_unset=True)
    policyholders_db[policyholder_id].update(update_data)

    return PolicyHolderSchema(**policyholders_db[policyholder_id])


@app.delete("/api/v1/policyholders/{policyholder_id}", status_code=204)
async def delete_policyholder(policyholder_id: int) -> None:
    """Delete a policyholder."""
    if policyholder_id not in policyholders_db:
        raise HTTPException(status_code=404, detail="PolicyHolder not found")
    del policyholders_db[policyholder_id]


# Policy endpoints
@app.get("/api/v1/policies/", response_model=list[PolicySchema])
async def list_policies(
    id: int | None = None,
    policyholder_id: int | None = None,
    policy_type: str | None = None,
    status: str | None = None,
    ordering: str | None = Query(None, description="Comma-separated fields, prefix with - for desc"),
    limit: int | None = Query(None, ge=1),
    offset: int | None = Query(None, ge=0),
) -> list[PolicySchema]:
    """List policies with filtering, ordering, and pagination."""
    results = list(policies_db.values())

    # Apply filters
    if id is not None:
        results = [p for p in results if p["id"] == id]
    if policyholder_id is not None:
        results = [p for p in results if p["policyholder_id"] == policyholder_id]
    if policy_type is not None:
        results = [p for p in results if p["policy_type"] == policy_type]
    if status is not None:
        results = [p for p in results if p["status"] == status]

    # Apply ordering
    if ordering:
        for field in reversed(ordering.split(",")):
            field = field.strip()
            reverse = field.startswith("-")
            field_name = field[1:] if reverse else field
            if field_name in ["id", "policy_number", "premium_amount", "start_date"]:
                results.sort(key=lambda x: x.get(field_name, ""), reverse=reverse)

    # Apply pagination
    if offset is not None:
        results = results[offset:]
    if limit is not None:
        results = results[:limit]

    return [PolicySchema(**policy) for policy in results]


@app.get("/api/v1/policies/{policy_id}", response_model=PolicySchema)
async def get_policy(policy_id: int) -> PolicySchema:
    """Get a single policy by ID."""
    if policy_id not in policies_db:
        raise HTTPException(status_code=404, detail="Policy not found")
    return PolicySchema(**policies_db[policy_id])


@app.post("/api/v1/policies/", response_model=PolicySchema, status_code=201)
async def create_policy(policy: PolicyCreateSchema) -> PolicySchema:
    """Create a new policy."""
    global policy_id_counter

    # Verify policyholder exists
    if policy.policyholder_id not in policyholders_db:
        raise HTTPException(status_code=400, detail="PolicyHolder does not exist")

    # Check for duplicate policy number
    for existing_policy in policies_db.values():
        if existing_policy["policy_number"] == policy.policy_number:
            raise HTTPException(status_code=400, detail="Policy number already exists")

    policy_data = policy.model_dump()
    policy_data["id"] = policy_id_counter
    policies_db[policy_id_counter] = policy_data
    policy_id_counter += 1

    return PolicySchema(**policy_data)


@app.put("/api/v1/policies/{policy_id}", response_model=PolicySchema)
async def update_policy(policy_id: int, policy: PolicyUpdateSchema) -> PolicySchema:
    """Update a policy."""
    if policy_id not in policies_db:
        raise HTTPException(status_code=404, detail="Policy not found")

    update_data = policy.model_dump(exclude_unset=True)
    policies_db[policy_id].update(update_data)

    return PolicySchema(**policies_db[policy_id])


@app.patch("/api/v1/policies/{policy_id}", response_model=PolicySchema)
async def partial_update_policy(policy_id: int, policy: PolicyUpdateSchema) -> PolicySchema:
    """Partially update a policy."""
    if policy_id not in policies_db:
        raise HTTPException(status_code=404, detail="Policy not found")

    update_data = policy.model_dump(exclude_unset=True)
    policies_db[policy_id].update(update_data)

    return PolicySchema(**policies_db[policy_id])


@app.delete("/api/v1/policies/{policy_id}", status_code=204)
async def delete_policy(policy_id: int) -> None:
    """Delete a policy."""
    if policy_id not in policies_db:
        raise HTTPException(status_code=404, detail="Policy not found")
    del policies_db[policy_id]


# Claim endpoints
@app.get("/api/v1/claims/", response_model=list[ClaimSchema])
async def list_claims(
    id: int | None = None,
    policy_id: int | None = None,
    status: str | None = None,
    ordering: str | None = Query(None, description="Comma-separated fields, prefix with - for desc"),
    limit: int | None = Query(None, ge=1),
    offset: int | None = Query(None, ge=0),
) -> list[ClaimSchema]:
    """List claims with filtering, ordering, and pagination."""
    results = list(claims_db.values())

    # Apply filters
    if id is not None:
        results = [c for c in results if c["id"] == id]
    if policy_id is not None:
        results = [c for c in results if c["policy_id"] == policy_id]
    if status is not None:
        results = [c for c in results if c["status"] == status]

    # Apply ordering
    if ordering:
        for field in reversed(ordering.split(",")):
            field = field.strip()
            reverse = field.startswith("-")
            field_name = field[1:] if reverse else field
            if field_name in ["id", "claim_number", "claim_date", "claim_amount"]:
                results.sort(key=lambda x: x.get(field_name, ""), reverse=reverse)

    # Apply pagination
    if offset is not None:
        results = results[offset:]
    if limit is not None:
        results = results[:limit]

    return [ClaimSchema(**claim) for claim in results]


@app.get("/api/v1/claims/{claim_id}", response_model=ClaimSchema)
async def get_claim(claim_id: int) -> ClaimSchema:
    """Get a single claim by ID."""
    if claim_id not in claims_db:
        raise HTTPException(status_code=404, detail="Claim not found")
    return ClaimSchema(**claims_db[claim_id])


@app.post("/api/v1/claims/", response_model=ClaimSchema, status_code=201)
async def create_claim(claim: ClaimCreateSchema) -> ClaimSchema:
    """Create a new claim."""
    global claim_id_counter

    # Verify policy exists
    if claim.policy_id not in policies_db:
        raise HTTPException(status_code=400, detail="Policy does not exist")

    # Check for duplicate claim number
    for existing_claim in claims_db.values():
        if existing_claim["claim_number"] == claim.claim_number:
            raise HTTPException(status_code=400, detail="Claim number already exists")

    claim_data = claim.model_dump()
    claim_data["id"] = claim_id_counter
    claims_db[claim_id_counter] = claim_data
    claim_id_counter += 1

    return ClaimSchema(**claim_data)


@app.put("/api/v1/claims/{claim_id}", response_model=ClaimSchema)
async def update_claim(claim_id: int, claim: ClaimUpdateSchema) -> ClaimSchema:
    """Update a claim."""
    if claim_id not in claims_db:
        raise HTTPException(status_code=404, detail="Claim not found")

    update_data = claim.model_dump(exclude_unset=True)
    claims_db[claim_id].update(update_data)

    return ClaimSchema(**claims_db[claim_id])


@app.patch("/api/v1/claims/{claim_id}", response_model=ClaimSchema)
async def partial_update_claim(claim_id: int, claim: ClaimUpdateSchema) -> ClaimSchema:
    """Partially update a claim."""
    if claim_id not in claims_db:
        raise HTTPException(status_code=404, detail="Claim not found")

    update_data = claim.model_dump(exclude_unset=True)
    claims_db[claim_id].update(update_data)

    return ClaimSchema(**claims_db[claim_id])


@app.delete("/api/v1/claims/{claim_id}", status_code=204)
async def delete_claim(claim_id: int) -> None:
    """Delete a claim."""
    if claim_id not in claims_db:
        raise HTTPException(status_code=404, detail="Claim not found")
    del claims_db[claim_id]


# Utility endpoints
@app.post("/api/v1/policyholders/bulk/", response_model=list[PolicyHolderSchema], status_code=201)
async def bulk_create_policyholders(
    policyholders: list[PolicyHolderCreateSchema],
) -> list[PolicyHolderSchema]:
    """Bulk create policyholders."""
    global policyholder_id_counter
    created_policyholders = []

    for ph in policyholders:
        ph_data = ph.model_dump()
        ph_data["id"] = policyholder_id_counter
        policyholders_db[policyholder_id_counter] = ph_data
        created_policyholders.append(PolicyHolderSchema(**ph_data))
        policyholder_id_counter += 1

    return created_policyholders


@app.delete("/api/v1/reset/", status_code=204)
async def reset_database() -> None:
    """Reset the database to initial state."""
    global policyholder_id_counter, policy_id_counter, claim_id_counter
    global policyholders_db, policies_db, claims_db
    policyholders_db.clear()
    policies_db.clear()
    claims_db.clear()
    policyholder_id_counter = 1
    policy_id_counter = 1
    claim_id_counter = 1
    await startup_event()
