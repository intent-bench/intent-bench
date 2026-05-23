# REQ-PROD-001: Product CRUD

## Status: MISSING
## Priority: P0
## Phase: 2

## Requirement

Implement full CRUD operations for products. Only admin users may create, update, or delete products. All authenticated users can list and view products. Product listing supports pagination with configurable page size. Product detail includes the average rating from approved reviews. Deletion is a soft delete that sets is_active to false.

## Acceptance Criteria

1. POST /products creates a new product and returns 201 Created (admin only).
2. POST /products with a duplicate SKU returns 409 Conflict.
3. GET /products returns a paginated list of active products with default page size of 20 and maximum of 100.
4. GET /products supports query parameters: page (default 1) and per_page (default 20, max 100).
5. GET /products/:id returns the product including its average_rating computed from approved reviews.
6. GET /products/:id returns 404 Not Found for nonexistent or inactive products.
7. PUT /products/:id updates the product (admin only) and returns 200 OK.
8. DELETE /products/:id soft-deletes the product by setting is_active=false (admin only) and returns 200 OK.
9. Non-admin users receive 403 Forbidden when attempting to create, update, or delete products.
10. The created_at timestamp is set on creation; updated_at is set on every update.

## API Endpoints

### POST /products

**Request:**
```json
{
  "name": "Wireless Headphones",
  "description": "Bluetooth over-ear headphones with noise cancellation",
  "price": 79.99,
  "sku": "WH-1000",
  "image_url": "https://example.com/images/wh-1000.jpg",
  "category_id": 3
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "name": "Wireless Headphones",
  "description": "Bluetooth over-ear headphones with noise cancellation",
  "price": 79.99,
  "sku": "WH-1000",
  "image_url": "https://example.com/images/wh-1000.jpg",
  "category_id": 3,
  "is_active": true,
  "created_at": "2026-01-15T10:30:00Z",
  "updated_at": "2026-01-15T10:30:00Z"
}
```

**Error (409 Conflict):**
```json
{
  "error": "SKU already exists"
}
```

**Error (403 Forbidden):**
```json
{
  "error": "admin access required"
}
```

### GET /products

**Response (200 OK):**
```json
{
  "products": [
    {
      "id": 1,
      "name": "Wireless Headphones",
      "price": 79.99,
      "sku": "WH-1000",
      "image_url": "https://example.com/images/wh-1000.jpg",
      "category_id": 3,
      "is_active": true,
      "average_rating": 4.5,
      "created_at": "2026-01-15T10:30:00Z"
    }
  ],
  "page": 1,
  "per_page": 20,
  "total": 1
}
```

### GET /products/:id

**Response (200 OK):**
```json
{
  "id": 1,
  "name": "Wireless Headphones",
  "description": "Bluetooth over-ear headphones with noise cancellation",
  "price": 79.99,
  "sku": "WH-1000",
  "image_url": "https://example.com/images/wh-1000.jpg",
  "category_id": 3,
  "is_active": true,
  "average_rating": 4.5,
  "created_at": "2026-01-15T10:30:00Z",
  "updated_at": "2026-01-15T10:30:00Z"
}
```

**Error (404 Not Found):**
```json
{
  "error": "product not found"
}
```

### PUT /products/:id

**Request:**
```json
{
  "name": "Wireless Headphones Pro",
  "price": 89.99
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "name": "Wireless Headphones Pro",
  "description": "Bluetooth over-ear headphones with noise cancellation",
  "price": 89.99,
  "sku": "WH-1000",
  "image_url": "https://example.com/images/wh-1000.jpg",
  "category_id": 3,
  "is_active": true,
  "created_at": "2026-01-15T10:30:00Z",
  "updated_at": "2026-01-16T08:00:00Z"
}
```

### DELETE /products/:id

**Response (200 OK):**
```json
{
  "message": "product deactivated"
}
```

## Dependencies

- REQ-AUTH-002: Requires JWT authentication and role-based authorization for admin checks.
