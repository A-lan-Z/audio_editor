from __future__ import annotations

import io
from collections.abc import Iterator
from uuid import UUID

import soundfile as sf
from fastapi import APIRouter
from starlette.responses import StreamingResponse

from backend.services.audio_renderer import AudioRenderError, render
from backend.utils.errors import ValidationError

router = APIRouter(prefix="/api/projects", tags=["preview"])


def _stream_bytes(data: bytes, *, chunk_size: int = 64 * 1024) -> Iterator[bytes]:
    for index in range(0, len(data), chunk_size):
        yield data[index : index + chunk_size]


@router.get("/{project_id}/preview")
def preview_audio(project_id: UUID) -> StreamingResponse:
    try:
        audio, sample_rate = render(project_id)
    except AudioRenderError as exc:
        raise ValidationError(str(exc)) from exc

    buffer = io.BytesIO()
    sf.write(buffer, audio, sample_rate, format="WAV", subtype="PCM_16")
    payload = buffer.getvalue()

    return StreamingResponse(
        _stream_bytes(payload),
        media_type="audio/wav",
        headers={"content-disposition": "inline; filename=preview.wav"},
    )
