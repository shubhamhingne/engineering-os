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
from ..repository.service import RepositoryState, build_repository_state
from ...ports.repository import RepositoryReader
from .cache import PassCache
from .context import CompilationReport, CompilerContext, ContextKey, ExecutionPlan, PassResult
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
REPOSITORY_STATE = ContextKey("repository_state", RepositoryState)

SEED_KEYS = (TITLE, IDEA, SOURCES)


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


class RepositorySyncPass:
    """Observe the remote and produce a RepositoryState. The one pass that touches remote state — so
    it is neither deterministic nor cacheable (the remote can change between runs). The credential is
    *configuration* injected at the boundary via the reader, never a context slot, so secrets never
    enter the hashed symbol table. This pass only observes; it makes no publishing decision (ADR-0015)."""

    descriptor = PassDescriptor("repository_sync", 1, (BUNDLE,), (REPOSITORY_STATE,), False, False)

    def __init__(self, reader: RepositoryReader, repository: str) -> None:
        self._reader = reader
        self._repository = repository

    def run(self, ctx: CompilerContext) -> dict:
        bundle = ctx.get(BUNDLE)
        local_hashes = {a.path: a.hash for a in bundle.artifacts}
        snapshot = self._reader.read_state(self._repository)
        return {REPOSITORY_STATE: build_repository_state(self._repository, local_hashes, snapshot)}


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
    produced_types = {k.name: k.type for p in passes for k in p.descriptor.produces}
    schema_versions = {
        name: t.schema_version for name, t in produced_types.items() if hasattr(t, "schema_version")
    }
    payload = {
        "compiler_version": COMPILER_VERSION,
        "passes": [
            [p.descriptor.id, p.descriptor.version,
             [k.name for k in p.descriptor.consumes], [k.name for k in p.descriptor.produces]]
            for p in passes
        ],
        "schema_versions": schema_versions,
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
    plan: Optional[ExecutionPlan] = None


def _cache_key(descriptor: PassDescriptor, input_hash: str, fingerprint: str) -> str:
    """Bind pass id, pass version, input hash, and compiler fingerprint — a hit means the same pass,
    same version, same inputs, same compiler produced this before."""
    return _hash(json.dumps([descriptor.id, descriptor.version, input_hash, fingerprint]))


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
    def __init__(self, passes, seed_keys=SEED_KEYS, cache: Optional[PassCache] = None) -> None:
        self._passes = list(passes)
        self._seed_keys = tuple(seed_keys)
        self._cache = cache
        validate_pipeline(self._passes, self._seed_keys)  # fail fast: an ill-formed pipeline never runs

    @property
    def fingerprint(self) -> str:
        return compute_fingerprint(self._passes, self._seed_keys)

    def _producers(self) -> dict:
        producer = {k.name: "<seed>" for k in self._seed_keys}
        for p in self._passes:
            for o in p.descriptor.produces:
                producer[o.name] = p.descriptor.id
        return producer

    def plan(self, seed: dict) -> ExecutionPlan:
        """Predict the minimal work this compile implies — *before* executing. A pass is required if
        any input it depends on will be recomputed (an upstream pass is required) or its own output is
        not in the cache; otherwise it is reused. The listed order is already topological (the
        validator guarantees it), so a single forward walk resolves dependencies."""
        fingerprint = self.fingerprint
        producer = self._producers()
        ctx = CompilerContext()
        for key, value in seed.items():
            ctx.set(key, value)

        required: list[str] = []
        required_set: set = set()
        reused: list[str] = []
        reasons: dict = {}
        for p in self._passes:
            d = p.descriptor
            if any(producer.get(c.name) in required_set for c in d.consumes):
                required.append(d.id); required_set.add(d.id)
                reasons[d.id] = "required: an upstream pass re-executes"
                continue
            cached = None
            if self._cache is not None and d.cacheable:
                cached = self._cache.peek(_cache_key(d, _hash_slots(ctx, d.consumes), fingerprint))
            if cached is not None:
                reused.append(d.id)
                reasons[d.id] = "reused: output is cached and inputs are unchanged"
                for slot, value in cached.items():
                    ctx.set(slot, value)
            else:
                required.append(d.id); required_set.add(d.id)
                reasons[d.id] = (
                    "required: pass is not cacheable (observes live state)"
                    if not d.cacheable else "required: output not in cache"
                )

        edges = build_dependency_graph(self._passes, self._seed_keys).edges
        return ExecutionPlan(fingerprint, required, reused, required, reasons, edges)

    def run(self, seed: dict, previous: Optional[CompilationReport] = None) -> CompilationResult:
        plan = self.plan(seed)
        reused = set(plan.reused)
        fingerprint = plan.fingerprint

        ctx = CompilerContext()
        for key, value in seed.items():
            ctx.set(key, value)

        results: list[PassResult] = []
        total_start = time.perf_counter()
        for p in self._passes:
            d = p.descriptor
            warned_before = len(ctx.warnings)
            input_hash = _hash_slots(ctx, d.consumes)

            if d.id in reused:
                cached = self._cache.get(_cache_key(d, input_hash, fingerprint))
                for slot, value in cached.items():
                    ctx.set(slot, value)
                duration = 0
                reason = "cache hit"
                cache_hit = True
            else:
                start = time.perf_counter()
                produced = p.run(ctx)
                for slot, value in produced.items():
                    ctx.set(slot, value)
                duration = int((time.perf_counter() - start) * 1000)
                reason = _invalidation_reason(d.id, input_hash, previous)
                cache_hit = False
                if self._cache is not None and d.cacheable:
                    self._cache.put(_cache_key(d, input_hash, fingerprint), produced)

            results.append(
                PassResult(
                    pass_id=d.id,
                    duration_ms=duration,
                    cache_hit=cache_hit,
                    inputs=[k.name for k in d.consumes],
                    outputs=[k.name for k in d.produces],
                    input_hash=input_hash,
                    output_hash=_hash_slots(ctx, d.produces),
                    invalidation_reason=reason,
                    warnings=ctx.warnings[warned_before:],
                )
            )
        total_ms = int((time.perf_counter() - total_start) * 1000)

        bundle_count = len(ctx.get(BUNDLE).artifacts) if ctx.has(BUNDLE) else 0
        bundle_reused = any("bundle" in r.outputs and r.cache_hit for r in results)
        report = CompilationReport(
            compiler_version=COMPILER_VERSION,
            fingerprint=fingerprint,
            schema_versions=ctx.schema_versions,
            passes_executed=results,
            artifacts_generated=0 if bundle_reused else bundle_count,
            artifacts_reused=bundle_count if bundle_reused else 0,
            cache_hits=sum(1 for r in results if r.cache_hit),
            warnings=list(ctx.warnings),
            duration_ms=total_ms,
        )
        # The remote-synchronization section: when a sync pass produced a RepositoryState, the report
        # surfaces the published commit and sync status it observed. Pure enrichment — no pass changes.
        if ctx.has(REPOSITORY_STATE):
            state = ctx.get(REPOSITORY_STATE)
            report.commit_sha = state.published_commit
            report.publisher_result = state.sync_status
        return CompilationResult(ctx, report, plan)


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


# --- The synchronization pipeline (Alpha-0.9) -----------------------------------------------------
# BuildPass is reused unchanged; RepositorySyncPass is the only addition. The reader (carrying the
# credential) is injected at the boundary, so the compiler still never sees identity.

def compile_sync(title: str, idea: str, sources: dict, reader: RepositoryReader, repository: str) -> CompilationResult:
    compiler = Compiler((BuildPass(), RepositorySyncPass(reader, repository)))
    return compiler.run({TITLE: title, IDEA: idea, SOURCES: sources})
