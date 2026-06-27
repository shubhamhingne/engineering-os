"""Renderers produce an explicit Artifact bundle (the 'what files exist' layer)."""
from engineering_os.modules.render.renderers import RenderContext, RendererRegistry


def test_registry_builds_bundle_with_expected_files():
    ctx = RenderContext(
        title="App",
        idea="a FastAPI app",
        artifacts={"vision": "# V\n\n## Vision\nx\n", "prd": "# P\n\n## Requirements\n- persist\n"},
    )
    bundle = RendererRegistry().build(ctx)
    paths = {a.path for a in bundle.artifacts}
    assert {"README.md", "docs/ADR-0001.md", "docs/vision.md", "docs/prd.md", "LICENSE", ".gitignore"} <= paths

    readme = next(a for a in bundle.artifacts if a.path == "README.md")
    assert "FastAPI" in readme.content and readme.provenance  # synthesized + provenance-carrying


def test_bundle_files_map():
    bundle = RendererRegistry().build(RenderContext(title="A", idea="x", artifacts={}))
    files = bundle.files()
    assert "README.md" in files and "LICENSE" in files
