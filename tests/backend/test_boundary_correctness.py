from __future__ import annotations

from uuid import UUID

import numpy as np
import soundfile as sf

from backend.models.edit_operation import EditOperation
from backend.models.project import Project
from backend.models.transcript import Token, Transcript
from backend.services.audio_renderer import _crossfade_concatenate, render
from backend.services.boundary_snapping import (
    frame_rms,
    snap_boundary_backward,
    snap_boundary_forward,
)
from backend.services.deletion_handler import sync_deleted_segments_for_active_edits
from backend.utils.storage import project_original_wav_path, save_project_metadata


def test_boundary_snapping_tie_breaking_is_deterministic() -> None:
    sample_rate = 1_000
    frame_samples = 10
    rms = np.asarray([0.2, 0.1, 0.1, 0.3], dtype=np.float32)

    backward = snap_boundary_backward(
        rms,
        sample_rate=sample_rate,
        frame_samples=frame_samples,
        center_time=0.03,
        window_ms=50,
    )
    forward = snap_boundary_forward(
        rms,
        sample_rate=sample_rate,
        frame_samples=frame_samples,
        center_time=0.01,
        window_ms=50,
    )

    # Backward chooses the latest minimum-energy frame; forward chooses earliest.
    assert backward == 0.02
    assert forward == 0.01


def test_delete_sentence_removes_audio_without_large_leakage(
    tmp_path: object, monkeypatch: object
) -> None:
    monkeypatch.setenv("TEXTAUDIO_PROJECTS_DIR", str(tmp_path / "projects"))
    monkeypatch.setenv("TEXTAUDIO_CROSSFADE_MS", "10")
    monkeypatch.setenv("TEXTAUDIO_REFINE_TIMESTAMPS", "1")
    monkeypatch.setenv("TEXTAUDIO_SNAP_WINDOW_MS", "300")
    monkeypatch.setenv("TEXTAUDIO_CUT_PADDING_MS", "0")

    project = Project(metadata={})
    audio_path = project_original_wav_path(project.id)
    project.audio_path = str(audio_path)

    sample_rate = 1_000
    audio = np.zeros((sample_rate,), dtype=np.float32)
    audio[: int(sample_rate * 0.2)] = 0.2
    audio[int(sample_rate * 0.2) : int(sample_rate * 0.4)] = 0.9
    audio[int(sample_rate * 0.4) : int(sample_rate * 0.45)] = 0.0
    audio[int(sample_rate * 0.45) : int(sample_rate * 0.7)] = 0.8
    audio[int(sample_rate * 0.7) :] = 0.3
    sf.write(audio_path, audio, sample_rate, subtype="PCM_16")

    w1 = UUID("11111111-1111-1111-1111-111111111111")
    w2 = UUID("22222222-2222-2222-2222-222222222222")
    w3 = UUID("33333333-3333-3333-3333-333333333333")
    w4 = UUID("44444444-4444-4444-4444-444444444444")
    transcript = Transcript(
        tokens=[
            Token(id=w1, text="a", start=0.0, end=0.3, type="word"),
            Token(id=w2, text="b", start=0.3, end=0.45, type="word"),
            Token(id=w3, text="c", start=0.45, end=0.65, type="word"),
            Token(id=w4, text="d", start=0.65, end=0.9, type="word"),
        ],
        language="en",
        duration=0.9,
    )

    delete_middle = EditOperation(
        type="delete",
        position=0,
        old_tokens=[w2, w3],
        new_text="",
    )
    sync_deleted_segments_for_active_edits(
        project=project,
        original_transcript=transcript,
        active_edits=[delete_middle],
    )
    save_project_metadata(project)

    rendered, rendered_rate = render(project.id)
    assert rendered_rate == sample_rate
    assert float(np.max(np.abs(rendered))) < 0.6

    frame_samples = max(1, int(round(float(sample_rate) * 0.01)))
    rms = frame_rms(audio, frame_samples=frame_samples)
    snapped_end = snap_boundary_backward(
        rms,
        sample_rate=sample_rate,
        frame_samples=frame_samples,
        center_time=0.3,
        window_ms=300,
    )
    snapped_start = snap_boundary_forward(
        rms,
        sample_rate=sample_rate,
        frame_samples=frame_samples,
        center_time=0.65,
        window_ms=300,
    )
    expected = _crossfade_concatenate(
        [
            audio[: int(round(float(sample_rate) * float(snapped_end)))],
            audio[int(round(float(sample_rate) * float(max(snapped_start, 0.65)))) : int(
                round(float(sample_rate) * 0.9)
            )],
        ],
        sample_rate=sample_rate,
        crossfade_ms=10.0,
    )
    assert rendered.shape == expected.shape
    assert np.allclose(rendered, expected, atol=1e-3)


def test_multiple_delete_edits_apply_without_dropping_segments() -> None:
    w1 = UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
    w2 = UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb")
    w3 = UUID("cccccccc-cccc-cccc-cccc-cccccccccccc")
    transcript = Transcript(
        tokens=[
            Token(id=w1, text="a", start=0.0, end=0.1, type="word"),
            Token(id=w2, text="b", start=0.1, end=0.2, type="word"),
            Token(id=w3, text="c", start=0.2, end=0.3, type="word"),
        ],
        language="en",
        duration=0.3,
    )
    project = Project(audio_path="/tmp/original.wav", metadata={})
    edits = [
        EditOperation(type="delete", position=0, old_tokens=[w2], new_text=""),
        EditOperation(type="delete", position=0, old_tokens=[w3], new_text=""),
    ]
    sync_deleted_segments_for_active_edits(
        project=project,
        original_transcript=transcript,
        active_edits=edits,
    )
    removed = {
        seg["id"]
        for seg in project.metadata["segments"]
        if isinstance(seg, dict) and seg.get("status") == "removed"
    }
    assert str(w2) in removed
    assert str(w3) in removed
