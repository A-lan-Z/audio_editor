from __future__ import annotations

from dataclasses import dataclass

from backend.models.transcript import Transcript
from backend.services.alignment_service import EnergyAlignmentService
from backend.utils.timestamp_refinement_config import TimestampRefinementConfig


@dataclass(frozen=True, slots=True)
class TranscriptRefinementResult:
    asr: Transcript
    refined: Transcript | None


def refine_transcript(
    *, audio_path: str, transcript_asr: Transcript, config: TimestampRefinementConfig
) -> TranscriptRefinementResult:
    if not config.enabled:
        return TranscriptRefinementResult(asr=transcript_asr, refined=None)

    # Lightweight refinement path: use energy-based alignment as a local default.
    # Heavier forced aligners can be introduced behind this interface later.
    aligner = EnergyAlignmentService(window_ms=min(200, max(config.snap_window_ms, 0)))
    refined = aligner.refine(audio_path=audio_path, transcript=transcript_asr).transcript
    return TranscriptRefinementResult(asr=transcript_asr, refined=refined)
