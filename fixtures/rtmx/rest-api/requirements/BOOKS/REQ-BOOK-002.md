# REQ-BOOK-002: Book CRUD

## Requirement
Full CRUD operations on books with proper HTTP status codes.

## Acceptance Criteria
- POST /books: 201 with created book (title, author, isbn, price, stock_quantity required)
- GET /books/:id: 200 with book object
- PUT /books/:id: 200 with updated book
- DELETE /books/:id: 204 no content

## Dependencies
- REQ-BOOK-001

## Test
`TestBookCRUD` in test module
