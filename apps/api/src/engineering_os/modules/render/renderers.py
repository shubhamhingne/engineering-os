"""Renderers — the "semantic compiler". Each renderer consumes the project's knowledge and
produces explicit Artifact[] (path + content + provenance). Renderers answer *what files should
exist*; Publishers (separately) answer *where they go* (ADR-0009).
"""
import hashlib
from dataclasses import dataclass, field
from typing import Optional, Protocol

from ..decision.service import ADRRenderer, DecisionExtractor
from ..knowledge.service import KnowledgeExtractor
from ..readme.service import ReadmeService

_MIT = "MIT License\n\nCopyright (c) 2026 Shubham Hingne\n\nPermission is hereby granted, free of charge, ...\n"
_GITIGNORE = "node_modules/\n.venv/\n__pycache__/\n.env\n.DS_Store\ndist/\n.next/\n"


@dataclass
class RenderedArtifact:
    path: str                       # e.g. "README.md", "docs/ADR-0001.md"
    kind: str                       # "markdown" | "text"
    content: str
    renderer: str
    provenance: dict[str, list[str]] = field(default_factory=dict)
    generated_at: Optional[str] = None
    hash: str = ""                  # content hash → enables diffing / incremental builds

    def __post_init__(self) -> None:
        if not self.hash:
            self.hash = hashlib.sha256(self.content.encode("utf-8")).hexdigest()[:12]


@dataclass
class ArtifactBundle:
    artifacts: list[RenderedArtifact] = field(default_factory=list)
    schema_version: str = "v1"

    def files(self) -> dict[str, str]:
        return {a.path: a.content for a in self.artifacts}


@dataclass
class RenderContext:
    title: str
    idea: str
    artifacts: dict[str, str]       # source artifacts: vision, prd, …


class Renderer(Protocol):
    name: str

    def render(self, ctx: RenderContext) -> list[RenderedArtifact]:
        ...


class ReadmeRenderer:
    name = "readme"

    def render(self, ctx: RenderContext) -> list[RenderedArtifact]:
        content, provenance, _score, _missing = ReadmeService().synthesize(ctx.title, ctx.idea, ctx.artifacts)
        return [RenderedArtifact("README.md", "markdown", content, self.name, provenance)]


class AdrRenderer:
    name = "adr"

    def render(self, ctx: RenderContext) -> list[RenderedArtifact]:
        if "vision" not in ctx.artifacts:
            return []
        graph = KnowledgeExtractor().extract(ctx.title, ctx.idea, ctx.artifacts)
        content = ADRRenderer().render_primary(DecisionExtractor().extract(graph))
        return [RenderedArtifact("docs/ADR-0001.md", "markdown", content, self.name)]


class DocsRenderer:
    name = "docs"

    def render(self, ctx: RenderContext) -> list[RenderedArtifact]:
        out: list[RenderedArtifact] = []
        for t in ("vision", "prd"):
            if t in ctx.artifacts:
                out.append(RenderedArtifact(f"docs/{t}.md", "markdown", ctx.artifacts[t], self.name))
        return out


class ScaffoldRenderer:
    name = "scaffold"

    def render(self, ctx: RenderContext) -> list[RenderedArtifact]:
        return [
            RenderedArtifact("LICENSE", "text", _MIT, self.name),
            RenderedArtifact(".gitignore", "text", _GITIGNORE, self.name),
        ]


class RendererRegistry:
    """Adding an output is implementing one Renderer and registering it — not editing a pipeline."""

    def __init__(self, renderers: Optional[list[Renderer]] = None) -> None:
        self._renderers: list[Renderer] = renderers or [
            ReadmeRenderer(),
            AdrRenderer(),
            DocsRenderer(),
            ScaffoldRenderer(),
        ]

    def build(self, ctx: RenderContext, only: Optional[set[str]] = None) -> ArtifactBundle:
        bundle = ArtifactBundle()
        for renderer in self._renderers:
            if only is not None and renderer.name not in only:
                continue
            bundle.artifacts.extend(renderer.render(ctx))
        return bundle

    def renderer_names(self) -> list[str]:
        return [r.name for r in self._renderers]
