# REQ-TAG-002: Tag Index Page

## Requirement
Generate `/tags/` index page listing all tags with post counts.

## Acceptance Criteria
- Output includes an HTML page at `/tags/index.html`
- Page lists all unique tags across all posts
- Each tag shows the number of posts with that tag
- Tags link to their per-tag page

## Dependencies
- REQ-TAG-001 (tags must be parsed first)

## Test
`TestTagIndex` in `zs_test.go`
