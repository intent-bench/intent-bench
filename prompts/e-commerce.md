# E-Commerce API

Build a complete e-commerce REST API from scratch in this empty project directory.

## Data Model

- **Users**: id, username, email, password_hash, role (customer|admin), created_at
- **Products**: id, name, description, price, sku, category_id, image_url, is_active, created_at, updated_at
- **Categories**: id, name, slug, parent_id (self-referencing for nested categories)
- **Inventory**: product_id, quantity, reserved_quantity, low_stock_threshold
- **Cart Items**: id, user_id, product_id, quantity, added_at
- **Orders**: id, user_id, status, total_amount, shipping_address, placed_at, updated_at
- **Order Items**: id, order_id, product_id, quantity, unit_price
- **Payments**: id, order_id, method, amount, status, transaction_id, paid_at
- **Shipments**: id, order_id, carrier, tracking_number, status, shipped_at, delivered_at
- **Reviews**: id, user_id, product_id, rating (1-5), title, body, is_approved, created_at
- **Discount Codes**: id, code, discount_percent, max_uses, current_uses, valid_from, valid_until, is_active
- **Notifications**: id, user_id, type, subject, body, is_read, created_at
- **Audit Log**: id, user_id, action, entity_type, entity_id, details, timestamp

## Endpoints

### Authentication
- POST /auth/register -- Create a new user (default role: customer)
- POST /auth/login -- Returns a JWT token
- GET /auth/profile -- Returns the authenticated user's profile
- PUT /auth/profile -- Update profile (username, email)

### Products
- GET /products -- List products with pagination and filtering (?category=&min_price=&max_price=&search=)
- GET /products/:id -- Get product details (includes average rating)
- POST /products -- Create product (admin only)
- PUT /products/:id -- Update product (admin only)
- DELETE /products/:id -- Soft delete product (admin only, sets is_active=false)

### Categories
- GET /categories -- List all categories (nested tree structure)
- POST /categories -- Create category (admin only)
- PUT /categories/:id -- Update category (admin only)

### Inventory
- GET /products/:id/inventory -- Get stock level
- PUT /products/:id/inventory -- Update stock (admin only)
- GET /inventory/low-stock -- List products below low_stock_threshold (admin only)

### Shopping Cart
- GET /cart -- Get current user's cart items with product details and subtotal
- POST /cart -- Add item to cart (quantity, product_id)
- PUT /cart/:item_id -- Update cart item quantity
- DELETE /cart/:item_id -- Remove item from cart
- DELETE /cart -- Clear entire cart

### Orders
- POST /orders -- Place order from current cart contents (validates stock, calculates total, reserves inventory)
- GET /orders -- List current user's orders
- GET /orders/:id -- Get order details with items
- PUT /orders/:id/cancel -- Cancel a pending order (releases reserved inventory)
- GET /orders/:id/history -- Get order status change history

### Payments
- POST /orders/:id/pay -- Process payment for an order (mock payment processor)
- POST /orders/:id/refund -- Refund a paid order (admin only)

### Shipping
- POST /orders/:id/ship -- Create shipment (admin only, sets carrier and tracking number)
- PUT /shipments/:id/status -- Update shipment status (admin only: processing, shipped, in_transit, delivered)
- GET /orders/:id/tracking -- Get shipment tracking info

### Reviews
- POST /products/:id/reviews -- Submit a review (must have a delivered order for this product)
- GET /products/:id/reviews -- List reviews for a product with pagination
- PUT /reviews/:id/approve -- Approve a review (admin only)
- DELETE /reviews/:id -- Delete a review (admin or review author)

### Discount Codes
- POST /discounts -- Create discount code (admin only)
- POST /cart/apply-discount -- Apply discount code to cart
- DELETE /cart/discount -- Remove applied discount

### Notifications
- GET /notifications -- List user's notifications
- PUT /notifications/:id/read -- Mark notification as read
- POST /notifications/read-all -- Mark all as read

### Admin
- GET /admin/audit-log -- List audit log entries with filtering (?entity_type=&user_id=&from=&to=)

## Requirements

1. Passwords must be hashed (bcrypt or argon2)
2. JWT tokens expire after 1 hour
3. Pagination: default 20 items per page, max 100
4. SKU must be unique across products
5. Cart quantities must not exceed available inventory
6. Order placement must atomically reserve inventory
7. Cancellation must release reserved inventory
8. Payment is a mock processor (always succeeds unless amount > 10000)
9. Only products the user has received (order delivered) can be reviewed
10. Each user can review a product only once
11. Reviews require admin approval before appearing in public listings
12. Discount codes enforce max_uses and date validity
13. Discount applies as percentage off the cart subtotal
14. Notifications are automatically created for: order placed, payment received, order shipped, order delivered
15. Audit log records every mutation (create, update, delete) with user context
16. Return 401 for missing/invalid tokens
17. Return 403 for insufficient permissions
18. Return 404 for missing resources
19. Return 409 for uniqueness violations (duplicate email, SKU, discount code)
20. Return 422 for validation errors with descriptive field-level messages

## Technical Constraints

- The service should listen on port 8080 by default
- You may use any programming language and framework
- Use SQLite for persistent storage
- Include a comprehensive test suite that can be run with a single command
- Tests should cover all endpoints, business rules, validation, and error cases
- The test suite should be self-contained (set up and tear down its own test database)
