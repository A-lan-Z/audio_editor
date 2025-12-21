from __future__ import annotations

import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from backend.models.project import Token, Transcript
from backend.services.transcription_service import TranscriptionService
from backend.utils.errors import ValidationError


@dataclass(frozen=True, slots=True)
class WhisperConfig:
    model_name: str = "tiny"
    language: str = "en"
    device: str = "cpu"
    compute_type: str = "int8"
    download_root: str | None = None


class WhisperTranscriptionService(TranscriptionService):
    def __init__(self, *, config: WhisperConfig | None = None) -> None:
        self._config = config or WhisperConfig()
        self._model_lock = threading.Lock()
        self._model: Any | None = None

    def _get_model(self) -> Any:
        if self._model is not None:
            return self._model
        with self._model_lock:
            if self._model is not None:
                return self._model
            try:
                from faster_whisper import (  # type: ignore[import-not-found]  # noqa: I001
                    WhisperModel,
                )
            except Exception as exc:  # noqa: BLE001
                raise ValidationError(
                    "ASR dependency missing. Install 'faster-whisper' to enable "
                    "transcription."
                ) from exc

            self._model = WhisperModel(
                self._config.model_name,
                device=self._config.device,
                compute_type=self._config.compute_type,
                download_root=self._config.download_root,
            )
            return self._model

    def transcribe(self, audio_path: str) -> Transcript:
        tokens = self.get_word_timestamps(audio_path)
        duration = max((token.end for token in tokens), default=0.0)
        return Transcript(
            tokens=tokens, language=self._config.language, duration=duration
        )

    def get_word_timestamps(self, audio_path: str) -> list[Token]:
        path = Path(audio_path)
        if not path.exists():
            raise ValidationError(f"Audio file not found: {audio_path}")
        if path.is_dir():
            raise ValidationError(f"Expected audio file, got directory: {audio_path}")

        model = self._get_model()
        segments, info = model.transcribe(
            str(path),
            language=self._config.language,
            beam_size=1,
            vad_filter=False,
            word_timestamps=True,
            # Avoid skipping segments on non-speech audio during early MVP/testing.
            # Later phases can tighten this once real speech audio is the norm.
            no_speech_threshold=1.0,
        )

        tokens: list[Token] = []
        for segment in segments:
            words = segment.words or []
            for word in words:
                text = (word.word or "").strip()
                if not text:
                    continue
                tokens.append(
                    Token(
                        text=text,
                        start=float(word.start),
                        end=float(word.end),
                        type="word",
                    )
                )

        _ = info  # reserved for later language/duration plumbing
        return tokens
