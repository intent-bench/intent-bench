# Project Guidance

Read REQUIREMENTS.md before starting implementation. It contains a structured
list of 41 requirements with dependency ordering and acceptance criteria.
Implement them in the specified dependency order to avoid rework.

Key cross-cutting concerns that must be enforced on every endpoint:
- Tenant isolation: all queries scoped to the current organization
- RBAC: role-based permission checks on every org endpoint
- Audit logging: record every mutation with user and IP context

Write a comprehensive test suite covering all requirements. Tests should be
self-contained and runnable with a single command.
