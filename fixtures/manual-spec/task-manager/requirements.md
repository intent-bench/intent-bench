# Requirements Specification

## Implementation Order

Requirements are listed in dependency order. Implement each
requirement fully before moving to the next. Later requirements
depend on earlier ones being complete.

---

## 1. REQ-DB-001: Database setup with SQLite and schema migrations

**Phase:** 1

*Foundation: all entities depend on database*

### Acceptance Criteria

1. A SQLite database file is created on application startup if it does not already exist.
2. The `users` table exists with columns: id (INTEGER PRIMARY KEY), username (TEXT UNIQUE NOT NULL), email (TEXT UNIQUE NOT NULL), password_hash (TEXT NOT NULL), created_at (TEXT NOT NULL).
3. The `projects` table exists with columns: id (INTEGER PRIMARY KEY), name (TEXT NOT NULL), description (TEXT), owner_id (INTEGER NOT NULL REFERENCES users(id)), created_at (TEXT NOT NULL), updated_at (TEXT NOT NULL).
4. The `tasks` table exists with columns: id (INTEGER PRIMARY KEY), title (TEXT NOT NULL), description (TEXT), status (TEXT NOT NULL DEFAULT 'TODO'), due_date (TEXT), is_overdue (INTEGER NOT NULL DEFAULT 0), project_id (INTEGER NOT NULL REFERENCES projects(id)), assignee_id (INTEGER REFERENCES users(id)), created_at (TEXT NOT NULL), updated_at (TEXT NOT NULL).
5. The `labels` table exists with columns: id (INTEGER PRIMARY KEY), name (TEXT UNIQUE NOT NULL), color (TEXT).
6. The `task_labels` table exists with columns: task_id (INTEGER NOT NULL REFERENCES tasks(id)), label_id (INTEGER NOT NULL REFERENCES labels(id)), PRIMARY KEY (task_id, label_id).
7. The `activity_log` table exists with columns: id (INTEGER PRIMARY KEY), timestamp (TEXT NOT NULL), user_id (INTEGER NOT NULL REFERENCES users(id)), action (TEXT NOT NULL), entity_type (TEXT NOT NULL), entity_id (INTEGER NOT NULL), details (TEXT).
8. Foreign key enforcement is enabled (PRAGMA foreign_keys = ON).
9. Indexes exist on: tasks(project_id), tasks(assignee_id), tasks(status), activity_log(entity_type, entity_id), task_labels(label_id).
10. A schema_version table tracks the current schema version number.

---

## 2. REQ-AUTH-001: User registration with password hashing

**Phase:** 1

**Depends on:** REQ-DB-001

*Authentication is required for all protected endpoints*

### Acceptance Criteria

1. POST /auth/register creates a new user and returns the user record (without password_hash).
2. The password is hashed with bcrypt or argon2 before being stored in the database.
3. The plaintext password is never stored in the database or returned in any response.
4. Attempting to register with a duplicate email returns 409 Conflict.
5. Attempting to register with a duplicate username returns 409 Conflict.
6. A successful registration returns 201 Created with the user's id, username, and email.
7. The created_at timestamp is set automatically at registration time.

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

## 3. REQ-AUTH-002: JWT login and authentication middleware

**Phase:** 1

**Depends on:** REQ-AUTH-001

*All CRUD endpoints depend on auth middleware*

### Acceptance Criteria

1. POST /auth/login with valid credentials returns a signed JWT in the response body.
2. POST /auth/login with an invalid email returns 401 Unauthorized.
3. POST /auth/login with a valid email but incorrect password returns 401 Unauthorized.
4. The JWT payload contains at minimum: user_id, username, and an expiration claim (exp).
5. The authentication middleware extracts the user from a valid JWT in the Authorization header (Bearer scheme).
6. The middleware returns 401 Unauthorized when no Authorization header is present.
7. The middleware returns 401 Unauthorized when the JWT is expired or has an invalid signature.
8. All routes except POST /auth/register and POST /auth/login are protected by the middleware.

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
    "email": "alice@example.com"
  }
}
```

**Error (401 Unauthorized):**
```json
{
  "error": "invalid credentials"
}
```

---

## 4. REQ-ERR-001: Consistent error responses across all endpoints

**Phase:** 2

**Depends on:** REQ-DB-001

*Consistent API contract for consumers*

### Acceptance Criteria

1. All error responses use the format: {"error": "descriptive message"}.
2. 401 Unauthorized is returned when the Authorization header is missing, the JWT is invalid, or the JWT is expired.
3. 403 Forbidden is returned when the authenticated user attempts to access or modify a resource they do not own.
4. 404 Not Found is returned when a requested resource (project, task, label) does not exist.
5. 409 Conflict is returned when a uniqueness constraint is violated (duplicate email, duplicate username, duplicate label name, duplicate task-label association).
6. 422 Unprocessable Entity is returned when input validation fails or an invalid state transition is attempted.
7. Error messages are descriptive enough to identify the problem without exposing internal implementation details.
8. No stack traces or internal paths are leaked in error responses.

### API

Applies to all endpoints. Example responses:

**401 Unauthorized:**
```json
{
  "error": "missing or invalid authentication token"
}
```

**403 Forbidden:**
```json
{
  "error": "not the project owner"
}
```

**404 Not Found:**
```json
{
  "error": "task not found"
}
```

**422 Unprocessable Entity:**
```json
{
  "error": "invalid status transition from TODO to DONE"
}
```

---

## 5. REQ-LOG-001: Append-only activity log for all mutations

**Phase:** 2

**Depends on:** REQ-AUTH-002

*Audit trail for compliance and debugging*

### Acceptance Criteria

1. Every create, update, or delete operation on projects, tasks, and labels automatically creates an activity_log entry.
2. Each log entry records: timestamp (ISO 8601), user_id, action ("create", "update", or "delete"), entity_type ("project", "task", or "label"), entity_id, and details (JSON string describing the change).
3. GET /projects/:id/activity returns all activity log entries related to the specified project, ordered by timestamp descending.
4. GET /projects/:id/activity returns 403 Forbidden if the authenticated user does not own the project.
5. Activity entries for tasks include the parent project_id so they appear in the project activity feed.
6. The activity log is append-only; there is no endpoint to update or delete log entries.
7. The details field contains a JSON object with relevant change information (e.g., old and new values for updates).

### API

### GET /projects/:id/activity

**Response (200 OK):**
```json
[
  {
    "id": 3,
    "timestamp": "2026-01-15T11:00:00Z",
    "user_id": 1,
    "action": "update",
    "entity_type": "task",
    "entity_id": 1,
    "details": "{\"field\": \"status\", \"old\": \"TODO\", \"new\": \"IN_PROGRESS\"}"
  },
  {
    "id": 2,
    "timestamp": "2026-01-15T10:30:00Z",
    "user_id": 1,
    "action": "create",
    "entity_type": "task",
    "entity_id": 1,
    "details": "{\"title\": \"Implement login\"}"
  },
  {
    "id": 1,
    "timestamp": "2026-01-15T10:00:00Z",
    "user_id": 1,
    "action": "create",
    "entity_type": "project",
    "entity_id": 1,
    "details": "{\"name\": \"My Project\"}"
  }
]
```

**Error (403 Forbidden):**
```json
{
  "error": "not the project owner"
}
```

---

## 6. REQ-VALID-001: Input validation on all endpoints

**Phase:** 2

**Depends on:** REQ-DB-001

*Prevents corrupt data and provides clear error messages*

### Acceptance Criteria

1. Email fields must match a valid email format (contains @ and a domain); invalid emails return 422.
2. Username must be 3-30 characters and contain only alphanumeric characters and underscores; violations return 422.
3. Password must be at least 8 characters; shorter passwords return 422.
4. Project name must be non-empty; an empty or missing name returns 422.
5. Task title must be non-empty; an empty or missing title returns 422.
6. Label name must be non-empty; an empty or missing name returns 422.
7. Due dates must be valid ISO 8601 format; invalid dates return 422.
8. Status values must be one of: "TODO", "IN_PROGRESS", "DONE"; other values return 422.
9. All 422 responses include a descriptive error message identifying which field failed validation and why.
10. Validation errors are returned before any database operations are attempted.

### API

Applies to all endpoints that accept input. Example error response:

**Error (422 Unprocessable Entity):**
```json
{
  "error": "username must be 3-30 alphanumeric characters"
}
```

```json
{
  "error": "invalid email format"
}
```

```json
{
  "error": "due_date must be in ISO 8601 format"
}
```

---

## 7. REQ-PROJ-001: Project CRUD operations scoped to authenticated user

**Phase:** 2

**Depends on:** REQ-AUTH-002

*Projects are containers for tasks*

### Acceptance Criteria

1. POST /projects creates a new project owned by the authenticated user and returns 201 Created.
2. GET /projects returns only the projects owned by the authenticated user.
3. GET /projects/:id returns the project if the authenticated user is the owner.
4. GET /projects/:id returns 403 Forbidden if the authenticated user is not the owner.
5. GET /projects/:id returns 404 Not Found if the project does not exist.
6. PUT /projects/:id updates the project name and/or description if the authenticated user is the owner.
7. PUT /projects/:id returns 403 Forbidden if the authenticated user is not the owner.
8. DELETE /projects/:id deletes the project and all associated tasks if the authenticated user is the owner.
9. DELETE /projects/:id returns 403 Forbidden if the authenticated user is not the owner.
10. The created_at and updated_at timestamps are set automatically on creation; updated_at is refreshed on update.

### API

### POST /projects

**Request:**
```json
{
  "name": "My Project",
  "description": "A sample project"
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "name": "My Project",
  "description": "A sample project",
  "owner_id": 1,
  "created_at": "2026-01-15T10:30:00Z",
  "updated_at": "2026-01-15T10:30:00Z"
}
```

### GET /projects

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "name": "My Project",
    "description": "A sample project",
    "owner_id": 1,
    "created_at": "2026-01-15T10:30:00Z",
    "updated_at": "2026-01-15T10:30:00Z"
  }
]
```

### PUT /projects/:id

**Request:**
```json
{
  "name": "Updated Project Name",
  "description": "Updated description"
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "name": "Updated Project Name",
  "description": "Updated description",
  "owner_id": 1,
  "created_at": "2026-01-15T10:30:00Z",
  "updated_at": "2026-01-15T11:00:00Z"
}
```

### DELETE /projects/:id

**Response (204 No Content)**

**Error (403 Forbidden):**
```json
{
  "error": "not the project owner"
}
```

---

## 8. REQ-TASK-001: Task CRUD operations scoped to project

**Phase:** 2

**Depends on:** REQ-PROJ-001

*Tasks are the core entity*

### Acceptance Criteria

1. POST /projects/:id/tasks creates a new task in the specified project and returns 201 Created.
2. POST /projects/:id/tasks returns 403 Forbidden if the authenticated user does not own the project.
3. GET /projects/:id/tasks returns all tasks belonging to the specified project.
4. GET /projects/:id/tasks returns 403 Forbidden if the authenticated user does not own the project.
5. GET /tasks/:id returns the task if the authenticated user owns the parent project.
6. GET /tasks/:id returns 403 Forbidden if the authenticated user does not own the parent project.
7. GET /tasks/:id returns 404 Not Found if the task does not exist.
8. PUT /tasks/:id updates the task fields (title, description, assignee_id) if the user owns the parent project.
9. PUT /tasks/:id returns 403 Forbidden if the authenticated user does not own the parent project.
10. DELETE /tasks/:id deletes the task if the user owns the parent project.
11. DELETE /tasks/:id returns 403 Forbidden if the authenticated user does not own the parent project.
12. New tasks default to status "TODO".
13. The created_at and updated_at timestamps are set automatically on creation; updated_at is refreshed on update.

### API

### POST /projects/:id/tasks

**Request:**
```json
{
  "title": "Implement login",
  "description": "Build the login endpoint",
  "assignee_id": 1
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "title": "Implement login",
  "description": "Build the login endpoint",
  "status": "TODO",
  "due_date": null,
  "is_overdue": false,
  "project_id": 1,
  "assignee_id": 1,
  "created_at": "2026-01-15T10:30:00Z",
  "updated_at": "2026-01-15T10:30:00Z"
}
```

### GET /projects/:id/tasks

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "title": "Implement login",
    "description": "Build the login endpoint",
    "status": "TODO",
    "due_date": null,
    "is_overdue": false,
    "project_id": 1,
    "assignee_id": 1,
    "created_at": "2026-01-15T10:30:00Z",
    "updated_at": "2026-01-15T10:30:00Z"
  }
]
```

### GET /tasks/:id

**Response (200 OK):**
```json
{
  "id": 1,
  "title": "Implement login",
  "description": "Build the login endpoint",
  "status": "TODO",
  "due_date": null,
  "is_overdue": false,
  "project_id": 1,
  "assignee_id": 1,
  "created_at": "2026-01-15T10:30:00Z",
  "updated_at": "2026-01-15T10:30:00Z"
}
```

### PUT /tasks/:id

**Request:**
```json
{
  "title": "Implement login (updated)",
  "description": "Updated description"
}
```

**Response (200 OK):** (updated task object)

### DELETE /tasks/:id

**Response (204 No Content)**

---

## 9. REQ-TASK-002: Task status state machine with valid transitions

**Phase:** 2

**Depends on:** REQ-TASK-001

*State machine prevents invalid workflows*

### Acceptance Criteria

1. PUT /tasks/:id/status accepts a new status and transitions the task if the transition is valid.
2. The transition TODO -> IN_PROGRESS is allowed and succeeds with 200 OK.
3. The transition IN_PROGRESS -> DONE is allowed and succeeds with 200 OK.
4. The transition IN_PROGRESS -> TODO is allowed and succeeds with 200 OK.
5. The transition TODO -> DONE is rejected with 422 Unprocessable Entity.
6. Any transition from DONE (DONE -> TODO, DONE -> IN_PROGRESS) is rejected with 422 Unprocessable Entity.
7. The error response for invalid transitions includes the current status and attempted status.
8. The updated_at timestamp is refreshed on a successful status transition.
9. The endpoint returns 403 Forbidden if the authenticated user does not own the parent project.

### API

### PUT /tasks/:id/status

**Request:**
```json
{
  "status": "IN_PROGRESS"
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "title": "Implement login",
  "status": "IN_PROGRESS",
  "project_id": 1,
  "updated_at": "2026-01-15T11:00:00Z"
}
```

**Error (422 Unprocessable Entity):**
```json
{
  "error": "invalid status transition from TODO to DONE"
}
```

---

## 10. REQ-TASK-003: Task due dates with overdue flag

**Phase:** 2

**Depends on:** REQ-TASK-001

*Due dates enable overdue detection*

### Acceptance Criteria

1. Tasks accept an optional due_date field in ISO 8601 format (e.g., "2026-02-01T00:00:00Z") at creation time.
2. The due_date field can be updated via PUT /tasks/:id.
3. The due_date field can be set to null to remove the due date.
4. The is_overdue field defaults to false when a task is created.
5. The is_overdue field is read-only in task creation and update requests (ignored if provided).
6. The is_overdue field is included in all task response objects.
7. Invalid date formats in due_date return 422 Unprocessable Entity.

### API

### POST /projects/:id/tasks (with due date)

**Request:**
```json
{
  "title": "Write report",
  "due_date": "2026-02-01T00:00:00Z"
}
```

**Response (201 Created):**
```json
{
  "id": 2,
  "title": "Write report",
  "status": "TODO",
  "due_date": "2026-02-01T00:00:00Z",
  "is_overdue": false,
  "project_id": 1,
  "created_at": "2026-01-15T10:30:00Z",
  "updated_at": "2026-01-15T10:30:00Z"
}
```

### PUT /tasks/:id (update due date)

**Request:**
```json
{
  "due_date": "2026-03-01T00:00:00Z"
}
```

---

## 11. REQ-LABEL-001: Label CRUD and task-label association

**Phase:** 3

**Depends on:** REQ-TASK-001

*Labels provide cross-cutting categorization*

### Acceptance Criteria

1. POST /labels creates a new label with a name and optional color, returning 201 Created.
2. POST /labels with a duplicate name returns 409 Conflict.
3. GET /labels returns all labels.
4. POST /tasks/:id/labels attaches an existing label to a task, returning 201 Created.
5. POST /tasks/:id/labels with an already-attached label returns 409 Conflict.
6. DELETE /tasks/:id/labels/:label_id detaches a label from a task, returning 204 No Content.
7. DELETE /tasks/:id/labels/:label_id returns 404 Not Found if the label is not attached to the task.
8. GET /tasks/:id/labels returns all labels attached to the specified task.
9. Label operations on tasks require ownership of the parent project (403 Forbidden otherwise).

### API

### POST /labels

**Request:**
```json
{
  "name": "urgent",
  "color": "#ff0000"
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "name": "urgent",
  "color": "#ff0000"
}
```

### GET /labels

**Response (200 OK):**
```json
[
  {"id": 1, "name": "urgent", "color": "#ff0000"},
  {"id": 2, "name": "bug", "color": "#cc0000"}
]
```

### POST /tasks/:id/labels

**Request:**
```json
{
  "label_id": 1
}
```

**Response (201 Created):**
```json
{
  "task_id": 1,
  "label_id": 1
}
```

### DELETE /tasks/:id/labels/:label_id

**Response (204 No Content)**

### GET /tasks/:id/labels

**Response (200 OK):**
```json
[
  {"id": 1, "name": "urgent", "color": "#ff0000"}
]
```

---

## 12. REQ-BG-001: Background overdue task detection

**Phase:** 3

**Depends on:** REQ-TASK-003

*Automated status management*

### Acceptance Criteria

1. POST /tasks/check-overdue scans all tasks and updates the is_overdue flag accordingly.
2. Tasks with due_date < now() and status != "DONE" have is_overdue set to true.
3. Tasks with due_date >= now() have is_overdue set to false (clearing any previous overdue flag).
4. Tasks with status "DONE" have is_overdue set to false regardless of due_date.
5. Tasks with no due_date (null) have is_overdue set to false.
6. The endpoint returns 200 OK with a summary of how many tasks were flagged as overdue.
7. The endpoint requires authentication.

### API

### POST /tasks/check-overdue

**Response (200 OK):**
```json
{
  "checked": 15,
  "overdue": 3,
  "cleared": 2
}
```

Where:
- `checked` is the total number of tasks examined.
- `overdue` is the number of tasks newly or still flagged as overdue.
- `cleared` is the number of tasks that had is_overdue cleared (due date moved or task completed).

---

## 13. REQ-TEST-001: Comprehensive test suite with single-command execution

**Phase:** 3

**Depends on:** REQ-TASK-002, REQ-LABEL-001, REQ-LOG-001, REQ-BG-001, REQ-VALID-001, REQ-ERR-001

*Verification depends on test coverage*

### Acceptance Criteria

1. A single command (e.g., `make test`, `npm test`, `pytest`, `go test ./...`) runs the entire test suite.
2. The test suite creates a fresh test database before running and tears it down after completion.
3. Tests do not depend on external services or pre-existing data.
4. All endpoints defined in REQ-AUTH-001 and REQ-AUTH-002 are covered (registration, login, middleware).
5. All endpoints defined in REQ-PROJ-001 are covered (project CRUD with ownership enforcement).
6. All endpoints defined in REQ-TASK-001 are covered (task CRUD with project scoping).
7. All status transitions defined in REQ-TASK-002 are covered (both valid and invalid).
8. Due date handling defined in REQ-TASK-003 is covered.
9. Label operations defined in REQ-LABEL-001 are covered (create, attach, detach, list).
10. Activity logging defined in REQ-LOG-001 is covered (auto-logging and query).
11. Overdue detection defined in REQ-BG-001 is covered.
12. All validation rules defined in REQ-VALID-001 are covered with invalid input cases.
13. All error codes defined in REQ-ERR-001 are covered (401, 403, 404, 409, 422).
14. The test command exits 0 when all tests pass.
15. The test command exits non-zero when any test fails.
16. Test output clearly identifies which tests passed and which failed.

### API

Not applicable. This requirement covers testing of all other requirements' endpoints.

---
