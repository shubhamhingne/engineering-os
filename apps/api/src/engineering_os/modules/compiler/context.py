"""The compiler's symbol table and its observability records (ADR-0013).

`CompilerContext` is not a typed bag — it is the symbol table the passes read from and write to.
Slots are addressed by typed `ContextKey`s (not strings), so the startup validator can prove a
pipeline is well-formed by *identity and type*, never string equality. Alongside the semantic
graphs it carries compiler *metadata* — warnings and, via the runner, an execution trace — which
turns a run into something observable rather than opaque."""
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass(frozen=True)
class ContextKey:
    """A typed identifier for one slot in the symbol table. Module-level constants (KNOWLEDGE,
    DECISIONS, …) are the only instances; passes reference those, giving the validator real
    identity to check instead of magic strings."""

    name: str
    type: type

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"<{self.name}:{self.type.__name__}>"


@dataclass
class PassResult:
    """What one pass did — the unit of the execution trace. Not a compiler output; compiler
    metadata. The hashes and `invalidation_reason` extend the explainability philosophy from project
    entities to the compiler itself: a pass can say *why* it ran. `cache_hit` is always False today;
    it is the hook the pass-cache will set once outputs are memoized by `input_hash`."""

    pass_id: str
    duration_ms: int
    cache_hit: bool
    inputs: list[str]
    outputs: list[str]
    input_hash: str = ""
    output_hash: str = ""
    invalidation_reason: str = ""
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class CompilationReport:
    """The semantic equivalent of a build log: what the compiler ran, produced, reused, and warned
    about. Becomes far richer once RepositoryState + caching exist (commit SHA, reused artifacts,
    publisher result) — those fields are present now and Optional, so the shape is stable."""

    compiler_version: str
    fingerprint: str                        # hash of the compiler config that produced this run
    schema_versions: dict[str, str]
    passes_executed: list[PassResult]
    artifacts_generated: int
    cache_hits: int
    warnings: list[str]
    duration_ms: int
    artifacts_reused: int = 0
    commit_sha: Optional[str] = None        # filled by RepositorySyncPass (Alpha-0.9)
    publisher_result: Optional[str] = None  # filled when a publish pass runs


@dataclass
class ExecutionPlan:
    """The predictive counterpart to CompilationReport (ADR-0017). Built from the dependency graph
    and the cache *before* execution, it states the minimal work a compile implies: which passes
    must run, which are reused, and in what order. The report is historical; the plan is predictive."""

    fingerprint: str
    required: list[str]               # pass ids that must execute (topological order)
    reused: list[str]                 # pass ids served from cache
    order: list[str]                  # execution order of the required subgraph
    reasons: dict                     # pass_id -> why it runs or is skipped
    edges: list = field(default_factory=list)   # dependency-graph edges (producer, consumer)


class CompilerContext:
    """The symbol table. Set/get slots by typed key; every write is type-checked, so a pass cannot
    smuggle the wrong shape into a slot the next pass trusts."""

    def __init__(self) -> None:
        self._values: dict[str, Any] = {}
        self._schema_versions: dict[str, str] = {}
        self.warnings: list[str] = []

    def set(self, key: ContextKey, value: Any) -> None:
        if not isinstance(value, key.type):
            raise TypeError(
                f"context slot '{key.name}' expects {key.type.__name__}, got {type(value).__name__}"
            )
        self._values[key.name] = value
        schema_version = getattr(value, "schema_version", None)
        if isinstance(schema_version, str):
            self._schema_versions[key.name] = schema_version

    def get(self, key: ContextKey) -> Any:
        return self._values[key.name]

    def has(self, key: ContextKey) -> bool:
        return key.name in self._values

    def warn(self, message: str) -> None:
        self.warnings.append(message)

    @property
    def schema_versions(self) -> dict[str, str]:
        return dict(self._schema_versions)
