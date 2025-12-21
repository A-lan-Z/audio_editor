from __future__ import annotations

import pytest

from backend.models.transcript import Token, Transcript


def test_transcript_to_text_roundtrip() -> None:
    transcript = Transcript(
        tokens=[
            Token(text="Hello", start=0.0, end=0.5, type="word"),
            Token(text=",", start=0.5, end=0.5, type="punctuation"),
            Token(text="world", start=0.5, end=1.0, type="word"),
            Token(text="!", start=1.0, end=1.0, type="punctuation"),
        ],
        language="en",
        duration=1.0,
    )

    assert transcript.to_text() == "Hello, world!"

    reloaded = Transcript.from_json(transcript.to_json())
    assert reloaded.to_text() == "Hello, world!"


def test_transcript_rejects_overlapping_tokens() -> None:
    with pytest.raises(ValueError, match="non-overlapping"):
        Transcript(
            tokens=[
                Token(text="a", start=0.0, end=1.0, type="word"),
                Token(text="b", start=0.5, end=1.5, type="word"),
            ]
        )
