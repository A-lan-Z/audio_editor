from __future__ import annotations

from uuid import UUID

from backend.models.edit_operation import EditOperation
from backend.models.project import Project
from backend.models.transcript import Transcript
from backend.services.audio_segment_manager import AudioSegmentManager


def handle_deletion(
    *, edit_operation: EditOperation, project: Project, original_transcript: Transcript
) -> list[UUID]:
    if edit_operation.type != "delete":
        return []
    if not edit_operation.old_tokens:
        return []
    manager = AudioSegmentManager.ensure_initialized(
        project=project, transcript=original_transcript
    )
    affected = manager.mark_removed_for_token_ids(edit_operation.old_tokens)
    manager.persist(project)
    return affected


def sync_deleted_segments_for_active_edits(
    *,
    project: Project,
    original_transcript: Transcript,
    active_edits: list[EditOperation],
) -> None:
    manager = AudioSegmentManager.ensure_initialized(
        project=project, transcript=original_transcript
    )
    manager.rebuild_from_active_edits(active_edits)
    manager.persist(project)
