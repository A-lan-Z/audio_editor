import json
import os
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from shutil import which

import numpy as np
import pytest
import soundfile as sf


@contextmanager
def run_server(*, projects_dir: Path) -> Iterator[str]:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]

    base_url = f"http://127.0.0.1:{port}"
    process_env = os.environ.copy()
    process_env["PYTHONUNBUFFERED"] = "1"
    process_env["TEXTAUDIO_PROJECTS_DIR"] = str(projects_dir)

    process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "backend.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
            "--log-level",
            "warning",
        ],
        env=process_env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        for _ in range(80):
            try:
                urllib.request.urlopen(f"{base_url}/health", timeout=0.2).read()
                break
            except OSError:
                time.sleep(0.1)
        else:
            raise RuntimeError("Server did not start")
        yield base_url
    finally:
        process.terminate()
        try:
            process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            process.kill()


def _request_json(
    method: str, url: str, payload: object | None = None
) -> tuple[int, object]:
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=data,
        headers={"content-type": "application/json"},
        method=method,
    )
    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8")
        parsed = json.loads(body) if body else {}
        return exc.code, parsed


def _post_multipart_file(
    url: str, *, field_name: str, filename: str, content_type: str, data: bytes
) -> tuple[int, object]:
    boundary = "----textaudio-boundary"
    body = b"".join(
        [
            f"--{boundary}\r\n".encode(),
            (
                f'Content-Disposition: form-data; name="{field_name}"; '
                f'filename="{filename}"\r\n'
            ).encode(),
            f"Content-Type: {content_type}\r\n\r\n".encode(),
            data,
            b"\r\n",
            f"--{boundary}--\r\n".encode(),
        ]
    )

    request = urllib.request.Request(
        url,
        data=body,
        headers={
            "content-type": f"multipart/form-data; boundary={boundary}",
            "content-length": str(len(body)),
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body_text = exc.read().decode("utf-8")
        parsed = json.loads(body_text) if body_text else {}
        return exc.code, parsed


def _create_wav_bytes(
    *, seconds: float, sample_rate: int = 44100, channels: int = 2
) -> bytes:
    t = np.linspace(0, seconds, int(sample_rate * seconds), endpoint=False)
    tone = 0.1 * np.sin(2 * np.pi * 440 * t)
    if channels == 1:
        audio = tone.astype("float32")
    else:
        audio = np.stack([tone, tone], axis=1).astype("float32")

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
        tmp = Path(tmp_file.name)
    try:
        sf.write(tmp, audio, sample_rate, subtype="PCM_16")
        return tmp.read_bytes()
    finally:
        tmp.unlink(missing_ok=True)


def test_valid_wav_upload(tmp_path: Path) -> None:
    projects_dir = tmp_path / "projects"
    with run_server(projects_dir=projects_dir) as base_url:
        status, created = _request_json(
            "POST", f"{base_url}/api/projects", {"metadata": {}}
        )
        assert status == 201
        project_id = created["project_id"]

        wav = _create_wav_bytes(seconds=0.25, sample_rate=44100, channels=2)
        status, body = _post_multipart_file(
            f"{base_url}/api/projects/{project_id}/upload",
            field_name="file",
            filename="test.wav",
            content_type="audio/wav",
            data=wav,
        )
        assert status == 200
        assert body["status"] == "processed"
        assert body["filename"] == "original.wav"

        meta = json.loads(
            (projects_dir / project_id / "metadata.json").read_text("utf-8")
        )
        assert meta["audio_path"].endswith("original.wav")
        assert meta["metadata"]["sample_rate"] == 16000
        assert meta["metadata"]["channels"] == 1


def test_invalid_format_rejected(tmp_path: Path) -> None:
    projects_dir = tmp_path / "projects"
    with run_server(projects_dir=projects_dir) as base_url:
        _, created = _request_json("POST", f"{base_url}/api/projects", {"metadata": {}})
        project_id = created["project_id"]

        status, body = _post_multipart_file(
            f"{base_url}/api/projects/{project_id}/upload",
            field_name="file",
            filename="bad.txt",
            content_type="audio/wav",
            data=b"nope",
        )
        assert status == 400
        assert body["code"] == "INVALID_AUDIO_FORMAT"


def test_corrupt_wav_rejected(tmp_path: Path) -> None:
    projects_dir = tmp_path / "projects"
    with run_server(projects_dir=projects_dir) as base_url:
        _, created = _request_json("POST", f"{base_url}/api/projects", {"metadata": {}})
        project_id = created["project_id"]

        status, body = _post_multipart_file(
            f"{base_url}/api/projects/{project_id}/upload",
            field_name="file",
            filename="bad.wav",
            content_type="audio/wav",
            data=b"not-a-wav",
        )
        assert status == 400
        assert body["code"] == "INVALID_AUDIO_FORMAT"

        project_dir = projects_dir / project_id
        assert not (project_dir / "original.wav").exists()
        assert list((project_dir / "uploads").glob("*")) == []


def test_too_long_rejected(tmp_path: Path) -> None:
    projects_dir = tmp_path / "projects"
    with run_server(projects_dir=projects_dir) as base_url:
        _, created = _request_json("POST", f"{base_url}/api/projects", {"metadata": {}})
        project_id = created["project_id"]

        sample_rate = 16000
        seconds = 601
        audio = np.zeros(sample_rate * seconds, dtype="int16")
        tmp_wav = tmp_path / "long.wav"
        sf.write(tmp_wav, audio, sample_rate, subtype="PCM_16")

        status, body = _post_multipart_file(
            f"{base_url}/api/projects/{project_id}/upload",
            field_name="file",
            filename="long.wav",
            content_type="audio/wav",
            data=tmp_wav.read_bytes(),
        )
        assert status == 400
        assert body["code"] == "VALIDATION_ERROR"
        assert "Max 10 minutes" in body["detail"]

        meta = json.loads(
            (projects_dir / project_id / "metadata.json").read_text("utf-8")
        )
        assert meta.get("audio_path") is None


@pytest.mark.skipif(which("ffmpeg") is None, reason="ffmpeg not installed")
def test_valid_mp3_upload_and_conversion(tmp_path: Path) -> None:
    projects_dir = tmp_path / "projects"
    wav = tmp_path / "src.wav"
    mp3 = tmp_path / "src.mp3"

    audio = np.zeros(int(16000 * 0.25), dtype="float32")
    sf.write(wav, audio, 16000, subtype="PCM_16")
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav), str(mp3)],
        check=True,
    )

    with run_server(projects_dir=projects_dir) as base_url:
        _, created = _request_json("POST", f"{base_url}/api/projects", {"metadata": {}})
        project_id = created["project_id"]

        status, body = _post_multipart_file(
            f"{base_url}/api/projects/{project_id}/upload",
            field_name="file",
            filename="test.mp3",
            content_type="audio/mpeg",
            data=mp3.read_bytes(),
        )
        assert status == 200
        assert body["filename"] == "original.wav"

        meta = json.loads(
            (projects_dir / project_id / "metadata.json").read_text("utf-8")
        )
        assert meta["audio_path"].endswith("original.wav")
