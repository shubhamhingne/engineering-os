"""Explanation module — a first-class compiler output, not a method on the graph.

`graph + decisions + bundle → ExplanationGraph`. Each explanation answers, for an entity (a topic
or a technology): what is it, where's the evidence, which sources, how confident, which produced
artifacts contain it, and which decisions relate to it. This is the product's differentiator —
explainable synthesis, not opaque generation (ADR-0011).
"""
from dataclasses import dataclass, field
from typing import Optional

from ..decision.service import DecisionGraph
from ..knowledge.service import KnowledgeGraph
from ..render.renderers import ArtifactBundle


@dataclass
class Explanation:
    entity_id: str            # "topic:authentication" | "tech:FastAPI"
    type: str                 # "topic" | "tech"
    label: str
    summary: str
    evidence: list[str] = field(default_factory=list)
    sources: list[str] = field(default_factory=list)       # source artifacts mentioning it
    appears_in: list[str] = field(default_factory=list)    # produced artifacts containing it
    related_decisions: list[str] = field(default_factory=list)
    confidence: float = 0.0


@dataclass
class ExplanationGraph:
    explanations: list[Explanation] = field(default_factory=list)
    schema_version: str = "v1"

    def get(self, entity_id: str) -> Optional[Explanation]:
        return next((e for e in self.explanations if e.entity_id == entity_id), None)


class ExplanationExtractor:
    def extract(
        self,
        graph: KnowledgeGraph,
        decisions: DecisionGraph,
        sources: dict[str, str],
        bundle: ArtifactBundle,
    ) -> ExplanationGraph:
        out: list[Explanation] = []
        entities = [("topic", t) for t in graph.topics] + [("tech", t) for t in graph.tech_stack]
        for kind, name in entities:
            needle = name.lower()
            src = [t for t, content in sources.items() if needle in content.lower()]
            produced = [a.path for a in bundle.artifacts if needle in a.content.lower()]
            related = [d.title for d in decisions.decisions if needle in (d.decision + " " + d.context).lower()]
            evidence = [f"Mentioned in {t}" for t in src] + [f"Appears in {p}" for p in produced]
            confidence = round(min(1.0, 0.5 + 0.12 * len(src) + 0.06 * len(produced)), 2)
            out.append(
                Explanation(
                    entity_id=f"{kind}:{name}",
                    type=kind,
                    label=name,
                    summary=f"'{name}' is a {kind} surfaced from the project's artifacts.",
                    evidence=evidence,
                    sources=sorted(src),
                    appears_in=sorted(produced),
                    related_decisions=related,
                    confidence=confidence,
                )
            )
        out.sort(key=lambda e: (-e.confidence, e.entity_id))
        return ExplanationGraph(explanations=out)
