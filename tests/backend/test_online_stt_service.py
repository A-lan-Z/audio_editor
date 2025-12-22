from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from backend.services.online_stt_service import (
    OnlineSttConfig,
    OnlineWordSpanTranscriptionService,
)
from backend.utils.errors import ValidationError


class _FakeResponse:
    def __init__(self, payload: dict) -> None:
        self._data = json.dumps(payload).encode("utf-8")

    def read(self) -> bytes:
        return self._data

    def __enter__(self) -> _FakeResponse:
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        return None


def test_online_stt_disabled_rejected(tmp_path: Path) -> None:
    audio_path = tmp_path / "audio.wav"
    audio_path.write_bytes(b"RIFF....WAVEfmt ")
    service = OnlineWordSpanTranscriptionService(
        config=OnlineSttConfig(enabled=False, url="http://example", auth_header=None)
    )
    with pytest.raises(ValidationError):
        service.get_word_timestamps(str(audio_path))


def test_online_stt_missing_url_rejected(tmp_path: Path) -> None:
    audio_path = tmp_path / "audio.wav"
    audio_path.write_bytes(b"RIFF....WAVEfmt ")
    service = OnlineWordSpanTranscriptionService(
        config=OnlineSttConfig(enabled=True, url=None, auth_header=None)
    )
    with pytest.raises(ValidationError):
        service.get_word_timestamps(str(audio_path))


def test_online_stt_parses_words(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    audio_path = tmp_path / "audio.wav"
    audio_path.write_bytes(b"RIFF....WAVEfmt ")

    payload = {
        "words": [
            {"text": "Hello", "start": 0.0, "end": 0.5},
            {"text": ",", "start": 0.5, "end": 0.5},
            {"text": "world", "start": 0.5, "end": 1.0},
        ]
    }

    def fake_urlopen(request: object, timeout: int = 0) -> _FakeResponse:
        _ = SimpleNamespace(request=request, timeout=timeout)
        return _FakeResponse(payload)

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    service = OnlineWordSpanTranscriptionService(
        config=OnlineSttConfig(
            enabled=True, url="http://example.invalid/transcribe", auth_header=None
        )
    )
    tokens = service.get_word_timestamps(str(audio_path))
    assert [t.type for t in tokens][:2] == ["word", "punctuation"]
    assert tokens[0].text == "Hello"
    assert tokens[-1].text == "world"
