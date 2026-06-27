"""Compiler passes — every transformation is a pass with a name, declared inputs/outputs, and a
deterministic `run` over a shared context. The pipeline is a *sequence of passes*, so the
semantic-compiler analogy is literal, not metaphorical (ADR-0011). Passes are uniformly testable
and (later) independently cacheable.
"""
from typing import Protocol

from ..decision.service import DecisionExtractor
from ..explain.service import ExplanationExtractor, ExplanationGraph
from ..knowledge.service import KnowledgeExtractor
from ..render.renderers import RenderContext, RendererRegistry


class CompilerPass(Protocol):
    name: str
    consumes: list[str]
    produces: list[str]
    deterministic: bool   # same inputs always yield the same outputs (no side effects, no I/O)
    cacheable: bool       # output may be memoized by input hash — distinct from deterministic:
    #                       a pass can be deterministic yet uncacheable (PublishPass must always run),
    #                       and cacheability is what the runner will key on once pass caching lands.

    def run(self, context: dict) -> dict:
        ...


class ExtractKnowledgePass:
    name = "extract_knowledge"
    consumes = ["title", "idea", "sources"]
    produces = ["knowledge"]
    deterministic = True
    cacheable = True

    def run(self, context: dict) -> dict:
        graph = KnowledgeExtractor().extract(context["title"], context["idea"], context["sources"])
        return {"knowledge": graph}


class ExtractDecisionPass:
    name = "extract_decision"
    consumes = ["knowledge"]
    produces = ["decisions"]
    deterministic = True
    cacheable = True

    def run(self, context: dict) -> dict:
        return {"decisions": DecisionExtractor().extract(context["knowledge"])}


class BuildPass:
    name = "build"
    consumes = ["title", "idea", "sources"]
    produces = ["bundle"]
    deterministic = True
    cacheable = True

    def run(self, context: dict) -> dict:
        ctx = RenderContext(title=context["title"], idea=context["idea"], artifacts=context["sources"])
        return {"bundle": RendererRegistry().build(ctx)}


class ExplainPass:
    name = "explain"
    consumes = ["knowledge", "decisions", "sources", "bundle"]
    produces = ["explanations"]
    deterministic = True
    cacheable = True

    def run(self, context: dict) -> dict:
        graph = ExplanationExtractor().extract(
            context["knowledge"], context["decisions"], context["sources"], context["bundle"]
        )
        return {"explanations": graph}


class PassRunner:
    def run(self, passes: list[CompilerPass], context: dict) -> dict:
        ctx = dict(context)
        for p in passes:
            missing = [c for c in p.consumes if c not in ctx]
            if missing:
                raise ValueError(f"pass '{p.name}' missing inputs: {missing}")
            ctx.update(p.run(ctx))
        return ctx


EXPLAIN_PIPELINE: list[CompilerPass] = [
    ExtractKnowledgePass(),
    ExtractDecisionPass(),
    BuildPass(),
    ExplainPass(),
]


def run_explain_pipeline(title: str, idea: str, sources: dict[str, str]) -> ExplanationGraph:
    ctx = PassRunner().run(EXPLAIN_PIPELINE, {"title": title, "idea": idea, "sources": sources})
    return ctx["explanations"]
