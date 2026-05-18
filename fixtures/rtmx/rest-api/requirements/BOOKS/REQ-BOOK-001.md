# REQ-BOOK-001: Book Listing with Pagination

## Requirement
GET /books returns paginated list with default 20 per page, max 100.

## Acceptance Criteria
- Query params: `page` (default 1), `per_page` (default 20, max 100)
- Response includes book array and total count
- Per_page > 100 is clamped to 100
- Returns 200 with empty array when no books exist

## Dependencies
- REQ-AUTH-002, REQ-AUTH-005 (requires authentication)

## Test
`TestListBooks` in test module
