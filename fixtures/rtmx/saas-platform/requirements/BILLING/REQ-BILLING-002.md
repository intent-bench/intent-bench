# REQ-BILLING-002: Plan Upgrade and Downgrade

## Status: MISSING
## Priority: P0
## Phase: 4

## Requirement

Implement plan change functionality allowing organization owners to upgrade or downgrade their billing plan. Upgrades take effect immediately and increase resource limits. Downgrades must validate that current usage does not exceed the new plan's limits before allowing the change. Only the organization owner can change the billing plan.

## Acceptance Criteria

1. PUT /orgs/:slug/billing/plan changes the organization's billing plan.
2. Only the organization owner can change the plan; admins, members, and viewers receive 403 Forbidden.
3. Upgrading immediately increases all resource limits to the new plan's values.
4. Downgrading checks current usage against the new plan's limits before allowing the change.
5. If current usage exceeds the new plan's limits, the downgrade is rejected with 400 Bad Request and a message indicating which limits are exceeded.
6. A successful plan change returns 200 OK with the updated plan details and new limits.
7. Changing to the same plan the organization is already on returns 400 Bad Request.
8. Changing to an invalid plan name returns 422 Unprocessable Entity.
9. The plan change is recorded in the audit log.
10. A notification is created for all organization owners when the plan changes.
11. The updated_at timestamp on the organization is refreshed.

## API Endpoints

### PUT /orgs/:slug/billing/plan

**Request (upgrade):**
```json
{
  "plan": "business"
}
```

**Response (200 OK):**
```json
{
  "plan": "business",
  "price_cents_monthly": 9900,
  "limits": {
    "max_members": 50,
    "max_projects": 50,
    "max_resources": 5000,
    "max_api_keys": 25
  },
  "usage": {
    "members": 4,
    "projects": 3,
    "resources": 47,
    "api_keys": 2
  },
  "previous_plan": "starter"
}
```

**Error (400 Bad Request - downgrade with exceeded limits):**
```json
{
  "error": "cannot downgrade: current usage exceeds free plan limits",
  "exceeded": {
    "members": {"current": 4, "limit": 3},
    "projects": {"current": 3, "limit": 2}
  }
}
```

**Error (403 Forbidden):**
```json
{
  "error": "only the organization owner can change the billing plan"
}
```

**Error (422 Unprocessable Entity):**
```json
{
  "error": "invalid plan: 'premium' is not a valid plan name"
}
```

## Dependencies

- REQ-BILLING-001: Requires plan definitions to validate plan names and limits.
