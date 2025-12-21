from __future__ import annotations

import logging
import tempfile
from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, ConfigDict

from backend.api.deps import get_transcription_jobs, get_transcription_service
from backend.models.transcript import Transcript
from backend.services.transcription_jobs import TranscriptionJobManager
from backend.services.transcription_service import TranscriptionService
from backend.utils.errors import ProjectNotFound, ValidationError
from backend.utils.storage import (
    StorageError,
    load_project_metadata,
    project_original_wav_path,
    save_project_metadata,
)

router = APIRouter(prefix="/api/projects", tags=["transcription"])
logger = logging.getLogger("textaudio")


class StartTranscriptionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    task_id: UUID
    status: str


class TranscriptionStatusResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    task_id: UUID | None
    status: str
    progress: float | None = None
    error: str | None = None


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


@router.post(
    "/{project_id}/transcribe",
    response_model=StartTranscriptionResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def transcribe_project(
    project_id: UUID,
    transcription_service: TranscriptionService = Depends(get_transcription_service),
    jobs: TranscriptionJobManager = Depends(get_transcription_jobs),
) -> StartTranscriptionResponse:
    try:
        project = load_project_metadata(project_id)
    except StorageError as exc:
        raise ProjectNotFound(project_id) from exc

    audio_path = Path(project.audio_path) if project.audio_path else None
    if audio_path is None:
        audio_path = project_original_wav_path(project_id)
    if not audio_path.exists():
        raise ValidationError("Audio file not found for project")

    project_dir = project_original_wav_path(project_id).parent
    transcript_path = project_dir / "transcript.json"

    def on_completed(transcript: Transcript) -> None:
        try:
            _atomic_write_text(transcript_path, transcript.to_json())
        except OSError as exc:
            raise StorageError("Failed to write transcript file") from exc

        updated = load_project_metadata(project_id)
        updated.metadata["transcript_path"] = str(transcript_path)
        save_project_metadata(updated)

    def on_failed(message: str) -> None:
        logger.warning(
            "Transcription failed project_id=%s error=%s", project_id, message
        )

    task = jobs.start(
        project_id=project_id,
        audio_path=str(audio_path),
        transcription_service=transcription_service,
        on_completed=on_completed,
        on_failed=on_failed,
    )

    return StartTranscriptionResponse(task_id=task.task_id, status="queued")


@router.get(
    "/{project_id}/transcribe/status", response_model=TranscriptionStatusResponse
)
def get_transcription_status(
    project_id: UUID,
    jobs: TranscriptionJobManager = Depends(get_transcription_jobs),
) -> TranscriptionStatusResponse:
    try:
        load_project_metadata(project_id)
    except StorageError as exc:
        raise ProjectNotFound(project_id) from exc

    state = jobs.get_state(project_id)
    if state is not None:
        task_id, task_state = state
        return TranscriptionStatusResponse(
            task_id=task_id,
            status=task_state.status,
            progress=task_state.progress,
            error=task_state.error,
        )

    project_dir = project_original_wav_path(project_id).parent
    transcript_path = project_dir / "transcript.json"
    if transcript_path.exists():
        return TranscriptionStatusResponse(
            task_id=None,
            status="completed",
            progress=1.0,
        )

    raise ValidationError("No transcription task found for project")


@router.get("/{project_id}/transcript", response_model=Transcript)
def get_transcript(project_id: UUID) -> Transcript:
    try:
        load_project_metadata(project_id)
    except StorageError as exc:
        raise ProjectNotFound(project_id) from exc

    project_dir = project_original_wav_path(project_id).parent
    transcript_path = project_dir / "transcript.json"
    if not transcript_path.exists():
        raise ValidationError("Transcript not found for project")
    return Transcript.from_json(transcript_path.read_text(encoding="utf-8"))
