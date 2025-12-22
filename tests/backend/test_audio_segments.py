from __future__ import annotations

from uuid import UUID

import numpy as np
import soundfile as sf

from backend.models.edit_operation import EditOperation
from backend.models.project import Project
from backend.models.transcript import Token, Transcript
from backend.services.audio_renderer import _crossfade_concatenate, render
from backend.services.audio_segment_manager import AudioSegmentManager
from backend.services.deletion_handler import handle_deletion
from backend.utils.storage import (
    load_project_metadata,
    project_original_wav_path,
    save_project_metadata,
)


def test_segment_manager_initializes_from_transcript() -> None:
    hello_id = UUID("11111111-1111-1111-1111-111111111111")
    comma_id = UUID("22222222-2222-2222-2222-222222222222")
    world_id = UUID("33333333-3333-3333-3333-333333333333")

    transcript = Transcript(
        tokens=[
            Token(id=hello_id, text="Hello", start=0.0, end=0.5, type="word"),
            Token(id=comma_id, text=",", start=0.5, end=0.5, type="punctuation"),
            Token(id=world_id, text="world", start=0.5, end=1.0, type="word"),
        ],
        language="en",
        duration=1.0,
    )

    project = Project(audio_path="/tmp/original.wav", metadata={})
    manager = AudioSegmentManager.ensure_initialized(
        project=project, transcript=transcript
    )
    segments = manager.get_all_segments()

    assert [seg.id for seg in segments] == [hello_id, world_id]
    assert segments[0].token_ids == [hello_id, comma_id]
    assert segments[0].file_path == "/tmp/original.wav"

    loaded = AudioSegmentManager.from_project(project).get_all_segments()
    assert [seg.id for seg in loaded] == [hello_id, world_id]


def test_segment_manager_inserts_gap_segments_and_removes_with_deletion() -> None:
    first_id = UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
    second_id = UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb")
    transcript = Transcript(
        tokens=[
            Token(id=first_id, text="First", start=0.0, end=0.25, type="word"),
            Token(id=second_id, text="Second", start=0.5, end=0.75, type="word"),
        ],
        language="en",
        duration=0.75,
    )
    project = Project(audio_path="/tmp/original.wav", metadata={})
    manager = AudioSegmentManager.ensure_initialized(
        project=project, transcript=transcript
    )
    segments = manager.get_all_segments()

    assert len(segments) == 3
    gap = next(seg for seg in segments if seg.start == 0.25 and seg.end == 0.5)
    assert gap.source == "original"
    assert gap.token_ids == [first_id, second_id]

    delete_op = EditOperation(
        type="delete",
        position=0,
        old_tokens=[first_id],
        new_text="",
    )
    handle_deletion(
        edit_operation=delete_op,
        project=project,
        original_transcript=transcript,
    )
    updated = {seg.start: seg for seg in AudioSegmentManager.from_project(project).get_all_segments()}
    assert updated[0.0].status == "removed"
    assert updated[0.25].status == "removed"
    assert updated[0.5].status == "kept"


def test_segment_marking_persists_to_metadata() -> None:
    hello_id = UUID("11111111-1111-1111-1111-111111111111")
    comma_id = UUID("22222222-2222-2222-2222-222222222222")
    world_id = UUID("33333333-3333-3333-3333-333333333333")

    transcript = Transcript(
        tokens=[
            Token(id=hello_id, text="Hello", start=0.0, end=0.5, type="word"),
            Token(id=comma_id, text=",", start=0.5, end=0.5, type="punctuation"),
            Token(id=world_id, text="world", start=0.5, end=1.0, type="word"),
        ],
        language="en",
        duration=1.0,
    )

    project = Project(audio_path="/tmp/original.wav", metadata={})
    manager = AudioSegmentManager.ensure_initialized(
        project=project, transcript=transcript
    )
    manager.mark_segment_removed(hello_id)
    manager.persist(project)

    reloaded = AudioSegmentManager.from_project(project)
    segments = {seg.id: seg for seg in reloaded.get_all_segments()}
    assert segments[hello_id].status == "removed"
    assert segments[world_id].status == "kept"

    reloaded.mark_segment_kept(hello_id)
    reloaded.persist(project)
    segments2 = {
        seg.id: seg
        for seg in AudioSegmentManager.from_project(project).get_all_segments()
    }
    assert segments2[hello_id].status == "kept"


def test_handle_deletion_marks_segments_removed() -> None:
    hello_id = UUID("11111111-1111-1111-1111-111111111111")
    comma_id = UUID("22222222-2222-2222-2222-222222222222")
    world_id = UUID("33333333-3333-3333-3333-333333333333")

    transcript = Transcript(
        tokens=[
            Token(id=hello_id, text="Hello", start=0.0, end=0.5, type="word"),
            Token(id=comma_id, text=",", start=0.5, end=0.5, type="punctuation"),
            Token(id=world_id, text="world", start=0.5, end=1.0, type="word"),
        ],
        language="en",
        duration=1.0,
    )

    project = Project(audio_path="/tmp/original.wav", metadata={})
    delete_op = EditOperation(
        type="delete",
        position=0,
        old_tokens=[hello_id, comma_id],
        new_text="",
    )
    affected = handle_deletion(
        edit_operation=delete_op,
        project=project,
        original_transcript=transcript,
    )
    assert affected == [hello_id]

    manager = AudioSegmentManager.from_project(project)
    segments = {seg.id: seg for seg in manager.get_all_segments()}
    assert segments[hello_id].status == "removed"
    assert segments[world_id].status == "kept"


def test_segments_persist_roundtrip(tmp_path: object, monkeypatch: object) -> None:
    monkeypatch.setenv("TEXTAUDIO_PROJECTS_DIR", str(tmp_path / "projects"))

    hello_id = UUID("11111111-1111-1111-1111-111111111111")
    comma_id = UUID("22222222-2222-2222-2222-222222222222")
    world_id = UUID("33333333-3333-3333-3333-333333333333")

    transcript = Transcript(
        tokens=[
            Token(id=hello_id, text="Hello", start=0.0, end=0.5, type="word"),
            Token(id=comma_id, text=",", start=0.5, end=0.5, type="punctuation"),
            Token(id=world_id, text="world", start=0.5, end=1.0, type="word"),
        ],
        language="en",
        duration=1.0,
    )

    project = Project(audio_path="original.wav", metadata={})
    manager = AudioSegmentManager.ensure_initialized(
        project=project, transcript=transcript
    )
    manager.mark_segment_removed(hello_id)
    manager.persist(project)
    save_project_metadata(project)

    loaded = load_project_metadata(project.id)
    loaded_manager = AudioSegmentManager.from_project(loaded)
    segments = {seg.id: seg for seg in loaded_manager.get_all_segments()}
    assert segments[hello_id].status == "removed"


def test_audio_renderer_renders_kept_segments(
    tmp_path: object, monkeypatch: object
) -> None:
    monkeypatch.setenv("TEXTAUDIO_PROJECTS_DIR", str(tmp_path / "projects"))

    project = Project(metadata={})
    audio_path = project_original_wav_path(project.id)
    project.audio_path = str(audio_path)

    sample_rate = 16_000
    original = np.linspace(0.0, 1.0, sample_rate, dtype=np.float32)
    sf.write(audio_path, original, sample_rate, subtype="PCM_16")

    seg1 = {
        "id": "11111111-1111-1111-1111-111111111111",
        "source": "original",
        "file_path": str(audio_path),
        "start": 0.0,
        "end": 0.5,
        "status": "kept",
        "token_ids": [],
    }
    seg2 = {
        "id": "22222222-2222-2222-2222-222222222222",
        "source": "original",
        "file_path": str(audio_path),
        "start": 0.5,
        "end": 1.0,
        "status": "removed",
        "token_ids": [],
    }
    project.metadata["segments"] = [seg1, seg2]
    save_project_metadata(project)

    rendered, rendered_rate = render(project.id)
    assert rendered_rate == sample_rate
    assert rendered.shape == (sample_rate // 2,)
    assert np.allclose(rendered, original[: sample_rate // 2], atol=1e-3)


def test_audio_renderer_concatenates_three_segments(
    tmp_path: object, monkeypatch: object
) -> None:
    monkeypatch.setenv("TEXTAUDIO_PROJECTS_DIR", str(tmp_path / "projects"))
    monkeypatch.setenv("TEXTAUDIO_CROSSFADE_MS", "10")

    project = Project(metadata={})
    audio_path = project_original_wav_path(project.id)
    project.audio_path = str(audio_path)

    sample_rate = 16_000
    original = np.linspace(0.0, 1.0, sample_rate, dtype=np.float32)
    sf.write(audio_path, original, sample_rate, subtype="PCM_16")

    project.metadata["segments"] = [
        {
            "id": "11111111-1111-1111-1111-111111111111",
            "source": "original",
            "file_path": str(audio_path),
            "start": 0.0,
            "end": 0.25,
            "status": "kept",
            "token_ids": [],
        },
        {
            "id": "22222222-2222-2222-2222-222222222222",
            "source": "original",
            "file_path": str(audio_path),
            "start": 0.25,
            "end": 0.5,
            "status": "kept",
            "token_ids": [],
        },
        {
            "id": "33333333-3333-3333-3333-333333333333",
            "source": "original",
            "file_path": str(audio_path),
            "start": 0.5,
            "end": 0.75,
            "status": "kept",
            "token_ids": [],
        },
    ]
    save_project_metadata(project)

    rendered, rendered_rate = render(project.id)
    assert rendered_rate == sample_rate
    expected = _crossfade_concatenate(
        [
            original[: int(sample_rate * 0.25)],
            original[int(sample_rate * 0.25) : int(sample_rate * 0.5)],
            original[int(sample_rate * 0.5) : int(sample_rate * 0.75)],
        ],
        sample_rate=sample_rate,
        crossfade_ms=10.0,
    )
    assert rendered.shape == expected.shape
    assert np.allclose(rendered, expected, atol=1e-3)


def test_audio_renderer_preserves_silent_gaps_between_segments(
    tmp_path: object, monkeypatch: object
) -> None:
    monkeypatch.setenv("TEXTAUDIO_PROJECTS_DIR", str(tmp_path / "projects"))
    monkeypatch.setenv("TEXTAUDIO_CROSSFADE_MS", "10")

    project = Project(metadata={})
    audio_path = project_original_wav_path(project.id)
    project.audio_path = str(audio_path)

    sample_rate = 16_000
    original = np.zeros((sample_rate,), dtype=np.float32)
    original[: int(sample_rate * 0.25)] = 0.6
    original[int(sample_rate * 0.5) : int(sample_rate * 0.75)] = 0.6
    sf.write(audio_path, original, sample_rate, subtype="PCM_16")

    project.metadata["segments"] = [
        {
            "id": "11111111-1111-1111-1111-111111111111",
            "source": "original",
            "file_path": str(audio_path),
            "start": 0.0,
            "end": 0.25,
            "status": "kept",
            "token_ids": [],
        },
        {
            "id": "22222222-2222-2222-2222-222222222222",
            "source": "original",
            "file_path": str(audio_path),
            "start": 0.5,
            "end": 0.75,
            "status": "kept",
            "token_ids": [],
        },
    ]
    save_project_metadata(project)

    rendered, rendered_rate = render(project.id)
    assert rendered_rate == sample_rate
    expected = _crossfade_concatenate(
        [
            original[: int(sample_rate * 0.25)],
            original[int(sample_rate * 0.25) : int(sample_rate * 0.5)],
            original[int(sample_rate * 0.5) : int(sample_rate * 0.75)],
        ],
        sample_rate=sample_rate,
        crossfade_ms=10.0,
    )
    assert rendered.shape == expected.shape
    assert np.allclose(rendered, expected, atol=1e-3)


def test_audio_renderer_does_not_include_gaps_around_removed_segments(
    tmp_path: object, monkeypatch: object
) -> None:
    monkeypatch.setenv("TEXTAUDIO_PROJECTS_DIR", str(tmp_path / "projects"))
    monkeypatch.setenv("TEXTAUDIO_CROSSFADE_MS", "10")

    project = Project(metadata={})
    audio_path = project_original_wav_path(project.id)
    project.audio_path = str(audio_path)

    sample_rate = 1_000
    original = np.zeros((sample_rate,), dtype=np.float32)
    original[: int(sample_rate * 0.25)] = 0.2
    original[int(sample_rate * 0.25) : int(sample_rate * 0.5)] = 0.9
    original[int(sample_rate * 0.5) : int(sample_rate * 0.75)] = 0.4
    sf.write(audio_path, original, sample_rate, subtype="PCM_16")

    project.metadata["segments"] = [
        {
            "id": "11111111-1111-1111-1111-111111111111",
            "source": "original",
            "file_path": str(audio_path),
            "start": 0.0,
            "end": 0.25,
            "status": "kept",
            "token_ids": [],
        },
        {
            "id": "22222222-2222-2222-2222-222222222222",
            "source": "original",
            "file_path": str(audio_path),
            "start": 0.25,
            "end": 0.5,
            "status": "removed",
            "token_ids": [],
        },
        {
            "id": "33333333-3333-3333-3333-333333333333",
            "source": "original",
            "file_path": str(audio_path),
            "start": 0.5,
            "end": 0.75,
            "status": "kept",
            "token_ids": [],
        },
    ]
    save_project_metadata(project)

    rendered, rendered_rate = render(project.id)
    assert rendered_rate == sample_rate
    expected = _crossfade_concatenate(
        [
            original[: int(sample_rate * 0.25)],
            original[int(sample_rate * 0.5) : int(sample_rate * 0.75)],
        ],
        sample_rate=sample_rate,
        crossfade_ms=10.0,
    )
    assert rendered.shape == expected.shape
    assert np.allclose(rendered, expected, atol=1e-3)


def test_audio_renderer_does_not_include_gap_after_removed_segment(
    tmp_path: object, monkeypatch: object
) -> None:
    monkeypatch.setenv("TEXTAUDIO_PROJECTS_DIR", str(tmp_path / "projects"))
    monkeypatch.setenv("TEXTAUDIO_CROSSFADE_MS", "10")

    project = Project(metadata={})
    audio_path = project_original_wav_path(project.id)
    project.audio_path = str(audio_path)

    sample_rate = 1_000
    original = np.zeros((sample_rate,), dtype=np.float32)
    original[: int(sample_rate * 0.25)] = 0.2
    original[int(sample_rate * 0.25) : int(sample_rate * 0.5)] = 0.9
    original[int(sample_rate * 0.5) : int(sample_rate * 0.6)] = 0.7
    original[int(sample_rate * 0.6) : int(sample_rate * 0.75)] = 0.4
    sf.write(audio_path, original, sample_rate, subtype="PCM_16")

    project.metadata["segments"] = [
        {
            "id": "11111111-1111-1111-1111-111111111111",
            "source": "original",
            "file_path": str(audio_path),
            "start": 0.0,
            "end": 0.25,
            "status": "kept",
            "token_ids": [],
        },
        {
            "id": "22222222-2222-2222-2222-222222222222",
            "source": "original",
            "file_path": str(audio_path),
            "start": 0.25,
            "end": 0.5,
            "status": "removed",
            "token_ids": [],
        },
        {
            "id": "33333333-3333-3333-3333-333333333333",
            "source": "original",
            "file_path": str(audio_path),
            "start": 0.6,
            "end": 0.75,
            "status": "kept",
            "token_ids": [],
        },
    ]
    save_project_metadata(project)

    rendered, rendered_rate = render(project.id)
    assert rendered_rate == sample_rate
    expected = _crossfade_concatenate(
        [
            original[: int(sample_rate * 0.25)],
            original[int(sample_rate * 0.6) : int(sample_rate * 0.75)],
        ],
        sample_rate=sample_rate,
        crossfade_ms=10.0,
    )
    assert rendered.shape == expected.shape
    assert np.allclose(rendered, expected, atol=1e-3)


def test_audio_renderer_trims_deleted_boundary_leakage(
    tmp_path: object, monkeypatch: object
) -> None:
    monkeypatch.setenv("TEXTAUDIO_PROJECTS_DIR", str(tmp_path / "projects"))
    monkeypatch.setenv("TEXTAUDIO_CROSSFADE_MS", "10")
    monkeypatch.setenv("TEXTAUDIO_REFINE_TIMESTAMPS", "1")
    monkeypatch.setenv("TEXTAUDIO_SNAP_WINDOW_MS", "200")
    monkeypatch.setenv("TEXTAUDIO_CUT_PADDING_MS", "50")

    project = Project(metadata={})
    audio_path = project_original_wav_path(project.id)
    project.audio_path = str(audio_path)

    sample_rate = 1_000
    original = np.zeros((sample_rate,), dtype=np.float32)
    original[: int(sample_rate * 0.2)] = 0.2
    original[int(sample_rate * 0.28) : int(sample_rate * 0.6)] = 0.9
    original[int(sample_rate * 0.65) : int(sample_rate * 0.8)] = 0.4
    sf.write(audio_path, original, sample_rate, subtype="PCM_16")

    project.metadata["segments"] = [
        {
            "id": "11111111-1111-1111-1111-111111111111",
            "source": "original",
            "file_path": str(audio_path),
            "start": 0.0,
            "end": 0.32,
            "status": "kept",
            "token_ids": [],
        },
        {
            "id": "22222222-2222-2222-2222-222222222222",
            "source": "original",
            "file_path": str(audio_path),
            "start": 0.32,
            "end": 0.6,
            "status": "removed",
            "token_ids": [],
        },
        {
            "id": "33333333-3333-3333-3333-333333333333",
            "source": "original",
            "file_path": str(audio_path),
            "start": 0.58,
            "end": 0.8,
            "status": "kept",
            "token_ids": [],
        },
    ]
    save_project_metadata(project)

    rendered, rendered_rate = render(project.id)
    assert rendered_rate == sample_rate
    assert rendered.size > 0
    assert float(np.max(np.abs(rendered))) < 0.7


def test_audio_renderer_clips_overlapping_segments(
    tmp_path: object, monkeypatch: object
) -> None:
    monkeypatch.setenv("TEXTAUDIO_PROJECTS_DIR", str(tmp_path / "projects"))
    monkeypatch.setenv("TEXTAUDIO_CROSSFADE_MS", "10")

    project = Project(metadata={})
    audio_path = project_original_wav_path(project.id)
    project.audio_path = str(audio_path)

    sample_rate = 16_000
    original = np.linspace(0.0, 1.0, sample_rate, dtype=np.float32)
    sf.write(audio_path, original, sample_rate, subtype="PCM_16")

    project.metadata["segments"] = [
        {
            "id": "11111111-1111-1111-1111-111111111111",
            "source": "original",
            "file_path": str(audio_path),
            "start": 0.0,
            "end": 0.6,
            "status": "kept",
            "token_ids": [],
        },
        {
            "id": "22222222-2222-2222-2222-222222222222",
            "source": "original",
            "file_path": str(audio_path),
            "start": 0.4,
            "end": 1.0,
            "status": "kept",
            "token_ids": [],
        },
    ]
    save_project_metadata(project)

    rendered, rendered_rate = render(project.id)
    assert rendered_rate == sample_rate
    expected = _crossfade_concatenate(
        [original[: int(sample_rate * 0.6)], original[int(sample_rate * 0.6) :]],
        sample_rate=sample_rate,
        crossfade_ms=10.0,
    )
    assert rendered.shape == expected.shape
    assert np.allclose(rendered, expected, atol=1e-3)


def test_crossfade_overlaps_audio() -> None:
    sample_rate = 1_000
    a = np.ones((100,), dtype=np.float32)
    b = np.zeros((100,), dtype=np.float32)

    out = _crossfade_concatenate([a, b], sample_rate=sample_rate, crossfade_ms=10.0)
    assert out.shape == (190,)
    assert out[0] == 1.0
    assert out[-1] == 0.0
    overlap = out[90:100]
    assert overlap.max() <= 1.0
    assert overlap.min() >= 0.0


def test_audio_renderer_handles_empty_segment_list(
    tmp_path: object, monkeypatch: object
) -> None:
    monkeypatch.setenv("TEXTAUDIO_PROJECTS_DIR", str(tmp_path / "projects"))

    project = Project(metadata={"segments": []})
    audio_path = project_original_wav_path(project.id)
    project.audio_path = str(audio_path)

    sample_rate = 16_000
    original = np.linspace(0.0, 1.0, sample_rate, dtype=np.float32)
    sf.write(audio_path, original, sample_rate, subtype="PCM_16")
    save_project_metadata(project)

    rendered, rendered_rate = render(project.id)
    assert rendered_rate == sample_rate
    assert rendered.shape == original.shape
    assert np.allclose(rendered, original, atol=1e-3)
