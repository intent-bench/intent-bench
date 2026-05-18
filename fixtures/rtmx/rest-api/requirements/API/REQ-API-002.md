# REQ-API-002: Not Found Handling

## Requirement
Missing resources return 404.

## Acceptance Criteria
- GET /books/:id with nonexistent id returns 404
- PUT /books/:id with nonexistent id returns 404
- DELETE /books/:id with nonexistent id returns 404

## Dependencies
- REQ-BOOK-002

## Test
`TestNotFound` in test module
