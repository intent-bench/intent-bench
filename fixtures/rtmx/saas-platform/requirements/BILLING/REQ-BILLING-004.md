# REQ-BILLING-004: Usage Tracking

## Status: MISSING
## Priority: HIGH
## Phase: 7

## Requirement

Implement metered usage tracking that records api_calls, storage_bytes, and resources_created metrics per organization. Usage records are aggregated per billing period and exposed via an endpoint for organization owners to monitor consumption. Usage data feeds into quota enforcement, billing invoices, and analytics.

## Acceptance Criteria

1. GET /orgs/:slug/billing/usage returns current period usage metrics for the organization.
2. Usage metrics include api_calls, storage_bytes, and resources_created counters.
3. Each usage record includes org_id, metric, value, and recorded_at timestamp.
4. API calls are counted on every authenticated request scoped to the organization.
5. The resources_created metric increments when a new resource is created within any project in the organization.
6. The storage_bytes metric tracks the total size of resource metadata across the organization.
7. Usage is aggregated per billing period (monthly) with period_start and period_end boundaries.
8. GET /orgs/:slug/billing/usage returns 403 if the authenticated user is not an owner of the organization.
9. Usage data is scoped to the organization via tenant isolation.
10. Historical usage for past billing periods is retained and accessible via the invoices endpoint.

## API Endpoints

### GET /orgs/:slug/billing/usage

**Request:**
```
GET /orgs/acme/billing/usage
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "org_id": 1,
  "period_start": "2026-01-01T00:00:00Z",
  "period_end": "2026-01-31T23:59:59Z",
  "metrics": {
    "api_calls": 12450,
    "storage_bytes": 5242880,
    "resources_created": 87
  }
}
```

**Error (403 Forbidden):**
```json
{
  "error": "owner access required"
}
```

## Dependencies

- REQ-BILLING-003: Requires invoice generation to associate usage data with billing periods.
