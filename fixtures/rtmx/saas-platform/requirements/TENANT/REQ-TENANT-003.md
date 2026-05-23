# REQ-TENANT-003: Tenant Isolation Enforcement

## Status: MISSING
## Priority: P0
## Phase: 2

## Requirement

Enforce tenant isolation on every database query so that users can only access data belonging to organizations they are members of. Every query against tenant-scoped tables must include an org_id filter. Cross-tenant data leakage is a critical security failure that must be prevented at the data access layer.

## Acceptance Criteria

1. Every database query against tenant-scoped tables (projects, resources, api_keys, webhooks, invoices, usage_records, audit_log, notifications) includes an org_id filter.
2. A user who is a member of org A cannot access projects, resources, or other data belonging to org B.
3. API key operations are scoped to the organization the key belongs to.
4. Audit log entries are scoped to organizations; members of org A cannot read audit logs for org B.
5. Attempting to access a resource in an organization the user does not belong to returns 404 Not Found (not 403, to avoid revealing existence).
6. Tenant isolation is enforced regardless of whether the user authenticates via JWT or API key.
7. Direct ID-based access (e.g., GET /orgs/:slug/resources/:id) validates that the resource belongs to the specified organization.
8. Bulk listing endpoints never return records from organizations the user does not belong to.
9. Webhook deliveries are scoped through the webhook's org_id; cross-tenant webhook data is inaccessible.
10. Notifications are scoped to the user and org; a user cannot see notifications for organizations they do not belong to.

## API Endpoints

Tenant isolation is not a single endpoint but a cross-cutting concern enforced on all org-scoped endpoints.

### Example: Cross-Tenant Access Attempt

**Request (user is member of org "acme-corp" but not "other-org"):**
```
GET /orgs/other-org/projects
Authorization: Bearer <jwt-for-acme-user>
```

**Response (404 Not Found):**
```json
{
  "error": "organization not found"
}
```

### Example: Direct Resource Access Across Tenants

**Request (resource 42 belongs to org "other-org"):**
```
GET /orgs/acme-corp/resources/42
Authorization: Bearer <jwt-for-acme-user>
```

**Response (404 Not Found):**
```json
{
  "error": "resource not found"
}
```

## Dependencies

- REQ-TENANT-002: Requires organization CRUD and membership checks to be in place.
