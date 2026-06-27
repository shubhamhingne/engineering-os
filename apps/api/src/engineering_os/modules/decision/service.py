"""Decision module — extracts a typed DecisionGraph from the KnowledgeGraph and renders ADRs.

Same pattern as README: structured model → renderer, never document → LLM → document. Keeps the
system deterministic, testable, and provenance-tracked.
"""
from dataclasses import dataclass, field

from ..knowledge.service import SCHEMA_VERSION, KnowledgeGraph


@dataclass
class Decision:
    title: str
    context: str
    decision: str
    alternatives: str
    consequences: str
    sources: list[str] = field(default_factory=list)


@dataclass
class DecisionGraph:
    decisions: list[Decision] = field(default_factory=list)
    schema_version: str = SCHEMA_VERSION


class DecisionExtractor:
    def extract(self, graph: KnowledgeGraph) -> DecisionGraph:
        decisions: list[Decision] = []
        present = graph.sources.get("Tech Stack", []) or ["vision"]

        if graph.tech_stack:
            decisions.append(
                Decision(
                    title="Adopt the project technology stack",
                    context=(graph.problem or graph.tagline),
                    decision="Use " + " · ".join(graph.tech_stack) + " as the core stack.",
                    alternatives=(
                        "Alternative stacks were considered and set aside as a poorer fit for the "
                        "problem and team; each component sits behind an interface so it can be swapped."
                    ),
                    consequences=(
                        "The project standardizes on this stack. Swapping a single component is "
                        "contained; a wholesale change would warrant a new ADR."
                    ),
                    sources=present,
                )
            )

        if graph.architecture:
            decisions.append(
                Decision(
                    title="Architecture approach",
                    context=graph.architecture,
                    decision="Follow the architecture described in the project's artifacts.",
                    alternatives="Ad-hoc structure was rejected in favor of an explicit, documented approach.",
                    consequences="Boundaries are clear and reviewable; future changes update this record.",
                    sources=["vision"],
                )
            )

        if graph.topics:
            caps = ", ".join(t.capitalize() for t in graph.topics[:4])
            decisions.append(
                Decision(
                    title="Core capabilities in scope",
                    context=f"The artifacts call out: {caps}.",
                    decision=f"Treat {caps} as first-class capabilities for the MVP.",
                    alternatives="Deferring these was considered; they are central to the product thesis.",
                    consequences="These capabilities anchor the roadmap and the test surface.",
                    sources=["vision", "prd"],
                )
            )

        return DecisionGraph(decisions=decisions)


class ADRRenderer:
    def _render(self, number: int, d: Decision) -> str:
        return "\n".join(
            [
                f"# {number:04d} — {d.title}",
                "",
                "- **Status:** Proposed",
                "",
                "## Context",
                d.context or "_TBD_",
                "",
                "## Decision",
                d.decision,
                "",
                "## Alternatives considered",
                d.alternatives,
                "",
                "## Consequences",
                d.consequences,
                "",
                "## Provenance",
                "Derived from: " + (", ".join(d.sources) if d.sources else "—"),
                "",
            ]
        )

    def render_primary(self, graph: DecisionGraph) -> str:
        if not graph.decisions:
            return "# 0001 — No decision recorded\n\nNot enough signal in the artifacts yet.\n"
        return self._render(1, graph.decisions[0])
