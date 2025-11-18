
### Fixed

- Use explicit `is not None` checks in `_equals_none_to_not_exists` to
avoid triggering `Filter.__bool__` UserWarning from cognite-sdk-python