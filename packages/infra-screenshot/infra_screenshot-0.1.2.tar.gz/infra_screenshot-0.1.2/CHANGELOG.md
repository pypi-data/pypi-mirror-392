# Changelog

All notable changes to `infra-screenshot` will be documented in this file.

## [0.1.0] - Unreleased

### Added
- Initial public packaging of the shared screenshot models, services, and CLI.
- Bundled documentation and configuration assets for offline reference.
- Dual licensing clarified with updated `LICENSE` and `NOTICE` contents.
- Test isolation via autouse fixture to prevent environment pollution between tests.
- Documentation for test environment variables (RUN_E2E, RUN_REAL_SITES, SKIP_PLAYWRIGHT_NAV_TESTS).

### Changed
- **BREAKING**: `collect_job_specs()` now returns `list[ScreenshotJobSpec]` instead of `list[dict[str, object]]`.
- **BREAKING**: Reduced public API surface in `models.py` from 44 to 8 exports. Internal types are still importable but not in `__all__`.
- Minimum timeout for Playwright runner increased from 1.0 to 5.0 seconds for better real-world reliability.
- Improved type safety throughout the codebase (removed unnecessary type: ignore comments).
- Reorganized documentation: user docs moved to root `/docs` directory (standard Python convention), development docs in `.dev_docs/`. Documentation no longer ships with the package.

### Fixed
- Test pollution issue where PLAYWRIGHT_BROWSERS_PATH environment variable persisted across tests.
- FrozenInstanceError in E2E tests when modifying frozen dataclass fields.
- Generic type consistency in ScreenshotService with proper covariant type variables.
- Duplicate `from __future__ import annotations` import in storage.py.
- Incorrect return type annotation in `_default_json_serializer` (now uses `Any`).
- Test code duplication by extracting shared `create_capture_result` helper to `test_utils.py`.
