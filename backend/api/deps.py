from __future__ import annotations

from backend.services.project_manager import ProjectManager

_project_manager = ProjectManager()


def get_project_manager() -> ProjectManager:
    return _project_manager
