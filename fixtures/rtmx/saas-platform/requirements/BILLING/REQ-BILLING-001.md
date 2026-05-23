# REQ-BILLING-001: Plan Definitions

## Status: MISSING
## Priority: P0
## Phase: 4

## Requirement

Define and implement billing plan definitions with resource limits for each tier. The platform supports four plans: free, starter, business, and enterprise. Each plan specifies limits on members, projects, resources, and API keys. Plan definitions are used by quota enforcement to gate create operations and by the billing endpoints to display current plan details.

## Acceptance Criteria

1. The system defines four billing plans: free, starter, business, and enterprise.
2. The free plan allows 3 members, 2 projects, 50 resources, and 1 API key at $0/month.
3. The starter plan allows 10 members, 10 projects, 500 resources, and 5 API keys at $29/month.
4. The business plan allows 50 members, 50 projects, 5000 resources, and 25 API keys at $99/month.
5. The enterprise plan allows unlimited members, projects, resources, and API keys at $299/month.
6. GET /orgs/:slug/billing/plan returns the current plan name, limits, current usage counts, and price.
7. New organizations are assigned the "free" plan by default.
8. Plan definitions are immutable at runtime; they are configured in the application code or seed data.
9. The response includes both the limit and current count for each resource type to show usage against limits.
10. Only members of the organization can view the billing plan; non-members receive 404 Not Found.
11. The billing plan endpoint is accessible to all roles (owner, admin, member, viewer).

## API Endpoints

### GET /orgs/:slug/billing/plan

**Response (200 OK):**
```json
{
  "plan": "starter",
  "price_cents_monthly": 2900,
  "limits": {
    "max_members": 10,
    "max_projects": 10,
    "max_resources": 500,
    "max_api_keys": 5
  },
  "usage": {
    "members": 4,
    "projects": 3,
    "resources": 47,
    "api_keys": 2
  }
}
```

### Plan Definitions Reference

```json
[
  {"plan": "free", "max_members": 3, "max_projects": 2, "max_resources": 50, "max_api_keys": 1, "price_cents_monthly": 0},
  {"plan": "starter", "max_members": 10, "max_projects": 10, "max_resources": 500, "max_api_keys": 5, "price_cents_monthly": 2900},
  {"plan": "business", "max_members": 50, "max_projects": 50, "max_resources": 5000, "max_api_keys": 25, "price_cents_monthly": 9900},
  {"plan": "enterprise", "max_members": -1, "max_projects": -1, "max_resources": -1, "max_api_keys": -1, "price_cents_monthly": 29900}
]
```

## Dependencies

- REQ-TENANT-001: Requires organization creation to associate a plan with an organization.
