# REQ-ENC-002: Fix Spurious Quoting of Boolean-like Field Names

## Requirement
Remove spurious quotes on boolean-like field names in struct marshal.

## Acceptance Criteria
- Field names `y`, `n`, `Y`, `N`, `yes`, `no` are not quoted when used as map keys
- Marshaling `image.Point{X: 4, Y: 5}` produces `x: 4\ny: 5` without quotes
- Boolean values (not keys) are still handled correctly
- YAML 1.1 boolean-like strings in value position continue to be quoted where needed

## Test
`TestBooleanLikeFieldNames` in `yaml_test.go`
