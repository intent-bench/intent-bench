# REQ-ANALYTICS-001: Organization Usage Analytics

## Status: MISSING
## Priority: HIGH
## Phase: 8

## Requirement

Implement organization-level usage analytics that provide aggregated metrics for organization owners. The analytics endpoint returns usage summaries for the current and previous billing periods, including API call counts, storage consumption, resource creation rates, and active member counts. This enables organization owners to understand consumption patterns and make informed decisions about plan selection.

## Acceptance Criteria

1. GET /orgs/:slug/analytics returns aggregated usage metrics for the organization.
2. The response includes current period and previous period metrics for comparison.
3. Metrics include api_calls, storage_bytes, resources_created, and active_members.
4. Each metric includes the current value and the value from the previous billing period.
5. The response includes the billing period boundaries (period_start, period_end).
6. GET /orgs/:slug/analytics supports an optional period query parameter to view historical periods.
7. GET /orgs/:slug/analytics returns 403 if the authenticated user is not an owner of the organization.
8. Analytics data is scoped to the organization via tenant isolation.
9. Analytics calculations do not impact the performance of other API endpoints.

## API Endpoints

### GET /orgs/:slug/analytics

**Request:**
```
GET /orgs/acme/analytics
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "org_id": 1,
  "period": {
    "start": "2026-01-01T00:00:00Z",
    "end": "2026-01-31T23:59:59Z"
  },
  "metrics": {
    "api_calls": {
      "current": 12450,
      "previous": 9800
    },
    "storage_bytes": {
      "current": 5242880,
      "previous": 4194304
    },
    "resources_created": {
      "current": 87,
      "previous": 65
    },
    "active_members": {
      "current": 18,
      "previous": 15
    }
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

- REQ-BILLING-004: Requires usage tracking to provide the raw usage data for aggregation.
