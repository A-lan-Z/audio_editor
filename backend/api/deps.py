from __future__ import annotations

from backend.services.online_stt_service import (
    OnlineSttConfig,
    OnlineWordSpanTranscriptionService,
)
from backend.services.project_manager import ProjectManager
from backend.services.transcription_jobs import TranscriptionJobManager
from backend.services.transcription_service import TranscriptionService
from backend.services.whisper_service import WhisperTranscriptionService

_project_manager = ProjectManager()
_transcription_service: TranscriptionService
_transcription_jobs = TranscriptionJobManager()

_online_config = OnlineSttConfig.from_env()
_transcription_service = (
    OnlineWordSpanTranscriptionService(config=_online_config)
    if _online_config.enabled
    else WhisperTranscriptionService()
)


def get_project_manager() -> ProjectManager:
    return _project_manager


def get_transcription_service() -> TranscriptionService:
    return _transcription_service


def get_transcription_jobs() -> TranscriptionJobManager:
    return _transcription_jobs
