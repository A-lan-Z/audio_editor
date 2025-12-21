from __future__ import annotations

import tempfile
from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Depends

from backend.api.deps import get_transcription_service
from backend.models.transcript import Transcript
from backend.services.transcription_service import TranscriptionService
from backend.utils.errors import ProjectNotFound, ValidationError
from backend.utils.storage import (
    StorageError,
    load_project_metadata,
    project_original_wav_path,
    save_project_metadata,
)

router = APIRouter(prefix="/api/projects", tags=["transcription"])


def _atomic_write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        dir=path.parent,
        suffix=".tmp",
        delete=False,
    ) as tmp_file:
        tmp_path = Path(tmp_file.name)
        tmp_file.write(content)
        tmp_file.flush()
    tmp_path.replace(path)


@router.post("/{project_id}/transcribe", response_model=Transcript)
def transcribe_project(
    project_id: UUID,
    transcription_service: TranscriptionService = Depends(get_transcription_service),
) -> Transcript:
    try:
        project = load_project_metadata(project_id)
    except StorageError as exc:
        raise ProjectNotFound(project_id) from exc

    audio_path = Path(project.audio_path) if project.audio_path else None
    if audio_path is None:
        audio_path = project_original_wav_path(project_id)
    if not audio_path.exists():
        raise ValidationError("Audio file not found for project")

    transcript = transcription_service.transcribe(str(audio_path))

    project_dir = project_original_wav_path(project_id).parent
    transcript_path = project_dir / "transcript.json"
    try:
        _atomic_write_text(transcript_path, transcript.to_json())
    except OSError as exc:
        raise StorageError("Failed to write transcript file") from exc

    project.metadata["transcript_path"] = str(transcript_path)
    save_project_metadata(project)

    return transcript
