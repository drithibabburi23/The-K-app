# Artisan Catalog AI

Member-2 service for converting artisan speech into validated, multilingual catalog data.

## Run

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[test]"
uvicorn artisan_catalog.app:app --reload
```

`OPENAI_API_KEY` enables Whisper audio transcription and OpenAI extraction/description. Without it, text requests use a conservative offline extractor for development; audio requests return `503` instead of inventing a transcript.

## Endpoints

- `POST /catalog/audio`: multipart upload with `audio`, optional `regional_language`, and optional `callback_url`.
- `POST /catalog/text`: JSON `{ "text": "...", "regional_language": "...", "callback_url": "..." }`.
- `POST /catalog/validate`: reruns the extraction and validation pipeline.
- `GET /health`: liveness check.

The backend payload contains `source_text`, structured `product`, multilingual `descriptions`, and validation metadata. Any AI field not traceable to the artisan's source text is set to `null` and reported in `warnings`/`omitted_fields`.

## Test

```powershell
py -3 -m pytest
```
