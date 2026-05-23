# REQ-QUOTA-002: Quota Warning Notifications

## Status: MISSING
## Priority: HIGH
## Phase: 6

## Requirement

Implement proactive quota warning notifications that alert organization owners and admins when resource usage reaches 80% of the plan limit. Warnings are generated for members, projects, resources, and API key quotas. Each warning is sent at most once per billing period per metric to avoid notification fatigue. Quota warnings help organizations take action before hitting hard limits.

## Acceptance Criteria

1. When an organization reaches 80% of its plan limit for members, a quota warning notification is created.
2. When an organization reaches 80% of its plan limit for projects, a quota warning notification is created.
3. When an organization reaches 80% of its plan limit for resources, a quota warning notification is created.
4. When an organization reaches 80% of its plan limit for API keys, a quota warning notification is created.
5. Quota warning notifications are sent to all owners and admins of the affected organization.
6. Each quota warning notification includes the metric name, current usage, and plan limit in the body.
7. Only one warning notification is sent per metric per billing period, even if usage fluctuates around the threshold.
8. Organizations on the enterprise plan (unlimited limits) never receive quota warnings.
9. GET /orgs/:slug/billing/plan includes a warnings array listing any metrics currently at or above 80%.
10. Quota warnings are checked on every create operation that increments a counted resource.

## API Endpoints

### GET /orgs/:slug/billing/plan

**Response (200 OK):**
```json
{
  "plan": "starter",
  "limits": {
    "max_members": 10,
    "max_projects": 10,
    "max_resources": 500,
    "max_api_keys": 5
  },
  "usage": {
    "members": 8,
    "projects": 9,
    "resources": 120,
    "api_keys": 2
  },
  "warnings": [
    {
      "metric": "members",
      "current": 8,
      "limit": 10,
      "percent": 80
    },
    {
      "metric": "projects",
      "current": 9,
      "limit": 10,
      "percent": 90
    }
  ]
}
```

## Dependencies

- REQ-QUOTA-001: Requires quota enforcement to track current usage against plan limits.
- REQ-APIKEY-003: Requires API key scope enforcement to count API keys against limits.
- REQ-NOTIF-002: Requires automated lifecycle notifications for delivering quota warnings to users.
