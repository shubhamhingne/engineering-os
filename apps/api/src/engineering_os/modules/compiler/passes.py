"""Compiler passes, the well-formedness validator, fingerprinting, and the Compiler
(ADR-0011, ADR-0013, ADR-0014).

Every transformation is a pass exposing a versioned `PassDescriptor` (id, version, typed
consumes/produces, deterministic, cacheable) and a `run(ctx)`. The descriptor is the single source
of truth: the startup validator proves the pipeline well-formed (and acyclic) before any work runs;
the fingerprint hashes the whole compiler configuration so a run records *which compiler* produced
it; and a future DAG scheduler consumes the same descriptors unchanged.
"""
import hashlib
import json
import time
from dataclasses import asdict, dataclass, is_dataclass
from typing import Optional, Protocol

from ..decision.service import DecisionExtractor, DecisionGraph
from ..explain.service import ExplanationExtractor, ExplanationGraph
from ..knowledge.service import KnowledgeExtractor, KnowledgeGraph
from ..publish.publishers import GitHubPublisher, ZipPublisher
from ..render.renderers import ArtifactBundle, RenderContext, RendererRegistry
from .context import CompilationReport, CompilerContext, ContextKey, PassResult
from .graph import build_dependency_graph

COMPILER_VERSION = "0.8.y"

# --- The symbol-table keys (typed slot identifiers) -----------------------------------------------
TITLE = ContextKey("title", str)
IDEA = ContextKey("idea", str)
SOURCES = ContextKey("sources", dict)
KNOWLEDGE = ContextKey("knowledge", KnowledgeGraph)
DECISIONS = ContextKey("decisions", DecisionGraph)
BUNDLE = ContextKey("bundle", ArtifactBundle)
EXPLANATIONS = ContextKey("explanations", ExplanationGraph)

SEED_KEYS = (TITLE, IDEA, SOURCES)
GRAPH_KEYS = (KNOWLEDGE, DECISIONS, BUNDLE, EXPLANATIONS)


@dataclass(frozen=True)
class PassDescriptor:
    id: str
    version: int           # bump when a pass's algorithm changes — feeds the fingerprint & cache key
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
    descriptor = PassDescriptor("extract_knowledge", 1, (TITLE, IDEA, SOURCES), (KNOWLEDGE,), True, True)

    def run(self, ctx: CompilerContext) -> dict:
        graph = KnowledgeExtractor().extract(ctx.get(TITLE), ctx.get(IDEA), ctx.get(SOURCES))
        return {KNOWLEDGE: graph}


class ExtractDecisionPass:
    descriptor = PassDescriptor("extract_decision", 1, (KNOWLEDGE,), (DECISIONS,), True, True)

    def run(self, ctx: CompilerContext) -> dict:
        return {DECISIONS: DecisionExtractor().extract(ctx.get(KNOWLEDGE))}


class BuildPass:
    descriptor = PassDescriptor("build", 1, (TITLE, IDEA, SOURCES), (BUNDLE,), True, True)

    def run(self, ctx: CompilerContext) -> dict:
        render_ctx = RenderContext(title=ctx.get(TITLE), idea=ctx.get(IDEA), artifacts=ctx.get(SOURCES))
        return {BUNDLE: RendererRegistry().build(render_ctx)}


class ExplainPass:
    descriptor = PassDescriptor(
        "explain", 1, (KNOWLEDGE, DECISIONS, SOURCES, BUNDLE), (EXPLANATIONS,), True, True
    )

    def run(self, ctx: CompilerContext) -> dict:
        graph = ExplanationExtractor().extract(
            ctx.get(KNOWLEDGE), ctx.get(DECISIONS), ctx.get(SOURCES), ctx.get(BUNDLE)
        )
        return {EXPLANATIONS: graph}


# --- Hashing: of values, of slot sets, and of the whole compiler configuration --------------------

def _canonical(value) -> str:
    payload = asdict(value) if is_dataclass(value) else value
    return json.dumps(payload, sort_keys=True, default=str)


def _hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]


def _hash_slots(ctx: CompilerContext, keys) -> str:
    combined = {k.name: _hash(_canonical(ctx.get(k))) for k in keys}
    return _hash(json.dumps(combined, sort_keys=True))


def compute_fingerprint(passes, seed_keys=SEED_KEYS) -> str:
    """Hash the compiler *configuration* — not the inputs. Answers "did the compiler itself change?"
    so identical project inputs producing different outputs after an upgrade is explainable."""
    payload = {
        "compiler_version": COMPILER_VERSION,
        "passes": [
            [p.descriptor.id, p.descriptor.version,
             [k.name for k in p.descriptor.consumes], [k.name for k in p.descriptor.produces]]
            for p in passes
        ],
        "schema_versions": {k.name: getattr(k.type, "schema_version", None) for k in GRAPH_KEYS},
        "renderers": RendererRegistry().renderer_names(),
        "publishers": [ZipPublisher.name, GitHubPublisher.name],
    }
    return _hash(json.dumps(payload, sort_keys=True))


# --- Startup validation: prove the pipeline is well-formed and acyclic before running anything -----

class PipelineValidationError(Exception):
    """The pipeline is ill-formed (missing/duplicate producer, type mismatch, cycle, or bad order)."""


def validate_pipeline(passes, seed_keys=SEED_KEYS) -> None:
    errors: list[str] = []

    # 1. Producer map over ALL passes — catches duplicates regardless of order.
    producer_of: dict[str, str] = {k.name: "<seed>" for k in seed_keys}
    key_type: dict[str, type] = {k.name: k.type for k in seed_keys}
    for p in passes:
        for o in p.descriptor.produces:
            if o.name in producer_of:
                errors.append(f"pass '{p.descriptor.id}' produces '{o.name}', already produced by '{producer_of[o.name]}'")
            else:
                producer_of[o.name] = p.descriptor.id
                key_type[o.name] = o.type

    # 2. Every consumed slot must have a producer, with a matching type.
    for p in passes:
        for c in p.descriptor.consumes:
            if c.name not in producer_of:
                errors.append(f"pass '{p.descriptor.id}' consumes '{c.name}' but no pass produces it")
            elif key_type[c.name] is not c.type:
                errors.append(
                    f"pass '{p.descriptor.id}' consumes '{c.name}' as {c.type.__name__} "
                    f"but it is produced as {key_type[c.name].__name__}"
                )

    if not errors:
        # 3. No cycles (a validation artifact today; real once passes form a true DAG).
        cycle = build_dependency_graph(passes, seed_keys).find_cycle()
        if cycle is not None:
            errors.append("dependency cycle: " + " → ".join(cycle))

        # 4. Sequential execution must be sound: each pass's inputs produced earlier in the list.
        seen = {k.name for k in seed_keys}
        for p in passes:
            for c in p.descriptor.consumes:
                if c.name not in seen:
                    errors.append(
                        f"pass '{p.descriptor.id}' consumes '{c.name}' before it is produced "
                        f"(listed out of dependency order)"
                    )
            for o in p.descriptor.produces:
                seen.add(o.name)

    if errors:
        raise PipelineValidationError("; ".join(errors))


# --- The Compiler: validates at construction, runs producing context + report ---------------------

@dataclass
class CompilationResult:
    context: CompilerContext
    report: CompilationReport


def _invalidation_reason(pass_id: str, input_hash: str, previous: Optional[CompilationReport]) -> str:
    if previous is None:
        return "cold build (no prior compilation)"
    prior = next((r for r in previous.passes_executed if r.pass_id == pass_id), None)
    if prior is None:
        return "new pass (absent from prior compilation)"
    if prior.input_hash != input_hash:
        return "inputs changed since last compilation"
    return "inputs unchanged (no pass cache yet)"


class Compiler:
    def __init__(self, passes, seed_keys=SEED_KEYS) -> None:
        self._passes = list(passes)
        self._seed_keys = tuple(seed_keys)
        validate_pipeline(self._passes, self._seed_keys)  # fail fast: an ill-formed pipeline never runs

    @property
    def fingerprint(self) -> str:
        return compute_fingerprint(self._passes, self._seed_keys)

    def run(self, seed: dict, previous: Optional[CompilationReport] = None) -> CompilationResult:
        ctx = CompilerContext()
        for key, value in seed.items():
            ctx.set(key, value)

        results: list[PassResult] = []
        total_start = time.perf_counter()
        for p in self._passes:
            d = p.descriptor
            warned_before = len(ctx.warnings)
            input_hash = _hash_slots(ctx, d.consumes)
            reason = _invalidation_reason(d.id, input_hash, previous)
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
                    input_hash=input_hash,
                    output_hash=_hash_slots(ctx, d.produces),
                    invalidation_reason=reason,
                    warnings=ctx.warnings[warned_before:],
                )
            )
        total_ms = int((time.perf_counter() - total_start) * 1000)

        report = CompilationReport(
            compiler_version=COMPILER_VERSION,
            fingerprint=self.fingerprint,
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


def explain_compiler() -> Compiler:
    return _EXPLAIN_COMPILER


def compile_project(
    title: str, idea: str, sources: dict, previous: Optional[CompilationReport] = None
) -> CompilationResult:
    return _EXPLAIN_COMPILER.run({TITLE: title, IDEA: idea, SOURCES: sources}, previous=previous)


def run_explain_pipeline(title: str, idea: str, sources: dict) -> ExplanationGraph:
    return compile_project(title, idea, sources).context.get(EXPLANATIONS)
