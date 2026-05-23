# Multi-Tenant SaaS Platform

Build a complete multi-tenant SaaS platform API from scratch in this empty project directory. The platform allows organizations to manage projects and resources with role-based access control, billing, API key access, webhooks, and an admin console.

## Core Concepts

- **Organizations**: Top-level tenant boundary. All data is scoped to an organization.
- **Members**: Users belong to organizations with assigned roles.
- **Projects**: Organizational unit within a tenant for grouping resources.
- **Resources**: Generic items managed within projects (name, type, metadata JSON).

## Data Model

- **Users**: id, username, email, password_hash, is_platform_admin, created_at
- **Organizations**: id, name, slug (unique), plan (free|starter|business|enterprise), created_at
- **Memberships**: id, user_id, org_id, role (owner|admin|member|viewer), invited_by, joined_at
- **Invitations**: id, org_id, email, role, token, invited_by, expires_at, accepted_at
- **Projects**: id, org_id, name, description, is_archived, created_at, updated_at
- **Resources**: id, project_id, name, type, metadata (JSON), status (active|archived|deleted), created_at, updated_at
- **API Keys**: id, org_id, name, key_hash, prefix (first 8 chars), scopes (JSON array), last_used_at, expires_at, created_by, created_at
- **Billing Plans**: plan name, max_members, max_projects, max_resources, max_api_keys, price_cents_monthly
- **Usage Records**: id, org_id, metric (api_calls|storage_bytes|resources_created), value, recorded_at
- **Invoices**: id, org_id, period_start, period_end, amount_cents, status (draft|issued|paid|overdue), issued_at, paid_at
- **Webhooks**: id, org_id, url, events (JSON array), secret, is_active, created_at
- **Webhook Deliveries**: id, webhook_id, event_type, payload (JSON), status_code, response_body, delivered_at, retry_count
- **Audit Log**: id, org_id, user_id, action, entity_type, entity_id, details (JSON), ip_address, timestamp
- **Notifications**: id, user_id, org_id, type, title, body, is_read, created_at

## Endpoints

### Authentication
- POST /auth/register -- Create a new user
- POST /auth/login -- Returns JWT token
- GET /auth/me -- Current user profile
- PUT /auth/me -- Update profile

### Organizations
- POST /orgs -- Create an organization (creator becomes owner)
- GET /orgs -- List organizations the user belongs to
- GET /orgs/:slug -- Get organization details
- PUT /orgs/:slug -- Update organization (owner/admin only)
- DELETE /orgs/:slug -- Delete organization (owner only, requires confirmation token)

### Membership & Invitations
- GET /orgs/:slug/members -- List members with roles
- PUT /orgs/:slug/members/:user_id/role -- Change member role (owner/admin only)
- DELETE /orgs/:slug/members/:user_id -- Remove member (owner/admin only, cannot remove last owner)
- POST /orgs/:slug/invitations -- Invite user by email (owner/admin only)
- GET /orgs/:slug/invitations -- List pending invitations
- DELETE /orgs/:slug/invitations/:id -- Cancel invitation
- POST /invitations/:token/accept -- Accept an invitation

### Projects
- POST /orgs/:slug/projects -- Create project (admin/member)
- GET /orgs/:slug/projects -- List projects (with archived filter)
- GET /orgs/:slug/projects/:id -- Get project details
- PUT /orgs/:slug/projects/:id -- Update project (admin/member)
- POST /orgs/:slug/projects/:id/archive -- Archive project (admin only)
- POST /orgs/:slug/projects/:id/unarchive -- Unarchive project (admin only)
- DELETE /orgs/:slug/projects/:id -- Delete project and all resources (admin only)

### Resources
- POST /orgs/:slug/projects/:id/resources -- Create resource (admin/member)
- GET /orgs/:slug/projects/:id/resources -- List resources (with type/status filters)
- GET /orgs/:slug/resources/:id -- Get resource details
- PUT /orgs/:slug/resources/:id -- Update resource (admin/member)
- DELETE /orgs/:slug/resources/:id -- Soft delete resource (admin/member)

### API Keys
- POST /orgs/:slug/api-keys -- Create API key (admin only, returns key once)
- GET /orgs/:slug/api-keys -- List API keys (prefix only, no full key)
- DELETE /orgs/:slug/api-keys/:id -- Revoke API key (admin only)
- All org endpoints also accept X-API-Key header with appropriate scopes

### Billing
- GET /orgs/:slug/billing/plan -- Current plan and usage against limits
- PUT /orgs/:slug/billing/plan -- Change plan (owner only)
- GET /orgs/:slug/billing/usage -- Current period usage metrics
- GET /orgs/:slug/billing/invoices -- List invoices
- GET /orgs/:slug/billing/invoices/:id -- Get invoice details

### Webhooks
- POST /orgs/:slug/webhooks -- Register webhook (admin only)
- GET /orgs/:slug/webhooks -- List webhooks
- PUT /orgs/:slug/webhooks/:id -- Update webhook
- DELETE /orgs/:slug/webhooks/:id -- Delete webhook
- GET /orgs/:slug/webhooks/:id/deliveries -- List delivery attempts

### Notifications
- GET /notifications -- List user's notifications across all orgs
- PUT /notifications/:id/read -- Mark as read
- POST /notifications/read-all -- Mark all as read

### Search
- GET /orgs/:slug/search?q=term -- Search across projects and resources within org

### Admin Console (platform admin only)
- GET /admin/orgs -- List all organizations with usage stats
- GET /admin/orgs/:slug/audit-log -- View org audit log
- PUT /admin/orgs/:slug/suspend -- Suspend an organization
- PUT /admin/orgs/:slug/unsuspend -- Unsuspend an organization
- GET /admin/analytics -- Platform-wide analytics (total orgs, users, resources, revenue)

### Audit Log
- GET /orgs/:slug/audit-log -- List audit entries (admin only, with filters)

## Business Rules

### Tenant Isolation
- Every database query must scope to the current organization
- Users can only access organizations they belong to
- API keys are scoped to a single organization
- Audit log entries are scoped to organizations
- No cross-tenant data leakage in any endpoint

### Role Permissions
| Action | Owner | Admin | Member | Viewer |
|--------|-------|-------|--------|--------|
| Manage org settings | Yes | Yes | No | No |
| Manage members | Yes | Yes | No | No |
| Manage billing | Yes | No | No | No |
| Create/edit projects | Yes | Yes | Yes | No |
| Archive/delete projects | Yes | Yes | No | No |
| Create/edit resources | Yes | Yes | Yes | No |
| View projects/resources | Yes | Yes | Yes | Yes |
| Manage API keys | Yes | Yes | No | No |
| Manage webhooks | Yes | Yes | No | No |
| View audit log | Yes | Yes | No | No |

### Billing Plans
| Plan | Members | Projects | Resources | API Keys | Price/mo |
|------|---------|----------|-----------|----------|----------|
| free | 3 | 2 | 50 | 1 | $0 |
| starter | 10 | 10 | 500 | 5 | $29 |
| business | 50 | 50 | 5000 | 25 | $99 |
| enterprise | unlimited | unlimited | unlimited | unlimited | $299 |

### Quota Enforcement
- Creating members, projects, resources, or API keys checks against plan limits
- Return 402 Payment Required when a limit would be exceeded
- Upgrading a plan immediately increases limits
- Downgrading checks current usage against new limits (reject if over)

### Webhooks
- Events: member.joined, member.removed, project.created, project.archived, project.deleted, resource.created, resource.updated, resource.deleted
- Payload signed with HMAC-SHA256 using webhook secret
- Retry failed deliveries 3 times with exponential backoff
- Record delivery status and response

### Notifications
- Auto-created for: invitation received, invitation accepted, member role changed, member removed, project archived, project deleted, plan changed, usage quota warning (80% of limit)

## Requirements Summary

1. Passwords must be hashed (bcrypt or argon2)
2. JWT tokens expire after 1 hour
3. Every endpoint enforces tenant isolation via org_id scoping
4. Role-based access control on every org endpoint
5. Pagination: default 20, max 100 on all list endpoints
6. API keys support scoped access (read, write, admin)
7. Billing plan limits enforced on create operations
8. Webhook payloads signed with HMAC-SHA256
9. Audit log records every mutation with user and IP context
10. All list endpoints support filtering and sorting
11. Return 401 for missing/invalid tokens
12. Return 402 when plan limits exceeded
13. Return 403 for insufficient role permissions
14. Return 404 for missing resources or wrong tenant
15. Return 409 for uniqueness violations
16. Return 422 for validation errors with field-level messages

## Technical Constraints

- The service should listen on port 8080 by default
- You may use any programming language and framework
- Use SQLite for persistent storage
- Include a comprehensive test suite that can be run with a single command
- Tests should cover tenant isolation, RBAC, billing enforcement, webhooks, and all error cases
- The test suite should be self-contained (set up and tear down its own test database)
