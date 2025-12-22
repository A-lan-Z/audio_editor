from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, status

from backend.models.edit_operation import EditOperation
from backend.models.project import Project
from backend.models.transcript import Transcript
from backend.services.deletion_handler import sync_deleted_segments_for_active_edits
from backend.utils.errors import ProjectNotFound, ValidationError
from backend.utils.storage import (
    StorageError,
    load_project_metadata,
    save_project_metadata,
    save_transcript,
)

router = APIRouter(prefix="/api/projects", tags=["edits"])

ORIGINAL_TRANSCRIPT_FILENAME = "transcript_original.json"


def _load_transcript(path: str) -> Transcript:
    raw = Path(path).read_text(encoding="utf-8")
    return Transcript.from_json(raw)


def _ensure_original_transcript(project: Project, transcript_path: str) -> Path:
    original = project.metadata.get("original_transcript_path")
    if isinstance(original, str):
        path = Path(original)
        if path.exists():
            return path

    original_path = Path(transcript_path).with_name(ORIGINAL_TRANSCRIPT_FILENAME)
    try:
        original_path.write_text(
            Path(transcript_path).read_text(encoding="utf-8"),
            encoding="utf-8",
        )
    except OSError as exc:
        raise ValidationError("Failed to persist original transcript") from exc

    project.metadata["original_transcript_path"] = str(original_path)
    return original_path


def _edit_cursor(project: Project) -> int:
    cursor = project.metadata.get("edit_cursor")
    if isinstance(cursor, int) and cursor >= 0:
        return min(cursor, len(project.edits))
    return len(project.edits)


def _rebuild_from_original(
    original: Transcript, edits: list[EditOperation]
) -> Transcript:
    current = original
    for edit in edits:
        current = edit.apply(current)
    return current


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
        _load_transcript(transcript_path)
    except OSError as exc:
        raise ValidationError("Transcript not found for project") from exc

    original_path = _ensure_original_transcript(project, transcript_path)
    original_transcript = _load_transcript(str(original_path))

    cursor = _edit_cursor(project)
    existing_index = next(
        (index for index, edit in enumerate(project.edits) if edit.id == operation.id),
        None,
    )
    if existing_index is None:
        if cursor < len(project.edits):
            project.edits = project.edits[:cursor]
        project.edits.append(operation)
        cursor = len(project.edits)
    else:
        project.edits[existing_index] = operation

    project.metadata["edit_cursor"] = cursor
    updated = _rebuild_from_original(original_transcript, project.edits[:cursor])
    saved_path = save_transcript(project_id, updated)

    sync_deleted_segments_for_active_edits(
        project=project,
        original_transcript=original_transcript,
        active_edits=project.edits[:cursor],
    )

    project.updated_at = datetime.now(UTC)
    project.metadata["transcript_path"] = str(saved_path)
    save_project_metadata(project)

    return updated


@router.post(
    "/{project_id}/undo",
    response_model=Transcript,
    status_code=status.HTTP_200_OK,
)
def undo_edit(project_id: UUID) -> Transcript:
    try:
        project = load_project_metadata(project_id)
    except StorageError as exc:
        raise ProjectNotFound(project_id) from exc

    transcript_path = project.metadata.get("transcript_path")
    if not isinstance(transcript_path, str):
        raise ValidationError("Transcript not found for project")

    original_path = _ensure_original_transcript(project, transcript_path)
    original_transcript = _load_transcript(str(original_path))

    cursor = _edit_cursor(project)
    cursor = max(cursor - 1, 0)
    project.metadata["edit_cursor"] = cursor

    updated = _rebuild_from_original(original_transcript, project.edits[:cursor])
    saved_path = save_transcript(project_id, updated)

    sync_deleted_segments_for_active_edits(
        project=project,
        original_transcript=original_transcript,
        active_edits=project.edits[:cursor],
    )

    project.updated_at = datetime.now(UTC)
    project.metadata["transcript_path"] = str(saved_path)
    save_project_metadata(project)

    return updated


@router.post(
    "/{project_id}/redo",
    response_model=Transcript,
    status_code=status.HTTP_200_OK,
)
def redo_edit(project_id: UUID) -> Transcript:
    try:
        project = load_project_metadata(project_id)
    except StorageError as exc:
        raise ProjectNotFound(project_id) from exc

    transcript_path = project.metadata.get("transcript_path")
    if not isinstance(transcript_path, str):
        raise ValidationError("Transcript not found for project")

    original_path = _ensure_original_transcript(project, transcript_path)
    original_transcript = _load_transcript(str(original_path))

    cursor = _edit_cursor(project)
    cursor = min(cursor + 1, len(project.edits))
    project.metadata["edit_cursor"] = cursor

    updated = _rebuild_from_original(original_transcript, project.edits[:cursor])
    saved_path = save_transcript(project_id, updated)

    sync_deleted_segments_for_active_edits(
        project=project,
        original_transcript=original_transcript,
        active_edits=project.edits[:cursor],
    )

    project.updated_at = datetime.now(UTC)
    project.metadata["transcript_path"] = str(saved_path)
    save_project_metadata(project)

    return updated
