from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, status
from pydantic import BaseModel, ConfigDict, Field

from backend.models.project import Project
from backend.models.transcript import Token, Transcript
from backend.services.audio_segment_manager import AudioSegment, AudioSegmentManager
from backend.services.boundary_snapping import (
    frame_rms,
    snap_boundary_backward,
    snap_boundary_forward,
)
from backend.utils.errors import ProjectNotFound, ValidationError
from backend.utils.storage import StorageError, load_project_metadata
from backend.utils.timestamp_refinement_config import TimestampRefinementConfig

router = APIRouter(prefix="/api/projects", tags=["diagnostics"])


def _load_transcript_optional(path: str | None) -> Transcript | None:
    if not path:
        return None
    try:
        raw = Path(path).read_text(encoding="utf-8")
        return Transcript.from_json(raw)
    except OSError:
        return None


def _token_by_id(transcript: Transcript | None) -> dict[UUID, Token]:
    if transcript is None:
        return {}
    return {token.id: token for token in transcript.tokens}


class TokenTimingDiagnostics(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID
    text: str
    type: str
    active_start: float
    active_end: float
    asr_start: float | None = None
    asr_end: float | None = None
    refined_start: float | None = None
    refined_end: float | None = None
    delta_asr_start: float | None = None
    delta_asr_end: float | None = None
    delta_refined_start: float | None = None
    delta_refined_end: float | None = None


class SegmentDiagnostics(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID
    source: str
    status: str
    start: float
    end: float
    token_ids: list[UUID] = Field(default_factory=list)


class BoundaryTrimDiagnostics(BaseModel):
    model_config = ConfigDict(extra="forbid")

    prev_segment_id: UUID
    next_segment_id: UUID
    prev_end_before: float
    prev_end_snapped: float
    prev_end_trimmed: float
    next_start_before: float
    next_start_snapped: float
    next_start_trimmed: float


class TimestampDiagnosticsResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    project_id: UUID
    computed_at: datetime
    transcript_active_source: str | None = None
    refinement_enabled: bool
    snap_window_ms: int
    cut_padding_ms: int
    tokens: list[TokenTimingDiagnostics]
    segments: list[SegmentDiagnostics]
    boundary_trims: list[BoundaryTrimDiagnostics]


def _compute_boundary_trims(
    *,
    project: Project,
    segments: list[AudioSegment],
    refine_cfg: TimestampRefinementConfig,
) -> list[BoundaryTrimDiagnostics]:
    if not refine_cfg.enabled:
        return []
    if not project.audio_path:
        return []
    audio_path = Path(project.audio_path)
    if not audio_path.exists():
        return []

    import soundfile as sf  # local import to keep endpoint lightweight
    import numpy as np

    audio, sample_rate = sf.read(audio_path, dtype="float32", always_2d=False)
    array = np.asarray(audio, dtype=np.float32)
    if array.ndim == 2:
        array = array[:, 0]

    frame_samples = max(1, int(round(float(sample_rate) * 0.01)))
    rms = frame_rms(array, frame_samples=frame_samples)
    snap_window_ms = int(refine_cfg.snap_window_ms)
    cut_padding_s = float(refine_cfg.cut_padding_ms) / 1000.0

    segments_sorted = sorted(segments, key=lambda seg: (seg.start, seg.end, str(seg.id)))
    trims: list[BoundaryTrimDiagnostics] = []
    previous_included_original = False
    removed_since_last_original = False
    last_original_start: float | None = None
    last_original_end: float | None = None
    last_original_id: UUID | None = None

    for segment in segments_sorted:
        include_segment = segment.status in {"kept", "generated"}
        if segment.source == "original" and segment.status == "removed":
            removed_since_last_original = True

        if include_segment and segment.source == "original":
            if (
                removed_since_last_original
                and previous_included_original
                and last_original_start is not None
                and last_original_end is not None
                and last_original_id is not None
            ):
                prev_snapped = snap_boundary_backward(
                    rms,
                    sample_rate=sample_rate,
                    frame_samples=frame_samples,
                    center_time=float(last_original_end),
                    window_ms=snap_window_ms,
                )
                prev_trimmed = max(float(last_original_start), float(prev_snapped) - cut_padding_s)

                next_snapped = snap_boundary_forward(
                    rms,
                    sample_rate=sample_rate,
                    frame_samples=frame_samples,
                    center_time=float(segment.start),
                    window_ms=snap_window_ms,
                )
                next_trimmed = max(float(next_snapped) + cut_padding_s, float(segment.start))

                trims.append(
                    BoundaryTrimDiagnostics(
                        prev_segment_id=last_original_id,
                        next_segment_id=segment.id,
                        prev_end_before=float(last_original_end),
                        prev_end_snapped=float(prev_snapped),
                        prev_end_trimmed=float(prev_trimmed),
                        next_start_before=float(segment.start),
                        next_start_snapped=float(next_snapped),
                        next_start_trimmed=float(next_trimmed),
                    )
                )

            removed_since_last_original = False
            previous_included_original = True
            last_original_start = float(segment.start)
            last_original_end = float(segment.end)
            last_original_id = segment.id
            continue

        if include_segment and segment.source != "original":
            previous_included_original = False
            last_original_start = None
            last_original_end = None
            last_original_id = None

    return trims


@router.get(
    "/{project_id}/diagnostics/timestamps",
    response_model=TimestampDiagnosticsResponse,
    status_code=status.HTTP_200_OK,
)
def get_timestamp_diagnostics(project_id: UUID) -> TimestampDiagnosticsResponse:
    try:
        project = load_project_metadata(project_id)
    except StorageError as exc:
        raise ProjectNotFound(project_id) from exc

    refine_cfg = TimestampRefinementConfig.from_env()
    active_path = project.metadata.get("transcript_path")
    if not isinstance(active_path, str):
        raise ValidationError("Transcript not found for project")

    active = _load_transcript_optional(active_path)
    if active is None:
        raise ValidationError("Transcript not found for project")

    transcript_asr = _load_transcript_optional(
        project.metadata.get("transcript_asr_path")
        if isinstance(project.metadata.get("transcript_asr_path"), str)
        else None
    )
    transcript_refined = _load_transcript_optional(
        project.metadata.get("transcript_refined_path")
        if isinstance(project.metadata.get("transcript_refined_path"), str)
        else None
    )

    asr_tokens = _token_by_id(transcript_asr)
    refined_tokens = _token_by_id(transcript_refined)

    token_rows: list[TokenTimingDiagnostics] = []
    for token in active.tokens:
        asr = asr_tokens.get(token.id)
        refined = refined_tokens.get(token.id)
        token_rows.append(
            TokenTimingDiagnostics(
                id=token.id,
                text=token.text,
                type=token.type,
                active_start=float(token.start),
                active_end=float(token.end),
                asr_start=float(asr.start) if asr is not None else None,
                asr_end=float(asr.end) if asr is not None else None,
                refined_start=float(refined.start) if refined is not None else None,
                refined_end=float(refined.end) if refined is not None else None,
                delta_asr_start=(
                    float(token.start) - float(asr.start) if asr is not None else None
                ),
                delta_asr_end=(
                    float(token.end) - float(asr.end) if asr is not None else None
                ),
                delta_refined_start=(
                    float(token.start) - float(refined.start)
                    if refined is not None
                    else None
                ),
                delta_refined_end=(
                    float(token.end) - float(refined.end) if refined is not None else None
                ),
            )
        )

    manager = AudioSegmentManager.from_project(project)
    segments = manager.get_all_segments()
    segment_rows = [
        SegmentDiagnostics(
            id=segment.id,
            source=segment.source,
            status=segment.status,
            start=float(segment.start),
            end=float(segment.end),
            token_ids=list(segment.token_ids),
        )
        for segment in segments
    ]
    boundary_trims = _compute_boundary_trims(
        project=project, segments=segments, refine_cfg=refine_cfg
    )

    return TimestampDiagnosticsResponse(
        project_id=project_id,
        computed_at=datetime.now(UTC),
        transcript_active_source=(
            project.metadata.get("transcript_active_source")
            if isinstance(project.metadata.get("transcript_active_source"), str)
            else None
        ),
        refinement_enabled=bool(refine_cfg.enabled),
        snap_window_ms=int(refine_cfg.snap_window_ms),
        cut_padding_ms=int(refine_cfg.cut_padding_ms),
        tokens=token_rows,
        segments=segment_rows,
        boundary_trims=boundary_trims,
    )

