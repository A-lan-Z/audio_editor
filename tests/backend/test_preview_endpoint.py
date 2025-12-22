import json
import urllib.error
import urllib.request
from pathlib import Path

import numpy as np
import soundfile as sf

from tests.backend.test_api_validation import _request_json, run_server


def _request_bytes(url: str) -> tuple[int, bytes, dict[str, str]]:
    request = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=3) as response:
            headers = dict(response.headers.items())
            return response.status, response.read(), headers
    except urllib.error.HTTPError as exc:
        headers = dict(exc.headers.items()) if exc.headers else {}
        return exc.code, exc.read(), headers


def test_preview_returns_wav(tmp_path: Path) -> None:
    projects_root = tmp_path / "projects"
    with run_server(env={"TEXTAUDIO_PROJECTS_DIR": str(projects_root)}) as base_url:
        status, body = _request_json(
            "POST", f"{base_url}/api/projects", {"metadata": {}}
        )
        assert status == 201
        project_id = body["project_id"]

        project_dir = projects_root / project_id
        audio_path = project_dir / "original.wav"
        metadata_path = project_dir / "metadata.json"

        sample_rate = 16_000
        audio = np.linspace(0.0, 1.0, sample_rate, dtype=np.float32)
        audio_path.parent.mkdir(parents=True, exist_ok=True)
        sf.write(audio_path, audio, sample_rate, subtype="PCM_16")

        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        metadata["audio_path"] = str(audio_path)
        metadata_path.write_text(
            json.dumps(metadata, indent=2, sort_keys=True), encoding="utf-8"
        )

        status, payload, headers = _request_bytes(
            f"{base_url}/api/projects/{project_id}/preview"
        )
        assert status == 200
        content_type = headers.get("content-type") or headers.get("Content-Type")
        assert content_type == "audio/wav"
        assert payload[:4] == b"RIFF"
