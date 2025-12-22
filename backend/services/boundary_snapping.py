from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True, slots=True)
class BoundarySnappingConfig:
    window_ms: int
    frame_ms: int = 10

    @property
    def window_seconds(self) -> float:
        return max(0.0, float(self.window_ms) / 1000.0)

    @property
    def frame_seconds(self) -> float:
        return max(0.001, float(self.frame_ms) / 1000.0)


def frame_rms(audio: np.ndarray, *, frame_samples: int) -> np.ndarray:
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


def _time_to_frame_index(*, time_s: float, sample_rate: int, frame_samples: int) -> int:
    return int(round(float(time_s) * float(sample_rate) / float(frame_samples)))


def _frame_index_to_time(
    *, frame_index: int, sample_rate: int, frame_samples: int
) -> float:
    return float(frame_index * frame_samples / float(sample_rate))


def snap_boundary_backward(
    rms: np.ndarray,
    *,
    sample_rate: int,
    frame_samples: int,
    center_time: float,
    window_ms: int,
) -> float:
    """Snap to the lowest-energy frame at or before center_time.

    If multiple frames share the same minimum energy, this chooses the latest
    such frame (closest to the center boundary).
    """

    if rms.size == 0:
        return float(center_time)
    window = max(0.0, float(window_ms) / 1000.0)
    center_index = _time_to_frame_index(
        time_s=float(center_time), sample_rate=sample_rate, frame_samples=frame_samples
    )
    span = int(round(window * float(sample_rate) / float(frame_samples)))
    start = max(0, center_index - span)
    end = min(len(rms), center_index + 1)
    if end <= start:
        return float(center_time)
    local = rms[start:end]
    minimum = float(np.min(local))
    candidates = np.where(local == minimum)[0]
    if candidates.size == 0:
        return float(center_time)
    best_local = int(candidates[-1])
    best_index = start + best_local
    return _frame_index_to_time(
        frame_index=best_index, sample_rate=sample_rate, frame_samples=frame_samples
    )


def snap_boundary_forward(
    rms: np.ndarray,
    *,
    sample_rate: int,
    frame_samples: int,
    center_time: float,
    window_ms: int,
) -> float:
    """Snap to the lowest-energy frame at or after center_time.

    If multiple frames share the same minimum energy, this chooses the earliest
    such frame (closest to the center boundary).
    """

    if rms.size == 0:
        return float(center_time)
    window = max(0.0, float(window_ms) / 1000.0)
    center_index = _time_to_frame_index(
        time_s=float(center_time), sample_rate=sample_rate, frame_samples=frame_samples
    )
    span = int(round(window * float(sample_rate) / float(frame_samples)))
    start = max(0, center_index)
    end = min(len(rms), center_index + span + 1)
    if end <= start:
        return float(center_time)
    local = rms[start:end]
    minimum = float(np.min(local))
    candidates = np.where(local == minimum)[0]
    if candidates.size == 0:
        return float(center_time)
    best_local = int(candidates[0])
    best_index = start + best_local
    return _frame_index_to_time(
        frame_index=best_index, sample_rate=sample_rate, frame_samples=frame_samples
    )
