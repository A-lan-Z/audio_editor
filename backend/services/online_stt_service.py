from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass

from backend.models.transcript import Token, Transcript
from backend.services.transcription_service import TranscriptionService
from backend.utils.asr_tokens import WordSpan, word_spans_to_tokens
from backend.utils.errors import ValidationError


@dataclass(frozen=True, slots=True)
class OnlineSttConfig:
    enabled: bool
    url: str | None
    auth_header: str | None

    @classmethod
    def from_env(cls) -> OnlineSttConfig:
        enabled = os.environ.get("TEXTAUDIO_STT_BACKEND", "local").strip().lower()
        is_online = enabled in {"online", "remote", "http"}
        url = os.environ.get("TEXTAUDIO_ONLINE_STT_URL")
        auth_header = os.environ.get("TEXTAUDIO_ONLINE_STT_AUTH_HEADER")
        return cls(enabled=is_online, url=url, auth_header=auth_header)


def _parse_word_spans(payload: object) -> list[WordSpan]:
    if not isinstance(payload, dict):
        raise ValidationError("Online STT response must be a JSON object")
    words = payload.get("words")
    if not isinstance(words, list):
        raise ValidationError("Online STT response must include 'words' list")

    spans: list[WordSpan] = []
    for item in words:
        if not isinstance(item, dict):
            continue
        text = item.get("text")
        start = item.get("start")
        end = item.get("end")
        if (
            not isinstance(text, str)
            or not isinstance(start, (int, float))
            or not isinstance(end, (int, float))
        ):
            continue
        cleaned = text.strip()
        if not cleaned:
            continue
        spans.append(WordSpan(text=cleaned, start=float(start), end=float(end)))

    if not spans:
        raise ValidationError("Online STT returned no words")
    return spans


class OnlineWordSpanTranscriptionService(TranscriptionService):
    """Optional STT backend via HTTP.

    This service is intentionally provider-agnostic. It POSTs the project audio
    bytes to `TEXTAUDIO_ONLINE_STT_URL` and expects a JSON response:

    {
      "words": [{"text": "Hello", "start": 0.0, "end": 0.5}, ...],
      "language": "en"  // optional
    }
    """

    def __init__(self, *, config: OnlineSttConfig | None = None) -> None:
        self._config = config or OnlineSttConfig.from_env()

    def _require_config(self) -> tuple[str, str | None]:
        if not self._config.enabled:
            raise ValidationError(
                "Online STT is disabled. Set TEXTAUDIO_STT_BACKEND=online to enable."
            )
        if not self._config.url:
            raise ValidationError(
                "Online STT is enabled but TEXTAUDIO_ONLINE_STT_URL is not set."
            )
        return self._config.url, self._config.auth_header

    def transcribe(self, audio_path: str) -> Transcript:
        tokens = self.get_word_timestamps(audio_path)
        duration = max((token.end for token in tokens), default=0.0)
        return Transcript(
            tokens=tokens,
            language=self._language_hint(),
            duration=duration,
        )

    def _language_hint(self) -> str:
        value = os.environ.get("TEXTAUDIO_ONLINE_STT_LANGUAGE")
        if isinstance(value, str) and value.strip():
            return value.strip()
        return "en"

    def get_word_timestamps(self, audio_path: str) -> list[Token]:
        url, auth_header = self._require_config()
        try:
            audio_bytes = open(audio_path, "rb").read()
        except OSError as exc:
            raise ValidationError(f"Audio file not found: {audio_path}") from exc

        request = urllib.request.Request(
            url,
            method="POST",
            data=audio_bytes,
            headers={
                "content-type": "audio/wav",
                **({"authorization": auth_header} if auth_header else {}),
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                raw = response.read()
        except urllib.error.HTTPError as exc:
            raise ValidationError(f"Online STT failed ({exc.code})") from exc
        except urllib.error.URLError as exc:
            raise ValidationError("Online STT request failed") from exc

        try:
            payload = json.loads(raw.decode("utf-8"))
        except Exception as exc:  # noqa: BLE001
            raise ValidationError("Online STT returned invalid JSON") from exc

        spans = _parse_word_spans(payload)
        try:
            return word_spans_to_tokens(spans)
        except ValueError as exc:
            raise ValidationError(f"Invalid online STT timestamps: {exc}") from exc
