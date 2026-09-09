from __future__ import annotations

import os
from io import BytesIO


class TranscriptionUnavailable(RuntimeError):
    pass


async def transcribe_audio(filename: str, content: bytes) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise TranscriptionUnavailable(
            "Audio transcription needs OPENAI_API_KEY. Send text to /catalog/text for offline development."
        )
    try:
        from openai import AsyncOpenAI
    except ImportError as error:
        raise TranscriptionUnavailable("Install the optional openai package to transcribe audio.") from error

    client = AsyncOpenAI(api_key=api_key)
    result = await client.audio.transcriptions.create(
        model=os.getenv("OPENAI_TRANSCRIPTION_MODEL", "whisper-1"),
        file=(filename, BytesIO(content)),
    )
    return result.text.strip()
