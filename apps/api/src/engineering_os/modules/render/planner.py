"""Build planner — decides WHICH renderers to run given the available knowledge. Generation
becomes conditional/incremental instead of unconditional (the compiler's planning phase, ADR-0010)."""
from dataclasses import dataclass, field

from ..knowledge.service import KnowledgeGraph


@dataclass
class PlanItem:
    renderer: str
    build: bool
    reason: str


@dataclass
class BuildPlan:
    items: list[PlanItem] = field(default_factory=list)
    schema_version: str = "v1"

    def to_build(self) -> set[str]:
        return {item.renderer for item in self.items if item.build}


class BuildPlanner:
    def plan(self, graph: KnowledgeGraph, present: dict[str, str]) -> BuildPlan:
        has_vision = "vision" in present
        has_sources = bool(present)
        items = [
            PlanItem("readme", True, "always — the project landing page"),
            PlanItem("adr", has_vision, "decisions derivable from the graph" if has_vision else "needs a Vision — skip"),
            PlanItem("docs", has_sources, "include source documents" if has_sources else "no source artifacts — skip"),
            PlanItem("scaffold", True, "always — LICENSE and .gitignore"),
            PlanItem("openapi", False, "no API specification in the project yet — skip"),
            PlanItem("diagrams", bool(graph.architecture), "architecture present" if graph.architecture else "missing architecture — skip"),
        ]
        return BuildPlan(items=items)
