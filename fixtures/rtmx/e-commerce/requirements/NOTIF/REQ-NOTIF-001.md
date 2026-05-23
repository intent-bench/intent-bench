# REQ-NOTIF-001: Notification System

## Status: MISSING
## Priority: HIGH
## Phase: 2

## Requirement

Implement a notification system infrastructure that allows the application to create and deliver notifications to users. Users can list their notifications (newest first with pagination), mark individual notifications as read, and mark all notifications as read in a single operation. Each notification has a type, subject, body, read status, and creation timestamp.

## Acceptance Criteria

1. GET /notifications returns a paginated list of the authenticated user's notifications, newest first.
2. GET /notifications supports page and per_page query parameters.
3. Each notification includes id, type, subject, body, is_read, and created_at fields.
4. PUT /notifications/:id/read marks the specified notification as read.
5. PUT /notifications/:id/read returns 404 if the notification does not exist or belongs to another user.
6. POST /notifications/read-all marks all of the authenticated user's unread notifications as read.
7. POST /notifications/read-all returns the count of notifications marked as read.
8. Newly created notifications have is_read set to false by default.
9. Users can only access their own notifications.
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
      "id": 5,
      "type": "order_placed",
      "subject": "Order Confirmed",
      "body": "Your order #5 has been placed successfully.",
      "is_read": false,
      "created_at": "2026-01-20T14:00:00Z"
    },
    {
      "id": 4,
      "type": "order_shipped",
      "subject": "Order Shipped",
      "body": "Your order #3 has been shipped via FedEx.",
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
  "id": 5,
  "type": "order_placed",
  "subject": "Order Confirmed",
  "body": "Your order #5 has been placed successfully.",
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
  "marked_read": 3
}
```

## Dependencies

- REQ-AUTH-001: Requires user registration to associate notifications with users.
