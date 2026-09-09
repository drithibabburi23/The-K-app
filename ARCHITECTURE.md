# KarigarConnect Architecture

## Selected Foundation

Use `m4-main` as the starting Flutter package for the final application. It is not currently a working app: its `lib/` source and Firebase configuration are absent. It is selected over `m1-main` because its declared dependencies already anticipate Firebase authentication/core services and HTTP API access. No existing Flutter UI can be preserved because neither shell contains one.

The original member directories remain reference inputs and are not overwritten.

## Target Structure

```text
karigar_connect/
  lib/
    core/                 # configuration, errors, networking, connectivity
    models/               # shared application models
    services/             # auth, catalog, image, marketplace, sync APIs
    repositories/         # remote/local data coordination
    screens/              # artisan, buyer, and admin flows
    widgets/              # accessible shared controls
    main.dart
  assets/
  test/
  pubspec.yaml
backend/
  api/                    # central authenticated API and persistence
  adapters/               # M2, M3, and M5 integration adapters
```

## Runtime Flow

```text
Flutter mobile app
  -> authenticated central backend/API
     -> M2 catalog adapter (text/audio, validation, translations)
     -> M3 image adapter (multipart image processing)
     -> M5 marketplace adapter (pricing/search/recommendations/enquiries)
     -> database and durable media storage
```

The Flutter app talks to service classes, never directly to OpenAI, image-processing internals, or database drivers. Backend credentials stay server-side. The current repository has no central backend, so that layer must be built rather than assumed to exist.

## Domain Mapping

M2's `CatalogResult.facts.facts` maps into the shared `Product` model. The adapter should preserve M2's `source_text`, `descriptions`, `supported_fields`, `omitted_fields`, and `warnings`, while mapping product fields such as `product_name`, `category`, `material`, `craft`, `color`, `dimensions`, and `price` into the central schema.

M3's returned `image_url` maps into `ProductImage.processedUrl`. M5's documented price guide maps into `PriceSuggestion`; its marketplace and enquiry concepts map into `Product` and `Enquiry` after the missing implementation is recovered or replaced with a backend-owned implementation.

## Delivery Constraints

1. Build the backend contract and shared models before wiring screens.
2. Keep original member folders unchanged.
3. Use explicit `NOT_CONFIGURED` states for missing Firebase, OpenAI, storage, and M5 integrations.
4. Add local draft persistence and idempotent sync only after the product model and authenticated API are stable.
5. Treat the final application as unready for production until authentication, persistence, secrets handling, dependency installation, tests, and release builds succeed.

## Current Blockers

- No Flutter application source exists to integrate.
- No M4 backend/API/database implementation exists.
- M5 implementation is absent.
- Firebase platform configuration and production environment values are absent.
- Python dependencies are not installed in the active environment, so existing Python tests/import checks are pending.