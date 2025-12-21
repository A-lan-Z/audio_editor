from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator

TokenType = Literal["word", "punctuation", "pause"]


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
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @field_validator("tokens")
    @classmethod
    def validate_token_timestamps(cls, value: list[Token]) -> list[Token]:
        previous_end = 0.0
        for token in value:
            if token.start < previous_end:
                raise ValueError("token timestamps must be non-overlapping")
            previous_end = token.end
        return value

    def to_json(self) -> str:
        return self.model_dump_json(indent=2)

    @classmethod
    def from_json(cls, data: str) -> Transcript:
        return cls.model_validate_json(data)

    def to_text(self) -> str:
        parts: list[str] = []
        for token in self.tokens:
            if token.type == "punctuation":
                if not parts:
                    parts.append(token.text)
                else:
                    parts[-1] = f"{parts[-1]}{token.text}"
                continue

            if not parts:
                parts.append(token.text)
            else:
                parts.append(f" {token.text}")

        return "".join(parts)
