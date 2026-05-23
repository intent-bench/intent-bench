# REQ-QUOTA-001: Quota Enforcement

## Status: MISSING
## Priority: P0
## Phase: 5

## Requirement

Implement quota enforcement that checks plan limits before allowing creation of members, projects, resources, or API keys. When a create operation would cause the organization to exceed its current plan's limits, the request must be rejected with 402 Payment Required. Enterprise plan organizations with unlimited limits bypass quota checks entirely.

## Acceptance Criteria

1. Creating a member (accepting an invitation) checks the member count against max_members; exceeding the limit returns 402 Payment Required.
2. Creating a project checks the project count against max_projects; exceeding the limit returns 402 Payment Required.
3. Creating a resource checks the resource count against max_resources; exceeding the limit returns 402 Payment Required.
4. Creating an API key checks the API key count against max_api_keys; exceeding the limit returns 402 Payment Required.
5. The 402 response includes which limit was exceeded, the current count, and the plan limit.
6. Enterprise plan organizations are exempt from quota checks (unlimited limits).
7. Quota checks count only active items (soft-deleted resources and revoked API keys are not counted).
8. Quota enforcement runs before the create operation, not after.
9. Upgrading a plan immediately allows creating resources up to the new limits without delay.
10. The quota check is atomic with the create operation to prevent race conditions.
11. Quota enforcement applies to both JWT-authenticated and API key-authenticated requests.

## API Endpoints

Quota enforcement is a cross-cutting concern on all create endpoints, not a standalone API.

### Example: Creating a Project When Quota is Exceeded

**Request:**
```
POST /orgs/acme-corp/projects
Authorization: Bearer <jwt-token>
```
```json
{
  "name": "Another Project"
}
```

**Response (402 Payment Required):**
```json
{
  "error": "plan limit exceeded",
  "limit": "max_projects",
  "current": 2,
  "max": 2,
  "plan": "free",
  "message": "upgrade your plan to create more projects"
}
```

### Example: Creating a Resource When Quota is Exceeded

**Request:**
```
POST /orgs/acme-corp/projects/1/resources
Authorization: Bearer <jwt-token>
```
```json
{
  "name": "New Resource",
  "type": "compute"
}
```

**Response (402 Payment Required):**
```json
{
  "error": "plan limit exceeded",
  "limit": "max_resources",
  "current": 50,
  "max": 50,
  "plan": "free",
  "message": "upgrade your plan to create more resources"
}
```

## Dependencies

- REQ-BILLING-002: Requires plan upgrade/downgrade to set the organization's current plan and its associated limits.
