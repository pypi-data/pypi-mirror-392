# Insurance Domain - Django API ORM Test Server

This directory contains a complete insurance domain implementation for testing the django-api-orm library with realistic, nested schemas and relationships.

## Domain Models

### 1. PolicyHolder (with nested Address)
The primary entity representing insurance policyholders.

**Fields:**
- `id`: int (auto-generated)
- `first_name`: str
- `last_name`: str
- `email`: EmailStr (unique)
- `phone`: str
- `date_of_birth`: date
- `address`: AddressSchema (nested)
  - `street`: str
  - `city`: str
  - `state`: str
  - `zip_code`: str
  - `country`: str (default: "USA")
- `active`: bool (default: True)

**Endpoints:**
- `GET /api/v1/policyholders/` - List with filtering (active, first_name, last_name, email, state)
- `GET /api/v1/policyholders/{id}` - Get by ID
- `POST /api/v1/policyholders/` - Create
- `PUT /api/v1/policyholders/{id}` - Full update
- `PATCH /api/v1/policyholders/{id}` - Partial update
- `DELETE /api/v1/policyholders/{id}` - Delete
- `POST /api/v1/policyholders/bulk/` - Bulk create

### 2. Policy
Insurance policies associated with policyholders.

**Fields:**
- `id`: int (auto-generated)
- `policy_number`: str (unique)
- `policyholder_id`: int (foreign key to PolicyHolder)
- `policy_type`: str ("auto", "home", "life", "health")
- `premium_amount`: float
- `coverage_amount`: float
- `start_date`: date
- `end_date`: date
- `status`: str ("active", "expired", "cancelled")

**Endpoints:**
- `GET /api/v1/policies/` - List with filtering (policyholder_id, policy_type, status)
- `GET /api/v1/policies/{id}` - Get by ID
- `POST /api/v1/policies/` - Create
- `PUT /api/v1/policies/{id}` - Full update
- `PATCH /api/v1/policies/{id}` - Partial update
- `DELETE /api/v1/policies/{id}` - Delete

### 3. Claim
Insurance claims filed against policies.

**Fields:**
- `id`: int (auto-generated)
- `claim_number`: str (unique)
- `policy_id`: int (foreign key to Policy)
- `claim_date`: date
- `incident_date`: date
- `claim_amount`: float
- `approved_amount`: float | None
- `status`: str ("pending", "approved", "denied", "paid")
- `description`: str

**Endpoints:**
- `GET /api/v1/claims/` - List with filtering (policy_id, status)
- `GET /api/v1/claims/{id}` - Get by ID
- `POST /api/v1/claims/` - Create
- `PUT /api/v1/claims/{id}` - Full update
- `PATCH /api/v1/claims/{id}` - Partial update
- `DELETE /api/v1/claims/{id}` - Delete

## Relationships

```
PolicyHolder (1) ----< (many) Policy (1) ----< (many) Claim
```

- One PolicyHolder can have multiple Policies
- One Policy can have multiple Claims
- Policies must have a valid PolicyHolder
- Claims must have a valid Policy

## Sample Data

The test server initializes with:

### PolicyHolders (3)
1. John Smith - Springfield, IL (Active)
2. Jane Doe - Chicago, IL (Active)
3. Bob Johnson - Naperville, IL (Inactive)

### Policies (4)
1. AUTO-2024-001 - John Smith's auto policy
2. HOME-2024-001 - John Smith's home policy
3. AUTO-2024-002 - Jane Doe's auto policy
4. LIFE-2023-001 - Jane Doe's life policy

### Claims (3)
1. CLM-2024-001 - Auto claim (approved)
2. CLM-2024-002 - Home claim (pending)
3. CLM-2024-003 - Auto claim (paid)

## Features Demonstrated

### 1. Nested Schemas
The `PolicyHolder` model demonstrates nested Pydantic schemas with the `address` field:

```python
class AddressSchema(BaseModel):
    street: str
    city: str
    state: str
    zip_code: str
    country: str = "USA"

class PolicyHolderSchema(BaseModel):
    # ... other fields
    address: AddressSchema  # Nested schema
```

### 2. Foreign Key Relationships
Policies and Claims demonstrate foreign key relationships:

```python
# Filter policies by policyholder
Policy.objects.filter(policyholder_id=1)

# Filter claims by policy
Claim.objects.filter(policy_id=1)
```

### 3. Complex Filtering
```python
# Filter by nested field
PolicyHolder.objects.filter(state="IL")

# Chain multiple filters
Policy.objects.filter(status="active").filter(policy_type="auto")

# Filter with multiple conditions
Claim.objects.filter(status="approved", policy_id=1)
```

### 4. Business Logic Features

**Policyholder Management:**
- Email uniqueness validation
- Active/inactive status tracking
- Address information with nested schema
- Filter by state (nested field)

**Policy Management:**
- Policy type categorization (auto, home, life, health)
- Premium and coverage tracking
- Date-based policy periods
- Status management (active, expired, cancelled)
- Validation that policyholder exists

**Claim Processing:**
- Claim lifecycle (pending → approved/denied → paid)
- Incident date tracking
- Claim amount vs approved amount
- Validation that policy exists

## Usage Examples

### Create a PolicyHolder with Nested Address

```python
from datetime import date
from pydantic import BaseModel

address = AddressSchema(
    street="123 Main St",
    city="Chicago",
    state="IL",
    zip_code="60601",
    country="USA"
)

policyholder = PolicyHolder.objects.create(
    first_name="John",
    last_name="Doe",
    email="john.doe@example.com",
    phone="555-0100",
    date_of_birth=date(1980, 1, 1),
    address=address,
    active=True
)

# Access nested fields
print(policyholder.address.city)  # "Chicago"
print(policyholder.address.state)  # "IL"
```

### Filter by Relationship

```python
# Get all policies for a policyholder
policyholder_policies = Policy.objects.filter(
    policyholder_id=policyholder.id
)

# Get all claims for a specific policy
policy_claims = Claim.objects.filter(
    policy_id=policy.id
)
```

### Complex Queries

```python
# Find all active auto policies with premium > $1000
expensive_auto = (
    Policy.objects
    .filter(status="active")
    .filter(policy_type="auto")
    .filter(premium_amount__gt=1000)  # Note: Django-style filtering
)

# Get approved claims for auto policies
auto_claims = Claim.objects.filter(
    status="approved",
    policy_id__in=[p.id for p in Policy.objects.filter(policy_type="auto")]
)
```

### Business Metrics

```python
# Calculate total premium revenue
total_premium = sum(
    p.premium_amount
    for p in Policy.objects.filter(status="active")
)

# Count pending claims
pending_claims = Claim.objects.filter(status="pending").count()

# Get policyholder with most policies
# (Would require aggregation - not yet implemented)
```

## API Testing

### Using curl

```bash
# Create a policyholder
curl -X POST http://localhost:8700/api/v1/policyholders/ \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Alice",
    "last_name": "Williams",
    "email": "alice@example.com",
    "phone": "555-0200",
    "date_of_birth": "1990-05-15",
    "address": {
      "street": "456 Elm St",
      "city": "Boston",
      "state": "MA",
      "zip_code": "02101",
      "country": "USA"
    },
    "active": true
  }'

# Filter policyholders by state
curl "http://localhost:8700/api/v1/policyholders/?state=IL"

# Get policies for a specific policyholder
curl "http://localhost:8700/api/v1/policies/?policyholder_id=1"

# Create a claim
curl -X POST http://localhost:8700/api/v1/claims/ \
  -H "Content-Type: application/json" \
  -d '{
    "claim_number": "CLM-2024-999",
    "policy_id": 1,
    "claim_date": "2024-06-15",
    "incident_date": "2024-06-10",
    "claim_amount": 5000.00,
    "status": "pending",
    "description": "Vehicle damage from collision"
  }'

# Update claim status
curl -X PATCH http://localhost:8700/api/v1/claims/1 \
  -H "Content-Type: application/json" \
  -d '{
    "status": "approved",
    "approved_amount": 4500.00
  }'
```

## Running the Tests

### 1. Start the Server
```bash
uvicorn examples.test_server:app --host 127.0.0.1 --port 8700 --reload
```

### 2. Run Synchronous Tests
```bash
uv run python examples/test_with_server.py
```

### 3. Run Asynchronous Tests
```bash
uv run python examples/test_with_server_async.py
```

### 4. Use the Interactive Docs
Open http://localhost:8700/docs in your browser to explore and test the API interactively.

## What's Tested

Both test scripts (`test_with_server.py` and `test_with_server_async.py`) demonstrate:

1. **CRUD Operations** - Create, Read, Update, Delete on all models
2. **Nested Schema Handling** - Working with the nested Address schema
3. **Relationship Filtering** - Filtering by foreign keys (policyholder_id, policy_id)
4. **Complex Queries** - Chained filters, ordering, slicing
5. **Aggregations** - Count, exists, sum calculations
6. **Value Extraction** - values() and values_list()
7. **Django ORM Patterns** - get(), filter(), first(), last(), order_by()
8. **Async Patterns** - async for, await, asyncio.gather()
9. **Error Handling** - Validation errors, not found errors
10. **Business Logic** - Premium calculations, claim approvals

## Design Decisions

### Why Insurance Domain?

1. **Real-world complexity** - Insurance has natural hierarchies and relationships
2. **Nested data** - Addresses are a common nested schema use case
3. **Business rules** - Status workflows, validations, calculations
4. **Multiple entity types** - Demonstrates relationships between models
5. **Relatable** - Most people understand insurance concepts

### Schema Design

- **Nested Address** - Demonstrates complex Pydantic models
- **Foreign Keys** - Shows relationships without Django's ORM magic
- **Status Fields** - Demonstrates enum-like string fields
- **Date Fields** - Common in business applications
- **Monetary Fields** - Float handling for currency (simplified)

### API Design

- **RESTful** - Standard HTTP methods and status codes
- **Filtering** - Query parameters for common filters
- **Validation** - Email uniqueness, foreign key existence
- **Pagination** - Limit/offset support
- **Ordering** - Ascending/descending sorting

## Future Enhancements

Potential additions to demonstrate more features:

1. **Aggregation Endpoints** - Sum, avg, max, min
2. **Bulk Operations** - Bulk update, bulk delete
3. **Search** - Full-text search on descriptions
4. **Computed Fields** - Age from date_of_birth, days until expiry
5. **Transactions** - Atomic operations across models
6. **Webhooks** - Notifications on claim status changes
7. **File Uploads** - Claim documentation attachments
8. **Audit Trail** - Track changes to records
9. **Soft Deletes** - Mark as deleted instead of removing
10. **Versioning** - Track policy versions over time

## Conclusion

This insurance domain provides a comprehensive, realistic test environment for django-api-orm that demonstrates:

- Nested Pydantic schemas
- Foreign key relationships
- Complex filtering and querying
- Business logic patterns
- Both synchronous and asynchronous usage

All while using a familiar, real-world domain that's easy to understand and extend.
