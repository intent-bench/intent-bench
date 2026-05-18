# REQ-TAG-004: Tag Edge Cases

## Requirement
Handle edge cases: empty tags, duplicate tags, whitespace-only tags.

## Acceptance Criteria
- Empty string tags are silently dropped
- Duplicate tags (after normalization) produce only one tag page
- Whitespace-only tags are treated as empty
- No crash or panic on malformed tag data

## Dependencies
- REQ-TAG-001

## Test
`TestTagEdgeCases` in `zs_test.go`
