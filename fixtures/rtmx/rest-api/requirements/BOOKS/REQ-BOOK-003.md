# REQ-BOOK-003: Book Validation

## Requirement
ISBN must be unique and valid (10 or 13 digits). Return 422 with field-level messages.

## Acceptance Criteria
- ISBN validated: must be exactly 10 or 13 digits
- Duplicate ISBN returns 409 or 422
- Missing required fields return 422 with field names
- Price must be non-negative
- Stock quantity must be non-negative integer

## Dependencies
- REQ-BOOK-002

## Test
`TestBookValidation` in test module
