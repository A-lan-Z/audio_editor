from __future__ import annotations

from uuid import UUID

import numpy as np
import soundfile as sf

from backend.models.project import Project
from backend.models.transcript import Token, Transcript
from backend.services.transcription_artifacts import persist_transcription_artifacts
from backend.utils.storage import load_project_metadata, save_project_metadata
from backend.utils.timestamp_refinement_config import TimestampRefinementConfig


def _write_test_audio(path: object) -> None:
    sample_rate = 16_000
    audio = np.zeros((sample_rate,), dtype=np.float32)
    audio[int(sample_rate * 0.2) : int(sample_rate * 0.25)] = 0.8
    audio[int(sample_rate * 0.55) : int(sample_rate * 0.6)] = 0.8
    sf.write(path, audio, sample_rate, subtype="PCM_16")


def test_persist_transcription_artifacts_writes_asr_and_active(
    tmp_path: object, monkeypatch: object
) -> None:
    monkeypatch.setenv("TEXTAUDIO_PROJECTS_DIR", str(tmp_path / "projects"))
    project = Project(
        id=UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"),
        metadata={"name": "demo"},
    )
    save_project_metadata(project)
    audio_path = tmp_path / "audio.wav"
    _write_test_audio(audio_path)

    transcript = Transcript(
        tokens=[
            Token(
                id=UUID("11111111-1111-1111-1111-111111111111"),
                text="hello",
                start=0.1,
                end=0.3,
                type="word",
            ),
            Token(
                id=UUID("22222222-2222-2222-2222-222222222222"),
                text="world",
                start=0.5,
                end=0.7,
                type="word",
            ),
        ],
        language="en",
        duration=1.0,
    )
    config = TimestampRefinementConfig(
        enabled=False,
        alignment_backend="none",
        snap_mode="rms",
        snap_window_ms=200,
        cut_padding_ms=40,
    )

    loaded = load_project_metadata(project.id)
    artifacts = persist_transcription_artifacts(
        project=loaded,
        audio_path=str(audio_path),
        transcript_asr=transcript,
        config=config,
    )
    save_project_metadata(loaded)

    assert artifacts.transcript_active_source == "asr"
    assert (tmp_path / "projects" / str(project.id) / "transcript_asr.json").exists()
    assert (tmp_path / "projects" / str(project.id) / "transcript.json").exists()
    assert (tmp_path / "projects" / str(project.id) / "transcript_original.json").exists()

    updated = load_project_metadata(project.id)
    assert updated.metadata["transcript_active_source"] == "asr"
    assert "transcript_asr_path" in updated.metadata
    assert "original_transcript_path" in updated.metadata


def test_persist_transcription_artifacts_writes_refined_when_enabled(
    tmp_path: object, monkeypatch: object
) -> None:
    monkeypatch.setenv("TEXTAUDIO_PROJECTS_DIR", str(tmp_path / "projects"))
    project = Project(id=UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"))
    save_project_metadata(project)
    audio_path = tmp_path / "audio.wav"
    _write_test_audio(audio_path)

    transcript = Transcript(
        tokens=[
            Token(
                id=UUID("33333333-3333-3333-3333-333333333333"),
                text="one",
                start=0.05,
                end=0.35,
                type="word",
            ),
            Token(
                id=UUID("44444444-4444-4444-4444-444444444444"),
                text="two",
                start=0.45,
                end=0.75,
                type="word",
            ),
        ],
        language="en",
        duration=1.0,
    )
    config = TimestampRefinementConfig(
        enabled=True,
        alignment_backend="none",
        snap_mode="rms",
        snap_window_ms=50,
        cut_padding_ms=40,
    )

    loaded = load_project_metadata(project.id)
    artifacts = persist_transcription_artifacts(
        project=loaded,
        audio_path=str(audio_path),
        transcript_asr=transcript,
        config=config,
    )
    save_project_metadata(loaded)

    assert artifacts.transcript_active_source in {"asr", "refined"}
    assert (tmp_path / "projects" / str(project.id) / "transcript_asr.json").exists()
    assert (tmp_path / "projects" / str(project.id) / "transcript.json").exists()

    refined_path = tmp_path / "projects" / str(project.id) / "transcript_refined.json"
    if artifacts.transcript_active_source == "refined":
        assert refined_path.exists()
