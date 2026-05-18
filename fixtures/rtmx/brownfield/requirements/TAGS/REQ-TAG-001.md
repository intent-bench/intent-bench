# REQ-TAG-001: Tag Parsing

## Requirement
Parse tags from YAML front matter as normalized lowercase list.

## Acceptance Criteria
- Tags specified as `tags: [Go, Web, Tutorial]` are parsed into `["go", "web", "tutorial"]`
- Whitespace is trimmed
- Empty strings are ignored
- Duplicate tags are deduplicated

## Test
`TestTagParsing` in `zs_test.go`
