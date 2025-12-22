from __future__ import annotations

from uuid import UUID

import numpy as np
import soundfile as sf

from backend.models.transcript import Token, Transcript
from backend.services.alignment_service import EnergyAlignmentService


def test_energy_alignment_is_monotonic(tmp_path: object) -> None:
    path = tmp_path / "audio.wav"
    sample_rate = 10_000
    audio = np.zeros((sample_rate,), dtype=np.float32)
    audio[int(sample_rate * 0.2) : int(sample_rate * 0.3)] = 0.8
    audio[int(sample_rate * 0.5) : int(sample_rate * 0.6)] = 0.8
    sf.write(path, audio, sample_rate, subtype="PCM_16")

    transcript = Transcript(
        tokens=[
            Token(
                id=UUID("11111111-1111-1111-1111-111111111111"),
                text="one",
                start=0.15,
                end=0.35,
                type="word",
            ),
            Token(
                id=UUID("22222222-2222-2222-2222-222222222222"),
                text="two",
                start=0.45,
                end=0.65,
                type="word",
            ),
        ],
        language="en",
        duration=1.0,
    )

    service = EnergyAlignmentService(window_ms=50, frame_ms=10)
    refined = service.refine(audio_path=str(path), transcript=transcript).transcript
    assert refined.tokens[0].start >= 0.0
    assert refined.tokens[0].end >= refined.tokens[0].start
    assert refined.tokens[1].start >= refined.tokens[0].end
    assert refined.tokens[1].end >= refined.tokens[1].start
