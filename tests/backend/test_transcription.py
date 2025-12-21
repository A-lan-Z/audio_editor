from __future__ import annotations

import os
import time
from pathlib import Path

import numpy as np
import pytest
import soundfile as sf

from backend.api.transcription import (
    get_transcript,
    get_transcription_status,
    transcribe_project,
)
from backend.models.transcript import Token, Transcript
from backend.services.project_manager import ProjectManager
from backend.services.transcription_jobs import TranscriptionJobManager
from backend.services.transcription_service import TranscriptionService
from backend.services.whisper_service import WhisperConfig, WhisperTranscriptionService
from backend.utils.errors import ValidationError
from backend.utils.storage import (
    load_project_metadata,
    project_original_wav_path,
    save_project_metadata,
)


class FakeTranscriptionService(TranscriptionService):
    def __init__(
        self, *, transcript: Transcript | None = None, error: Exception | None = None
    ) -> None:
        self._transcript = transcript
        self._error = error

    def transcribe(self, audio_path: str) -> Transcript:
        _ = audio_path
        if self._error is not None:
            raise self._error
        return self._transcript or Transcript()

    def get_word_timestamps(self, audio_path: str) -> list[Token]:
        transcript = self.transcribe(audio_path)
        return transcript.tokens


def _write_sine_wav(path: Path, *, seconds: float, sample_rate: int = 16_000) -> None:
    t = np.linspace(0, seconds, int(sample_rate * seconds), endpoint=False)
    audio = (0.05 * np.sin(2 * np.pi * 440 * t)).astype("float32")
    path.parent.mkdir(parents=True, exist_ok=True)
    sf.write(path, audio, sample_rate, subtype="PCM_16")


def test_transcription_pipeline_saves_transcript(
    tmp_path: Path, monkeypatch: object
) -> None:
    monkeypatch.setenv("TEXTAUDIO_PROJECTS_DIR", str(tmp_path / "projects"))

    manager = ProjectManager()
    project = manager.create_project(metadata={})
    save_project_metadata(project)

    wav_path = project_original_wav_path(project.id)
    _write_sine_wav(wav_path, seconds=2.0)

    transcript = Transcript(
        tokens=[
            Token(text="Hello", start=0.0, end=0.5, type="word"),
            Token(text=",", start=0.5, end=0.5, type="punctuation"),
            Token(text="world", start=0.5, end=1.0, type="word"),
            Token(text="!", start=1.0, end=1.0, type="punctuation"),
        ],
        language="en",
        duration=2.0,
    )
    service = FakeTranscriptionService(transcript=transcript)
    jobs = TranscriptionJobManager()

    start = transcribe_project(project.id, transcription_service=service, jobs=jobs)
    assert start.status == "queued"

    for _ in range(100):
        status_resp = get_transcription_status(project.id, jobs=jobs)
        if status_resp.status == "completed":
            break
        time.sleep(0.05)
    assert status_resp.status == "completed"

    loaded = get_transcript(project.id)
    assert loaded.to_text() == "Hello, world!"

    updated = load_project_metadata(project.id)
    transcript_path = updated.metadata.get("transcript_path")
    assert isinstance(transcript_path, str)
    assert Path(transcript_path).exists()


def test_transcription_handles_empty_audio(tmp_path: Path, monkeypatch: object) -> None:
    monkeypatch.setenv("TEXTAUDIO_PROJECTS_DIR", str(tmp_path / "projects"))

    manager = ProjectManager()
    project = manager.create_project(metadata={})
    save_project_metadata(project)

    wav_path = project_original_wav_path(project.id)
    _write_sine_wav(wav_path, seconds=1.0)

    service = FakeTranscriptionService(
        transcript=Transcript(tokens=[], language="en", duration=1.0)
    )
    jobs = TranscriptionJobManager()

    transcribe_project(project.id, transcription_service=service, jobs=jobs)
    for _ in range(100):
        status_resp = get_transcription_status(project.id, jobs=jobs)
        if status_resp.status == "completed":
            break
        time.sleep(0.05)
    assert status_resp.status == "completed"
    loaded = get_transcript(project.id)
    assert loaded.tokens == []


def test_transcription_failed_state_when_service_errors(
    tmp_path: Path, monkeypatch: object
) -> None:
    monkeypatch.setenv("TEXTAUDIO_PROJECTS_DIR", str(tmp_path / "projects"))

    manager = ProjectManager()
    project = manager.create_project(metadata={})
    save_project_metadata(project)

    wav_path = project_original_wav_path(project.id)
    _write_sine_wav(wav_path, seconds=1.0)

    service = FakeTranscriptionService(error=ValidationError("Corrupt audio"))
    jobs = TranscriptionJobManager()

    transcribe_project(project.id, transcription_service=service, jobs=jobs)
    for _ in range(100):
        status_resp = get_transcription_status(project.id, jobs=jobs)
        if status_resp.status == "failed":
            break
        time.sleep(0.05)
    assert status_resp.status == "failed"
    with pytest.raises(ValidationError):
        get_transcript(project.id)


def test_synthetic_sample_audio_generated(tmp_path: Path) -> None:
    path = tmp_path / "synthetic_2min.wav"
    _write_sine_wav(path, seconds=120.0)
    assert path.exists()
    assert path.stat().st_size > 0


@pytest.mark.skipif(
    os.environ.get("TEXTAUDIO_RUN_ASR_TESTS") != "1",
    reason="Set TEXTAUDIO_RUN_ASR_TESTS=1 to run real ASR integration test",
)
def test_real_asr_transcribes_audio(tmp_path: Path, monkeypatch: object) -> None:
    monkeypatch.setenv("TEXTAUDIO_PROJECTS_DIR", str(tmp_path / "projects"))
    monkeypatch.setenv("TEXTAUDIO_MODELS_DIR", str(tmp_path / "models"))

    manager = ProjectManager()
    project = manager.create_project(metadata={})
    save_project_metadata(project)

    wav_path = project_original_wav_path(project.id)
    _write_sine_wav(wav_path, seconds=3.0)

    service = WhisperTranscriptionService(config=WhisperConfig(model_name="tiny"))
    jobs = TranscriptionJobManager()

    transcribe_project(project.id, transcription_service=service, jobs=jobs)
    for _ in range(200):
        status_resp = get_transcription_status(project.id, jobs=jobs)
        if status_resp.status in {"completed", "failed"}:
            break
        time.sleep(0.05)
    assert status_resp.status == "completed"
    transcript = get_transcript(project.id)
    assert len(transcript.tokens) >= 1
