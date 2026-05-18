# REQ-RENDER-001: Fix ConsoleRenderer Style Dict Mutation

## Requirement
Fix ConsoleRenderer mutating caller's level_styles dict.

## Acceptance Criteria
- Constructing a ConsoleRenderer does not modify the passed-in level_styles dict
- Creating multiple renderers with the same dict does not cause style accumulation
- Default styles continue to work when no dict is passed

## Test
`test_style_dict_not_mutated` in `test_dev.py`
