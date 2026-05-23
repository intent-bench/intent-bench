# REQ-DB-001: Database Schema

## Status: MISSING
## Priority: P0
## Phase: 1

## Requirement

Initialize a SQLite database with the complete schema for the e-commerce application. The schema must include tables for users, products, categories, inventory, cart items, orders, order items, payments, shipments, reviews, discount codes, notifications, and an audit log. The database must enforce referential integrity via foreign keys and support schema versioning to enable future migrations.

## Acceptance Criteria

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

## API Endpoints

Not applicable. This is an internal infrastructure requirement.

## Dependencies

None. This is the foundational requirement.
