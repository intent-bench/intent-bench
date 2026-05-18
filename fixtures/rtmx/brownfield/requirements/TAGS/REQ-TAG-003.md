# REQ-TAG-003: Per-Tag Pages

## Requirement
Generate per-tag pages at `/tags/<tag>/` listing tagged posts.

## Acceptance Criteria
- For each unique tag, generate an HTML page at `/tags/<tag>/index.html`
- Page lists all posts with that tag, with titles and dates
- Posts are sorted by date descending

## Dependencies
- REQ-TAG-001 (tags must be parsed first)

## Test
`TestTagPages` in `zs_test.go`
