from uuid import UUID

import pytest

from backend.models.project import Project
from backend.utils.storage import (
    StorageError,
    load_audio_file,
    load_project_metadata,
    save_audio_file,
    save_project_metadata,
)


def test_save_and_load_project_metadata(tmp_path: object, monkeypatch: object) -> None:
    monkeypatch.setenv("TEXTAUDIO_PROJECTS_DIR", str(tmp_path / "projects"))
    project = Project(metadata={"name": "demo"})

    save_project_metadata(project)
    loaded = load_project_metadata(project.id)

    assert loaded.id == project.id
    assert loaded.metadata["name"] == "demo"
    assert (tmp_path / "projects" / str(project.id) / "voice_profile").is_dir()
    assert (tmp_path / "projects" / str(project.id) / "transcript.json").is_file()


def test_audio_save_and_load(tmp_path: object, monkeypatch: object) -> None:
    monkeypatch.setenv("TEXTAUDIO_PROJECTS_DIR", str(tmp_path / "projects"))
    project_id = UUID("00000000-0000-0000-0000-000000000000")

    payload = b"RIFF....WAVEfmt "  # minimal placeholder bytes
    save_audio_file(project_id, payload)

    loaded = load_audio_file(project_id)
    assert loaded == payload


def test_load_metadata_missing_raises(tmp_path: object, monkeypatch: object) -> None:
    monkeypatch.setenv("TEXTAUDIO_PROJECTS_DIR", str(tmp_path / "projects"))
    project_id = UUID("00000000-0000-0000-0000-000000000000")

    with pytest.raises(StorageError):
        load_project_metadata(project_id)


def test_load_audio_missing_raises(tmp_path: object, monkeypatch: object) -> None:
    monkeypatch.setenv("TEXTAUDIO_PROJECTS_DIR", str(tmp_path / "projects"))
    project_id = UUID("00000000-0000-0000-0000-000000000000")

    with pytest.raises(StorageError):
        load_audio_file(project_id)
