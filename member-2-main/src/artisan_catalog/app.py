from __future__ import annotations

from fastapi import FastAPI, File, Form, HTTPException, UploadFile

from .ai import build_provider
from .models import CatalogResult, PipelineRequest, TextRequest
from .pipeline import CatalogPipeline
from .transcription import TranscriptionUnavailable, transcribe_audio

app = FastAPI(title="Artisan Catalog AI", version="0.1.0")
pipeline = CatalogPipeline(build_provider())


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/catalog/text", response_model=CatalogResult)
async def catalog_from_text(request: PipelineRequest) -> CatalogResult:
    result = await pipeline.run(request.text, request.regional_language)
    if request.callback_url:
        try:
            await pipeline.send_to_backend(request.callback_url, result)
        except Exception as error:
            raise HTTPException(status_code=502, detail=f"Backend callback failed: {error}") from error
    return result


@app.post("/catalog/audio", response_model=CatalogResult)
async def catalog_from_audio(
    audio: UploadFile = File(...),
    regional_language: str | None = Form(default=None),
    callback_url: str | None = Form(default=None),
) -> CatalogResult:
    content = await audio.read()
    if not content:
        raise HTTPException(status_code=400, detail="Audio file is empty.")
    try:
        source_text = await transcribe_audio(audio.filename or "artisan-audio", content)
    except TranscriptionUnavailable as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    if not source_text:
        raise HTTPException(status_code=422, detail="No speech was detected in the audio.")
    result = await pipeline.run(source_text, regional_language)
    if callback_url:
        try:
            await pipeline.send_to_backend(callback_url, result)
        except Exception as error:
            raise HTTPException(status_code=502, detail=f"Backend callback failed: {error}") from error
    return result


@app.post("/catalog/validate", response_model=CatalogResult)
async def validate_catalog(request: TextRequest) -> CatalogResult:
    """Re-run extraction and validation when Member 4 needs a fresh result."""
    return await pipeline.run(request.text, request.regional_language)
