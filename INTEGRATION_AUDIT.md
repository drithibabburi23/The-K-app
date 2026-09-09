# KarigarConnect Integration Audit

Audit scope: the files currently present under `The K-app`. No member folder was modified during this audit.

## Executive Findings

- `m1-main` and `m4-main` are Flutter project shells. They contain manifests and generated dependency metadata but no `lib/` source, entry point, screens, services, or assets.
- `member-2-main` is the most complete functional contribution: a FastAPI catalog pipeline with text extraction, optional OpenAI extraction, validation, multilingual descriptions, audio transcription integration, and tests.
- `m3-main` is a functional Flask image service with local upload/output storage, image enhancement, optional `rembg` background removal, and an API endpoint.
- `mem-2--main` is Member 5's marketplace documentation and dependency outline, but the documented `member5_marketplace` package and tests are not present in this workspace.
- There is no implemented central backend, database, authentication API, marketplace implementation, mobile UI, offline persistence, admin interface, or end-to-end integration in the current files.

## M1: `m1-main`

1. **Language/framework:** Dart and Flutter, based on `pubspec.yaml`.
2. **Entry point:** None present. No `lib/main.dart` or `lib/` directory exists.
3. **UI/screens:** None present.
4. **APIs/backend/database/AI/image processing/marketplace:** None present.
5. **Dependencies:** Flutter SDK, `provider`, `cupertino_icons`, `flutter_test`, and `flutter_lints`.
6. **Environment variables:** None documented or present.
7. **Run state:** `flutter analyze` succeeds because this is an empty valid Flutter shell. It is not a usable application.
8. **Implemented functionality:** Generated project metadata only.
9. **Missing functionality:** All product requirements, including authentication, navigation, product creation, integrations, persistence, and tests.
10. **Reusable material:** Flutter package baseline and analysis configuration only.

## M2: `member-2-main`

1. **Language/framework:** Python 3.11+ with FastAPI, Pydantic v2, httpx, and OpenAI SDK.
2. **Entry point:** `artisan_catalog.app:app`, run with Uvicorn.
3. **UI/screens:** None. This is an HTTP service.
4. **Implemented APIs:** `GET /health`, `POST /catalog/text`, `POST /catalog/audio`, and `POST /catalog/validate`.
5. **Implemented AI:** `LocalAIProvider` provides conservative offline extraction; `OpenAIProvider` optionally performs structured extraction and description generation when `OPENAI_API_KEY` is configured.
6. **Implemented validation:** Only facts traceable to source text are retained; unsupported values are omitted and reported as warnings.
7. **Implemented multilingual output:** English and Hindi fields are returned; a requested regional-language field is supported by the model contract, but the local provider leaves it `null` and does not translate.
8. **Environment variables:** `OPENAI_API_KEY`, `OPENAI_MODEL`, and `OPENAI_TRANSCRIPTION_MODEL`.
9. **Run/test state:** The repository documents Uvicorn and Pytest commands. The current machine lacks `pytest`, so the tests were not executed.
10. **Reusable material:** Models, pipeline, validation rules, provider interface, audio endpoint, and focused tests.
11. **Adaptation required:** Add authentication, request limits/authentication for callbacks, production error mapping, persistence, and an adapter to the central backend's product model.

## M3: `m3-main`

1. **Language/framework:** Python with Flask and Pillow; `rembg[cpu]` is optional at runtime in the implementation but listed as a dependency.
2. **Entry point:** `main.py`, which runs Flask on `0.0.0.0:5000` with debug mode enabled.
3. **UI/screens:** A small server-rendered HTML upload page at `/`.
4. **Implemented API:** `POST /api/process` accepts multipart field `image` and returns `image_url` and `filename`; processed files are served from `/outputs/<filename>`.
5. **Implemented image processing:** EXIF orientation, color/contrast/sharpness enhancement, optional background removal, centered 1200x1200 canvas, and soft shadow; output is JPEG.
6. **Storage:** Local `uploads/` and `outputs/` directories created beside the service. No database or cleanup policy exists.
7. **Environment variables:** `REMOVE_BACKGROUND=false` disables background removal. No API authentication or external storage configuration exists.
8. **Run/test state:** Import is blocked on this machine because Pillow is not installed. No tests are present.
9. **Reusable material:** `process_image`, file validation, and the multipart endpoint contract.
10. **Adaptation required:** Disable debug in production, add auth/size and content validation, avoid exposing arbitrary local output storage, add lifecycle cleanup, and place the endpoint behind a service adapter.

## M4: `m4-main`

1. **Language/framework:** Dart and Flutter.
2. **Entry point:** None present. No `lib/` directory exists.
3. **UI/screens:** None present.
4. **Dependencies:** Flutter SDK, `firebase_auth`, `firebase_core`, `http`, `cupertino_icons`, `flutter_test`, and `flutter_lints`.
5. **Authentication/database/backend:** No Dart source or Firebase configuration is present, so no authentication flow or database integration is actually implemented.
6. **Environment variables:** None documented or present. Firebase platform configuration files are absent.
7. **Run state:** `flutter analyze` succeeds for the empty shell.
8. **Implemented functionality:** Generated Flutter metadata and declared dependencies only.
9. **Missing functionality:** All M4 responsibilities: users, roles, products, categories, enquiries, backend APIs, persistence, admin, and security rules.
10. **Reusable material:** Best foundation shell due to its declared Firebase Auth/Core and HTTP dependencies, subject to adding actual source and configuration.

## M5: `mem-2--main`

1. **Language/framework:** The README describes a Python standard-library module, with optional development tools in `requirements.txt`.
2. **Entry point:** None present.
3. **UI/API/backend/database:** None present.
4. **Documented capabilities:** Price guide, marketplace search/filtering/product details, and buyer enquiries.
5. **Documented data:** Price ranges based on category/material/craft/complexity, plus product and enquiry examples.
6. **Actual implementation:** The README references `member5_marketplace.price_guide`, `marketplace`, and `enquiry`, but those modules and their tests are absent from this workspace. No code can be imported or integrated directly.
7. **Dependencies/environment:** README says standard library; `requirements.txt` lists pytest, pytest-cov, black, flake8, mypy, and Sphinx. No environment variables are documented.
8. **Reusable material:** Domain examples, pricing rules, field names, and intended function signatures as a provisional contract only.
9. **Adaptation required:** Reconstruct or obtain the missing implementation, then add an HTTP/service boundary and persistence-backed marketplace behavior.

## Cross-Project Conflicts and Blockers

- There are two Flutter package shells but no UI to compare. M4 is selected as the foundation only because its declared dependencies align more closely with authentication and API integration.
- M2 returns `facts`, while the documented M5 examples and target application use a flatter product shape. An adapter/model mapping is required.
- M2's callback URL is caller-controlled and has no authentication contract; it must not be exposed as an unrestricted production callback.
- M3 uses local filesystem storage and serves generated files directly. This is suitable for development, not durable production storage.
- M3 runs Flask with `debug=True`; this must be changed before deployment.
- M5's implementation is missing, so price/search/recommendation/enquiry behavior cannot be claimed or tested from this workspace.
- No central backend or database exists. Authentication, product persistence, category management, recommendations, enquiries, admin, and offline synchronization remain to be implemented.
- No real secrets were found. The only secret-shaped configuration is the empty `OPENAI_API_KEY` placeholder in M2's `.env.example`.

## Recommended Reuse

**Directly reusable:** M2 pipeline/models/validation and M3 processing function/API shape.

**Reusable with hardening:** M2 OpenAI/transcription integrations and M3 Flask service.

**Provisional only:** M5 README contracts and pricing examples.

**Not reusable as application functionality:** M1/M4 generated Flutter shells; M4 can be used as the new application's package baseline.

## Audit Validation

- `flutter analyze` passed for both Flutter shells, confirming only that their generated metadata is syntactically valid.
- M2 tests could not run because `pytest` is not installed in the active Python environment.
- M3 import could not run because `Pillow` is not installed in the active Python environment.