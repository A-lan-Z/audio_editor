from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, status

from backend.models.edit_operation import EditOperation
from backend.models.transcript import Transcript
from backend.utils.errors import ProjectNotFound, ValidationError
from backend.utils.storage import (
    StorageError,
    load_project_metadata,
    save_project_metadata,
    save_transcript,
)

router = APIRouter(prefix="/api/projects", tags=["edits"])


@router.post(
    "/{project_id}/edit",
    response_model=Transcript,
    status_code=status.HTTP_200_OK,
)
def submit_edit(project_id: UUID, operation: EditOperation) -> Transcript:
    try:
        project = load_project_metadata(project_id)
    except StorageError as exc:
        raise ProjectNotFound(project_id) from exc

    transcript_path = project.metadata.get("transcript_path")
    if not isinstance(transcript_path, str):
        raise ValidationError("Transcript not found for project")

    try:
        raw = Path(transcript_path).read_text(encoding="utf-8")
        transcript = Transcript.from_json(raw)
    except OSError as exc:
        raise ValidationError("Transcript not found for project") from exc

    updated = operation.apply(transcript)
    saved_path = save_transcript(project_id, updated)

    project.edits.append(operation)
    project.updated_at = datetime.now(UTC)
    project.metadata["transcript_path"] = str(saved_path)
    save_project_metadata(project)

    return updated
