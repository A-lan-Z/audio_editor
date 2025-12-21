from uuid import UUID

import pytest

from backend.services.project_manager import ProjectManager
from backend.utils.errors import ProjectNotFound


def test_create_and_get_project() -> None:
    manager = ProjectManager()
    project = manager.create_project(metadata={"name": "demo"})

    loaded = manager.get_project(project.id)
    assert loaded.id == project.id
    assert loaded.metadata["name"] == "demo"


def test_get_project_not_found() -> None:
    manager = ProjectManager()
    missing_id = UUID("00000000-0000-0000-0000-000000000000")

    with pytest.raises(ProjectNotFound):
        manager.get_project(missing_id)


def test_update_project() -> None:
    manager = ProjectManager()
    project = manager.create_project(metadata={"name": "before"})

    updated = project.model_copy(update={"metadata": {"name": "after"}})
    manager.update_project(updated)

    loaded = manager.get_project(project.id)
    assert loaded.metadata["name"] == "after"


def test_delete_project() -> None:
    manager = ProjectManager()
    project = manager.create_project()

    manager.delete_project(project.id)

    with pytest.raises(ProjectNotFound):
        manager.get_project(project.id)


def test_list_projects() -> None:
    manager = ProjectManager()
    p1 = manager.create_project(metadata={"i": 1})
    p2 = manager.create_project(metadata={"i": 2})

    ids = {p.id for p in manager.list_projects()}
    assert ids == {p1.id, p2.id}
