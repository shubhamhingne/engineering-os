"""Unit tests — project, artifact, and generation services with a fake provider."""
import pytest

from engineering_os.adapters.ai.fake import FakeAIProvider
from engineering_os.modules.artifacts.service import ArtifactService
from engineering_os.modules.generation.service import GenerationService
from engineering_os.modules.projects.service import NotFoundError, ProjectService


def test_create_and_get_project(db):
    service = ProjectService(db)
    project = service.create("My Tool", "an idea worth building")
    assert project.id and service.get(project.id).idea == "an idea worth building"


def test_get_missing_raises(db):
    with pytest.raises(NotFoundError):
        ProjectService(db).get("does-not-exist")


def test_artifact_versions_append_and_current(db):
    project = ProjectService(db).create("T", "idea")
    artifacts = ArtifactService(db)
    v1 = artifacts.add_version(project.id, "vision", "draft", "ai", model="fake-1")
    v2 = artifacts.add_version(project.id, "vision", "edited", "human")
    assert v1.version_no == 1 and v2.version_no == 2
    assert artifacts.current(project.id, "vision").content == "edited"
    assert [v.version_no for v in artifacts.versions(project.id, "vision")] == [2, 1]


def test_types_present(db):
    project = ProjectService(db).create("T", "idea")
    artifacts = ArtifactService(db)
    artifacts.add_version(project.id, "vision", "v", "ai")
    artifacts.add_version(project.id, "prd", "p", "ai")
    assert artifacts.types_present(project.id) == ["prd", "vision"]


def test_generation_vision_then_prd():
    gen = GenerationService(FakeAIProvider())
    vision = gen.generate("vision", {"idea": "build a thing"})
    assert "# Product Vision" in vision.content
    prd = gen.generate("prd", {"vision": vision.content})
    assert "# Product Requirements Document" in prd.content


def test_generation_prd_requires_vision():
    with pytest.raises(ValueError):
        GenerationService(FakeAIProvider()).generate("prd", {"vision": ""})


def test_generation_rejects_empty_idea():
    with pytest.raises(ValueError):
        GenerationService(FakeAIProvider()).generate("vision", {"idea": "   "})
