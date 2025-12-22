from __future__ import annotations

from typing import Literal
from uuid import UUID, uuid5

from pydantic import BaseModel, ConfigDict, Field

from backend.models.edit_operation import EditOperation
from backend.models.project import Project
from backend.models.transcript import Token, Transcript

SegmentSource = Literal["original", "generated"]
SegmentStatus = Literal["kept", "removed", "generated"]

SEGMENTS_VERSION_WITH_GAPS = 2
_GAP_SEGMENT_NAMESPACE = UUID("7bdc0dc2-3c2d-4e9b-8f35-c52c2940c3fa")


class AudioSegment(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID
    source: SegmentSource
    file_path: str
    start: float = Field(ge=0)
    end: float = Field(ge=0)
    status: SegmentStatus = Field(default="kept")
    token_ids: list[UUID] = Field(default_factory=list)


def _group_tokens_for_segments(tokens: list[Token]) -> list[AudioSegment]:
    segments: list[AudioSegment] = []
    current_word: Token | None = None
    current_ids: list[UUID] = []

    def flush() -> None:
        nonlocal current_word, current_ids
        if current_word is None:
            current_ids = []
            return
        segments.append(
            AudioSegment(
                id=current_word.id,
                source="original",
                file_path="",
                start=float(current_word.start),
                end=float(current_word.end),
                status="kept",
                token_ids=list(current_ids),
            )
        )
        current_word = None
        current_ids = []

    for token in tokens:
        if token.type == "word":
            flush()
            current_word = token
            current_ids = [token.id]
            continue

        if token.type == "punctuation":
            if current_word is None:
                continue
            current_ids.append(token.id)
            continue

        if token.type == "pause":
            flush()
            segments.append(
                AudioSegment(
                    id=token.id,
                    source="original",
                    file_path="",
                    start=float(token.start),
                    end=float(token.end),
                    status="kept",
                    token_ids=[token.id],
                )
            )
            continue

    flush()
    segments.sort(key=lambda seg: (seg.start, seg.end, str(seg.id)))
    return segments


def _insert_gap_segments(segments: list[AudioSegment]) -> list[AudioSegment]:
    if len(segments) < 2:
        return list(segments)

    out: list[AudioSegment] = [segments[0]]
    for segment in segments[1:]:
        previous = out[-1]
        gap_start = float(previous.end)
        gap_end = float(segment.start)
        if gap_end > gap_start:
            gap_id = uuid5(_GAP_SEGMENT_NAMESPACE, f"{previous.id}:{segment.id}")
            out.append(
                AudioSegment(
                    id=gap_id,
                    source="original",
                    file_path="",
                    start=gap_start,
                    end=gap_end,
                    status="kept",
                    token_ids=[previous.id, segment.id],
                )
            )
        out.append(segment)
    out.sort(key=lambda seg: (seg.start, seg.end, str(seg.id)))
    return out


def _apply_statuses(
    *,
    segments: list[AudioSegment],
    existing_by_id: dict[UUID, AudioSegment],
) -> list[AudioSegment]:
    out: list[AudioSegment] = []
    for segment in segments:
        existing = existing_by_id.get(segment.id)
        if existing is not None:
            out.append(segment.model_copy(update={"status": existing.status}))
            continue

        if segment.token_ids:
            removed = any(
                existing_by_id.get(token_id, None) is not None
                and existing_by_id[token_id].status == "removed"
                for token_id in segment.token_ids
            )
            if removed:
                out.append(segment.model_copy(update={"status": "removed"}))
                continue

        out.append(segment)
    return out


class AudioSegmentManager:
    def __init__(self, segments: list[AudioSegment]) -> None:
        self._segments = segments

    @classmethod
    def from_project(cls, project: Project) -> AudioSegmentManager:
        raw = project.metadata.get("segments")
        if not isinstance(raw, list):
            return cls([])
        segments: list[AudioSegment] = []
        for item in raw:
            if not isinstance(item, dict):
                continue
            segments.append(AudioSegment.model_validate(item))
        segments.sort(key=lambda seg: (seg.start, seg.end, str(seg.id)))
        return cls(segments)

    @classmethod
    def ensure_initialized(
        cls, *, project: Project, transcript: Transcript
    ) -> AudioSegmentManager:
        manager = cls.from_project(project)
        segments_version = project.metadata.get("segments_version")
        if (
            manager._segments
            and isinstance(segments_version, int)
            and segments_version >= SEGMENTS_VERSION_WITH_GAPS
        ):
            return manager

        existing_by_id = {segment.id: segment for segment in manager._segments}
        base_segments = _group_tokens_for_segments(transcript.tokens)
        segments = _insert_gap_segments(base_segments)
        if existing_by_id:
            segments = _apply_statuses(segments=segments, existing_by_id=existing_by_id)
            segments.extend(
                segment for segment in manager._segments if segment.source == "generated"
            )
        audio_path = project.audio_path
        if not audio_path:
            raise ValueError("Project audio_path is required to initialize segments")
        for segment in segments:
            if segment.source == "original":
                segment.file_path = audio_path

        manager = cls(segments)
        manager.persist(project)
        return manager

    def persist(self, project: Project) -> None:
        project.metadata["segments"] = [
            seg.model_dump(mode="json") for seg in self._segments
        ]
        project.metadata["segments_version"] = SEGMENTS_VERSION_WITH_GAPS

    def get_all_segments(self) -> list[AudioSegment]:
        return list(self._segments)

    def mark_removed(self, segment_id: UUID) -> None:
        for index, segment in enumerate(self._segments):
            if segment.id != segment_id:
                continue
            self._segments[index] = segment.model_copy(update={"status": "removed"})
            return
        raise KeyError(f"Segment not found: {segment_id}")

    def mark_kept(self, segment_id: UUID) -> None:
        for index, segment in enumerate(self._segments):
            if segment.id != segment_id:
                continue
            next_status: SegmentStatus = (
                "generated" if segment.source == "generated" else "kept"
            )
            self._segments[index] = segment.model_copy(update={"status": next_status})
            return
        raise KeyError(f"Segment not found: {segment_id}")

    def mark_segment_removed(self, segment_id: UUID) -> None:
        self.mark_removed(segment_id)

    def mark_segment_kept(self, segment_id: UUID) -> None:
        self.mark_kept(segment_id)

    def add_generated_segment(
        self,
        *,
        segment_id: UUID,
        file_path: str,
        start: float,
        end: float,
        token_ids: list[UUID] | None = None,
    ) -> AudioSegment:
        segment = AudioSegment(
            id=segment_id,
            source="generated",
            file_path=file_path,
            start=start,
            end=end,
            status="generated",
            token_ids=token_ids or [],
        )
        self._segments.append(segment)
        self._segments.sort(key=lambda seg: (seg.start, seg.end, str(seg.id)))
        return segment

    def find_segment_ids_for_token_ids(self, token_ids: list[UUID]) -> list[UUID]:
        if not token_ids:
            return []
        token_set = set(token_ids)
        hits: list[UUID] = []
        for segment in self._segments:
            if segment.source != "original":
                continue
            if token_set.intersection(segment.token_ids):
                hits.append(segment.id)
        return hits

    def mark_removed_for_token_ids(self, token_ids: list[UUID]) -> list[UUID]:
        segment_ids = self.find_segment_ids_for_token_ids(token_ids)
        for segment_id in segment_ids:
            try:
                self.mark_removed(segment_id)
            except KeyError:
                continue
        return segment_ids

    def rebuild_from_active_edits(self, edits: list[EditOperation]) -> None:
        for index, segment in enumerate(self._segments):
            if segment.source != "original":
                continue
            if segment.status == "generated":
                continue
            self._segments[index] = segment.model_copy(update={"status": "kept"})

        for edit in edits:
            if edit.type != "delete":
                continue
            self.mark_removed_for_token_ids(edit.old_tokens)
