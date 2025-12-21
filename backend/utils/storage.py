from __future__ import annotations

import json
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from uuid import UUID

from backend.models.project import Project
from backend.models.transcript import Transcript

DEFAULT_PROJECTS_ROOT = Path("data/projects")


@dataclass(frozen=True, slots=True)
class StorageError(Exception):
    message: str

    def __str__(self) -> str:
        return self.message


def _projects_root() -> Path:
    configured = os.environ.get("TEXTAUDIO_PROJECTS_DIR")
    if configured:
        return Path(configured)
    return DEFAULT_PROJECTS_ROOT


def _resolve_projects_root() -> Path:
    try:
        return _projects_root().resolve()
    except OSError as exc:
        raise StorageError(f"Failed to resolve projects directory: {exc}") from exc


def _project_dir(project_id: UUID) -> Path:
    root = _resolve_projects_root()
    project_dir = (root / str(project_id)).resolve()
    if not project_dir.is_relative_to(root):
        raise StorageError("Invalid project path")
    return project_dir


def _ensure_project_dir(project_id: UUID) -> Path:
    project_dir = _project_dir(project_id)
    try:
        project_dir.mkdir(parents=True, exist_ok=True)
        (project_dir / "voice_profile").mkdir(parents=True, exist_ok=True)
        (project_dir / "uploads").mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise StorageError(f"Failed to create project directory: {exc}") from exc
    return project_dir


def project_uploads_dir(project_id: UUID) -> Path:
    project_dir = _ensure_project_dir(project_id)
    return project_dir / "uploads"


def project_original_wav_path(project_id: UUID) -> Path:
    project_dir = _ensure_project_dir(project_id)
    return project_dir / "original.wav"


def project_transcript_path(project_id: UUID) -> Path:
    project_dir = _ensure_project_dir(project_id)
    return project_dir / "transcript.json"


def _atomic_write_bytes(path: Path, data: bytes) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(
            mode="wb", dir=path.parent, delete=False
        ) as tmp_file:
            tmp_file.write(data)
            tmp_file.flush()
            os.fsync(tmp_file.fileno())
            tmp_path = Path(tmp_file.name)
        tmp_path.replace(path)
    except OSError as exc:
        raise StorageError(f"Failed to write file: {path}") from exc


def _atomic_write_json(path: Path, obj: Any) -> None:
    try:
        data = json.dumps(obj, indent=2, sort_keys=True).encode("utf-8")
    except TypeError as exc:
        raise StorageError(f"Failed to serialize JSON for: {path}") from exc
    _atomic_write_bytes(path, data)


def save_audio_file(project_id: UUID, audio_bytes: bytes) -> Path:
    project_dir = _ensure_project_dir(project_id)
    audio_path = project_dir / "original.wav"
    _atomic_write_bytes(audio_path, audio_bytes)
    return audio_path


def load_audio_file(project_id: UUID) -> bytes:
    audio_path = _project_dir(project_id) / "original.wav"
    try:
        return audio_path.read_bytes()
    except FileNotFoundError as exc:
        raise StorageError("Audio file not found for project") from exc
    except OSError as exc:
        raise StorageError(f"Failed to read audio file: {exc}") from exc


def save_project_metadata(project: Project) -> Path:
    project_dir = _ensure_project_dir(project.id)
    metadata_path = project_dir / "metadata.json"
    _atomic_write_json(
        metadata_path, project.model_dump(mode="json", exclude_none=True)
    )
    return metadata_path


def load_project_metadata(project_id: UUID) -> Project:
    metadata_path = _project_dir(project_id) / "metadata.json"
    try:
        raw = json.loads(metadata_path.read_text(encoding="utf-8"))
        return Project.model_validate(raw)
    except FileNotFoundError as exc:
        raise StorageError("Project metadata not found") from exc
    except json.JSONDecodeError as exc:
        raise StorageError("Project metadata is invalid JSON") from exc
    except OSError as exc:
        raise StorageError(f"Failed to read project metadata: {exc}") from exc


def save_transcript(project_id: UUID, transcript: Transcript) -> Path:
    transcript_path = project_transcript_path(project_id)
    try:
        data = transcript.to_json().encode("utf-8")
    except Exception as exc:  # noqa: BLE001
        raise StorageError("Failed to serialize transcript JSON") from exc
    _atomic_write_bytes(transcript_path, data)
    return transcript_path


def load_transcript(project_id: UUID) -> Transcript:
    transcript_path = project_transcript_path(project_id)
    try:
        raw = transcript_path.read_text(encoding="utf-8")
        return Transcript.from_json(raw)
    except FileNotFoundError as exc:
        raise StorageError("Transcript not found for project") from exc
    except Exception as exc:  # noqa: BLE001
        raise StorageError("Transcript JSON is invalid") from exc
