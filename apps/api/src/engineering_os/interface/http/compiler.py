"""Compiler introspection — the pipeline as a self-describing artifact (ADR-0014).

Static (not project-scoped): it describes the compiler itself — its fingerprint and dependency
graph — so the engine can be visualized and diagnosed independently of any one project."""
from fastapi import APIRouter, Depends

from ...adapters.db.models import User
from ...modules.compiler.graph import build_dependency_graph
from ...modules.compiler.passes import COMPILER_VERSION, EXPLAIN_PIPELINE, SEED_KEYS, explain_compiler
from .deps import get_current_user
from .schemas import CompilerPipelineOut, PipelineEdgeOut

router = APIRouter(prefix="/api/v1")


@router.get("/compiler/pipeline", response_model=CompilerPipelineOut)
def compiler_pipeline(_user: User = Depends(get_current_user)) -> CompilerPipelineOut:
    dag = build_dependency_graph(EXPLAIN_PIPELINE, SEED_KEYS)
    return CompilerPipelineOut(
        fingerprint=explain_compiler().fingerprint,
        compiler_version=COMPILER_VERSION,
        nodes=dag.nodes,
        edges=[PipelineEdgeOut(producer=src, consumer=dst) for src, dst in dag.edges],
        mermaid=dag.mermaid(),
        cycle=dag.find_cycle(),
        unreachable=dag.unreachable(),
    )
