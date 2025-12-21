from __future__ import annotations

import re
from dataclasses import dataclass

from backend.models.transcript import Token

_PART_RE = re.compile(r"[A-Za-z0-9]+(?:['-][A-Za-z0-9]+)*|[^\\w\\s]+")


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

        for part in parts:
            if any(ch.isalnum() for ch in part):
                tokens.append(Token(text=part, start=start, end=end, type="word"))
                previous_end = end
            else:
                anchor = previous_end if tokens else start
                tokens.append(
                    Token(text=part, start=anchor, end=anchor, type="punctuation")
                )

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
