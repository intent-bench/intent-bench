# REQ-DB-001: Database Schema

## Status: MISSING
## Priority: P0
## Phase: 1

## Requirement

Initialize a SQLite database with the complete schema for the microservice gateway. The schema must include tables for services, routes, api_keys, and audit_log with proper types and constraints. The database must enforce referential integrity via foreign keys and support all persistent gateway state.

## Acceptance Criteria

1. A SQLite database file is created on application startup if it does not already exist.
2. The `services` table exists with columns: id (INTEGER PRIMARY KEY), name (TEXT UNIQUE NOT NULL), base_url (TEXT NOT NULL), health_check_path (TEXT NOT NULL DEFAULT '/health'), is_healthy (INTEGER NOT NULL DEFAULT 1), last_health_check (TEXT), created_at (TEXT NOT NULL).
3. The `routes` table exists with columns: id (INTEGER PRIMARY KEY), path_pattern (TEXT NOT NULL), method (TEXT NOT NULL DEFAULT '*'), service_id (INTEGER NOT NULL REFERENCES services(id)), strip_prefix (INTEGER NOT NULL DEFAULT 0), timeout_ms (INTEGER NOT NULL DEFAULT 5000), middleware_config (TEXT DEFAULT '{}'), created_at (TEXT NOT NULL).
4. The `api_keys` table exists with columns: id (INTEGER PRIMARY KEY), key_hash (TEXT UNIQUE NOT NULL), name (TEXT NOT NULL), role (TEXT NOT NULL CHECK(role IN ('admin', 'service'))), rate_limit_override (INTEGER), is_active (INTEGER NOT NULL DEFAULT 1), created_at (TEXT NOT NULL).
5. The `audit_log` table exists with columns: id (INTEGER PRIMARY KEY), timestamp (TEXT NOT NULL), api_key_id (INTEGER REFERENCES api_keys(id)), method (TEXT NOT NULL), path (TEXT NOT NULL), target_service (TEXT NOT NULL), status_code (INTEGER NOT NULL), latency_ms (REAL NOT NULL).
6. Foreign key enforcement is enabled (PRAGMA foreign_keys = ON).
7. Indexes exist on: routes(service_id), routes(path_pattern), api_keys(key_hash), audit_log(timestamp), audit_log(target_service).
8. A schema_version table tracks the current schema version number.
9. Inserting a route with a non-existent service_id is rejected by the foreign key constraint.
10. The middleware_config column in routes stores valid JSON as TEXT.

## API Endpoints

Not applicable. This is an internal infrastructure requirement.

## Dependencies

None. This is the foundational requirement.
