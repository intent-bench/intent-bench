# REQ-INV-001: Inventory Tracking

## Status: MISSING
## Priority: P0
## Phase: 2

## Requirement

Implement inventory tracking for each product with quantity, reserved quantity, and low stock threshold management. Admin users can view and update inventory levels. A low-stock endpoint reports all products whose available quantity (quantity minus reserved_quantity) falls below their configured threshold.

## Acceptance Criteria

1. Each product has exactly one inventory record created when the product is created.
2. GET /products/:id/inventory returns the inventory record including quantity, reserved_quantity, low_stock_threshold, and computed available quantity.
3. PUT /products/:id/inventory updates quantity and/or low_stock_threshold (admin only).
4. PUT /products/:id/inventory returns 403 Forbidden for non-admin users.
5. GET /inventory/low-stock returns a list of products where (quantity - reserved_quantity) is below the low_stock_threshold.
6. Available quantity is computed as quantity minus reserved_quantity.
7. reserved_quantity cannot exceed quantity (invariant enforced on updates).
8. GET /products/:id/inventory returns 404 Not Found for nonexistent products.
9. PUT /products/:id/inventory with negative quantity returns 400 Bad Request.
10. The low_stock_threshold defaults to 10 for new inventory records.

## API Endpoints

### GET /products/:id/inventory

**Response (200 OK):**
```json
{
  "product_id": 1,
  "quantity": 50,
  "reserved_quantity": 5,
  "available": 45,
  "low_stock_threshold": 10
}
```

**Error (404 Not Found):**
```json
{
  "error": "product not found"
}
```

### PUT /products/:id/inventory

**Request:**
```json
{
  "quantity": 100,
  "low_stock_threshold": 15
}
```

**Response (200 OK):**
```json
{
  "product_id": 1,
  "quantity": 100,
  "reserved_quantity": 5,
  "available": 95,
  "low_stock_threshold": 15
}
```

**Error (403 Forbidden):**
```json
{
  "error": "admin access required"
}
```

**Error (400 Bad Request):**
```json
{
  "error": "quantity must not be negative"
}
```

### GET /inventory/low-stock

**Response (200 OK):**
```json
{
  "products": [
    {
      "product_id": 3,
      "name": "USB-C Cable",
      "quantity": 8,
      "reserved_quantity": 2,
      "available": 6,
      "low_stock_threshold": 10
    }
  ]
}
```

## Dependencies

- REQ-PROD-001: Requires the products table and product creation logic to associate inventory records.
