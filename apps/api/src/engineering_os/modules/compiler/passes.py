"""Compiler passes, the well-formedness validator, and the Compiler (ADR-0011, ADR-0013).

Every transformation is a pass that exposes a `PassDescriptor` (id, typed consumes/produces,
deterministic, cacheable) and a `run(ctx)` that reads typed slots and returns produced slots. The
descriptor is the single source of truth: the **startup validator** uses it to prove the pipeline
is well-formed *before any work runs*, and a future DAG scheduler will consume the very same
descriptors — so the migration from sequential to scheduled needs no pass to change.
"""
import time
from dataclasses import dataclass
from typing import Protocol

from ..decision.service import DecisionExtractor, DecisionGraph
from ..explain.service import ExplanationExtractor, ExplanationGraph
from ..knowledge.service import KnowledgeExtractor, KnowledgeGraph
from ..render.renderers import ArtifactBundle, RenderContext, RendererRegistry
from .context import CompilationReport, CompilerContext, ContextKey, PassResult

COMPILER_VERSION = "0.8.x"

# --- The symbol-table keys (typed slot identifiers) -----------------------------------------------
TITLE = ContextKey("title", str)
IDEA = ContextKey("idea", str)
SOURCES = ContextKey("sources", dict)
KNOWLEDGE = ContextKey("knowledge", KnowledgeGraph)
DECISIONS = ContextKey("decisions", DecisionGraph)
BUNDLE = ContextKey("bundle", ArtifactBundle)
EXPLANATIONS = ContextKey("explanations", ExplanationGraph)

SEED_KEYS = (TITLE, IDEA, SOURCES)


@dataclass(frozen=True)
class PassDescriptor:
    id: str
    consumes: tuple        # tuple[ContextKey, ...]
    produces: tuple        # tuple[ContextKey, ...]
    deterministic: bool    # same inputs → same outputs, no side effects
    cacheable: bool        # output may be memoized by input hash (⇒ deterministic)


class CompilerPass(Protocol):
    descriptor: PassDescriptor

    def run(self, ctx: CompilerContext) -> dict:
        """Read inputs from `ctx`; return {ContextKey: value} for declared produces."""
        ...


class ExtractKnowledgePass:
    descriptor = PassDescriptor("extract_knowledge", (TITLE, IDEA, SOURCES), (KNOWLEDGE,), True, True)

    def run(self, ctx: CompilerContext) -> dict:
        graph = KnowledgeExtractor().extract(ctx.get(TITLE), ctx.get(IDEA), ctx.get(SOURCES))
        return {KNOWLEDGE: graph}


class ExtractDecisionPass:
    descriptor = PassDescriptor("extract_decision", (KNOWLEDGE,), (DECISIONS,), True, True)

    def run(self, ctx: CompilerContext) -> dict:
        return {DECISIONS: DecisionExtractor().extract(ctx.get(KNOWLEDGE))}


class BuildPass:
    descriptor = PassDescriptor("build", (TITLE, IDEA, SOURCES), (BUNDLE,), True, True)

    def run(self, ctx: CompilerContext) -> dict:
        render_ctx = RenderContext(title=ctx.get(TITLE), idea=ctx.get(IDEA), artifacts=ctx.get(SOURCES))
        return {BUNDLE: RendererRegistry().build(render_ctx)}


class ExplainPass:
    descriptor = PassDescriptor(
        "explain", (KNOWLEDGE, DECISIONS, SOURCES, BUNDLE), (EXPLANATIONS,), True, True
    )

    def run(self, ctx: CompilerContext) -> dict:
        graph = ExplanationExtractor().extract(
            ctx.get(KNOWLEDGE), ctx.get(DECISIONS), ctx.get(SOURCES), ctx.get(BUNDLE)
        )
        return {EXPLANATIONS: graph}


# --- Startup validation: prove the pipeline is well-formed before running anything ----------------

class PipelineValidationError(Exception):
    """The pipeline is ill-formed (missing/duplicate producer, or a type mismatch on a slot)."""


def validate_pipeline(passes, seed_keys=SEED_KEYS) -> None:
    """Walk the passes in order and check the compiler itself is well-formed:
      ✓ every consumed slot is produced by an earlier pass (or seeded)
      ✓ a consumed slot's type matches how it is produced
      ✓ no slot has two producers
    (Cycle detection arrives with the DAG scheduler; a linear list cannot cycle.)"""
    available: dict[str, ContextKey] = {k.name: k for k in seed_keys}
    producers: dict[str, str] = {k.name: "<seed>" for k in seed_keys}
    errors: list[str] = []

    for p in passes:
        d = p.descriptor
        for c in d.consumes:
            produced = available.get(c.name)
            if produced is None:
                errors.append(f"pass '{d.id}' consumes '{c.name}' but no earlier pass produces it")
            elif produced.type is not c.type:
                errors.append(
                    f"pass '{d.id}' consumes '{c.name}' as {c.type.__name__} "
                    f"but it is produced as {produced.type.__name__}"
                )
        for o in d.produces:
            if o.name in producers:
                errors.append(
                    f"pass '{d.id}' produces '{o.name}', already produced by '{producers[o.name]}'"
                )
            else:
                producers[o.name] = d.id
                available[o.name] = o

    if errors:
        raise PipelineValidationError("; ".join(errors))


# --- The Compiler: validates at construction, runs producing context + report ---------------------

@dataclass
class CompilationResult:
    context: CompilerContext
    report: CompilationReport


class Compiler:
    def __init__(self, passes, seed_keys=SEED_KEYS) -> None:
        self._passes = list(passes)
        self._seed_keys = tuple(seed_keys)
        validate_pipeline(self._passes, self._seed_keys)  # fail fast: an ill-formed pipeline never runs

    def run(self, seed: dict) -> CompilationResult:
        ctx = CompilerContext()
        for key, value in seed.items():
            ctx.set(key, value)

        results: list[PassResult] = []
        total_start = time.perf_counter()
        for p in self._passes:
            d = p.descriptor
            warned_before = len(ctx.warnings)
            start = time.perf_counter()
            produced = p.run(ctx)
            for key, value in produced.items():
                ctx.set(key, value)
            results.append(
                PassResult(
                    pass_id=d.id,
                    duration_ms=int((time.perf_counter() - start) * 1000),
                    cache_hit=False,
                    inputs=[k.name for k in d.consumes],
                    outputs=[k.name for k in d.produces],
                    warnings=ctx.warnings[warned_before:],
                )
            )
        total_ms = int((time.perf_counter() - total_start) * 1000)

        report = CompilationReport(
            compiler_version=COMPILER_VERSION,
            schema_versions=ctx.schema_versions,
            passes_executed=results,
            artifacts_generated=len(ctx.get(BUNDLE).artifacts) if ctx.has(BUNDLE) else 0,
            cache_hits=sum(1 for r in results if r.cache_hit),
            warnings=list(ctx.warnings),
            duration_ms=total_ms,
        )
        return CompilationResult(ctx, report)


# --- The explainability pipeline (validated once, at import/startup) ------------------------------

EXPLAIN_PIPELINE = (ExtractKnowledgePass(), ExtractDecisionPass(), BuildPass(), ExplainPass())
_EXPLAIN_COMPILER = Compiler(EXPLAIN_PIPELINE)


def compile_project(title: str, idea: str, sources: dict) -> CompilationResult:
    return _EXPLAIN_COMPILER.run({TITLE: title, IDEA: idea, SOURCES: sources})


def run_explain_pipeline(title: str, idea: str, sources: dict) -> ExplanationGraph:
    return compile_project(title, idea, sources).context.get(EXPLANATIONS)
