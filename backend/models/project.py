from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator

TokenType = Literal["word", "punctuation", "pause"]
EditType = Literal["insert", "delete", "replace", "pause_adjust"]


class Token(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID = Field(default_factory=uuid4)
    text: str = Field(min_length=1)
    start: float = Field(ge=0)
    end: float = Field(ge=0)
    type: TokenType

    @field_validator("end")
    @classmethod
    def validate_end_after_start(cls, value: float, info: Any) -> float:
        start = info.data.get("start")
        if start is not None and value < start:
            raise ValueError("end must be >= start")
        return value


class Transcript(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tokens: list[Token] = Field(default_factory=list)
    language: str = Field(min_length=2, default="en")
    duration: float = Field(ge=0, default=0)


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
