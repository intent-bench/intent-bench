# REQ-SHIP-002: Shipment Status

## Status: MISSING
## Priority: P0
## Phase: 5

## Requirement

Implement shipment status tracking that allows administrators to update a shipment through its lifecycle statuses. Valid statuses are "processing", "shipped", "in_transit", and "delivered", and only forward transitions are permitted. When a shipment reaches "delivered" status, the associated order status is updated to "delivered" and a delivered_at timestamp is recorded. A tracking endpoint allows users to view shipment information for their orders.

## Acceptance Criteria

1. PUT /shipments/:id/status updates the status of the specified shipment.
2. Only users with the admin role may update shipment status.
3. PUT /shipments/:id/status returns 403 if the authenticated user is not an admin.
4. Valid shipment statuses are: processing, shipped, in_transit, delivered.
5. Only forward transitions are allowed (processing -> shipped -> in_transit -> delivered).
6. PUT /shipments/:id/status returns 400 if the transition is not a valid forward transition.
7. When status is updated to "delivered", the associated order status is set to "delivered".
8. When status is updated to "delivered", a delivered_at timestamp is recorded on the shipment.
9. GET /orders/:id/tracking returns the shipment information for the specified order.
10. GET /orders/:id/tracking returns 404 if no shipment exists for the order.
11. Only the order owner or an admin can view tracking information.

## API Endpoints

### PUT /shipments/:id/status

**Request:**
```json
{
  "status": "shipped"
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "order_id": 5,
  "carrier": "FedEx",
  "tracking_number": "FX-1234567890",
  "status": "shipped",
  "updated_at": "2026-01-22T12:00:00Z"
}
```

**Error (400 Bad Request):**
```json
{
  "error": "invalid status transition from processing to delivered"
}
```

### PUT /shipments/:id/status (delivered)

**Response (200 OK):**
```json
{
  "id": 1,
  "order_id": 5,
  "carrier": "FedEx",
  "tracking_number": "FX-1234567890",
  "status": "delivered",
  "delivered_at": "2026-01-25T15:30:00Z",
  "updated_at": "2026-01-25T15:30:00Z"
}
```

### GET /orders/:id/tracking

**Response (200 OK):**
```json
{
  "shipment_id": 1,
  "order_id": 5,
  "carrier": "FedEx",
  "tracking_number": "FX-1234567890",
  "status": "in_transit",
  "created_at": "2026-01-22T08:00:00Z",
  "updated_at": "2026-01-23T10:00:00Z"
}
```

**Error (404 Not Found):**
```json
{
  "error": "no shipment found for this order"
}
```

## Dependencies

- REQ-SHIP-001: Requires shipment creation to produce shipments whose status can be tracked.
- REQ-ORD-002: Requires order status tracking to update order to "delivered".
