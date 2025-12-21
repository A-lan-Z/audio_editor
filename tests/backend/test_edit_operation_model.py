from __future__ import annotations

from uuid import UUID

import pytest

from backend.models.edit_operation import EditOperation
from backend.models.transcript import Token, Transcript


@pytest.fixture()
def sample_transcript() -> Transcript:
    hello_id = UUID("11111111-1111-1111-1111-111111111111")
    comma_id = UUID("22222222-2222-2222-2222-222222222222")
    world_id = UUID("33333333-3333-3333-3333-333333333333")

    return Transcript(
        tokens=[
            Token(id=hello_id, text="Hello", start=0.0, end=0.5, type="word"),
            Token(id=comma_id, text=",", start=0.5, end=0.5, type="punctuation"),
            Token(id=world_id, text="world", start=0.5, end=1.0, type="word"),
        ],
        language="en",
        duration=1.0,
    )


def test_edit_operation_json_round_trip() -> None:
    op = EditOperation(type="insert", position=0, old_tokens=[], new_text="Hi")
    payload = op.to_json()
    parsed = EditOperation.from_json(payload)

    assert parsed.id == op.id
    assert parsed.type == op.type
    assert parsed.position == op.position
    assert parsed.old_tokens == op.old_tokens
    assert parsed.new_text == op.new_text


def test_apply_delete_by_token_ids(sample_transcript: Transcript) -> None:
    old_ids = [sample_transcript.tokens[2].id]
    op = EditOperation(type="delete", position=7, old_tokens=old_ids, new_text="")
    updated = op.apply(sample_transcript)

    assert updated.to_text() == "Hello,"
    deleted = [token for token in updated.tokens if token.id in set(old_ids)]
    assert deleted
    assert all(token.status == "deleted" for token in deleted)


def test_apply_insert_by_position(sample_transcript: Transcript) -> None:
    # Insert before "world" in "Hello, world".
    op = EditOperation(type="insert", position=7, old_tokens=[], new_text="big")
    updated = op.apply(sample_transcript)

    assert updated.to_text() == "Hello, big world"
    inserted = [token for token in updated.tokens if token.text == "big"]
    assert inserted


def test_apply_replace_by_token_ids(sample_transcript: Transcript) -> None:
    old_ids = [sample_transcript.tokens[2].id]
    op = EditOperation(type="replace", position=7, old_tokens=old_ids, new_text="there")
    updated = op.apply(sample_transcript)

    assert updated.to_text() == "Hello, there"
    replaced = [token for token in updated.tokens if token.id in set(old_ids)]
    assert replaced
    assert all(token.status == "replaced" for token in replaced)
    inserted = [token for token in updated.tokens if token.text == "there"]
    assert inserted
    assert all(token.status == "inserted" for token in inserted)


def test_apply_sequence_delete_replace_preserves_tombstones(
    sample_transcript: Transcript,
) -> None:
    original = sample_transcript

    delete_ids = [original.tokens[0].id, original.tokens[1].id]
    delete_op = EditOperation(
        type="delete", position=0, old_tokens=delete_ids, new_text=""
    )
    after_delete = delete_op.apply(original)
    assert after_delete.to_text() == "world"
    assert {t.id for t in after_delete.tokens if t.status == "deleted"} >= set(
        delete_ids
    )

    replace_ids = [original.tokens[2].id]
    replace_op = EditOperation(
        type="replace", position=0, old_tokens=replace_ids, new_text="there"
    )
    after_replace = replace_op.apply(after_delete)
    assert after_replace.to_text() == "there"
    assert any(
        t.id in set(replace_ids) and t.status == "replaced"
        for t in after_replace.tokens
    )
    assert any(
        t.text == "there" and t.status == "inserted" for t in after_replace.tokens
    )
