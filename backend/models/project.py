from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field

from backend.models.transcript import Transcript

EditType = Literal["insert", "delete", "replace", "pause_adjust"]


class EditOperation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: EditType
    position: int = Field(ge=0)
    old_tokens: list[UUID] = Field(default_factory=list)
    new_text: str = Field(default="")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


class Project(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    audio_path: str | None = Field(default=None)
    metadata: dict[str, Any] = Field(default_factory=dict)
    transcript: Transcript | None = Field(default=None)
    edits: list[EditOperation] = Field(default_factory=list)
