# REQ-AUTH-004: Token Expiry

## Requirement
JWT tokens expire after 1 hour.

## Acceptance Criteria
- Token `exp` claim is set to 1 hour from issuance
- Expired tokens return 401

## Dependencies
- REQ-AUTH-002

## Test
`TestTokenExpiry` in test module
