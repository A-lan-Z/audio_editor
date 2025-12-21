from __future__ import annotations

from abc import ABC, abstractmethod

from backend.models.project import Token, Transcript


class TranscriptionService(ABC):
    """Abstract interface for ASR implementations.

    Concrete implementations should be swappable so the rest of the backend
    does not depend on a specific ASR library or model choice.
    """

    @abstractmethod
    def transcribe(self, audio_path: str) -> Transcript:
        """Transcribe an audio file and return a structured transcript."""

    @abstractmethod
    def get_word_timestamps(self, audio_path: str) -> list[Token]:
        """Return word/token timestamps extracted from an audio file."""
