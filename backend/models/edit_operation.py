from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field

from backend.models.transcript import Token, Transcript
from backend.utils.asr_tokens import WordSpan, word_spans_to_tokens

EditType = Literal["insert", "delete", "replace", "pause_adjust"]


def _token_char_spans(tokens: list[Token]) -> list[tuple[int, int]]:
    offset = 0
    spans: list[tuple[int, int]] = []
    for token in tokens:
        if token.type == "punctuation":
            start = offset
            end = offset + len(token.text)
            spans.append((start, end))
            offset = end
            continue

        if offset > 0:
            offset += 1
        start = offset
        end = offset + len(token.text)
        spans.append((start, end))
        offset = end

    return spans


def _insertion_index_for_position(tokens: list[Token], position: int) -> int:
    spans = _token_char_spans(tokens)
    if not spans:
        return 0

    for index, (start, end) in enumerate(spans):
        if position < start:
            return index
        if start <= position < end:
            midpoint = start + max(end - start, 1) // 2
            return index if position < midpoint else index + 1

    return len(tokens)


def _deletion_index_for_position(tokens: list[Token], position: int) -> int | None:
    spans = _token_char_spans(tokens)
    if not spans:
        return None

    for index, (start, end) in enumerate(spans):
        if start <= position < end:
            return index
        if position < start:
            return index - 1 if index > 0 else None

    return len(tokens) - 1


def _anchor_time(tokens: list[Token], insertion_index: int) -> float:
    if insertion_index <= 0:
        return 0.0
    return float(tokens[insertion_index - 1].end)


class EditOperation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID = Field(default_factory=uuid4)
    type: EditType
    position: int = Field(ge=0)
    old_tokens: list[UUID] = Field(default_factory=list)
    new_text: str = Field(default="")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))

    def to_json(self) -> str:
        return self.model_dump_json(indent=2)

    @classmethod
    def from_json(cls, data: str) -> EditOperation:
        return cls.model_validate_json(data)

    def apply(self, transcript: Transcript) -> Transcript:
        if self.type == "pause_adjust":
            raise ValueError("pause_adjust operations are not supported yet")

        tokens = list(transcript.tokens)

        if self.type == "delete":
            if self.old_tokens:
                remove = set(self.old_tokens)
                tokens = [token for token in tokens if token.id not in remove]
            else:
                index = _deletion_index_for_position(tokens, self.position)
                if index is not None and 0 <= index < len(tokens):
                    tokens = [token for i, token in enumerate(tokens) if i != index]

            return Transcript(
                tokens=tokens,
                language=transcript.language,
                duration=transcript.duration,
                created_at=transcript.created_at,
            )

        if self.type == "replace":
            insertion_index: int
            if self.old_tokens:
                remove = set(self.old_tokens)
                indices = [i for i, token in enumerate(tokens) if token.id in remove]
                insertion_index = (
                    min(indices)
                    if indices
                    else _insertion_index_for_position(tokens, self.position)
                )
                tokens = [token for token in tokens if token.id not in remove]
            else:
                insertion_index = _insertion_index_for_position(tokens, self.position)

            anchor = _anchor_time(tokens, insertion_index)
            inserted = word_spans_to_tokens(
                [WordSpan(text=self.new_text, start=anchor, end=anchor)]
            )
            tokens = [*tokens[:insertion_index], *inserted, *tokens[insertion_index:]]

            return Transcript(
                tokens=tokens,
                language=transcript.language,
                duration=transcript.duration,
                created_at=transcript.created_at,
            )

        if self.type == "insert":
            insertion_index = _insertion_index_for_position(tokens, self.position)
            anchor = _anchor_time(tokens, insertion_index)
            inserted = word_spans_to_tokens(
                [WordSpan(text=self.new_text, start=anchor, end=anchor)]
            )
            tokens = [*tokens[:insertion_index], *inserted, *tokens[insertion_index:]]

            return Transcript(
                tokens=tokens,
                language=transcript.language,
                duration=transcript.duration,
                created_at=transcript.created_at,
            )

        raise ValueError(f"Unknown edit operation type: {self.type}")
