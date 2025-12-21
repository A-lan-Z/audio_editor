from __future__ import annotations

import threading
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Literal
from uuid import UUID, uuid4

from backend.models.transcript import Transcript
from backend.services.transcription_service import TranscriptionService

TranscriptionStatus = Literal["queued", "processing", "completed", "failed"]


@dataclass(frozen=True, slots=True)
class TranscriptionTask:
    task_id: UUID
    project_id: UUID


@dataclass(slots=True)
class TranscriptionTaskState:
    status: TranscriptionStatus
    progress: float | None = None
    error: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def touch(self) -> None:
        self.updated_at = datetime.now(UTC)


class TranscriptionJobManager:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._states: dict[UUID, TranscriptionTaskState] = {}
        self._tasks_by_project: dict[UUID, UUID] = {}

    def start(
        self,
        *,
        project_id: UUID,
        audio_path: str,
        transcription_service: TranscriptionService,
        on_completed: Callable[[Transcript], None],
        on_failed: Callable[[str], None],
    ) -> TranscriptionTask:
        task_id = uuid4()
        task = TranscriptionTask(task_id=task_id, project_id=project_id)
        state = TranscriptionTaskState(status="queued")

        with self._lock:
            self._states[task_id] = state
            self._tasks_by_project[project_id] = task_id

        thread = threading.Thread(
            target=self._run_task,
            name=f"transcribe-{project_id}",
            daemon=True,
            kwargs={
                "task_id": task_id,
                "audio_path": audio_path,
                "transcription_service": transcription_service,
                "on_completed": on_completed,
                "on_failed": on_failed,
            },
        )
        thread.start()
        return task

    def get_state(self, project_id: UUID) -> tuple[UUID, TranscriptionTaskState] | None:
        with self._lock:
            task_id = self._tasks_by_project.get(project_id)
            if task_id is None:
                return None
            state = self._states.get(task_id)
            if state is None:
                return None
            return task_id, state

    def _set_state(
        self,
        *,
        task_id: UUID,
        status: TranscriptionStatus,
        progress: float | None = None,
        error: str | None = None,
    ) -> None:
        with self._lock:
            state = self._states.get(task_id)
            if state is None:
                return
            state.status = status
            state.progress = progress
            state.error = error
            state.touch()

    def _run_task(
        self,
        *,
        task_id: UUID,
        audio_path: str,
        transcription_service: TranscriptionService,
        on_completed: Callable[[Transcript], None],
        on_failed: Callable[[str], None],
    ) -> None:
        self._set_state(task_id=task_id, status="processing")
        try:
            transcript = transcription_service.transcribe(audio_path)
            on_completed(transcript)
            self._set_state(task_id=task_id, status="completed", progress=1.0)
        except Exception as exc:  # noqa: BLE001
            message = str(exc) or "Transcription failed"
            on_failed(message)
            self._set_state(task_id=task_id, status="failed", error=message)
