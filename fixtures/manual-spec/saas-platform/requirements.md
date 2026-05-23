# Requirements Specification

## Implementation Order

Requirements are listed in dependency order. Implement each
requirement fully before moving to the next. Later requirements
depend on earlier ones being complete.

---

## 1. REQ-DB-001: Database setup with SQLite and schema for all entities

**Phase:** 1

*Foundation: all entities depend on database*

### Acceptance Criteria

1. The users table exists with columns: id, username (unique), email (unique), password_hash, is_platform_admin (default false), created_at, updated_at.
2. The organizations table exists with columns: id, name, slug (unique), plan (default 'free'), created_at, updated_at.
3. The memberships table exists with columns: id, user_id, org_id, role, invited_by, joined_at, with a unique constraint on (user_id, org_id).
4. The invitations table exists with columns: id, org_id, email, role, token (unique), invited_by, expires_at, accepted_at.
5. The projects table exists with columns: id, org_id, name, description, is_archived (default false), created_at, updated_at.
6. The resources table exists with columns: id, project_id, name, type, metadata (JSON), status (default 'active'), created_at, updated_at.
7. The api_keys table exists with columns: id, org_id, name, key_hash, prefix, scopes (JSON), last_used_at, expires_at, created_by, created_at.
8. The invoices table exists with columns: id, org_id, period_start, period_end, amount_cents, status (default 'draft'), issued_at, paid_at.
9. The usage_records table exists with columns: id, org_id, metric, value, recorded_at.
10. The webhooks table exists with columns: id, org_id, url, events (JSON), secret, is_active (default true), created_at.
11. The webhook_deliveries table exists with columns: id, webhook_id, event_type, payload (JSON), status_code, response_body, delivered_at, retry_count.
12. The audit_log table exists with columns: id, org_id, user_id, action, entity_type, entity_id, details (JSON), ip_address, timestamp.
13. The notifications table exists with columns: id, user_id, org_id, type, title, body, is_read (default false), created_at.
14. Foreign key constraints are enforced (PRAGMA foreign_keys = ON).
15. Indexes exist on all foreign key columns and commonly queried fields (slug, email, username, token, prefix).

### API

Schema is created at application startup. No direct API endpoint is exposed.

```sql
CREATE TABLE users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT NOT NULL UNIQUE,
  email TEXT NOT NULL UNIQUE,
  password_hash TEXT NOT NULL,
  is_platform_admin BOOLEAN NOT NULL DEFAULT 0,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE organizations (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  slug TEXT NOT NULL UNIQUE,
  plan TEXT NOT NULL DEFAULT 'free',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

---

## 2. REQ-AUTH-001: User registration with password hashing

**Phase:** 1

**Depends on:** REQ-DB-001

*Authentication required for all operations*

### Acceptance Criteria

1. POST /auth/register creates a new user and returns the user record without password_hash.
2. The password is hashed with bcrypt or argon2 before being stored in the database.
3. The plaintext password is never stored in the database or returned in any response.
4. New users have is_platform_admin set to false by default.
5. Attempting to register with a duplicate email returns 409 Conflict.
6. Attempting to register with a duplicate username returns 409 Conflict.
7. A successful registration returns 201 Created with the user's id, username, email, is_platform_admin, and created_at.
8. The created_at and updated_at timestamps are set automatically at registration time.
9. Registration with missing required fields (username, email, password) returns 400 Bad Request.
10. Email format is validated; invalid emails return 422 Unprocessable Entity.
11. Password must be at least 8 characters; shorter passwords return 422 Unprocessable Entity.

### API

### POST /auth/register

**Request:**
```json
{
  "username": "alice",
  "email": "alice@example.com",
  "password": "securepassword123"
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "username": "alice",
  "email": "alice@example.com",
  "is_platform_admin": false,
  "created_at": "2026-01-15T10:30:00Z"
}
```

**Error (409 Conflict):**
```json
{
  "error": "email already registered"
}
```

---

## 3. REQ-VALID-001: Input validation on all endpoints

**Phase:** 2

**Depends on:** REQ-DB-001

*Prevents corrupt data and provides clear error messages*

### Acceptance Criteria

1. Email fields must conform to a valid email format; invalid emails return 422 with a descriptive field-level error.
2. Username must be 3-30 characters and contain only alphanumeric characters; violations return 422.
3. Password must be at least 8 characters; shorter passwords return 422.
4. Organization name must be non-empty and at most 100 characters; violations return 422.
5. Organization slug must be 3-50 characters, lowercase alphanumeric with hyphens only; violations return 422.
6. Project name must be non-empty and at most 200 characters; violations return 422.
7. Resource name must be non-empty; empty names return 422.
8. Resource type must be non-empty; empty types return 422.
9. Resource metadata must be valid JSON if provided; invalid JSON returns 422.
10. Webhook URL must be a valid HTTPS URL; invalid URLs return 422.
11. API key scopes must be a non-empty array containing only recognized values (read, write, admin); violations return 422.
12. Date fields must conform to ISO 8601 format; invalid dates return 422.

### API

**Error (422 Unprocessable Entity):**
```json
{
  "error": "validation failed",
  "details": [
    {
      "field": "email",
      "message": "invalid email format"
    },
    {
      "field": "password",
      "message": "password must be at least 8 characters"
    }
  ]
}
```

---

## 4. REQ-AUTH-002: JWT login and authentication middleware

**Phase:** 1

**Depends on:** REQ-AUTH-001

*All endpoints depend on auth middleware*

### Acceptance Criteria

1. POST /auth/login accepts email and password, returning a JWT token on success.
2. The JWT token includes the user's id in the payload and expires after 1 hour.
3. Invalid email or password returns 401 Unauthorized with a generic error message.
4. The authentication middleware extracts the JWT from the Authorization header (Bearer scheme).
5. Requests without a valid Authorization header to protected endpoints return 401 Unauthorized.
6. Expired tokens return 401 Unauthorized with an appropriate error message.
7. Malformed or tampered tokens return 401 Unauthorized.
8. The middleware attaches the authenticated user's ID to the request context for downstream handlers.
9. Login with missing required fields (email, password) returns 400 Bad Request.
10. A successful login returns 200 OK with the token and user details (without password_hash).

### API

### POST /auth/login

**Request:**
```json
{
  "email": "alice@example.com",
  "password": "securepassword123"
}
```

**Response (200 OK):**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "user": {
    "id": 1,
    "username": "alice",
    "email": "alice@example.com",
    "is_platform_admin": false
  }
}
```

**Error (401 Unauthorized):**
```json
{
  "error": "invalid email or password"
}
```

---

## 5. REQ-VALID-002: Consistent error response format

**Phase:** 2

**Depends on:** REQ-VALID-001

*Consistent API contract for consumers*

### Acceptance Criteria

1. All error responses return a JSON object with at minimum an "error" field containing a descriptive message.
2. 401 Unauthorized is returned when no authentication token is provided or the token is invalid/expired.
3. 402 Payment Required is returned when an operation would exceed the organization's plan limits.
4. 403 Forbidden is returned when the authenticated user lacks the required role or permission for the operation.
5. 404 Not Found is returned when the requested resource does not exist or belongs to a different tenant.
6. 409 Conflict is returned when an operation violates a uniqueness constraint (duplicate email, username, slug, etc.).
7. 422 Unprocessable Entity is returned for validation errors and includes a details array with field-level messages.
8. 400 Bad Request is returned for malformed requests or missing required query parameters.
9. 500 Internal Server Error responses include a generic error message and never expose internal implementation details.
10. All error responses include the Content-Type: application/json header.

### API

**Error (401 Unauthorized):**
```json
{
  "error": "authentication required"
}
```

**Error (402 Payment Required):**
```json
{
  "error": "plan limit exceeded: upgrade to add more projects"
}
```

**Error (403 Forbidden):**
```json
{
  "error": "insufficient permissions"
}
```

**Error (404 Not Found):**
```json
{
  "error": "resource not found"
}
```

**Error (409 Conflict):**
```json
{
  "error": "slug already in use"
}
```

---

## 6. REQ-AUTH-003: User profile view and update

**Phase:** 2

**Depends on:** REQ-AUTH-002

*User self-service account management*

### Acceptance Criteria

1. GET /auth/me returns the authenticated user's profile (id, username, email, is_platform_admin, created_at, updated_at).
2. PUT /auth/me updates the authenticated user's username and/or email.
3. The password_hash is never included in any profile response.
4. Updating to a username that is already taken returns 409 Conflict.
5. Updating to an email that is already taken returns 409 Conflict.
6. The updated_at timestamp is refreshed on successful update.
7. A successful update returns 200 OK with the full updated profile.
8. Unauthenticated requests return 401 Unauthorized.
9. PUT /auth/me with no valid fields to update returns 400 Bad Request.
10. Users cannot modify is_platform_admin through this endpoint; attempts to set it are ignored.

### API

### GET /auth/me

**Response (200 OK):**
```json
{
  "id": 1,
  "username": "alice",
  "email": "alice@example.com",
  "is_platform_admin": false,
  "created_at": "2026-01-15T10:30:00Z",
  "updated_at": "2026-01-15T10:30:00Z"
}
```

### PUT /auth/me

**Request:**
```json
{
  "username": "alice_updated",
  "email": "alice.new@example.com"
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "username": "alice_updated",
  "email": "alice.new@example.com",
  "is_platform_admin": false,
  "created_at": "2026-01-15T10:30:00Z",
  "updated_at": "2026-01-16T08:00:00Z"
}
```

---

## 7. REQ-TENANT-001: Organization creation with owner assignment

**Phase:** 2

**Depends on:** REQ-AUTH-002

*Organizations are the top-level tenant boundary*

### Acceptance Criteria

1. POST /orgs creates a new organization and returns the organization details.
2. The authenticated user is automatically added as a member with the "owner" role.
3. The organization slug must be unique; duplicate slugs return 409 Conflict.
4. The organization is created with the default plan of "free".
5. A successful creation returns 201 Created with id, name, slug, plan, and created_at.
6. The slug must contain only lowercase letters, numbers, and hyphens; invalid slugs return 422 Unprocessable Entity.
7. The name and slug fields are required; missing fields return 400 Bad Request.
8. GET /orgs returns only organizations the authenticated user belongs to.
9. The membership record includes the user_id, org_id, role ("owner"), and joined_at timestamp.
10. Unauthenticated requests return 401 Unauthorized.

### API

### POST /orgs

**Request:**
```json
{
  "name": "Acme Corp",
  "slug": "acme-corp"
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "name": "Acme Corp",
  "slug": "acme-corp",
  "plan": "free",
  "created_at": "2026-01-15T10:30:00Z"
}
```

### GET /orgs

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "name": "Acme Corp",
    "slug": "acme-corp",
    "plan": "free",
    "role": "owner",
    "created_at": "2026-01-15T10:30:00Z"
  }
]
```

---

## 8. REQ-BILLING-001: Billing plan definitions and limits

**Phase:** 4

**Depends on:** REQ-TENANT-001

*Plans define the resource limits for each org*

### Acceptance Criteria

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

### API

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

---

## 9. REQ-TENANT-002: Organization CRUD with tenant isolation

**Phase:** 2

**Depends on:** REQ-TENANT-001

*Tenant isolation must be enforced on every query*

### Acceptance Criteria

1. GET /orgs/:slug returns organization details for members of that organization.
2. GET /orgs/:slug returns 404 Not Found for users who are not members of the organization.
3. PUT /orgs/:slug updates organization name; only owners and admins can update.
4. PUT /orgs/:slug by a member or viewer returns 403 Forbidden.
5. DELETE /orgs/:slug deletes the organization; only the owner can delete.
6. DELETE /orgs/:slug by a non-owner returns 403 Forbidden.
7. The slug cannot be changed after creation; attempts to update it are ignored or return an error.
8. A successful update returns 200 OK with the updated organization details.
9. A successful deletion returns 204 No Content and removes the organization and all associated data.
10. GET /orgs/:slug for a non-existent slug returns 404 Not Found.
11. All organization queries are scoped to the authenticated user's memberships; no cross-tenant data leakage.

### API

### GET /orgs/:slug

**Response (200 OK):**
```json
{
  "id": 1,
  "name": "Acme Corp",
  "slug": "acme-corp",
  "plan": "starter",
  "created_at": "2026-01-15T10:30:00Z",
  "updated_at": "2026-02-01T12:00:00Z"
}
```

### PUT /orgs/:slug

**Request:**
```json
{
  "name": "Acme Corporation"
}
```

### DELETE /orgs/:slug

**Response (204 No Content)**

---

## 10. REQ-TENANT-003: Tenant isolation enforcement on all queries

**Phase:** 2

**Depends on:** REQ-TENANT-002

*Cross-tenant data leakage is a critical security failure*

### Acceptance Criteria

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

### API

Tenant isolation is a cross-cutting concern enforced on all org-scoped endpoints.

**Example cross-tenant access attempt (user belongs to acme-corp, not other-org):**
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

---

## 11. REQ-ADMIN-001: Platform admin organization management

**Phase:** 5

**Depends on:** REQ-TENANT-002

*Platform operator management capabilities*

### Acceptance Criteria

1. GET /admin/orgs returns a paginated list of all organizations on the platform with usage statistics.
2. Each organization in the list includes id, name, slug, plan, member_count, project_count, resource_count, is_suspended, and created_at.
3. GET /admin/orgs supports page, per_page, and plan query parameters for filtering.
4. PUT /admin/orgs/:slug/suspend suspends the specified organization, blocking member access.
5. PUT /admin/orgs/:slug/unsuspend restores access to a previously suspended organization.
6. PUT /admin/orgs/:slug/suspend returns 400 if the organization is already suspended.
7. PUT /admin/orgs/:slug/unsuspend returns 400 if the organization is not currently suspended.
8. All /admin/* endpoints return 403 if the authenticated user does not have is_platform_admin=true.
9. Suspended organizations return 403 with a descriptive message on any member-facing endpoint.
10. Suspension and unsuspension actions are recorded in the audit log.

### API

### GET /admin/orgs

**Response (200 OK):**
```json
{
  "organizations": [
    {
      "id": 1,
      "name": "Acme Corp",
      "slug": "acme",
      "plan": "business",
      "member_count": 25,
      "project_count": 18,
      "resource_count": 1200,
      "is_suspended": false,
      "created_at": "2025-06-01T00:00:00Z"
    }
  ],
  "page": 1,
  "per_page": 20,
  "total": 1
}
```

### PUT /admin/orgs/:slug/suspend

**Response (200 OK):**
```json
{
  "slug": "acme",
  "is_suspended": true,
  "suspended_at": "2026-01-15T10:30:00Z"
}
```

---

## 12. REQ-BILLING-002: Plan upgrade and downgrade

**Phase:** 4

**Depends on:** REQ-BILLING-001

*Revenue management and self-service tier changes*

### Acceptance Criteria

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

### API

### PUT /orgs/:slug/billing/plan

**Request:**
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

**Error (400 Bad Request -- downgrade with exceeded limits):**
```json
{
  "error": "cannot downgrade: current usage exceeds free plan limits",
  "exceeded": {
    "members": {"current": 4, "limit": 3},
    "projects": {"current": 3, "limit": 2}
  }
}
```

---

## 13. REQ-RBAC-001: Role assignment for organization members

**Phase:** 3

**Depends on:** REQ-TENANT-001

*RBAC controls access to all org resources*

### Acceptance Criteria

1. The system supports four roles: owner, admin, member, and viewer, with a clear permission hierarchy.
2. Organization creators are automatically assigned the "owner" role.
3. Invited users are assigned the role specified in the invitation upon acceptance.
4. PUT /orgs/:slug/members/:user_id/role changes a member's role.
5. Only owners and admins can change member roles.
6. An admin cannot promote a member to owner or change another admin's role.
7. An owner can assign any role including owner (transferring ownership).
8. The last owner of an organization cannot have their role changed; the request returns 400 Bad Request.
9. Changing a role to an invalid value returns 422 Unprocessable Entity.
10. A successful role change returns 200 OK with the updated membership details.
11. Attempting to change the role of a non-member returns 404 Not Found.

### API

### PUT /orgs/:slug/members/:user_id/role

**Request:**
```json
{
  "role": "admin"
}
```

**Response (200 OK):**
```json
{
  "user_id": 2,
  "org_id": 1,
  "role": "admin",
  "joined_at": "2026-01-20T14:00:00Z"
}
```

**Error (400 Bad Request):**
```json
{
  "error": "cannot remove the last owner of the organization"
}
```

---

## 14. REQ-RBAC-002: Role-based access control middleware

**Phase:** 3

**Depends on:** REQ-RBAC-001, REQ-TENANT-003

*Every org endpoint must check role permissions*

### Acceptance Criteria

1. The middleware checks the user's role in the target organization for every org-scoped request.
2. Owners and admins can manage org settings (PUT /orgs/:slug).
3. Owners and admins can manage members (invite, change role, remove).
4. Only owners can manage billing (PUT /orgs/:slug/billing/plan).
5. Owners, admins, and members can create and edit projects and resources.
6. Only owners and admins can archive and delete projects.
7. All roles (including viewer) can view projects and resources.
8. Only owners and admins can manage API keys and webhooks.
9. Only owners and admins can view the audit log.
10. A user with insufficient permissions receives 403 Forbidden with a descriptive error message.
11. The middleware runs after authentication and tenant isolation checks.
12. Platform admins bypass org-level RBAC checks for admin console endpoints only.

### API

RBAC enforcement is a cross-cutting middleware applied to all org-scoped endpoints.

**Example: Viewer attempting to create a project:**
```
POST /orgs/acme-corp/projects
Authorization: Bearer <jwt-for-viewer>
```

**Response (403 Forbidden):**
```json
{
  "error": "insufficient permissions: viewer cannot create projects"
}
```

---

## 15. REQ-RBAC-003: Member management and invitation flow

**Phase:** 3

**Depends on:** REQ-RBAC-002

*Onboarding and offboarding org members*

### Acceptance Criteria

1. POST /orgs/:slug/invitations creates an invitation with a unique token, email, role, invited_by, and expires_at.
2. POST /orgs/:slug/invitations returns 403 if the authenticated user is not an owner or admin.
3. POST /orgs/:slug/invitations returns 409 if the email is already a member of the organization.
4. GET /orgs/:slug/invitations lists all pending (unaccepted, unexpired) invitations for the organization.
5. DELETE /orgs/:slug/invitations/:id cancels a pending invitation (owner/admin only).
6. POST /invitations/:token/accept adds the authenticated user to the organization with the invited role.
7. POST /invitations/:token/accept returns 404 for invalid or expired tokens.
8. PUT /orgs/:slug/members/:user_id/role changes a member's role (owner/admin only).
9. PUT /orgs/:slug/members/:user_id/role returns 403 if the authenticated user lacks permission.
10. DELETE /orgs/:slug/members/:user_id removes a member from the organization (owner/admin only).
11. DELETE /orgs/:slug/members/:user_id returns 400 if the target is the last owner of the organization.
12. All invitation and member management operations create audit log entries and trigger notifications.

### API

### POST /orgs/:slug/invitations

**Request:**
```json
{
  "email": "bob@example.com",
  "role": "member"
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "org_id": 1,
  "email": "bob@example.com",
  "role": "member",
  "token": "inv_abc123def456",
  "invited_by": 1,
  "expires_at": "2026-02-15T10:30:00Z",
  "created_at": "2026-01-15T10:30:00Z"
}
```

### POST /invitations/:token/accept

**Response (200 OK):**
```json
{
  "org_id": 1,
  "user_id": 5,
  "role": "member",
  "joined_at": "2026-01-16T09:00:00Z"
}
```

### DELETE /orgs/:slug/members/:user_id

**Response (204 No Content)**

---

## 16. REQ-PROJ-001: Project CRUD within organization

**Phase:** 4

**Depends on:** REQ-RBAC-002

*Projects organize resources within an org*

### Acceptance Criteria

1. POST /orgs/:slug/projects creates a new project within the organization.
2. Only owners, admins, and members can create projects; viewers receive 403 Forbidden.
3. GET /orgs/:slug/projects lists all non-archived projects in the organization (default behavior).
4. GET /orgs/:slug/projects?archived=true includes archived projects in the listing.
5. GET /orgs/:slug/projects/:id returns the details of a specific project.
6. PUT /orgs/:slug/projects/:id updates the project name and/or description.
7. Only owners, admins, and members can update projects; viewers receive 403 Forbidden.
8. A successful creation returns 201 Created with id, org_id, name, description, is_archived, and created_at.
9. Project names within an organization do not need to be unique.
10. Listing supports pagination with default 20 and max 100 per page.
11. Projects from other organizations are never returned (tenant isolation).

### API

### POST /orgs/:slug/projects

**Request:**
```json
{
  "name": "Website Redesign",
  "description": "Q2 website overhaul project"
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "org_id": 1,
  "name": "Website Redesign",
  "description": "Q2 website overhaul project",
  "is_archived": false,
  "created_at": "2026-02-01T10:00:00Z",
  "updated_at": "2026-02-01T10:00:00Z"
}
```

### GET /orgs/:slug/projects

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "org_id": 1,
    "name": "Website Redesign",
    "description": "Q2 website overhaul project",
    "is_archived": false,
    "created_at": "2026-02-01T10:00:00Z",
    "updated_at": "2026-02-01T10:00:00Z"
  }
]
```

---

## 17. REQ-APIKEY-001: API key creation and management

**Phase:** 5

**Depends on:** REQ-RBAC-002

*Programmatic access for integrations*

### Acceptance Criteria

1. POST /orgs/:slug/api-keys creates a new API key and returns the full key value exactly once.
2. The API key is stored as a hash (bcrypt or SHA-256); the plaintext key is never stored in the database.
3. Only owners and admins can create API keys; members and viewers receive 403 Forbidden.
4. The response at creation includes the full key, id, name, prefix, scopes, and created_at.
5. GET /orgs/:slug/api-keys lists all API keys for the organization, showing prefix (first 8 chars) but never the full key.
6. DELETE /orgs/:slug/api-keys/:id revokes an API key, making it permanently unusable.
7. Only owners and admins can revoke API keys.
8. The key supports configurable scopes: read, write, admin.
9. A successful creation returns 201 Created.
10. A successful revocation returns 204 No Content.
11. API keys can have an optional expiration date; expired keys are rejected during authentication.
12. Creating an API key records the creating user's ID in the created_by field.

### API

### POST /orgs/:slug/api-keys

**Request:**
```json
{
  "name": "CI/CD Pipeline",
  "scopes": ["read", "write"],
  "expires_at": "2027-01-01T00:00:00Z"
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "name": "CI/CD Pipeline",
  "key": "rtmx_k8f9a2b1c3d4e5f6g7h8i9j0k1l2m3n4",
  "prefix": "rtmx_k8f",
  "scopes": ["read", "write"],
  "expires_at": "2027-01-01T00:00:00Z",
  "created_by": 1,
  "created_at": "2026-02-15T10:00:00Z"
}
```

### GET /orgs/:slug/api-keys

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "name": "CI/CD Pipeline",
    "prefix": "rtmx_k8f",
    "scopes": ["read", "write"],
    "last_used_at": "2026-03-01T12:00:00Z",
    "expires_at": "2027-01-01T00:00:00Z",
    "created_by": 1,
    "created_at": "2026-02-15T10:00:00Z"
  }
]
```

### DELETE /orgs/:slug/api-keys/:id

**Response (204 No Content)**

---

## 18. REQ-WEBHOOK-001: Webhook registration and management

**Phase:** 6

**Depends on:** REQ-RBAC-002

*Event-driven integration with external systems*

### Acceptance Criteria

1. POST /orgs/:slug/webhooks creates a new webhook with url, events, secret, and is_active fields.
2. POST /orgs/:slug/webhooks auto-generates a cryptographically random secret if none is provided.
3. POST /orgs/:slug/webhooks returns 403 if the authenticated user is not an owner or admin.
4. POST /orgs/:slug/webhooks validates that the events array contains only recognized event types.
5. GET /orgs/:slug/webhooks returns a list of all webhooks for the organization.
6. GET /orgs/:slug/webhooks does not expose the webhook secret in list responses.
7. PUT /orgs/:slug/webhooks/:id updates the webhook url, events, or is_active status.
8. PUT /orgs/:slug/webhooks/:id allows regenerating the secret by passing a new value.
9. DELETE /orgs/:slug/webhooks/:id deletes the webhook and all associated delivery records.
10. Recognized event types are: member.joined, member.removed, project.created, project.archived, project.deleted, resource.created, resource.updated, resource.deleted.
11. All webhook CRUD operations are scoped to the current organization via tenant isolation.

### API

### POST /orgs/:slug/webhooks

**Request:**
```json
{
  "url": "https://example.com/webhook",
  "events": ["project.created", "resource.created", "resource.updated"],
  "is_active": true
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "org_id": 1,
  "url": "https://example.com/webhook",
  "events": ["project.created", "resource.created", "resource.updated"],
  "secret": "whsec_a1b2c3d4e5f6g7h8",
  "is_active": true,
  "created_at": "2026-01-15T10:30:00Z"
}
```

### DELETE /orgs/:slug/webhooks/:id

**Response (204 No Content)**

---

## 19. REQ-AUDIT-001: Audit log for all mutations with user and IP context

**Phase:** 3

**Depends on:** REQ-RBAC-002

*Compliance and security visibility*

### Acceptance Criteria

1. Every create operation on organizations, members, projects, resources, API keys, webhooks, and billing records creates an audit log entry.
2. Every update operation on the above entities creates an audit log entry.
3. Every delete operation on the above entities creates an audit log entry.
4. Each audit log entry contains org_id, user_id, action, entity_type, entity_id, details (JSON), ip_address, and timestamp.
5. The action field is one of: "create", "update", "delete".
6. The details field contains a JSON representation of the relevant changes or entity state at the time of the action.
7. The ip_address field captures the client IP from the request.
8. Audit log entries are append-only: no PUT or DELETE endpoints exist for audit log entries.
9. Audit log entries are scoped to the organization in which the action occurred.
10. Audit logging does not block or slow the triggering API response beyond negligible overhead.
11. Role changes, invitation sends, and invitation acceptances are all recorded as audit events.

### API

**Example audit log entry:**
```json
{
  "id": 42,
  "org_id": 1,
  "user_id": 2,
  "action": "create",
  "entity_type": "project",
  "entity_id": 5,
  "details": {
    "name": "Q4 Report",
    "description": "Quarterly analysis project"
  },
  "ip_address": "192.168.1.100",
  "timestamp": "2026-01-15T10:30:00Z"
}
```

---

## 20. REQ-NOTIF-001: Notification system infrastructure

**Phase:** 4

**Depends on:** REQ-RBAC-003

*In-app notification delivery*

### Acceptance Criteria

1. GET /notifications returns a paginated list of the authenticated user's notifications, newest first.
2. GET /notifications supports page and per_page query parameters with defaults of page=1 and per_page=20.
3. Each notification includes id, user_id, org_id, type, title, body, is_read, and created_at fields.
4. PUT /notifications/:id/read marks the specified notification as read and returns the updated notification.
5. PUT /notifications/:id/read returns 404 if the notification does not exist or belongs to another user.
6. POST /notifications/read-all marks all of the authenticated user's unread notifications as read.
7. POST /notifications/read-all returns the count of notifications that were marked as read.
8. Newly created notifications have is_read set to false by default.
9. Users can only access their own notifications; no cross-user notification access is permitted.
10. GET /notifications returns 401 if the user is not authenticated.

### API

### GET /notifications

**Response (200 OK):**
```json
{
  "notifications": [
    {
      "id": 12,
      "user_id": 3,
      "org_id": 1,
      "type": "invitation_received",
      "title": "You have been invited",
      "body": "You have been invited to join Acme Corp as a member.",
      "is_read": false,
      "created_at": "2026-01-20T14:00:00Z"
    }
  ],
  "page": 1,
  "per_page": 20,
  "total": 1
}
```

### PUT /notifications/:id/read

**Response (200 OK):**
```json
{
  "id": 12,
  "user_id": 3,
  "org_id": 1,
  "type": "invitation_received",
  "title": "You have been invited",
  "body": "You have been invited to join Acme Corp as a member.",
  "is_read": true,
  "created_at": "2026-01-20T14:00:00Z"
}
```

### POST /notifications/read-all

**Response (200 OK):**
```json
{
  "marked_read": 5
}
```

---

## 21. REQ-QUOTA-001: Quota enforcement on create operations

**Phase:** 5

**Depends on:** REQ-BILLING-002

*Prevents exceeding plan limits*

### Acceptance Criteria

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

### API

**Example: Creating a project when quota is exceeded:**
```
POST /orgs/acme-corp/projects
Authorization: Bearer <jwt-token>
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

---

## 22. REQ-PROJ-002: Project archival and restoration

**Phase:** 4

**Depends on:** REQ-PROJ-001

*Lifecycle management for completed projects*

### Acceptance Criteria

1. POST /orgs/:slug/projects/:id/archive sets the project's is_archived flag to true.
2. POST /orgs/:slug/projects/:id/unarchive sets the project's is_archived flag to false.
3. Only owners and admins can archive or unarchive projects; members and viewers receive 403 Forbidden.
4. Archiving an already-archived project returns 400 Bad Request.
5. Unarchiving a non-archived project returns 400 Bad Request.
6. Archived projects are excluded from GET /orgs/:slug/projects by default.
7. Archived projects are included when GET /orgs/:slug/projects?archived=true is specified.
8. Resources within an archived project remain accessible for read operations but cannot be created or updated.
9. A successful archive or unarchive returns 200 OK with the updated project details.
10. The updated_at timestamp is refreshed on archive and unarchive operations.

### API

### POST /orgs/:slug/projects/:id/archive

**Response (200 OK):**
```json
{
  "id": 1,
  "org_id": 1,
  "name": "Website Redesign",
  "description": "Q2 website overhaul project",
  "is_archived": true,
  "created_at": "2026-02-01T10:00:00Z",
  "updated_at": "2026-04-01T09:00:00Z"
}
```

### POST /orgs/:slug/projects/:id/unarchive

**Response (200 OK):**
```json
{
  "id": 1,
  "org_id": 1,
  "name": "Website Redesign",
  "description": "Q2 website overhaul project",
  "is_archived": false,
  "created_at": "2026-02-01T10:00:00Z",
  "updated_at": "2026-04-05T11:00:00Z"
}
```

---

## 23. REQ-RES-001: Resource CRUD within projects

**Phase:** 5

**Depends on:** REQ-PROJ-001

*Resources are the core managed entity*

### Acceptance Criteria

1. POST /orgs/:slug/projects/:id/resources creates a new resource within the specified project.
2. Only owners, admins, and members can create resources; viewers receive 403 Forbidden.
3. GET /orgs/:slug/projects/:id/resources lists all active resources in the project.
4. GET /orgs/:slug/resources/:id returns the details of a specific resource.
5. PUT /orgs/:slug/resources/:id updates the resource name, type, metadata, or status.
6. DELETE /orgs/:slug/resources/:id performs a soft delete by setting status to "deleted".
7. A successful creation returns 201 Created with id, project_id, name, type, metadata, status, and created_at.
8. Resources are created with a default status of "active".
9. The metadata field accepts arbitrary JSON and stores it as-is.
10. Resources from archived projects cannot be created or updated; attempts return 400 Bad Request.
11. Soft-deleted resources are excluded from default listings.
12. Tenant isolation is enforced; resources from other organizations return 404 Not Found.

### API

### POST /orgs/:slug/projects/:id/resources

**Request:**
```json
{
  "name": "Production Database",
  "type": "database",
  "metadata": {
    "engine": "postgresql",
    "version": "15",
    "region": "us-east-1"
  }
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "project_id": 1,
  "name": "Production Database",
  "type": "database",
  "metadata": {
    "engine": "postgresql",
    "version": "15",
    "region": "us-east-1"
  },
  "status": "active",
  "created_at": "2026-02-15T10:00:00Z",
  "updated_at": "2026-02-15T10:00:00Z"
}
```

### DELETE /orgs/:slug/resources/:id

**Response (200 OK):**
```json
{
  "id": 1,
  "project_id": 1,
  "name": "Production Database",
  "type": "database",
  "status": "deleted",
  "updated_at": "2026-03-10T16:00:00Z"
}
```

---

## 24. REQ-APIKEY-002: API key authentication middleware

**Phase:** 5

**Depends on:** REQ-APIKEY-001

*API keys provide alternative to JWT for automation*

### Acceptance Criteria

1. The middleware accepts an X-API-Key header on all org-scoped endpoints.
2. A valid API key authenticates the request and resolves the associated organization.
3. An invalid or revoked API key returns 401 Unauthorized.
4. An expired API key returns 401 Unauthorized with a message indicating expiration.
5. The middleware updates the last_used_at timestamp on successful authentication.
6. When both Authorization (JWT) and X-API-Key headers are provided, JWT takes precedence.
7. API key authentication sets the org context but does not set a user context (user_id is null in audit logs for API key requests).
8. The middleware identifies the key by matching the prefix, then validates by comparing the full key hash.
9. Requests without any authentication header to protected endpoints return 401 Unauthorized.
10. API key authentication enforces tenant isolation; the key can only access data within its associated organization.

### API

**Example: Accessing resources via API key:**
```
GET /orgs/acme-corp/projects
X-API-Key: rtmx_k8f9a2b1c3d4e5f6g7h8i9j0k1l2m3n4
```

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "org_id": 1,
    "name": "Website Redesign",
    "description": "Q2 website overhaul project",
    "is_archived": false,
    "created_at": "2026-02-01T10:00:00Z"
  }
]
```

**Example: Invalid API key:**

**Response (401 Unauthorized):**
```json
{
  "error": "invalid API key"
}
```

---

## 25. REQ-WEBHOOK-002: Webhook event delivery with HMAC signing

**Phase:** 6

**Depends on:** REQ-WEBHOOK-001

*Secure event delivery to registered endpoints*

### Acceptance Criteria

1. When a subscribed event occurs, the system sends an HTTP POST to each active webhook registered for that event type.
2. The request body contains a JSON payload with event_type, timestamp, org_id, and event-specific data.
3. The payload is signed with HMAC-SHA256 using the webhook's secret key.
4. The signature is included in the X-Webhook-Signature header as sha256=<hex_digest>.
5. The delivery request includes a Content-Type: application/json header.
6. The delivery request includes an X-Webhook-Event header with the event type.
7. A delivery is considered successful if the endpoint returns a 2xx status code.
8. Each delivery attempt is recorded in the webhook_deliveries table with webhook_id, event_type, payload, status_code, response_body, and delivered_at.
9. Inactive webhooks (is_active=false) do not receive deliveries.
10. Webhook deliveries do not block the API response that triggered the event.
11. If the endpoint does not respond within 10 seconds, the delivery is marked as timed out with status_code 0.

### API

**Webhook delivery payload format:**
```
POST https://example.com/webhook
Content-Type: application/json
X-Webhook-Event: project.created
X-Webhook-Signature: sha256=5d41402abc4b2a76b9719d911017c592
```

```json
{
  "event_type": "project.created",
  "timestamp": "2026-01-15T10:30:00Z",
  "org_id": 1,
  "data": {
    "id": 5,
    "name": "New Project",
    "description": "A newly created project",
    "created_at": "2026-01-15T10:30:00Z"
  }
}
```

---

## 26. REQ-AUDIT-002: Audit log querying with filters

**Phase:** 4

**Depends on:** REQ-AUDIT-001

*Audit investigation and compliance reporting*

### Acceptance Criteria

1. GET /orgs/:slug/audit-log returns a paginated list of audit log entries for the organization, newest first.
2. GET /orgs/:slug/audit-log supports filtering by entity_type query parameter (e.g., project, resource, membership).
3. GET /orgs/:slug/audit-log supports filtering by user_id query parameter.
4. GET /orgs/:slug/audit-log supports filtering by action query parameter (create, update, delete).
5. GET /orgs/:slug/audit-log supports filtering by start_date and end_date query parameters in ISO 8601 format.
6. GET /orgs/:slug/audit-log supports page and per_page query parameters with defaults of page=1 and per_page=20.
7. GET /orgs/:slug/audit-log returns 403 if the authenticated user is not an owner or admin of the organization.
8. Results are scoped to the current organization; no cross-tenant audit data is accessible.
9. Multiple filters can be combined in a single query (e.g., entity_type=project AND user_id=5 AND action=delete).
10. The total count of matching entries is returned in the response for pagination.

### API

### GET /orgs/:slug/audit-log

**Request:**
```
GET /orgs/acme/audit-log?entity_type=project&user_id=2&action=create&page=1&per_page=20
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "entries": [
    {
      "id": 42,
      "org_id": 1,
      "user_id": 2,
      "action": "create",
      "entity_type": "project",
      "entity_id": 5,
      "details": {
        "name": "Q4 Report",
        "description": "Quarterly analysis project"
      },
      "ip_address": "192.168.1.100",
      "timestamp": "2026-01-15T10:30:00Z"
    }
  ],
  "page": 1,
  "per_page": 20,
  "total": 1
}
```

---

## 27. REQ-NOTIF-002: Automated lifecycle notifications

**Phase:** 5

**Depends on:** REQ-NOTIF-001

*Keep members informed of org changes*

### Acceptance Criteria

1. When a user receives an invitation, a notification of type "invitation_received" is created for the invited user.
2. When an invitation is accepted, a notification of type "invitation_accepted" is created for the user who sent the invitation.
3. When a member's role is changed, a notification of type "role_changed" is created for the affected member.
4. When a member is removed from an organization, a notification of type "member_removed" is created for the removed user.
5. When a project is archived, a notification of type "project_archived" is created for all members of the organization.
6. When a project is deleted, a notification of type "project_deleted" is created for all members of the organization.
7. When an organization's billing plan is changed, a notification of type "plan_changed" is created for the organization owner.
8. When usage reaches 80% of a plan limit, a notification of type "quota_warning" is created for organization owners and admins.
9. Each automated notification includes a descriptive title and body with relevant context (org name, project name, role, etc.).
10. Automated notifications are created asynchronously and do not block the triggering API response.

### API

Not applicable. Notifications are accessed via the endpoints defined in REQ-NOTIF-001.

**Example notification payloads:**

```json
{
  "type": "invitation_received",
  "title": "Organization Invitation",
  "body": "You have been invited to join Acme Corp as a member."
}
```

```json
{
  "type": "plan_changed",
  "title": "Plan Updated",
  "body": "Acme Corp plan has been changed from starter to business."
}
```

---

## 28. REQ-PROJ-003: Project deletion with resource cascade

**Phase:** 4

**Depends on:** REQ-PROJ-002

*Permanent data removal with cascading cleanup*

### Acceptance Criteria

1. DELETE /orgs/:slug/projects/:id permanently deletes the project.
2. All resources belonging to the deleted project are permanently removed.
3. Only owners and admins can delete projects; members and viewers receive 403 Forbidden.
4. A successful deletion returns 204 No Content.
5. Deleting a non-existent project returns 404 Not Found.
6. Deleting a project in another organization returns 404 Not Found (tenant isolation).
7. An audit log entry is created for the deletion before the project is removed.
8. Webhook events (project.deleted) are fired before the project data is removed.
9. The deletion cascades atomically; if any part fails, the entire operation rolls back.
10. Archived projects can also be deleted.

### API

### DELETE /orgs/:slug/projects/:id

**Response (204 No Content)**

**Error (403 Forbidden):**
```json
{
  "error": "insufficient permissions: member cannot delete projects"
}
```

**Error (404 Not Found):**
```json
{
  "error": "project not found"
}
```

---

## 29. REQ-RES-002: Resource filtering and listing

**Phase:** 5

**Depends on:** REQ-RES-001

*Discovery and organization of resources*

### Acceptance Criteria

1. GET /orgs/:slug/projects/:id/resources supports a type query parameter to filter by resource type.
2. GET /orgs/:slug/projects/:id/resources supports a status query parameter to filter by status (active, archived, deleted).
3. GET /orgs/:slug/projects/:id/resources supports a search query parameter that matches against resource name.
4. Multiple filters can be combined (e.g., ?type=database&status=active).
5. Pagination is supported with page and per_page query parameters.
6. The default page size is 20 and the maximum is 100; requesting more than 100 clamps to 100.
7. The response includes pagination metadata (total count, current page, per_page, total pages).
8. Resources with status "deleted" are excluded from listings unless status=deleted is explicitly specified.
9. An invalid status filter value returns 422 Unprocessable Entity.
10. Filtering is case-insensitive for the search parameter.
11. An empty result set returns 200 OK with an empty array, not 404.

### API

### GET /orgs/:slug/projects/:id/resources?type=database&status=active&search=prod&page=1&per_page=10

**Response (200 OK):**
```json
{
  "data": [
    {
      "id": 1,
      "project_id": 1,
      "name": "Production Database",
      "type": "database",
      "metadata": {
        "engine": "postgresql",
        "version": "15"
      },
      "status": "active",
      "created_at": "2026-02-15T10:00:00Z",
      "updated_at": "2026-02-15T10:00:00Z"
    }
  ],
  "pagination": {
    "total": 1,
    "page": 1,
    "per_page": 10,
    "total_pages": 1
  }
}
```

---

## 30. REQ-APIKEY-003: API key scope enforcement

**Phase:** 6

**Depends on:** REQ-APIKEY-002

*Fine-grained access control for integrations*

### Acceptance Criteria

1. API keys with "read" scope can perform GET requests on org-scoped endpoints.
2. API keys with "write" scope can perform GET, POST, PUT, and DELETE requests on resource and project endpoints.
3. API keys with "admin" scope can perform all operations including member management, API key management, and webhook management.
4. A "read" scope key attempting a POST returns 403 Forbidden.
5. A "write" scope key attempting to manage members or API keys returns 403 Forbidden.
6. Scope enforcement is checked after API key authentication succeeds.
7. The error response includes which scope is required for the attempted operation.
8. An API key with multiple scopes has the union of all permissions from those scopes.
9. An API key with no scopes can only authenticate but cannot access any endpoints (returns 403 for all operations).
10. Scope enforcement does not apply to JWT-authenticated requests (JWT uses RBAC roles instead).

### API

**Example: Read-only key attempting a write:**
```
POST /orgs/acme-corp/projects
X-API-Key: rtmx_readonly_key_value
```

**Response (403 Forbidden):**
```json
{
  "error": "API key scope 'write' required for this operation"
}
```

---

## 31. REQ-ADMIN-002: Platform admin cross-org audit log access

**Phase:** 6

**Depends on:** REQ-ADMIN-001, REQ-AUDIT-002

*Platform-wide compliance and investigation*

### Acceptance Criteria

1. GET /admin/orgs/:slug/audit-log returns a paginated list of audit log entries for the specified organization.
2. GET /admin/orgs/:slug/audit-log supports filtering by entity_type, user_id, action, start_date, and end_date query parameters.
3. GET /admin/orgs/:slug/audit-log supports page and per_page query parameters.
4. GET /admin/orgs/:slug/audit-log returns 403 if the authenticated user does not have is_platform_admin=true.
5. GET /admin/orgs/:slug/audit-log returns 404 if the specified organization slug does not exist.
6. Platform admins can access audit logs for any organization regardless of membership.
7. The response format is identical to the organization-level audit log endpoint (GET /orgs/:slug/audit-log).
8. Platform admin audit log access is itself recorded in the audit log with a distinct entity_type of "admin_access".

### API

### GET /admin/orgs/:slug/audit-log

**Request:**
```
GET /admin/orgs/acme/audit-log?entity_type=membership&action=delete&page=1&per_page=20
Authorization: Bearer <admin_token>
```

**Response (200 OK):**
```json
{
  "entries": [
    {
      "id": 120,
      "org_id": 1,
      "user_id": 1,
      "action": "delete",
      "entity_type": "membership",
      "entity_id": 7,
      "details": {
        "removed_user_id": 7,
        "removed_role": "member"
      },
      "ip_address": "10.0.0.5",
      "timestamp": "2026-01-14T16:00:00Z"
    }
  ],
  "page": 1,
  "per_page": 20,
  "total": 1
}
```

---

## 32. REQ-SEARCH-001: Full-text search across projects and resources

**Phase:** 6

**Depends on:** REQ-RES-002

*Cross-entity discovery within an org*

### Acceptance Criteria

1. GET /orgs/:slug/search?q=term searches project names and descriptions within the organization.
2. GET /orgs/:slug/search?q=term also searches resource names within the organization.
3. Search is case-insensitive and matches partial terms.
4. Results are grouped by entity type (projects, resources) in the response.
5. Each result includes the entity id, name, type, and a snippet of the matching text.
6. GET /orgs/:slug/search supports page and per_page query parameters for pagination.
7. GET /orgs/:slug/search returns 400 if the q parameter is missing or empty.
8. GET /orgs/:slug/search returns 403 if the authenticated user is not a member of the organization.
9. Search results are scoped to the organization via tenant isolation; no cross-tenant results are returned.
10. Archived projects and soft-deleted resources are excluded from search results by default.
11. Search results are ordered by relevance (exact matches first, then partial matches).

### API

### GET /orgs/:slug/search

**Request:**
```
GET /orgs/acme/search?q=report&page=1&per_page=20
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "query": "report",
  "results": {
    "projects": [
      {
        "id": 5,
        "name": "Q4 Report",
        "description": "Quarterly financial analysis and reporting",
        "type": "project"
      }
    ],
    "resources": [
      {
        "id": 22,
        "name": "Monthly Report Template",
        "type": "document",
        "project_id": 3
      }
    ]
  },
  "total": 2,
  "page": 1,
  "per_page": 20
}
```

---

## 33. REQ-QUOTA-002: Quota warning notifications

**Phase:** 6

**Depends on:** REQ-QUOTA-001, REQ-APIKEY-003, REQ-NOTIF-002

*Proactive warning before hitting hard limits*

### Acceptance Criteria

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

### API

### GET /orgs/:slug/billing/plan (with warnings)

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

---

## 34. REQ-WEBHOOK-003: Webhook delivery retry with exponential backoff

**Phase:** 7

**Depends on:** REQ-WEBHOOK-002, REQ-PROJ-003

*Resilient delivery despite endpoint failures*

### Acceptance Criteria

1. A failed webhook delivery (non-2xx status code or timeout) is retried up to 3 additional times.
2. Retry delays follow exponential backoff: 10 seconds, 60 seconds, 300 seconds (5 minutes).
3. Each retry attempt is recorded as a separate entry in the webhook_deliveries table with an incremented retry_count.
4. The retry payload and signature are identical to the original delivery attempt.
5. If a retry succeeds (2xx response), no further retries are attempted.
6. After all 3 retries fail, the delivery is marked as permanently failed with no further attempts.
7. Retries are processed asynchronously and do not block any API request.
8. The webhook delivery history shows all attempts (original plus retries) for a given event.
9. When a project is deleted and cascading webhooks fire, the retry mechanism handles those deliveries consistently.
10. If a webhook is deactivated or deleted between retries, remaining retries for that webhook are cancelled.

### API

Not applicable. Delivery status is visible via the webhook delivery history endpoint defined in REQ-WEBHOOK-004.

---

## 35. REQ-BILLING-003: Invoice generation and listing

**Phase:** 7

**Depends on:** REQ-BILLING-002, REQ-QUOTA-002

*Financial records for billing cycles*

### Acceptance Criteria

1. GET /orgs/:slug/billing/invoices returns a paginated list of invoices for the organization, newest first.
2. GET /orgs/:slug/billing/invoices/:id returns the full details of a specific invoice.
3. Each invoice includes id, org_id, period_start, period_end, amount_cents, status, issued_at, and paid_at.
4. Invoice status progresses through: draft, issued, paid, or overdue.
5. The amount_cents is calculated from the organization's plan price for the billing period.
6. GET /orgs/:slug/billing/invoices returns 403 if the authenticated user is not an owner of the organization.
7. GET /orgs/:slug/billing/invoices/:id returns 404 if the invoice does not exist or belongs to another organization.
8. Invoices are scoped to the organization via tenant isolation.
9. Invoices are generated at the end of each billing period (monthly).
10. Free plan organizations receive invoices with amount_cents of 0.

### API

### GET /orgs/:slug/billing/invoices

**Response (200 OK):**
```json
{
  "invoices": [
    {
      "id": 3,
      "org_id": 1,
      "period_start": "2026-01-01T00:00:00Z",
      "period_end": "2026-01-31T23:59:59Z",
      "amount_cents": 9900,
      "status": "paid",
      "issued_at": "2026-02-01T00:00:00Z",
      "paid_at": "2026-02-05T12:00:00Z"
    }
  ],
  "page": 1,
  "per_page": 20,
  "total": 1
}
```

### GET /orgs/:slug/billing/invoices/:id

**Response (200 OK):**
```json
{
  "id": 3,
  "org_id": 1,
  "period_start": "2026-01-01T00:00:00Z",
  "period_end": "2026-01-31T23:59:59Z",
  "amount_cents": 9900,
  "status": "paid",
  "issued_at": "2026-02-01T00:00:00Z",
  "paid_at": "2026-02-05T12:00:00Z"
}
```

---

## 36. REQ-WEBHOOK-004: Webhook delivery history and status

**Phase:** 7

**Depends on:** REQ-WEBHOOK-003

*Debugging and monitoring webhook integrations*

### Acceptance Criteria

1. GET /orgs/:slug/webhooks/:id/deliveries returns a paginated list of delivery attempts for the specified webhook.
2. Deliveries are listed in reverse chronological order (newest first).
3. Each delivery record includes id, webhook_id, event_type, payload, status_code, response_body, delivered_at, and retry_count.
4. GET /orgs/:slug/webhooks/:id/deliveries supports page and per_page query parameters.
5. GET /orgs/:slug/webhooks/:id/deliveries returns 404 if the webhook does not exist or belongs to another organization.
6. GET /orgs/:slug/webhooks/:id/deliveries returns 403 if the authenticated user is not an owner or admin.
7. Successful deliveries (2xx status codes) and failed deliveries are both included in the history.
8. The response body field is truncated to 1024 characters to prevent excessive storage.

### API

### GET /orgs/:slug/webhooks/:id/deliveries

**Response (200 OK):**
```json
{
  "deliveries": [
    {
      "id": 15,
      "webhook_id": 1,
      "event_type": "resource.created",
      "payload": {
        "event_type": "resource.created",
        "timestamp": "2026-01-15T10:30:00Z",
        "org_id": 1,
        "data": {"id": 10, "name": "Report Q4"}
      },
      "status_code": 200,
      "response_body": "OK",
      "delivered_at": "2026-01-15T10:30:01Z",
      "retry_count": 0
    }
  ],
  "page": 1,
  "per_page": 20,
  "total": 1
}
```

---

## 37. REQ-BILLING-004: Usage tracking and reporting

**Phase:** 7

**Depends on:** REQ-BILLING-003

*Metered usage for billing and quotas*

### Acceptance Criteria

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

### API

### GET /orgs/:slug/billing/usage

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

---

## 38. REQ-ANALYTICS-001: Organization usage analytics

**Phase:** 8

**Depends on:** REQ-BILLING-004

*Self-service usage visibility for org owners*

### Acceptance Criteria

1. GET /orgs/:slug/analytics returns aggregated usage metrics for the organization.
2. The response includes current period and previous period metrics for comparison.
3. Metrics include api_calls, storage_bytes, resources_created, and active_members.
4. Each metric includes the current value and the value from the previous billing period.
5. The response includes the billing period boundaries (period_start, period_end).
6. GET /orgs/:slug/analytics supports an optional period query parameter to view historical periods.
7. GET /orgs/:slug/analytics returns 403 if the authenticated user is not an owner of the organization.
8. Analytics data is scoped to the organization via tenant isolation.
9. Analytics calculations do not impact the performance of other API endpoints.

### API

### GET /orgs/:slug/analytics

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

---

## 39. REQ-ANALYTICS-002: Platform-wide analytics dashboard

**Phase:** 9

**Depends on:** REQ-ANALYTICS-001, REQ-ADMIN-002, REQ-WEBHOOK-004, REQ-SEARCH-001

*Platform operator business intelligence*

### Acceptance Criteria

1. GET /admin/analytics returns platform-wide aggregate metrics.
2. The response includes total_orgs, total_users, total_projects, and total_resources counts.
3. The response includes revenue breakdown by plan tier (free, starter, business, enterprise) with org counts and monthly revenue per tier.
4. The response includes growth metrics showing new organizations and new users in the current period.
5. The response includes active_orgs count (organizations with at least one API call in the current period).
6. GET /admin/analytics returns 403 if the authenticated user does not have is_platform_admin=true.
7. Analytics are calculated from live data and reflect the current state of the platform.
8. The endpoint responds within acceptable performance bounds even with large datasets.

### API

### GET /admin/analytics

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

---

## 40. REQ-ANALYTICS-003: Analytics data export

**Phase:** 9

**Depends on:** REQ-ANALYTICS-002

*Integration with external BI tools*

### Acceptance Criteria

1. GET /admin/analytics/export returns analytics data in CSV format.
2. The response Content-Type is text/csv with a Content-Disposition header for file download.
3. The CSV includes columns for org_id, org_name, plan, metric, value, and period.
4. GET /admin/analytics/export supports start_date and end_date query parameters to filter by date range.
5. GET /admin/analytics/export supports a metrics query parameter to filter by specific metric types (api_calls, storage_bytes, resources_created).
6. GET /admin/analytics/export returns 403 if the authenticated user does not have is_platform_admin=true.
7. The CSV export includes a header row with column names.
8. Large exports are streamed to avoid memory exhaustion.
9. The default date range is the current billing period if no date parameters are provided.

### API

### GET /admin/analytics/export

**Request:**
```
GET /admin/analytics/export?start_date=2026-01-01&end_date=2026-01-31&metrics=api_calls,resources_created
Authorization: Bearer <admin_token>
```

**Response (200 OK):**
```
Content-Type: text/csv
Content-Disposition: attachment; filename="analytics-2026-01.csv"
```

```csv
org_id,org_name,plan,metric,value,period
1,Acme Corp,business,api_calls,12450,2026-01
1,Acme Corp,business,resources_created,87,2026-01
2,Startup Co,starter,api_calls,3200,2026-01
2,Startup Co,starter,resources_created,24,2026-01
```

---

## 41. REQ-TEST-001: Comprehensive test suite covering all requirements

**Phase:** 10

**Depends on:** REQ-AUTH-003, REQ-TENANT-003, REQ-RBAC-003, REQ-PROJ-003, REQ-RES-002, REQ-APIKEY-003, REQ-BILLING-004, REQ-QUOTA-002, REQ-WEBHOOK-004, REQ-AUDIT-002, REQ-NOTIF-002, REQ-SEARCH-001, REQ-ADMIN-002, REQ-ANALYTICS-003, REQ-VALID-002

*Verification depends on test coverage*

### Acceptance Criteria

1. A single command (e.g., `make test`, `npm test`, `pytest`, `go test ./...`) runs the entire test suite.
2. The test suite creates a fresh test database before each run and tears it down after completion.
3. Tests do not depend on external services or pre-existing data.
4. Auth tests cover user registration, JWT login, token validation, and profile management (REQ-AUTH-001 through REQ-AUTH-003).
5. Tenant tests cover organization CRUD, tenant isolation enforcement, and cross-tenant data leakage prevention (REQ-TENANT-001 through REQ-TENANT-003).
6. RBAC tests cover role assignment, permission matrix enforcement, member management, and invitation flow (REQ-RBAC-001 through REQ-RBAC-003).
7. Project tests cover CRUD, archival, restoration, and deletion with resource cascade (REQ-PROJ-001 through REQ-PROJ-003).
8. Resource tests cover CRUD, filtering, and soft deletion (REQ-RES-001, REQ-RES-002).
9. API key tests cover creation, authentication via X-API-Key header, and scope enforcement (REQ-APIKEY-001 through REQ-APIKEY-003).
10. Billing tests cover plan definitions, upgrade/downgrade validation, invoice generation, and usage tracking (REQ-BILLING-001 through REQ-BILLING-004).
11. Quota tests cover limit enforcement returning 402 and warning notifications at 80% (REQ-QUOTA-001, REQ-QUOTA-002).
12. Webhook tests cover CRUD, HMAC-SHA256 signed delivery, retry with exponential backoff, and delivery history (REQ-WEBHOOK-001 through REQ-WEBHOOK-004).
13. Audit log tests cover automatic recording of all mutations and query with filters (REQ-AUDIT-001, REQ-AUDIT-002).
14. Notification tests cover listing, read marking, and automatic creation for lifecycle events (REQ-NOTIF-001, REQ-NOTIF-002).
15. Search tests cover full-text search across projects and resources with tenant scoping (REQ-SEARCH-001).
16. Admin tests cover platform admin org management and cross-org audit log access (REQ-ADMIN-001, REQ-ADMIN-002).
17. Analytics tests cover org-level usage analytics, platform-wide analytics, and CSV export (REQ-ANALYTICS-001 through REQ-ANALYTICS-003).
18. Validation tests cover all invalid input cases returning 422 with field-level errors (REQ-VALID-001).
19. Error code tests cover 401, 402, 403, 404, 409, and 422 responses with consistent format (REQ-VALID-002).
20. The test command exits 0 when all tests pass and non-zero when any test fails.

### API

Not applicable. This requirement covers testing of all other requirements' endpoints.

---
