from __future__ import annotations

from dataclasses import dataclass
from threading import Lock
from typing import Any
from uuid import UUID

from backend.models.project import Project


@dataclass(frozen=True, slots=True)
class ProjectNotFound(Exception):
    project_id: UUID

    def __str__(self) -> str:
        return f"Project not found: {self.project_id}"


class ProjectManager:
    def __init__(self) -> None:
        self._lock = Lock()
        self._projects: dict[UUID, Project] = {}

    def create_project(self, *, metadata: dict[str, Any] | None = None) -> Project:
        project = Project(metadata=metadata or {})
        with self._lock:
            self._projects[project.id] = project
        return project

    def get_project(self, project_id: UUID) -> Project:
        with self._lock:
            project = self._projects.get(project_id)
        if project is None:
            raise ProjectNotFound(project_id)
        return project

    def update_project(self, project: Project) -> Project:
        with self._lock:
            if project.id not in self._projects:
                raise ProjectNotFound(project.id)
            self._projects[project.id] = project
        return project

    def delete_project(self, project_id: UUID) -> None:
        with self._lock:
            if project_id not in self._projects:
                raise ProjectNotFound(project_id)
            del self._projects[project_id]

    def list_projects(self) -> list[Project]:
        with self._lock:
            return list(self._projects.values())
