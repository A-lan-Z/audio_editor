from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class ProjectNotFound(Exception):
    project_id: UUID

    def __str__(self) -> str:
        return f"Project not found: {self.project_id}"


@dataclass(frozen=True, slots=True)
class InvalidAudioFormat(Exception):
    detail: str = "Invalid audio format"

    def __str__(self) -> str:
        return self.detail


@dataclass(frozen=True, slots=True)
class ValidationError(Exception):
    detail: str

    def __str__(self) -> str:
        return self.detail

