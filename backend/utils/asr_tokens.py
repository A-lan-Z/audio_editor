from __future__ import annotations

import re
from dataclasses import dataclass

from backend.models.transcript import Token

_PART_RE = re.compile(r"[A-Za-z0-9]+(?:['-][A-Za-z0-9]+)*|[^\w\s]+")


@dataclass(frozen=True, slots=True)
class WordSpan:
    text: str
    start: float
    end: float


def word_spans_to_tokens(spans: list[WordSpan]) -> list[Token]:
    """Convert ASR word spans into Token objects.

    Punctuation is emitted as separate `Token(type='punctuation')` tokens, using
    the nearest word boundary as its timestamp anchor.
    """

    tokens: list[Token] = []
    previous_end = 0.0

    for span in spans:
        raw = (span.text or "").strip()
        if not raw:
            continue

        start = float(span.start)
        end = float(span.end)
        if start < 0 or end < 0:
            raise ValueError("Token timestamps must be non-negative")

        if start < previous_end:
            start = previous_end
        if end < start:
            end = start

        parts = _PART_RE.findall(raw)
        if not parts:
            continue

        word_parts = [part for part in parts if any(ch.isalnum() for ch in part)]
        if not word_parts:
            anchor = previous_end if tokens else start
            for part in parts:
                tokens.append(
                    Token(text=part, start=anchor, end=anchor, type="punctuation")
                )
            continue

        span_duration = end - start
        total_weight = sum(len(part) for part in word_parts)
        cursor = start
        remaining_words = len(word_parts)

        for part in parts:
            if not any(ch.isalnum() for ch in part):
                anchor = previous_end if tokens else cursor
                tokens.append(
                    Token(text=part, start=anchor, end=anchor, type="punctuation")
                )
                continue

            remaining_words -= 1
            if remaining_words <= 0:
                part_start = cursor
                part_end = end
            elif span_duration <= 0 or total_weight <= 0:
                part_start = cursor
                part_end = cursor
            else:
                weight = len(part)
                part_duration = span_duration * (weight / float(total_weight))
                part_start = cursor
                part_end = min(end, cursor + part_duration)
                total_weight -= weight

            tokens.append(Token(text=part, start=part_start, end=part_end, type="word"))
            cursor = part_end
            previous_end = part_end

    return _validate_monotonic(tokens)


def _validate_monotonic(tokens: list[Token]) -> list[Token]:
    previous_end = 0.0
    for token in tokens:
        if token.start < previous_end:
            raise ValueError("Token timestamps overlap")
        if token.end < token.start:
            raise ValueError("Token end before start")
        previous_end = token.end
    return tokens
