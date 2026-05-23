# REQ-NOTIF-001: Notification System Infrastructure

## Status: MISSING
## Priority: HIGH
## Phase: 4

## Requirement

Implement an in-app notification system that allows the platform to create notifications for users and provides endpoints for users to list, read, and manage their notifications. Each notification is associated with a user and optionally an organization, and includes a type, title, body, read status, and creation timestamp. Notifications are listed newest first with pagination.

## Acceptance Criteria

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

## API Endpoints

### GET /notifications

**Request:**
```
GET /notifications?page=1&per_page=20
Authorization: Bearer <token>
```

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
    },
    {
      "id": 8,
      "user_id": 3,
      "org_id": 2,
      "type": "role_changed",
      "title": "Role Updated",
      "body": "Your role in Widget Inc has been changed to admin.",
      "is_read": true,
      "created_at": "2026-01-19T10:00:00Z"
    }
  ],
  "page": 1,
  "per_page": 20,
  "total": 2
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

**Error (404 Not Found):**
```json
{
  "error": "notification not found"
}
```

### POST /notifications/read-all

**Response (200 OK):**
```json
{
  "marked_read": 5
}
```

## Dependencies

- REQ-RBAC-003: Requires member management to generate invitation and role-change notifications.
