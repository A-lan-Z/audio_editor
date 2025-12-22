from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Literal

SnapMode = Literal["rms", "vad"]
AlignmentBackend = Literal["none", "mfa"]


TRANSCRIPT_ACTIVE_FILENAME = "transcript.json"
TRANSCRIPT_ASR_FILENAME = "transcript_asr.json"
TRANSCRIPT_REFINED_FILENAME = "transcript_refined.json"
TRANSCRIPT_ORIGINAL_FILENAME = "transcript_original.json"

METADATA_TRANSCRIPT_PATH = "transcript_path"
METADATA_TRANSCRIPT_ASR_PATH = "transcript_asr_path"
METADATA_TRANSCRIPT_REFINED_PATH = "transcript_refined_path"
METADATA_TRANSCRIPT_ACTIVE_SOURCE = "transcript_active_source"
METADATA_TRANSCRIPT_ORIGINAL_PATH = "original_transcript_path"


def _env_bool(name: str, default: bool) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    value = raw.strip().lower()
    if value in {"1", "true", "yes", "on"}:
        return True
    if value in {"0", "false", "no", "off"}:
        return False
    return default


def _env_int(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


@dataclass(frozen=True, slots=True)
class TimestampRefinementConfig:
    enabled: bool
    alignment_backend: AlignmentBackend
    snap_mode: SnapMode
    snap_window_ms: int
    cut_padding_ms: int

    @classmethod
    def from_env(cls) -> TimestampRefinementConfig:
        enabled = _env_bool("TEXTAUDIO_REFINE_TIMESTAMPS", False)
        alignment_backend = os.environ.get("TEXTAUDIO_ALIGNMENT_BACKEND", "none")
        if alignment_backend not in {"none", "mfa"}:
            alignment_backend = "none"

        snap_mode = os.environ.get("TEXTAUDIO_SNAP_MODE", "rms")
        if snap_mode not in {"rms", "vad"}:
            snap_mode = "rms"

        snap_window_ms = max(0, _env_int("TEXTAUDIO_SNAP_WINDOW_MS", 200))
        cut_padding_ms = max(0, _env_int("TEXTAUDIO_CUT_PADDING_MS", 40))
        return cls(
            enabled=enabled,
            alignment_backend=alignment_backend,  # type: ignore[arg-type]
            snap_mode=snap_mode,  # type: ignore[arg-type]
            snap_window_ms=snap_window_ms,
            cut_padding_ms=cut_padding_ms,
        )
