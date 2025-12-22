from __future__ import annotations

from uuid import UUID

from backend.models.project import Project
from backend.models.transcript import Token, Transcript
from backend.services.audio_segment_manager import AudioSegmentManager


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
