import json
import os
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from collections.abc import Iterator
from contextlib import contextmanager


@contextmanager
def run_server(*, env: dict[str, str] | None = None) -> Iterator[str]:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]

    base_url = f"http://127.0.0.1:{port}"
    process_env = os.environ.copy()
    process_env["PYTHONUNBUFFERED"] = "1"
    if env:
        process_env.update(env)

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
        for _ in range(50):
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
        with urllib.request.urlopen(request, timeout=2) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8")
        parsed = json.loads(body) if body else {}
        return exc.code, parsed


def test_project_not_found_uses_standard_error_shape() -> None:
    with run_server() as base_url:
        status, body = _request_json(
            "GET", f"{base_url}/api/projects/00000000-0000-0000-0000-000000000000"
        )
        assert status == 404
        assert body["code"] == "PROJECT_NOT_FOUND"
        assert isinstance(body["error"], str)
        assert isinstance(body["detail"], str)


def test_request_too_large_uses_standard_error_shape() -> None:
    with run_server(env={"TEXTAUDIO_MAX_BODY_BYTES": "1"}) as base_url:
        status, body = _request_json(
            "POST", f"{base_url}/api/projects", {"metadata": {}}
        )
        assert status == 413
        assert body["code"] == "REQUEST_TOO_LARGE"
