# REQ-ANALYTICS-002: Platform-Wide Analytics

## Status: MISSING
## Priority: HIGH
## Phase: 9

## Requirement

Implement a platform-wide analytics endpoint for platform administrators that provides aggregate business intelligence metrics across all organizations. The dashboard includes total counts for organizations, users, projects, and resources, revenue summaries by plan tier, and growth trends. This enables platform operators to monitor overall platform health and business performance.

## Acceptance Criteria

1. GET /admin/analytics returns platform-wide aggregate metrics.
2. The response includes total_orgs, total_users, total_projects, and total_resources counts.
3. The response includes revenue breakdown by plan tier (free, starter, business, enterprise) with org counts and monthly revenue per tier.
4. The response includes growth metrics showing new organizations and new users in the current period.
5. The response includes active_orgs count (organizations with at least one API call in the current period).
6. GET /admin/analytics returns 403 if the authenticated user does not have is_platform_admin=true.
7. Analytics are calculated from live data and reflect the current state of the platform.
8. The endpoint responds within acceptable performance bounds even with large datasets.

## API Endpoints

### GET /admin/analytics

**Request:**
```
GET /admin/analytics
Authorization: Bearer <admin_token>
```

**Response (200 OK):**
```json
{
  "totals": {
    "organizations": 150,
    "users": 2400,
    "projects": 890,
    "resources": 45000
  },
  "revenue": {
    "total_monthly_cents": 1250000,
    "by_plan": {
      "free": {"orgs": 80, "revenue_cents": 0},
      "starter": {"orgs": 40, "revenue_cents": 116000},
      "business": {"orgs": 25, "revenue_cents": 247500},
      "enterprise": {"orgs": 5, "revenue_cents": 149500}
    }
  },
  "growth": {
    "new_orgs_this_period": 12,
    "new_users_this_period": 85
  },
  "active_orgs": 120
}
```

**Error (403 Forbidden):**
```json
{
  "error": "platform admin access required"
}
```

## Dependencies

- REQ-ANALYTICS-001: Requires organization usage analytics to provide per-org metrics for platform aggregation.
- REQ-ADMIN-002: Requires platform admin audit log access for admin authorization patterns.
- REQ-WEBHOOK-004: Requires webhook delivery history to include integration health metrics.
- REQ-SEARCH-001: Requires full-text search infrastructure for search usage metrics.
