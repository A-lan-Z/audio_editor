from __future__ import annotations

import json
from pathlib import Path

from backend.models.transcript import Token, Transcript
from backend.services.project_manager import ProjectManager
from backend.utils.storage import (
    load_transcript,
    save_project_metadata,
    save_transcript,
)


def test_transcript_save_load_roundtrip(tmp_path: Path, monkeypatch: object) -> None:
    monkeypatch.setenv("TEXTAUDIO_PROJECTS_DIR", str(tmp_path / "projects"))

    manager = ProjectManager()
    project = manager.create_project(metadata={})
    save_project_metadata(project)

    transcript = Transcript(
        tokens=[
            Token(text="Hello", start=0.0, end=0.5, type="word"),
            Token(text="!", start=0.5, end=0.5, type="punctuation"),
        ],
        language="en",
        duration=0.5,
    )
    path = save_transcript(project.id, transcript)

    raw = path.read_text(encoding="utf-8")
    assert raw.startswith("{")
    assert "\n  " in raw  # pretty printed
    parsed = json.loads(raw)
    assert "tokens" in parsed

    reloaded = load_transcript(project.id)
    assert reloaded.to_text() == "Hello!"
