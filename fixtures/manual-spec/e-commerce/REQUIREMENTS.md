# Requirements Specification

## Implementation Order

Requirements are listed in dependency order. Implement each
requirement fully before moving to the next. Later requirements
depend on earlier ones being complete.

---

## 1. REQ-DB-001: Database Schema

**Phase:** 1

*Foundation: all entities depend on database*

### Acceptance Criteria

1. A SQLite database file is created on application startup if it does not already exist.
2. The `users` table exists with columns: id (INTEGER PRIMARY KEY), username (TEXT UNIQUE NOT NULL), email (TEXT UNIQUE NOT NULL), password_hash (TEXT NOT NULL), role (TEXT NOT NULL DEFAULT 'customer'), created_at (TEXT NOT NULL), updated_at (TEXT NOT NULL).
3. The `categories` table exists with columns: id (INTEGER PRIMARY KEY), name (TEXT NOT NULL), slug (TEXT UNIQUE NOT NULL), parent_id (INTEGER REFERENCES categories(id)), created_at (TEXT NOT NULL).
4. The `products` table exists with columns: id (INTEGER PRIMARY KEY), name (TEXT NOT NULL), description (TEXT), price (REAL NOT NULL), sku (TEXT UNIQUE NOT NULL), image_url (TEXT), category_id (INTEGER REFERENCES categories(id)), is_active (INTEGER NOT NULL DEFAULT 1), created_at (TEXT NOT NULL), updated_at (TEXT NOT NULL).
5. The `inventory` table exists with columns: id (INTEGER PRIMARY KEY), product_id (INTEGER UNIQUE NOT NULL REFERENCES products(id)), quantity (INTEGER NOT NULL DEFAULT 0), reserved_quantity (INTEGER NOT NULL DEFAULT 0), low_stock_threshold (INTEGER NOT NULL DEFAULT 10).
6. The `cart_items` table exists with columns: id (INTEGER PRIMARY KEY), user_id (INTEGER NOT NULL REFERENCES users(id)), product_id (INTEGER NOT NULL REFERENCES products(id)), quantity (INTEGER NOT NULL), added_at (TEXT NOT NULL).
7. The `orders` table exists with columns: id (INTEGER PRIMARY KEY), user_id (INTEGER NOT NULL REFERENCES users(id)), status (TEXT NOT NULL DEFAULT 'pending'), total (REAL NOT NULL), discount_code_id (INTEGER REFERENCES discount_codes(id)), shipping_address (TEXT NOT NULL), created_at (TEXT NOT NULL), updated_at (TEXT NOT NULL).
8. The `order_items` table exists with columns: id (INTEGER PRIMARY KEY), order_id (INTEGER NOT NULL REFERENCES orders(id)), product_id (INTEGER NOT NULL REFERENCES products(id)), quantity (INTEGER NOT NULL), unit_price (REAL NOT NULL).
9. The `payments` table exists with columns: id (INTEGER PRIMARY KEY), order_id (INTEGER NOT NULL REFERENCES orders(id)), amount (REAL NOT NULL), method (TEXT NOT NULL), status (TEXT NOT NULL DEFAULT 'pending'), transaction_id (TEXT), created_at (TEXT NOT NULL).
10. The `shipments` table exists with columns: id (INTEGER PRIMARY KEY), order_id (INTEGER NOT NULL REFERENCES orders(id)), carrier (TEXT NOT NULL), tracking_number (TEXT), status (TEXT NOT NULL DEFAULT 'pending'), shipped_at (TEXT), delivered_at (TEXT).
11. The `reviews` table exists with columns: id (INTEGER PRIMARY KEY), product_id (INTEGER NOT NULL REFERENCES products(id)), user_id (INTEGER NOT NULL REFERENCES users(id)), rating (INTEGER NOT NULL CHECK(rating BETWEEN 1 AND 5)), comment (TEXT), status (TEXT NOT NULL DEFAULT 'pending'), created_at (TEXT NOT NULL).
12. The `discount_codes` table exists with columns: id (INTEGER PRIMARY KEY), code (TEXT UNIQUE NOT NULL), discount_percent (INTEGER NOT NULL CHECK(discount_percent BETWEEN 1 AND 100)), max_uses (INTEGER), current_uses (INTEGER NOT NULL DEFAULT 0), valid_from (TEXT NOT NULL), valid_until (TEXT NOT NULL), is_active (INTEGER NOT NULL DEFAULT 1).
13. The `notifications` table exists with columns: id (INTEGER PRIMARY KEY), user_id (INTEGER NOT NULL REFERENCES users(id)), type (TEXT NOT NULL), message (TEXT NOT NULL), is_read (INTEGER NOT NULL DEFAULT 0), created_at (TEXT NOT NULL).
14. The `audit_log` table exists with columns: id (INTEGER PRIMARY KEY), timestamp (TEXT NOT NULL), user_id (INTEGER REFERENCES users(id)), action (TEXT NOT NULL), entity_type (TEXT NOT NULL), entity_id (INTEGER NOT NULL), details (TEXT).
15. Foreign key enforcement is enabled (PRAGMA foreign_keys = ON).
16. Indexes exist on: products(category_id), products(sku), cart_items(user_id), orders(user_id), orders(status), order_items(order_id), reviews(product_id), audit_log(entity_type, entity_id).
17. A schema_version table tracks the current schema version number.

---

## 2. REQ-AUTH-001: User Registration

**Phase:** 1

**Depends on:** REQ-DB-001

*Authentication is required for all protected endpoints*

### Acceptance Criteria

1. POST /auth/register creates a new user and returns the user record without password_hash.
2. The password is hashed with bcrypt or argon2 before being stored in the database.
3. The plaintext password is never stored in the database or returned in any response.
4. New users are assigned the default role of "customer".
5. Attempting to register with a duplicate email returns 409 Conflict.
6. Attempting to register with a duplicate username returns 409 Conflict.
7. A successful registration returns 201 Created with the user's id, username, email, role, and created_at.
8. The created_at and updated_at timestamps are set automatically at registration time.
9. Registration with missing required fields (username, email, password) returns 400 Bad Request.

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
  "role": "customer",
  "created_at": "2026-01-15T10:30:00Z"
}
```

**Error (409 Conflict):**
```json
{
  "error": "email already registered"
}
```

**Error (400 Bad Request):**
```json
{
  "error": "username, email, and password are required"
}
```

---

## 3. REQ-AUTH-002: JWT Authentication

**Phase:** 1

**Depends on:** REQ-AUTH-001

*All CRUD endpoints depend on auth middleware*

### Acceptance Criteria

1. POST /auth/login with valid credentials returns a signed JWT in the response body.
2. POST /auth/login with an invalid email returns 401 Unauthorized.
3. POST /auth/login with a valid email but incorrect password returns 401 Unauthorized.
4. The JWT payload contains at minimum: user_id, username, role, and an expiration claim (exp) set to 1 hour from issuance.
5. The authentication middleware extracts the user from a valid JWT in the Authorization header (Bearer scheme).
6. The middleware returns 401 Unauthorized when no Authorization header is present.
7. The middleware returns 401 Unauthorized when the JWT is expired or has an invalid signature.
8. All routes except POST /auth/register and POST /auth/login are protected by the middleware.
9. The user's role from the JWT is available to downstream handlers for authorization checks.

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
    "email": "alice@example.com",
    "role": "customer"
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

## 4. REQ-VALID-001: Input Validation

**Phase:** 2

**Depends on:** REQ-DB-001

*Prevents corrupt data and provides clear error messages*

### Acceptance Criteria

1. Email fields must conform to a valid email format; invalid emails return 422 with a descriptive error.
2. Username must be 3-30 characters and contain only alphanumeric characters; violations return 422.
3. Password must be at least 8 characters; shorter passwords return 422.
4. Product name must be non-empty; empty names return 422.
5. Product price must be greater than 0; zero or negative prices return 422.
6. Product SKU must be non-empty; empty SKUs return 422.
7. Review rating must be an integer between 1 and 5 inclusive; out-of-range values return 422.
8. Discount code percent must be an integer between 1 and 100 inclusive; out-of-range values return 422.
9. Date fields must conform to ISO 8601 format; invalid dates return 422.
10. Quantity fields must be positive integers; zero or negative quantities return 422.
11. Requests without a valid authentication token return 401 Unauthorized.
12. Requests where the authenticated user lacks required permissions return 403 Forbidden.
13. Requests referencing a non-existent resource return 404 Not Found.
14. Requests that violate uniqueness constraints (duplicate email, username, SKU, review) return 409 Conflict.

### API

All validation errors follow a consistent format.

**Error (422 Unprocessable Entity):**
```json
{
  "error": "validation failed",
  "details": [
    {
      "field": "email",
      "message": "invalid email format"
    },
    {
      "field": "password",
      "message": "password must be at least 8 characters"
    }
  ]
}
```

**Error (401 Unauthorized):**
```json
{
  "error": "authentication required"
}
```

**Error (403 Forbidden):**
```json
{
  "error": "insufficient permissions"
}
```

**Error (404 Not Found):**
```json
{
  "error": "resource not found"
}
```

**Error (409 Conflict):**
```json
{
  "error": "email already registered"
}
```

---

## 5. REQ-AUTH-003: User Profile

**Phase:** 2

**Depends on:** REQ-AUTH-002

*Profile management for authenticated users*

### Acceptance Criteria

1. GET /auth/profile returns the authenticated user's id, username, email, role, and created_at.
2. PUT /auth/profile updates the user's username and/or email.
3. PUT /auth/profile ignores any attempt to change the role field.
4. PUT /auth/profile with a duplicate email returns 409 Conflict.
5. PUT /auth/profile with a duplicate username returns 409 Conflict.
6. The updated_at timestamp is set automatically on profile update.
7. GET /auth/profile returns 401 Unauthorized when no valid token is provided.
8. A successful update returns 200 OK with the updated user record.

### API

### GET /auth/profile

**Response (200 OK):**
```json
{
  "id": 1,
  "username": "alice",
  "email": "alice@example.com",
  "role": "customer",
  "created_at": "2026-01-15T10:30:00Z"
}
```

**Error (401 Unauthorized):**
```json
{
  "error": "authentication required"
}
```

### PUT /auth/profile

**Request:**
```json
{
  "username": "alice_updated",
  "email": "alice_new@example.com"
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "username": "alice_updated",
  "email": "alice_new@example.com",
  "role": "customer",
  "created_at": "2026-01-15T10:30:00Z",
  "updated_at": "2026-01-16T08:00:00Z"
}
```

**Error (409 Conflict):**
```json
{
  "error": "email already in use"
}
```

---

## 6. REQ-NOTIF-001: Notification System

**Phase:** 2

**Depends on:** REQ-AUTH-001

*Notification infrastructure for user communications*

### Acceptance Criteria

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

### API

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

---

## 7. REQ-PROD-001: Product CRUD

**Phase:** 2

**Depends on:** REQ-AUTH-002

*Products are the core catalog entity*

### Acceptance Criteria

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

### API

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

---

## 8. REQ-PROD-002: Product Categories

**Phase:** 2

**Depends on:** REQ-PROD-001

*Hierarchical categorization of products*

### Acceptance Criteria

1. GET /categories returns the full category tree with nested children.
2. POST /categories creates a new category (admin only) and returns 201 Created.
3. POST /categories with a duplicate slug returns 409 Conflict.
4. PUT /categories/:id updates the category name, slug, or parent_id (admin only).
5. PUT /categories/:id with a duplicate slug returns 409 Conflict.
6. Categories with a null parent_id are root-level categories.
7. Categories with a valid parent_id are nested under their parent in the tree response.
8. Non-admin users receive 403 Forbidden when attempting to create or update categories.
9. GET /categories/:id returns a single category with its children.
10. GET /categories/:id returns 404 Not Found for nonexistent categories.

### API

### GET /categories

**Response (200 OK):**
```json
{
  "categories": [
    {
      "id": 1,
      "name": "Electronics",
      "slug": "electronics",
      "parent_id": null,
      "children": [
        {
          "id": 3,
          "name": "Headphones",
          "slug": "headphones",
          "parent_id": 1,
          "children": []
        }
      ]
    },
    {
      "id": 2,
      "name": "Books",
      "slug": "books",
      "parent_id": null,
      "children": []
    }
  ]
}
```

### POST /categories

**Request:**
```json
{
  "name": "Headphones",
  "slug": "headphones",
  "parent_id": 1
}
```

**Response (201 Created):**
```json
{
  "id": 3,
  "name": "Headphones",
  "slug": "headphones",
  "parent_id": 1,
  "created_at": "2026-01-15T10:30:00Z"
}
```

**Error (409 Conflict):**
```json
{
  "error": "slug already exists"
}
```

**Error (403 Forbidden):**
```json
{
  "error": "admin access required"
}
```

### PUT /categories/:id

**Request:**
```json
{
  "name": "Audio Headphones",
  "slug": "audio-headphones"
}
```

**Response (200 OK):**
```json
{
  "id": 3,
  "name": "Audio Headphones",
  "slug": "audio-headphones",
  "parent_id": 1,
  "created_at": "2026-01-15T10:30:00Z"
}
```

### GET /categories/:id

**Response (200 OK):**
```json
{
  "id": 1,
  "name": "Electronics",
  "slug": "electronics",
  "parent_id": null,
  "children": [
    {
      "id": 3,
      "name": "Headphones",
      "slug": "headphones",
      "parent_id": 1,
      "children": []
    }
  ],
  "created_at": "2026-01-15T10:00:00Z"
}
```

**Error (404 Not Found):**
```json
{
  "error": "category not found"
}
```

---

## 9. REQ-INV-001: Inventory Tracking

**Phase:** 2

**Depends on:** REQ-PROD-001

*Stock management for products*

### Acceptance Criteria

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

### API

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

---

## 10. REQ-AUDIT-001: Audit Logging

**Phase:** 3

**Depends on:** REQ-AUTH-002

*Append-only audit trail for compliance and debugging*

### Acceptance Criteria

1. Every create operation on products, orders, payments, shipments, reviews, and discount codes creates an audit log entry.
2. Every update operation on the above entities creates an audit log entry.
3. Every delete operation on the above entities creates an audit log entry.
4. Each audit log entry contains user_id, action, entity_type, entity_id, details (JSON), and timestamp.
5. The action field is one of: "create", "update", "delete".
6. The details field contains a JSON representation of the relevant changes or entity state.
7. GET /admin/audit-log returns a paginated list of audit log entries (admin only).
8. GET /admin/audit-log supports filtering by entity_type query parameter.
9. GET /admin/audit-log supports filtering by user_id query parameter.
10. GET /admin/audit-log supports filtering by start_date and end_date query parameters (ISO 8601).
11. GET /admin/audit-log returns 403 if the authenticated user is not an admin.
12. Audit log entries are append-only: no PUT or DELETE endpoints exist for audit log entries.

### API

### GET /admin/audit-log

**Request:**
```
GET /admin/audit-log?entity_type=product&user_id=2&start_date=2026-01-01T00:00:00Z&end_date=2026-01-31T23:59:59Z&page=1&per_page=20
Authorization: Bearer <admin_token>
```

**Response (200 OK):**
```json
{
  "entries": [
    {
      "id": 42,
      "user_id": 2,
      "action": "create",
      "entity_type": "product",
      "entity_id": 3,
      "details": {
        "name": "Widget",
        "price": 39.99,
        "sku": "WDG-001"
      },
      "timestamp": "2026-01-10T08:00:00Z"
    },
    {
      "id": 45,
      "user_id": 2,
      "action": "update",
      "entity_type": "product",
      "entity_id": 3,
      "details": {
        "field": "price",
        "old_value": 39.99,
        "new_value": 34.99
      },
      "timestamp": "2026-01-15T09:00:00Z"
    }
  ],
  "page": 1,
  "per_page": 20,
  "total": 2
}
```

**Error (403 Forbidden):**
```json
{
  "error": "admin access required"
}
```

---

## 11. REQ-PROD-003: Product Search

**Phase:** 3

**Depends on:** REQ-PROD-001, REQ-PROD-002

*Search and filtering capabilities for the product catalog*

### Acceptance Criteria

1. GET /products?search=keyword performs a case-insensitive text search across product name and description fields.
2. GET /products?category=id filters products by the specified category_id.
3. GET /products?min_price=X&max_price=Y filters products within the given price range (inclusive).
4. GET /products?sort=price_asc sorts products by price ascending.
5. GET /products?sort=price_desc sorts products by price descending.
6. GET /products?sort=newest sorts products by created_at descending.
7. Multiple filters can be combined (e.g., ?search=phone&category=1&min_price=100&max_price=500&sort=price_asc).
8. Only products with is_active=true are returned regardless of filters applied.
9. Search results include pagination metadata (page, per_page, total).
10. An empty search result returns 200 OK with an empty products array and total of 0.

### API

### GET /products?search=wireless&category=3&min_price=50&max_price=100&sort=price_asc

**Response (200 OK):**
```json
{
  "products": [
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
      "created_at": "2026-01-15T10:30:00Z"
    }
  ],
  "page": 1,
  "per_page": 20,
  "total": 1
}
```

### GET /products?search=nonexistent

**Response (200 OK):**
```json
{
  "products": [],
  "page": 1,
  "per_page": 20,
  "total": 0
}
```

---

## 12. REQ-CART-001: Shopping Cart

**Phase:** 3

**Depends on:** REQ-AUTH-002, REQ-PROD-001, REQ-INV-001

*Cart management for authenticated users*

### Acceptance Criteria

1. GET /cart returns the authenticated user's cart items with product details (name, price, image_url) and per-item subtotal.
2. GET /cart includes a cart_total representing the sum of all item subtotals.
3. POST /cart adds an item to the cart with product_id and quantity, returning 201 Created.
4. POST /cart with a product_id for an inactive product returns 400 Bad Request.
5. POST /cart for a product already in the cart increments the existing quantity rather than creating a duplicate entry.
6. PUT /cart/:item_id updates the quantity of a cart item and returns 200 OK.
7. PUT /cart/:item_id with quantity of 0 removes the item from the cart.
8. DELETE /cart/:item_id removes a specific item from the cart and returns 200 OK.
9. DELETE /cart clears all items from the authenticated user's cart and returns 200 OK.
10. GET /cart returns 401 Unauthorized when no valid token is provided.
11. PUT /cart/:item_id returns 404 Not Found for items not belonging to the authenticated user.

### API

### GET /cart

**Response (200 OK):**
```json
{
  "items": [
    {
      "id": 1,
      "product_id": 1,
      "name": "Wireless Headphones",
      "price": 79.99,
      "image_url": "https://example.com/images/wh-1000.jpg",
      "quantity": 2,
      "subtotal": 159.98
    }
  ],
  "cart_total": 159.98
}
```

### POST /cart

**Request:**
```json
{
  "product_id": 1,
  "quantity": 2
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "product_id": 1,
  "name": "Wireless Headphones",
  "price": 79.99,
  "quantity": 2,
  "subtotal": 159.98
}
```

**Error (400 Bad Request):**
```json
{
  "error": "product is not available"
}
```

### PUT /cart/:item_id

**Request:**
```json
{
  "quantity": 3
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "product_id": 1,
  "name": "Wireless Headphones",
  "price": 79.99,
  "quantity": 3,
  "subtotal": 239.97
}
```

**Error (404 Not Found):**
```json
{
  "error": "cart item not found"
}
```

### DELETE /cart/:item_id

**Response (200 OK):**
```json
{
  "message": "item removed from cart"
}
```

### DELETE /cart

**Response (200 OK):**
```json
{
  "message": "cart cleared"
}
```

---

## 13. REQ-CART-002: Cart Validation

**Phase:** 3

**Depends on:** REQ-CART-001

*Inventory-aware cart validation*

### Acceptance Criteria

1. POST /cart rejects adding a quantity that exceeds the available inventory (quantity - reserved_quantity) with 400 Bad Request.
2. PUT /cart/:item_id rejects updating to a quantity that exceeds the available inventory with 400 Bad Request.
3. The error response for insufficient stock includes the available quantity.
4. If a product's available inventory drops to zero after being added to a cart, the item remains in the cart but is flagged with an out_of_stock indicator.
5. GET /cart includes an out_of_stock boolean on each cart item reflecting current inventory availability.
6. Cart subtotal for each item is calculated as item quantity multiplied by the product's current unit price.
7. The cart_total reflects the sum of all item subtotals using current prices.
8. Updating a cart item quantity to a value within available stock succeeds with 200 OK.
9. Adding zero or negative quantity returns 400 Bad Request.

### API

### POST /cart (insufficient stock)

**Request:**
```json
{
  "product_id": 1,
  "quantity": 999
}
```

**Error (400 Bad Request):**
```json
{
  "error": "insufficient stock",
  "available": 45
}
```

### GET /cart (with out-of-stock item)

**Response (200 OK):**
```json
{
  "items": [
    {
      "id": 1,
      "product_id": 1,
      "name": "Wireless Headphones",
      "price": 79.99,
      "image_url": "https://example.com/images/wh-1000.jpg",
      "quantity": 2,
      "subtotal": 159.98,
      "out_of_stock": false
    },
    {
      "id": 2,
      "product_id": 5,
      "name": "Vintage Record Player",
      "price": 249.99,
      "image_url": "https://example.com/images/vrp-100.jpg",
      "quantity": 1,
      "subtotal": 249.99,
      "out_of_stock": true
    }
  ],
  "cart_total": 409.97
}
```

### PUT /cart/:item_id (insufficient stock)

**Request:**
```json
{
  "quantity": 500
}
```

**Error (400 Bad Request):**
```json
{
  "error": "insufficient stock",
  "available": 45
}
```

---

## 14. REQ-DISC-001: Discount Codes

**Phase:** 3

**Depends on:** REQ-PROD-001, REQ-CART-001

*Discount code management and cart application*

### Acceptance Criteria

1. POST /discounts creates a new discount code (admin only) and returns 201 Created.
2. POST /discounts with a duplicate code returns 409 Conflict.
3. The discount_percent must be between 1 and 100 inclusive; values outside this range return 400 Bad Request.
4. POST /cart/apply-discount validates the code exists and is_active before applying.
5. POST /cart/apply-discount validates the code is within the valid_from and valid_until date range.
6. POST /cart/apply-discount validates current_uses is below max_uses (if max_uses is set).
7. POST /cart/apply-discount returns 400 Bad Request with a descriptive error if any validation fails.
8. A successfully applied discount is reflected in the cart_total returned by GET /cart.
9. DELETE /cart/discount removes the applied discount from the cart and returns 200 OK.
10. The current_uses field is incremented when an order is placed with the discount code, not when the code is applied to the cart.
11. Non-admin users receive 403 Forbidden when attempting to create discount codes.

### API

### POST /discounts

**Request:**
```json
{
  "code": "SUMMER20",
  "discount_percent": 20,
  "max_uses": 100,
  "valid_from": "2026-06-01T00:00:00Z",
  "valid_until": "2026-08-31T23:59:59Z"
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "code": "SUMMER20",
  "discount_percent": 20,
  "max_uses": 100,
  "current_uses": 0,
  "valid_from": "2026-06-01T00:00:00Z",
  "valid_until": "2026-08-31T23:59:59Z",
  "is_active": true
}
```

**Error (409 Conflict):**
```json
{
  "error": "discount code already exists"
}
```

**Error (403 Forbidden):**
```json
{
  "error": "admin access required"
}
```

### POST /cart/apply-discount

**Request:**
```json
{
  "code": "SUMMER20"
}
```

**Response (200 OK):**
```json
{
  "message": "discount applied",
  "discount_percent": 20,
  "cart_total": 127.98,
  "discount_amount": 32.00
}
```

**Error (400 Bad Request):**
```json
{
  "error": "discount code has expired"
}
```

**Error (400 Bad Request):**
```json
{
  "error": "discount code usage limit reached"
}
```

### DELETE /cart/discount

**Response (200 OK):**
```json
{
  "message": "discount removed",
  "cart_total": 159.98
}
```

---

## 15. REQ-ORD-001: Order Placement

**Phase:** 4

**Depends on:** REQ-CART-001

*Atomic cart-to-order conversion*

### Acceptance Criteria

1. POST /orders creates an order from the authenticated user's cart and returns 201 Created.
2. The order total is calculated from all cart item subtotals, with any applied discount code percentage deducted.
3. A shipping_address field is required; omitting it returns 400 Bad Request.
4. Each product's reserved_quantity is incremented by the ordered quantity during order placement.
5. If any cart item quantity exceeds the product's available inventory, the entire order fails with 400 Bad Request.
6. The error response for insufficient stock identifies which product(s) are unavailable.
7. Order items are created with the unit_price locked at the product's current price at time of order.
8. The cart is cleared after successful order placement.
9. If a discount code is applied, its current_uses is incremented by one.
10. The new order's status is set to "pending".
11. The operation is atomic: if any step fails, no inventory is reserved, no order is created, and the cart is unchanged.
12. POST /orders with an empty cart returns 400 Bad Request.

### API

### POST /orders

**Request:**
```json
{
  "shipping_address": "123 Main St, Springfield, IL 62704"
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "user_id": 1,
  "status": "pending",
  "items": [
    {
      "id": 1,
      "product_id": 1,
      "name": "Wireless Headphones",
      "quantity": 2,
      "unit_price": 79.99,
      "subtotal": 159.98
    }
  ],
  "subtotal": 159.98,
  "discount_percent": 20,
  "discount_amount": 32.00,
  "total": 127.98,
  "shipping_address": "123 Main St, Springfield, IL 62704",
  "created_at": "2026-01-20T14:00:00Z"
}
```

**Error (400 Bad Request - empty cart):**
```json
{
  "error": "cart is empty"
}
```

**Error (400 Bad Request - insufficient stock):**
```json
{
  "error": "insufficient stock",
  "unavailable_items": [
    {
      "product_id": 5,
      "name": "Vintage Record Player",
      "requested": 3,
      "available": 1
    }
  ]
}
```

**Error (400 Bad Request - missing address):**
```json
{
  "error": "shipping_address is required"
}
```

---

## 16. REQ-ORD-002: Order Status

**Phase:** 4

**Depends on:** REQ-ORD-001

*Order status state machine with valid transitions*

### Acceptance Criteria

1. Orders support the following status values: pending, paid, shipped, in_transit, delivered, cancelled.
2. The valid status transitions are: pending to paid, paid to shipped, shipped to in_transit, in_transit to delivered, and pending to cancelled.
3. PUT /orders/:id/status with an invalid transition returns 422 Unprocessable Entity with the current status and allowed transitions.
4. When an order is cancelled (pending to cancelled), all reserved_quantity values for the order's items are decremented (released).
5. GET /orders/:id returns the order with its current status and all order items.
6. GET /orders/:id/history returns the chronological list of status changes with timestamps.
7. Only the order's owner or an admin can view or update the order status.
8. GET /orders/:id returns 404 Not Found for orders not belonging to the authenticated user (unless admin).
9. Each status change is recorded in the audit_log with the old and new status values.
10. PUT /orders/:id/status on an already delivered or cancelled order returns 422 Unprocessable Entity.
11. GET /orders lists all orders for the authenticated user with pagination.

### API

### PUT /orders/:id/status

**Request:**
```json
{
  "status": "paid"
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "status": "paid",
  "previous_status": "pending",
  "updated_at": "2026-01-20T15:00:00Z"
}
```

**Error (422 Unprocessable Entity):**
```json
{
  "error": "invalid status transition",
  "current_status": "pending",
  "allowed_transitions": ["paid", "cancelled"]
}
```

### GET /orders/:id

**Response (200 OK):**
```json
{
  "id": 1,
  "user_id": 1,
  "status": "paid",
  "items": [
    {
      "id": 1,
      "product_id": 1,
      "name": "Wireless Headphones",
      "quantity": 2,
      "unit_price": 79.99,
      "subtotal": 159.98
    }
  ],
  "total": 127.98,
  "shipping_address": "123 Main St, Springfield, IL 62704",
  "created_at": "2026-01-20T14:00:00Z",
  "updated_at": "2026-01-20T15:00:00Z"
}
```

**Error (404 Not Found):**
```json
{
  "error": "order not found"
}
```

### GET /orders/:id/history

**Response (200 OK):**
```json
{
  "order_id": 1,
  "history": [
    {
      "from_status": null,
      "to_status": "pending",
      "timestamp": "2026-01-20T14:00:00Z"
    },
    {
      "from_status": "pending",
      "to_status": "paid",
      "timestamp": "2026-01-20T15:00:00Z"
    }
  ]
}
```

### GET /orders

**Response (200 OK):**
```json
{
  "orders": [
    {
      "id": 1,
      "status": "paid",
      "total": 127.98,
      "created_at": "2026-01-20T14:00:00Z"
    }
  ],
  "page": 1,
  "per_page": 20,
  "total": 1
}
```

---

## 17. REQ-PAY-001: Payment Processing

**Phase:** 4

**Depends on:** REQ-ORD-001

*Mock payment processor for order payment*

### Acceptance Criteria

1. POST /orders/:id/pay processes payment for the specified order.
2. The mock payment processor accepts any amount where amount <= 10000.
3. The mock payment processor rejects amounts where amount > 10000 with a payment failure error.
4. A successful payment creates a payment record with method, amount, and a UUID transaction_id.
5. A successful payment transitions the order status from "pending" to "paid".
6. POST /orders/:id/pay returns 400 if the order is not in "pending" status.
7. POST /orders/:id/pay returns 403 if the authenticated user is not the order owner.
8. POST /orders/:id/pay returns 404 if the order does not exist.
9. The payment record stores the payment method (e.g., "credit_card", "debit_card").
10. POST /orders/:id/pay returns 402 Payment Required when the mock processor rejects the payment.

### API

### POST /orders/:id/pay

**Request:**
```json
{
  "method": "credit_card"
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "order_id": 5,
  "method": "credit_card",
  "amount": 79.98,
  "transaction_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "completed",
  "created_at": "2026-01-20T14:05:00Z"
}
```

**Error (400 Bad Request):**
```json
{
  "error": "order is not in pending status"
}
```

**Error (402 Payment Required):**
```json
{
  "error": "payment rejected: amount exceeds processor limit"
}
```

**Error (403 Forbidden):**
```json
{
  "error": "not authorized to pay for this order"
}
```

---

## 18. REQ-SHIP-001: Shipment Creation

**Phase:** 5

**Depends on:** REQ-ORD-001

*Fulfillment shipment creation for paid orders*

### Acceptance Criteria

1. POST /orders/:id/ship creates a new shipment record for the specified order.
2. Only users with the admin role may create shipments.
3. POST /orders/:id/ship returns 403 if the authenticated user is not an admin.
4. Only orders in "paid" status can be shipped.
5. POST /orders/:id/ship returns 400 if the order is not in "paid" status.
6. The request must include carrier and tracking_number fields.
7. POST /orders/:id/ship returns 422 if carrier or tracking_number is missing.
8. The shipment record is created with status "processing".
9. A successful shipment creation transitions the order status from "paid" to "shipped".
10. Upon shipment creation, reserved_quantity for each order item is deducted from inventory (actual stock reduction).
11. POST /orders/:id/ship returns 404 if the order does not exist.

### API

### POST /orders/:id/ship

**Request:**
```json
{
  "carrier": "FedEx",
  "tracking_number": "FX-1234567890"
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "order_id": 5,
  "carrier": "FedEx",
  "tracking_number": "FX-1234567890",
  "status": "processing",
  "created_at": "2026-01-22T08:00:00Z"
}
```

**Error (400 Bad Request):**
```json
{
  "error": "only paid orders can be shipped"
}
```

**Error (403 Forbidden):**
```json
{
  "error": "admin access required"
}
```

**Error (422 Unprocessable Entity):**
```json
{
  "error": "carrier and tracking_number are required"
}
```

---

## 19. REQ-ORD-003: Order History

**Phase:** 5

**Depends on:** REQ-ORD-002

*Order listing, detail, history, and cancellation*

### Acceptance Criteria

1. GET /orders returns a paginated list of the authenticated user's orders sorted by creation date (newest first).
2. GET /orders supports page and per_page query parameters with sensible defaults (page=1, per_page=20).
3. GET /orders/:id returns the full order record including line items, totals, and current status.
4. GET /orders/:id returns 404 if the order does not exist or belongs to another user.
5. GET /orders/:id/history returns the chronological list of status changes for the order, each with old_status, new_status, changed_at, and changed_by.
6. PUT /orders/:id/cancel transitions a pending order to "cancelled" status.
7. PUT /orders/:id/cancel releases all reserved_quantity for the order's items back to available inventory.
8. PUT /orders/:id/cancel returns 400 if the order is not in "pending" status.
9. PUT /orders/:id/cancel returns 403 if the authenticated user is not the order owner.
10. A cancellation event is recorded in the order's status change history.

### API

### GET /orders

**Request:**
```
GET /orders?page=1&per_page=10
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "orders": [
    {
      "id": 5,
      "user_id": 1,
      "status": "paid",
      "total": 79.98,
      "item_count": 2,
      "created_at": "2026-01-20T14:00:00Z"
    }
  ],
  "page": 1,
  "per_page": 10,
  "total": 1
}
```

### GET /orders/:id

**Response (200 OK):**
```json
{
  "id": 5,
  "user_id": 1,
  "status": "paid",
  "total": 79.98,
  "items": [
    {
      "product_id": 3,
      "product_name": "Widget",
      "quantity": 2,
      "unit_price": 39.99
    }
  ],
  "created_at": "2026-01-20T14:00:00Z",
  "updated_at": "2026-01-20T14:05:00Z"
}
```

**Error (404 Not Found):**
```json
{
  "error": "order not found"
}
```

### GET /orders/:id/history

**Response (200 OK):**
```json
{
  "history": [
    {
      "old_status": null,
      "new_status": "pending",
      "changed_at": "2026-01-20T14:00:00Z",
      "changed_by": 1
    },
    {
      "old_status": "pending",
      "new_status": "paid",
      "changed_at": "2026-01-20T14:05:00Z",
      "changed_by": 1
    }
  ]
}
```

### PUT /orders/:id/cancel

**Response (200 OK):**
```json
{
  "id": 5,
  "status": "cancelled",
  "cancelled_at": "2026-01-21T09:00:00Z"
}
```

**Error (400 Bad Request):**
```json
{
  "error": "only pending orders can be cancelled"
}
```

---

## 20. REQ-PAY-002: Payment Refunds

**Phase:** 5

**Depends on:** REQ-PAY-001, REQ-ORD-002

*Admin-initiated refunds for paid orders*

### Acceptance Criteria

1. POST /orders/:id/refund processes a refund for the specified order.
2. Only users with the admin role may issue refunds.
3. POST /orders/:id/refund returns 403 if the authenticated user is not an admin.
4. Only orders in "paid" status can be refunded.
5. POST /orders/:id/refund returns 400 if the order is not in "paid" status.
6. A refund creates a payment record with a negative amount equal to the original payment amount.
7. The refund payment record includes a new transaction_id (UUID) and method "refund".
8. A successful refund transitions the order status from "paid" to "cancelled".
9. A successful refund releases all reserved_quantity for the order's items back to available inventory.
10. POST /orders/:id/refund returns 404 if the order does not exist.

### API

### POST /orders/:id/refund

**Request:**
```
POST /orders/5/refund
Authorization: Bearer <admin_token>
```

**Response (200 OK):**
```json
{
  "id": 2,
  "order_id": 5,
  "method": "refund",
  "amount": -79.98,
  "transaction_id": "f1e2d3c4-b5a6-7890-abcd-ef0987654321",
  "status": "completed",
  "created_at": "2026-01-21T10:00:00Z"
}
```

**Error (400 Bad Request):**
```json
{
  "error": "only paid orders can be refunded"
}
```

**Error (403 Forbidden):**
```json
{
  "error": "admin access required"
}
```

---

## 21. REQ-SHIP-002: Shipment Status

**Phase:** 5

**Depends on:** REQ-SHIP-001, REQ-ORD-002

*Shipment lifecycle tracking with forward-only transitions*

### Acceptance Criteria

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

### API

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

---

## 22. REQ-REV-001: Review Submission

**Phase:** 6

**Depends on:** REQ-AUTH-002, REQ-PROD-001, REQ-ORD-002, REQ-SHIP-002

*Product reviews from verified purchasers*

### Acceptance Criteria

1. POST /products/:id/reviews creates a new review for the specified product.
2. The user must have at least one delivered order containing the product to submit a review.
3. POST /products/:id/reviews returns 403 if the user has no delivered order containing the product.
4. Rating must be an integer between 1 and 5 inclusive.
5. Title and body fields are required and must be non-empty.
6. POST /products/:id/reviews returns 422 if rating, title, or body is missing or invalid.
7. A user may submit only one review per product.
8. POST /products/:id/reviews returns 409 if the user has already reviewed the product.
9. Newly created reviews have is_approved set to false by default.
10. GET /products/:id/reviews returns a paginated list of approved reviews only.
11. GET /products/:id/reviews supports page and per_page query parameters.
12. Unapproved reviews are not visible in the GET /products/:id/reviews listing.

### API

### POST /products/:id/reviews

**Request:**
```json
{
  "rating": 5,
  "title": "Excellent product",
  "body": "This widget exceeded my expectations. Highly recommended."
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "product_id": 3,
  "user_id": 1,
  "rating": 5,
  "title": "Excellent product",
  "body": "This widget exceeded my expectations. Highly recommended.",
  "is_approved": false,
  "created_at": "2026-01-26T10:00:00Z"
}
```

**Error (403 Forbidden):**
```json
{
  "error": "you must have a delivered order containing this product to submit a review"
}
```

**Error (409 Conflict):**
```json
{
  "error": "you have already reviewed this product"
}
```

**Error (422 Unprocessable Entity):**
```json
{
  "error": "rating must be between 1 and 5"
}
```

### GET /products/:id/reviews

**Request:**
```
GET /products/3/reviews?page=1&per_page=10
```

**Response (200 OK):**
```json
{
  "reviews": [
    {
      "id": 1,
      "product_id": 3,
      "user_id": 1,
      "username": "alice",
      "rating": 5,
      "title": "Excellent product",
      "body": "This widget exceeded my expectations. Highly recommended.",
      "created_at": "2026-01-26T10:00:00Z"
    }
  ],
  "page": 1,
  "per_page": 10,
  "total": 1
}
```

---

## 23. REQ-REV-002: Review Moderation

**Phase:** 6

**Depends on:** REQ-REV-001

*Admin approval and deletion of reviews*

### Acceptance Criteria

1. PUT /reviews/:id/approve sets is_approved to true on the specified review.
2. Only users with the admin role may approve reviews.
3. PUT /reviews/:id/approve returns 403 if the authenticated user is not an admin.
4. DELETE /reviews/:id deletes the specified review.
5. Only the review author or an admin may delete a review.
6. DELETE /reviews/:id returns 403 if the user is neither the author nor an admin.
7. DELETE /reviews/:id returns 404 if the review does not exist.
8. Product average_rating is computed from approved reviews only.
9. Product review_count reflects only approved reviews.
10. GET /products/:id includes average_rating and review_count fields.
11. When an approved review is deleted, the product's average_rating and review_count are recalculated.

### API

### PUT /reviews/:id/approve

**Request:**
```
PUT /reviews/1/approve
Authorization: Bearer <admin_token>
```

**Response (200 OK):**
```json
{
  "id": 1,
  "product_id": 3,
  "user_id": 1,
  "rating": 5,
  "title": "Excellent product",
  "body": "This widget exceeded my expectations. Highly recommended.",
  "is_approved": true,
  "created_at": "2026-01-26T10:00:00Z"
}
```

**Error (403 Forbidden):**
```json
{
  "error": "admin access required"
}
```

### DELETE /reviews/:id

**Response (204 No Content):**
```
(empty body)
```

**Error (403 Forbidden):**
```json
{
  "error": "not authorized to delete this review"
}
```

### GET /products/:id (with review aggregates)

**Response (200 OK):**
```json
{
  "id": 3,
  "name": "Widget",
  "description": "A fine widget",
  "price": 39.99,
  "sku": "WDG-001",
  "average_rating": 4.5,
  "review_count": 12,
  "created_at": "2026-01-10T08:00:00Z"
}
```

---

## 24. REQ-NOTIF-002: Order Notifications

**Phase:** 6

**Depends on:** REQ-NOTIF-001, REQ-ORD-002, REQ-SHIP-002

*Automated notifications at order lifecycle events*

### Acceptance Criteria

1. An "order_placed" notification is created for the user when POST /orders succeeds.
2. A "payment_received" notification is created for the user when POST /orders/:id/pay succeeds.
3. An "order_shipped" notification is created for the user when POST /orders/:id/ship succeeds.
4. An "order_delivered" notification is created for the user when a shipment status is updated to "delivered".
5. Each notification includes the order ID in the body text.
6. The "order_placed" notification body includes the order total.
7. The "payment_received" notification body includes the payment amount and transaction ID.
8. The "order_shipped" notification body includes the carrier and tracking number.
9. The "order_delivered" notification body includes the delivery timestamp.
10. All auto-created notifications have is_read set to false.
11. Notifications are created for the order owner, not the admin performing the action.

### API

Notifications are created as side effects of existing endpoints. The following examples show the notification records produced.

**order_placed notification:**
```json
{
  "id": 1,
  "user_id": 1,
  "type": "order_placed",
  "subject": "Order Confirmed",
  "body": "Your order #5 has been placed. Total: $79.98.",
  "is_read": false,
  "created_at": "2026-01-20T14:00:00Z"
}
```

**payment_received notification:**
```json
{
  "id": 2,
  "user_id": 1,
  "type": "payment_received",
  "subject": "Payment Received",
  "body": "Payment of $79.98 received for order #5. Transaction: a1b2c3d4-e5f6-7890-abcd-ef1234567890.",
  "is_read": false,
  "created_at": "2026-01-20T14:05:00Z"
}
```

**order_shipped notification:**
```json
{
  "id": 3,
  "user_id": 1,
  "type": "order_shipped",
  "subject": "Order Shipped",
  "body": "Your order #5 has been shipped via FedEx. Tracking: FX-1234567890.",
  "is_read": false,
  "created_at": "2026-01-22T08:00:00Z"
}
```

**order_delivered notification:**
```json
{
  "id": 4,
  "user_id": 1,
  "type": "order_delivered",
  "subject": "Order Delivered",
  "body": "Your order #5 was delivered on 2026-01-25T15:30:00Z.",
  "is_read": false,
  "created_at": "2026-01-25T15:30:00Z"
}
```

---

## 25. REQ-TEST-001: Comprehensive Test Suite

**Phase:** 7

**Depends on:** REQ-AUTH-003, REQ-PROD-003, REQ-CART-002, REQ-DISC-001, REQ-ORD-003, REQ-PAY-002, REQ-SHIP-002, REQ-REV-002, REQ-NOTIF-002, REQ-AUDIT-001, REQ-VALID-001

*Verification depends on test coverage across all requirements*

### Acceptance Criteria

1. A single command (e.g., `make test`, `npm test`, `pytest`, `go test ./...`) runs the entire test suite.
2. The test suite creates a fresh test database before each run and tears it down after completion.
3. Tests do not depend on external services or pre-existing data.
4. Auth tests cover user registration, login, profile view/update, and role-based access control (REQ-AUTH-001 through REQ-AUTH-003).
5. Product tests cover CRUD operations, category management, search, filtering, and pagination (REQ-PROD-001 through REQ-PROD-003).
6. Inventory tests cover stock level tracking, reserved quantity management, and low-stock alerts (REQ-INV-001).
7. Cart tests cover add/update/remove/clear operations, stock validation, and discount code application (REQ-CART-001, REQ-CART-002, REQ-DISC-001).
8. Order tests cover placement, status transitions, history listing, and cancellation with inventory release (REQ-ORD-001 through REQ-ORD-003).
9. Payment tests cover successful processing, mock processor rejection for amounts over 10000, and admin refunds with inventory release (REQ-PAY-001, REQ-PAY-002).
10. Shipping tests cover shipment creation, status transitions (forward-only), delivery confirmation, and tracking retrieval (REQ-SHIP-001, REQ-SHIP-002).
11. Review tests cover submission with purchase eligibility check, one-review-per-user enforcement, approval moderation, deletion, and average rating computation (REQ-REV-001, REQ-REV-002).
12. Notification tests cover listing, read marking, read-all, and automatic creation at order lifecycle events (REQ-NOTIF-001, REQ-NOTIF-002).
13. Audit log tests cover automatic recording of all mutations and admin query with filtering (REQ-AUDIT-001).
14. Validation tests cover all invalid input cases returning 422 with descriptive errors (REQ-VALID-001).
15. Error code tests cover 401 (missing/invalid token), 403 (insufficient permissions), 404 (missing resource), and 409 (uniqueness violations).
16. The test command exits 0 when all tests pass and non-zero when any test fails.
17. Test output clearly identifies which tests passed and which failed.

---
