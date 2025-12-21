from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, ConfigDict, Field

from backend.api.deps import get_project_manager
from backend.models.project import Project
from backend.services.project_manager import ProjectManager
from backend.utils.errors import ProjectNotFound
from backend.utils.storage import (
    StorageError,
    load_project_metadata,
    save_project_metadata,
)

router = APIRouter(prefix="/api/projects", tags=["projects"])


class CreateProjectRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    metadata: dict[str, Any] = Field(default_factory=dict)


class ProjectMetadataResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    project_id: UUID
    created_at: datetime
    updated_at: datetime
    audio_path: str | None
    metadata: dict[str, Any]


def _to_project_metadata_response(project: Project) -> ProjectMetadataResponse:
    return ProjectMetadataResponse(
        project_id=project.id,
        created_at=project.created_at,
        updated_at=project.updated_at,
        audio_path=project.audio_path,
        metadata=project.metadata,
    )


@router.post(
    "", response_model=ProjectMetadataResponse, status_code=status.HTTP_201_CREATED
)
def create_project(
    request: CreateProjectRequest,
    project_manager: ProjectManager = Depends(get_project_manager),
) -> ProjectMetadataResponse:
    project = project_manager.create_project(metadata=request.metadata)
    save_project_metadata(project)
    return _to_project_metadata_response(project)


@router.get("/{project_id}", response_model=ProjectMetadataResponse)
def get_project(project_id: UUID) -> ProjectMetadataResponse:
    try:
        project = load_project_metadata(project_id)
    except StorageError as exc:
        raise ProjectNotFound(project_id) from exc
    if project.id != project_id:
        raise RuntimeError("Invalid project metadata")
    return _to_project_metadata_response(project)


@router.get("", response_model=list[ProjectMetadataResponse])
def list_projects(
    project_manager: ProjectManager = Depends(get_project_manager),
) -> list[ProjectMetadataResponse]:
    projects: list[ProjectMetadataResponse] = []
    for project in project_manager.list_projects():
        projects.append(_to_project_metadata_response(project))
    return projects
