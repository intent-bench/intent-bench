# REQ-VALID-002: Required Field Warning

## Requirement
Warn on missing required title field in front matter.

## Acceptance Criteria
- When a markdown file has valid YAML front matter but no `title` field, log a warning
- Processing continues (do not abort)
- The warning includes the filename

## Dependencies
- REQ-VALID-001 (front matter parsing must exist first)

## Test
`TestMissingTitle` in `zs_test.go`
