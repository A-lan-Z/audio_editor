from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from uuid import UUID

import numpy as np
import soundfile as sf

from backend.models.project import Project
from backend.services.audio_segment_manager import AudioSegment, AudioSegmentManager
from backend.utils.storage import StorageError, load_project_metadata


@dataclass(frozen=True, slots=True)
class AudioRenderError(Exception):
    message: str

    def __str__(self) -> str:
        return self.message


DEFAULT_CROSSFADE_MS = 20.0
MIN_CROSSFADE_MS = 10.0
MAX_CROSSFADE_MS = 50.0


def _crossfade_ms() -> float:
    raw = os.environ.get("TEXTAUDIO_CROSSFADE_MS")
    if raw is None:
        return DEFAULT_CROSSFADE_MS
    try:
        value = float(raw)
    except ValueError:
        return DEFAULT_CROSSFADE_MS
    return float(min(MAX_CROSSFADE_MS, max(MIN_CROSSFADE_MS, value)))


def _cosine_fade(length: int) -> np.ndarray:
    if length <= 0:
        return np.zeros((0,), dtype=np.float32)
    t = np.linspace(0.0, 1.0, length, endpoint=True, dtype=np.float32)
    return 0.5 - 0.5 * np.cos(np.pi * t)


def _crossfade_concatenate(
    chunks: list[np.ndarray], *, sample_rate: int, crossfade_ms: float
) -> np.ndarray:
    if not chunks:
        return np.zeros((0,), dtype=np.float32)
    if len(chunks) == 1:
        return np.asarray(chunks[0], dtype=np.float32)

    fade_samples = int(round(float(sample_rate) * float(crossfade_ms) / 1000.0))
    if fade_samples <= 0:
        return np.concatenate(chunks)

    out = np.asarray(chunks[0], dtype=np.float32)
    fade_in = _cosine_fade(fade_samples)
    fade_out = 1.0 - fade_in

    for next_chunk in chunks[1:]:
        b = np.asarray(next_chunk, dtype=np.float32)
        if out.size < fade_samples or b.size < fade_samples:
            out = np.concatenate([out, b])
            continue

        a_head = out[:-fade_samples]
        a_tail = out[-fade_samples:]
        b_head = b[:fade_samples]
        b_tail = b[fade_samples:]
        overlapped = a_tail * fade_out + b_head * fade_in
        out = np.concatenate([a_head, overlapped, b_tail])

    return out


def _read_mono_audio(path: Path) -> tuple[np.ndarray, int]:
    audio, sample_rate = sf.read(path, dtype="float32", always_2d=False)
    array = np.asarray(audio, dtype=np.float32)
    if array.ndim == 2:
        array = array[:, 0]
    return array, int(sample_rate)


def _project_audio_path(project: Project) -> Path:
    if not project.audio_path:
        raise AudioRenderError("Project audio_path is not set")
    return Path(project.audio_path)


def _default_segment(
    project: Project, audio: np.ndarray, sample_rate: int
) -> AudioSegment:
    duration = float(len(audio) / float(sample_rate))
    return AudioSegment(
        id=UUID(int=0),
        source="original",
        file_path=str(_project_audio_path(project)),
        start=0.0,
        end=duration,
        status="kept",
        token_ids=[],
    )


def _slice_segment(
    *, audio: np.ndarray, sample_rate: int, start: float, end: float
) -> np.ndarray:
    start_sample = int(round(max(start, 0.0) * float(sample_rate)))
    end_sample = int(round(max(end, 0.0) * float(sample_rate)))
    start_sample = max(0, min(start_sample, len(audio)))
    end_sample = max(0, min(end_sample, len(audio)))
    if end_sample <= start_sample:
        return np.zeros((0,), dtype=np.float32)
    return audio[start_sample:end_sample]


def _load_segment_audio(
    *, segment: AudioSegment, original_audio: np.ndarray, sample_rate: int
) -> np.ndarray:
    if segment.source == "original":
        return _slice_segment(
            audio=original_audio,
            sample_rate=sample_rate,
            start=segment.start,
            end=segment.end,
        )

    segment_audio, segment_rate = _read_mono_audio(Path(segment.file_path))
    if segment_rate != sample_rate:
        raise AudioRenderError(
            f"Generated segment sample rate mismatch: {segment_rate} != {sample_rate}"
        )
    return segment_audio


def render(project_id: UUID) -> tuple[np.ndarray, int]:
    try:
        project = load_project_metadata(project_id)
    except StorageError as exc:
        raise AudioRenderError(str(exc)) from exc

    audio_path = _project_audio_path(project)
    if not audio_path.exists():
        raise AudioRenderError("Audio file not found for project")

    original_audio, sample_rate = _read_mono_audio(audio_path)
    manager = AudioSegmentManager.from_project(project)
    segments = manager.get_all_segments()
    if not segments:
        segments = [_default_segment(project, original_audio, sample_rate)]

    kept = [seg for seg in segments if seg.status in {"kept", "generated"}]
    kept.sort(key=lambda seg: (seg.start, seg.end, str(seg.id)))

    chunks: list[np.ndarray] = []
    last_original_end = 0.0
    for segment in kept:
        if segment.source == "original":
            start = max(float(segment.start), float(last_original_end))
            end = max(float(segment.end), start)
            last_original_end = max(last_original_end, end)
            chunk = _slice_segment(
                audio=original_audio, sample_rate=sample_rate, start=start, end=end
            )
        else:
            chunk = _load_segment_audio(
                segment=segment,
                original_audio=original_audio,
                sample_rate=sample_rate,
            )
        if chunk.size:
            chunks.append(chunk)

    if not chunks:
        return np.zeros((0,), dtype=np.float32), sample_rate

    return (
        _crossfade_concatenate(
            chunks, sample_rate=sample_rate, crossfade_ms=_crossfade_ms()
        ),
        sample_rate,
    )
