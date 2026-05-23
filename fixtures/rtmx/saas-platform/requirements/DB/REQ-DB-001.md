# REQ-DB-001: Database Schema for Multi-Tenant SaaS Platform

## Status: MISSING
## Priority: P0
## Phase: 1

## Requirement

Implement the SQLite database schema with all tables required for the multi-tenant SaaS platform. All tables must have proper column types, constraints, indexes, and foreign key relationships. The schema must support tenant isolation by including org_id on all tenant-scoped tables with appropriate foreign key constraints.

## Acceptance Criteria

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

## API Endpoints

### Schema Initialization

The database schema is created at application startup. No direct API endpoint is exposed for schema creation.

**Example table DDL:**
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

## Dependencies

- None. This is the foundational requirement for all other requirements.
