# KarigarConnect Integration Contracts

This document records contracts that are supported by source code in the workspace. Contracts described only in Member 5's README are marked provisional and are not treated as implemented APIs.

## M2: Artisan Catalog Service

Base service: Uvicorn serving `artisan_catalog.app:app`.

### `GET /health`

- **Input:** none.
- **Output:** `{ "status": "ok" }`.
- **Authentication:** none in current implementation.
- **Errors:** standard FastAPI errors only.

### `POST /catalog/text`

- **Content type:** `application/json`.
- **Input:** `{ "text": string, "regional_language": string|null, "callback_url": string|null }`.
- **Constraints:** `text` is 1-10,000 characters; regional language is at most 40 characters.
- **Output:**

```json
{
  "source_text": "This is a handmade cotton saree in blue.",
  "facts": {
    "facts": {
      "product_name": null,
      "category": "Textiles",
      "material": "cotton",
      "craft": "handmade",
      "color": "blue",
      "dimensions": null,
      "price": null,
      "description": null
    },
    "supported_fields": ["category", "material", "craft", "color"],
    "omitted_fields": ["product_name", "dimensions", "price", "description"],
    "warnings": []
  },
  "descriptions": {"en": "...", "hi": "...", "regional": null},
  "backend_payload": {
    "source_text": "...",
    "product": {"category": "Textiles", "material": "cotton"},
    "descriptions": {"en": "...", "hi": "...", "regional": null},
    "validation": {"supported_fields": [], "omitted_fields": [], "warnings": []}
  },
  "warnings": []
}
```

- **Authentication:** none in current implementation; central backend must authenticate the caller before forwarding.
- **Errors:** FastAPI validation `422`; callback failure `502`; provider errors may currently surface as server errors.
- **Example request:** `POST /catalog/text` with `{ "text": "A handwoven cotton saree in blue", "regional_language": "mr" }`.
- **Environment:** `OPENAI_API_KEY`, `OPENAI_MODEL`, `OPENAI_TRANSCRIPTION_MODEL`. Without the key, text uses the conservative local provider and regional output remains null.

### `POST /catalog/audio`

- **Content type:** `multipart/form-data`.
- **Input:** required file field `audio`; optional form fields `regional_language` and `callback_url`.
- **Output:** same `CatalogResult` shape as `/catalog/text`.
- **Authentication:** none currently.
- **Errors:** `400` empty audio, `503` transcription unavailable, `422` no detected speech, `502` callback failure.
- **Example request:** multipart upload of `audio=product-note.m4a` plus `regional_language=hi`.
- **Environment:** requires `OPENAI_API_KEY` and the configured transcription model for real audio processing.

### `POST /catalog/validate`

- **Input:** `{ "text": string, "regional_language": string|null }`.
- **Output:** same `CatalogResult` shape.
- **Purpose:** reruns extraction and source-traceability validation.
- **Authentication/errors:** same current limitations as `/catalog/text`.

## M3: Image Processing Service

Base service: Flask `main.py`, default port `5000`.

### `POST /api/process`

- **Content type:** `multipart/form-data`.
- **Input:** required file field `image`; accepted extensions are `jpg`, `jpeg`, `png`, and `webp`; configured upload limit is 15 MiB.
- **Output:** `{ "image_url": "/outputs/karigar_<token>.jpg", "filename": "karigar_<token>.jpg" }`.
- **Authentication:** none currently.
- **Processing:** EXIF correction, enhancement, optional background removal, square 1200px JPEG output.
- **Errors:** invalid/missing file returns `400`; processing exceptions can currently escape from the API route and need a production error adapter.
- **Example request:** multipart `image=product.jpg`.
- **Environment:** `REMOVE_BACKGROUND=false` disables `rembg`; default is enabled when `rembg` is installed.
- **Security gap:** output URLs and service access are unauthenticated; Flask debug mode is enabled in the current entry point.

### `GET /outputs/<filename>`

- **Input:** generated output filename.
- **Output:** JPEG file.
- **Authentication:** none currently.
- **Production requirement:** replace local public file serving with authenticated durable media storage or a signed URL.

## M4: Backend, Authentication, Users, Products, Categories, Enquiries

No M4 API or backend implementation is present. `m4-main` contains only a Flutter manifest with declared Firebase/Auth and HTTP dependencies. The following are required target contracts, but must not be presented as existing functionality until implemented:

- authentication: register, login, logout, current user, role selection;
- users/artisans/buyers: authenticated profile CRUD;
- products/categories: draft, edit, publish, list, detail, category management;
- enquiries: create, list, status update;
- admin: authenticated role-restricted counts and management operations.

## M5: Price Guide, Marketplace, Recommendations, Enquiries

`mem-2--main/README.md` documents Python functions such as `generate_price_guide`, `search_products`, `get_product_details`, `create_enquiry`, `get_artisan_enquiries`, and `update_enquiry_status`. The referenced package files are absent, so there is no verified HTTP method, JSON schema, authentication behavior, persistence, error format, or runnable implementation in this workspace.

The README's provisional price shape is:

```json
{
  "minimum_price": 1200,
  "maximum_price": 1600,
  "currency": "INR",
  "basis": ["Textiles", "Cotton", "Handwoven"],
  "confidence": "high"
}
```

Before integration, recover the missing implementation or define and test a replacement backend contract for price suggestions, marketplace search/filtering, recommendations, and enquiries. Do not fabricate an existing M5 API.

## Central Adapter Rules

1. Authenticate the mobile caller at the central backend and pass only server-side service credentials to M2/M3/M5.
2. Map M2 `facts.facts` to the central `Product` model and preserve validation metadata for review.
3. Treat a missing or failed optional integration as an explicit status (`NOT_CONFIGURED`, `FAILED`, or `PENDING`) rather than inventing data.
4. Use request IDs and idempotency keys for publish and offline synchronization.
5. Normalize errors into a user-safe shape such as `{ "code": "...", "message": "...", "request_id": "..." }` while retaining technical details in server logs only.