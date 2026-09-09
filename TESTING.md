# Testing Status

## Verified

- `m1-main`: `flutter analyze` passes for the generated shell.
- `m4-main`: `flutter analyze` passes for the generated shell.
- `karigar_connect`: `flutter analyze` passes.
- `karigar_connect`: focused tests cover local catalog extraction, empty-input rejection, and draft status.

## Not Yet Runnable Here

- M2 Pytest suite: the active Python environment does not have `pytest` installed.
- M3 import check: the active Python environment does not have `Pillow` installed.
- M5 tests: the documented package and tests are absent.

## Required Integration Tests

Once the central backend exists, add tests for authentication, product creation/editing/publishing, M2 text/audio/validation, M3 image upload/processing, M5 pricing/search/recommendations/enquiries, admin permissions, offline drafts, idempotent synchronization, and the full artisan and buyer journeys.

Each external integration should also cover timeout, no-network, unavailable-service, invalid-response, authentication failure, and user-safe error states.