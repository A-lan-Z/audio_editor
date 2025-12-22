from __future__ import annotations

import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import soundfile as sf

from backend.models.transcript import Token, Transcript
from backend.utils.errors import ValidationError


@dataclass(frozen=True, slots=True)
class AlignmentResult:
    transcript: Transcript


class AlignmentService(ABC):
    @abstractmethod
    def refine(self, *, audio_path: str, transcript: Transcript) -> AlignmentResult: ...


def _read_mono_audio(path: Path) -> tuple[np.ndarray, int]:
    audio, sample_rate = sf.read(path, dtype="float32", always_2d=False)
    array = np.asarray(audio, dtype=np.float32)
    if array.ndim == 2:
        array = array[:, 0]
    return array, int(sample_rate)


def _frame_rms(audio: np.ndarray, *, frame_samples: int) -> np.ndarray:
    if frame_samples <= 0:
        raise ValueError("frame_samples must be > 0")
    if audio.size <= 0:
        return np.zeros((0,), dtype=np.float32)
    if audio.size <= frame_samples:
        return np.asarray([np.sqrt(np.mean(audio**2))], dtype=np.float32)

    full_frames = int(audio.size // frame_samples)
    trimmed = audio[: full_frames * frame_samples]
    frames = np.reshape(trimmed, (full_frames, frame_samples))
    rms = np.sqrt(np.mean(frames**2, axis=1, dtype=np.float32))

    tail = audio[full_frames * frame_samples :]
    if tail.size:
        tail_rms = np.asarray([np.sqrt(np.mean(tail**2))], dtype=np.float32)
        rms = np.concatenate([rms, tail_rms])

    return np.asarray(rms, dtype=np.float32)


def _nearest_min_time(
    rms: np.ndarray,
    *,
    sample_rate: int,
    frame_samples: int,
    center_time: float,
    window_ms: int,
) -> float:
    if rms.size == 0:
        return float(center_time)
    window = max(0.0, float(window_ms) / 1000.0)
    center_index = int(round(float(center_time) * float(sample_rate) / frame_samples))
    span = int(round(window * float(sample_rate) / frame_samples))
    start = max(0, center_index - span)
    end = min(len(rms), center_index + span + 1)
    if end <= start:
        return float(center_time)
    local = rms[start:end]
    local_min = int(np.argmin(local))
    best_index = start + local_min
    return float(best_index * frame_samples / float(sample_rate))


class NoopAlignmentService(AlignmentService):
    def refine(self, *, audio_path: str, transcript: Transcript) -> AlignmentResult:
        _ = audio_path
        return AlignmentResult(transcript=transcript)


class EnergyAlignmentService(AlignmentService):
    """Lightweight local refinement based on energy minima.

    This is not a full phoneme-level forced aligner, but it is a deterministic
    refinement that can improve boundary stability for edit operations and
    downstream snapping, without adding heavy dependencies.
    """

    def __init__(
        self,
        *,
        window_ms: int = 50,
        frame_ms: int = 10,
    ) -> None:
        self._window_ms = max(0, int(window_ms))
        self._frame_ms = max(1, int(frame_ms))

    def refine(self, *, audio_path: str, transcript: Transcript) -> AlignmentResult:
        path = Path(audio_path)
        if not path.exists():
            raise ValidationError(f"Audio file not found: {audio_path}")
        if path.is_dir():
            raise ValidationError(f"Expected audio file, got directory: {audio_path}")

        audio, sample_rate = _read_mono_audio(path)
        frame_samples = max(1, int(round(float(sample_rate) * self._frame_ms / 1000.0)))
        rms = _frame_rms(audio, frame_samples=frame_samples)

        refined_tokens: list[Token] = []
        previous_end = 0.0
        for token in transcript.tokens:
            if token.type != "word":
                refined_tokens.append(token)
                previous_end = max(previous_end, float(token.end))
                continue

            start = _nearest_min_time(
                rms,
                sample_rate=sample_rate,
                frame_samples=frame_samples,
                center_time=float(token.start),
                window_ms=self._window_ms,
            )
            end = _nearest_min_time(
                rms,
                sample_rate=sample_rate,
                frame_samples=frame_samples,
                center_time=float(token.end),
                window_ms=self._window_ms,
            )

            start = max(start, previous_end)
            end = max(end, start)
            refined = token.model_copy(update={"start": start, "end": end})
            refined_tokens.append(refined)
            previous_end = end

        refined_transcript = Transcript(
            tokens=refined_tokens,
            language=transcript.language,
            duration=transcript.duration,
            created_at=transcript.created_at,
        )
        return AlignmentResult(transcript=refined_transcript)


def alignment_service_from_env() -> AlignmentService:
    backend = os.environ.get("TEXTAUDIO_ALIGNMENT_BACKEND", "none").strip().lower()
    if backend == "none":
        return NoopAlignmentService()
    if backend == "mfa":
        raise ValidationError(
            "Alignment backend 'mfa' is configured but not implemented. "
            "Set TEXTAUDIO_ALIGNMENT_BACKEND=none to disable."
        )
    return NoopAlignmentService()
