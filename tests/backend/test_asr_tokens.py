from __future__ import annotations

import pytest

from backend.utils.asr_tokens import WordSpan, word_spans_to_tokens


def test_word_spans_to_tokens_splits_punctuation() -> None:
    spans = [
        WordSpan(text="hello,", start=0.0, end=0.5),
        WordSpan(text="world!", start=0.5, end=1.0),
    ]
    tokens = word_spans_to_tokens(spans)
    assert [t.text for t in tokens] == ["hello", ",", "world", "!"]
    assert [t.type for t in tokens] == ["word", "punctuation", "word", "punctuation"]


def test_word_spans_to_tokens_clamps_overlaps() -> None:
    spans = [
        WordSpan(text="a", start=0.0, end=1.0),
        WordSpan(text="b", start=0.5, end=1.5),
    ]
    tokens = word_spans_to_tokens(spans)
    assert len(tokens) == 2
    assert tokens[0].text == "a"
    assert tokens[1].text == "b"
    assert tokens[1].start >= tokens[0].end


def test_word_spans_to_tokens_rejects_invalid_sequence() -> None:
    spans = [
        WordSpan(text="a", start=0.0, end=1.0),
        WordSpan(text="b", start=-1.0, end=-0.5),
    ]
    with pytest.raises(ValueError, match="non-negative"):
        word_spans_to_tokens(spans)
