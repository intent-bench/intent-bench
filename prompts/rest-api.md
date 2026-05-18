# Task: Build a REST API with Authentication

Build a REST API for a bookstore inventory system. The API must support
user authentication and role-based access control.

## Data Model

- **Books**: id, title, author, isbn, price, stock_quantity, created_at
- **Users**: id, username, email, password_hash, role (admin|staff|viewer), created_at

## Endpoints

### Authentication
- POST /auth/register -- Create a new user (default role: viewer)
- POST /auth/login -- Returns a JWT token
- GET /auth/me -- Returns the authenticated user's profile

### Books (all require authentication)
- GET /books -- List books with pagination (?page=1&per_page=20)
- GET /books/:id -- Get a single book
- POST /books -- Create a book (admin and staff only)
- PUT /books/:id -- Update a book (admin and staff only)
- DELETE /books/:id -- Delete a book (admin only)

### Admin
- GET /users -- List all users (admin only)
- PUT /users/:id/role -- Change a user's role (admin only)

## Requirements

1. Passwords must be hashed (bcrypt or argon2)
2. JWT tokens expire after 1 hour
3. Pagination: default 20 items per page, max 100
4. ISBN must be unique and validated (10 or 13 digits)
5. Return 401 for missing/invalid tokens
6. Return 403 for insufficient role permissions
7. Return 404 for missing resources
8. Return 422 for validation errors with field-level messages
9. All list endpoints return total count in response headers or body
10. Include a /health endpoint (no auth required)

## Success Criterion

All tests pass. The API must be testable without external services
(use an in-memory or SQLite database).
