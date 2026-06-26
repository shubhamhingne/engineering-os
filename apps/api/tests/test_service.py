"""Unit tests — service layer with a fake provider behind the port (deterministic)."""
import pytest

from engineering_os.adapters.ai.fake import FakeAIProvider
from engineering_os.modules.generation.service import GenerationService
from engineering_os.modules.projects.service import NotFoundError, ProjectService


def test_create_and_get_project(db):
    service = ProjectService(db)
    project = service.create("My Tool", "an idea worth building")
    assert project.id and project.title == "My Tool"
    assert service.get(project.id).idea == "an idea worth building"


def test_get_missing_raises(db):
    with pytest.raises(NotFoundError):
        ProjectService(db).get("does-not-exist")


def test_set_and_update_vision_increments_version(db):
    service = ProjectService(db)
    project = service.create("T", "idea")
    first = service.set_vision(project.id, "draft", "ai", model="fake-1")
    assert first.version == 1 and first.source == "ai"
    second = service.set_vision(project.id, "edited", "human")
    assert second.version == 2 and second.source == "human" and second.content == "edited"


def test_generation_service_uses_port():
    result = GenerationService(FakeAIProvider()).generate_vision("build a thing")
    assert "# Product Vision" in result.content
    assert result.model == "fake-1"


def test_generation_rejects_empty_idea():
    with pytest.raises(ValueError):
        GenerationService(FakeAIProvider()).generate_vision("   ")
