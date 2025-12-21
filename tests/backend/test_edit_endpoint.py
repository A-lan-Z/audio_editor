import json
from pathlib import Path
from uuid import UUID

from backend.models.transcript import Token, Transcript
from tests.backend.test_api_validation import _request_json, run_server


def test_submit_edit_appends_to_log_and_updates_transcript(tmp_path: Path) -> None:
    projects_root = tmp_path / "projects"
    with run_server(env={"TEXTAUDIO_PROJECTS_DIR": str(projects_root)}) as base_url:
        status, body = _request_json(
            "POST", f"{base_url}/api/projects", {"metadata": {}}
        )
        assert status == 201
        project_id = body["project_id"]

        transcript_path = projects_root / project_id / "transcript.json"
        metadata_path = projects_root / project_id / "metadata.json"

        transcript = Transcript(
            tokens=[
                Token(
                    id=UUID("11111111-1111-1111-1111-111111111111"),
                    text="Hello",
                    start=0.0,
                    end=0.5,
                    type="word",
                ),
                Token(
                    id=UUID("22222222-2222-2222-2222-222222222222"),
                    text=",",
                    start=0.5,
                    end=0.5,
                    type="punctuation",
                ),
                Token(
                    id=UUID("33333333-3333-3333-3333-333333333333"),
                    text="world",
                    start=0.5,
                    end=1.0,
                    type="word",
                ),
            ],
            language="en",
            duration=1.0,
        )

        transcript_path.write_text(transcript.to_json(), encoding="utf-8")
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        metadata.setdefault("metadata", {})["transcript_path"] = str(transcript_path)
        metadata_path.write_text(
            json.dumps(metadata, indent=2, sort_keys=True), encoding="utf-8"
        )

        edit_payload = {
            "type": "replace",
            "position": 7,
            "old_tokens": ["33333333-3333-3333-3333-333333333333"],
            "new_text": "there",
        }
        status, updated = _request_json(
            "POST", f"{base_url}/api/projects/{project_id}/edit", edit_payload
        )
        assert status == 200
        updated_transcript = Transcript.model_validate(updated)
        assert updated_transcript.to_text() == "Hello, there"

        persisted = Transcript.from_json(transcript_path.read_text(encoding="utf-8"))
        assert persisted.to_text() == "Hello, there"

        stored_metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        assert stored_metadata["edits"]
        assert stored_metadata["edits"][-1]["type"] == "replace"
