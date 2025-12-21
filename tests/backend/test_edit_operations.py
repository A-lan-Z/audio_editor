from __future__ import annotations

from uuid import UUID

import pytest

from backend.models.edit_operation import EditOperation
from backend.models.transcript import Token, Transcript


@pytest.fixture()
def base_transcript() -> Transcript:
    return Transcript(
        tokens=[
            Token(
                id=UUID("11111111-1111-1111-1111-111111111111"),
                text="one",
                start=0.0,
                end=0.2,
                type="word",
            ),
            Token(
                id=UUID("22222222-2222-2222-2222-222222222222"),
                text=",",
                start=0.2,
                end=0.2,
                type="punctuation",
            ),
            Token(
                id=UUID("33333333-3333-3333-3333-333333333333"),
                text="two",
                start=0.2,
                end=0.4,
                type="word",
            ),
            Token(
                id=UUID("44444444-4444-4444-4444-444444444444"),
                text="three",
                start=0.4,
                end=0.6,
                type="word",
            ),
        ],
        language="en",
        duration=0.6,
    )


def _apply_ops(
    original: Transcript, ops: list[EditOperation], cursor: int
) -> Transcript:
    current = original
    for op in ops[:cursor]:
        current = op.apply(current)
    return current


def test_delete_single_word_marks_token(base_transcript: Transcript) -> None:
    delete_ids = [UUID("33333333-3333-3333-3333-333333333333")]
    op = EditOperation(type="delete", position=0, old_tokens=delete_ids, new_text="")
    updated = op.apply(base_transcript)

    assert updated.to_text() == "one, three"
    target = [t for t in updated.tokens if t.id in set(delete_ids)]
    assert target
    assert all(t.status == "deleted" for t in target)


def test_delete_multiple_words_marks_tokens(base_transcript: Transcript) -> None:
    delete_ids = [
        UUID("11111111-1111-1111-1111-111111111111"),
        UUID("22222222-2222-2222-2222-222222222222"),
        UUID("33333333-3333-3333-3333-333333333333"),
    ]
    op = EditOperation(type="delete", position=0, old_tokens=delete_ids, new_text="")
    updated = op.apply(base_transcript)

    assert updated.to_text() == "three"
    assert all(t.status == "deleted" for t in updated.tokens if t.id in set(delete_ids))


def test_insert_text_at_position(base_transcript: Transcript) -> None:
    # Insert at the beginning of the active text.
    op = EditOperation(type="insert", position=0, old_tokens=[], new_text="zero")
    updated = op.apply(base_transcript)
    assert updated.to_text().startswith("zero")
    assert any(t.text == "zero" and t.status == "inserted" for t in updated.tokens)


def test_replace_word_marks_old_and_inserts_new(base_transcript: Transcript) -> None:
    replace_ids = [UUID("33333333-3333-3333-3333-333333333333")]
    op = EditOperation(
        type="replace", position=0, old_tokens=replace_ids, new_text="TWO"
    )
    updated = op.apply(base_transcript)

    assert updated.to_text() == "one, TWO three"
    assert any(
        t.id in set(replace_ids) and t.status == "replaced" for t in updated.tokens
    )
    assert any(t.text == "TWO" and t.status == "inserted" for t in updated.tokens)


def test_undo_redo_by_rebuilding_cursor(base_transcript: Transcript) -> None:
    replace_ids = [UUID("33333333-3333-3333-3333-333333333333")]
    ops = [
        EditOperation(
            type="replace", position=0, old_tokens=replace_ids, new_text="TWO"
        ),
        EditOperation(type="insert", position=0, old_tokens=[], new_text="zero"),
    ]

    applied = _apply_ops(base_transcript, ops, cursor=2)
    assert "zero" in applied.to_text()

    undone = _apply_ops(base_transcript, ops, cursor=1)
    assert undone.to_text() == "one, TWO three"

    redone = _apply_ops(base_transcript, ops, cursor=2)
    assert redone.to_text() == applied.to_text()


def test_complex_sequence_preserves_mapping_integrity(
    base_transcript: Transcript,
) -> None:
    delete_ids = [UUID("44444444-4444-4444-4444-444444444444")]
    replace_ids = [UUID("33333333-3333-3333-3333-333333333333")]
    ops = [
        EditOperation(type="delete", position=0, old_tokens=delete_ids, new_text=""),
        EditOperation(
            type="replace", position=0, old_tokens=replace_ids, new_text="TWO"
        ),
        EditOperation(type="insert", position=0, old_tokens=[], new_text="zero"),
    ]

    updated = _apply_ops(base_transcript, ops, cursor=3)
    assert updated.to_text().startswith("zero one, TWO")
    assert any(
        t.id in set(delete_ids) and t.status == "deleted" for t in updated.tokens
    )
    assert any(
        t.id in set(replace_ids) and t.status == "replaced" for t in updated.tokens
    )
    assert any(t.text == "zero" and t.status == "inserted" for t in updated.tokens)
