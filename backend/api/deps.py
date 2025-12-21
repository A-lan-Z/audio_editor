from __future__ import annotations

from backend.services.project_manager import ProjectManager
from backend.services.transcription_service import TranscriptionService
from backend.services.whisper_service import WhisperTranscriptionService

_project_manager = ProjectManager()
_transcription_service: TranscriptionService = WhisperTranscriptionService()


def get_project_manager() -> ProjectManager:
    return _project_manager


def get_transcription_service() -> TranscriptionService:
    return _transcription_service
