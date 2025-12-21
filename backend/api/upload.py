from __future__ import annotations

import logging
import shutil
import tempfile
from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, File, UploadFile
from pydantic import BaseModel, ConfigDict

from backend.utils.audio_processing import (
    MAX_DURATION_SECONDS,
    WARN_DURATION_SECONDS,
    ensure_wav_pcm16,
    get_duration_seconds,
    normalize_to_mono_wav,
    validate_audio_decodable,
)
from backend.utils.errors import ProjectNotFound, ValidationError
from backend.utils.storage import (
    StorageError,
    load_project_metadata,
    project_original_wav_path,
    project_uploads_dir,
)

router = APIRouter(prefix="/api/projects", tags=["upload"])
logger = logging.getLogger("textaudio")


class UploadResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    project_id: UUID
    filename: str
    content_type: str | None
    size_bytes: int
    status: str


def _safe_filename(filename: str) -> str:
    name = Path(filename).name
    if name in {"", ".", ".."}:
        raise ValidationError("Invalid filename")
    return name


def _assert_content_type(content_type: str | None) -> None:
    if content_type is None:
        return
    if content_type.startswith("audio/"):
        return
    if content_type in {"application/octet-stream"}:
        return
    raise ValidationError(f"Unsupported content-type: {content_type}")


@router.post("/{project_id}/upload", response_model=UploadResponse)
def upload_audio(project_id: UUID, file: UploadFile = File(...)) -> UploadResponse:
    try:
        project = load_project_metadata(project_id)
    except StorageError as exc:
        raise ProjectNotFound(project_id) from exc

    _assert_content_type(file.content_type)
    safe_name = _safe_filename(file.filename or "")
    uploads_dir = project_uploads_dir(project_id)

    tmp_path: Path
    with tempfile.NamedTemporaryFile(
        mode="wb", dir=uploads_dir, delete=False
    ) as tmp_file:
        shutil.copyfileobj(file.file, tmp_file)
        tmp_path = Path(tmp_file.name)

    dest_path = uploads_dir / safe_name
    if dest_path.exists():
        dest_path = uploads_dir / f"{project_id}-{safe_name}"

    try:
        tmp_path.replace(dest_path)
    except OSError as exc:
        raise ValidationError("Failed to save uploaded file") from exc

    try:
        validate_audio_decodable(dest_path)
        converted_path = ensure_wav_pcm16(dest_path)
        if converted_path != dest_path:
            dest_path.unlink(missing_ok=True)
            dest_path = converted_path
        duration_seconds = get_duration_seconds(dest_path)
        if duration_seconds > WARN_DURATION_SECONDS:
            logger.warning(
                "Audio duration exceeds warning threshold: %.1fs project_id=%s",
                duration_seconds,
                project_id,
            )
        if duration_seconds > MAX_DURATION_SECONDS:
            minutes = duration_seconds / 60.0
            raise ValidationError(
                f"This file is too long ({minutes:.1f} min). Max 10 minutes."
            )

        normalize_to_mono_wav(
            src_path=dest_path,
            dest_path=project_original_wav_path(project_id),
        )
    except Exception:  # noqa: BLE001
        dest_path.unlink(missing_ok=True)
        raise

    return UploadResponse(
        project_id=project.id,
        filename=dest_path.name,
        content_type=file.content_type,
        size_bytes=dest_path.stat().st_size,
        status="uploaded",
    )
