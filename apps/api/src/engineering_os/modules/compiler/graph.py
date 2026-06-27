"""The pipeline dependency graph — a *validation artifact*, not an execution engine (ADR-0014).

Built from `PassDescriptor`s, it lets the compiler detect cycles, surface unreachable passes, and
visualize itself, all while execution stays sequential. When the DAG scheduler arrives (v1.0) it
consumes exactly this graph; nothing here changes."""
from dataclasses import dataclass, field
from typing import Optional

SEED = "<seed>"


@dataclass
class DependencyGraph:
    nodes: list[str] = field(default_factory=list)             # pass ids (+ SEED)
    edges: list[tuple] = field(default_factory=list)           # (producer_id, consumer_id)

    def find_cycle(self) -> Optional[list[str]]:
        """Return a node cycle if one exists (a linear pipeline never has one; a malformed
        descriptor set can). DFS with grey/black colouring."""
        adjacency: dict[str, list[str]] = {n: [] for n in self.nodes}
        for src, dst in self.edges:
            adjacency.setdefault(src, []).append(dst)
            adjacency.setdefault(dst, adjacency.get(dst, []))

        WHITE, GREY, BLACK = 0, 1, 2
        colour = {n: WHITE for n in adjacency}
        stack: list[str] = []

        def visit(node: str) -> Optional[list[str]]:
            colour[node] = GREY
            stack.append(node)
            for nxt in adjacency[node]:
                if colour[nxt] == GREY:
                    return stack[stack.index(nxt):] + [nxt]
                if colour[nxt] == WHITE:
                    found = visit(nxt)
                    if found:
                        return found
            stack.pop()
            colour[node] = BLACK
            return None

        for node in adjacency:
            if colour[node] == WHITE:
                found = visit(node)
                if found:
                    return found
        return None

    def unreachable(self) -> list[str]:
        """Pass nodes with no path from the seed — they can never execute."""
        adjacency: dict[str, list[str]] = {n: [] for n in self.nodes}
        for src, dst in self.edges:
            adjacency.setdefault(src, []).append(dst)
        reachable = set()
        frontier = [SEED]
        while frontier:
            node = frontier.pop()
            for nxt in adjacency.get(node, []):
                if nxt not in reachable:
                    reachable.add(nxt)
                    frontier.append(nxt)
        return [n for n in self.nodes if n != SEED and n not in reachable]

    def mermaid(self) -> str:
        lines = ["graph TD"]
        for src, dst in self.edges:
            lines.append(f"    {src.replace('<', '').replace('>', '')} --> {dst}")
        return "\n".join(lines)


def build_dependency_graph(passes, seed_keys) -> DependencyGraph:
    """Edges run producer → consumer: for every slot a pass consumes, draw an edge from whoever
    produces that slot (a pass, or SEED) to this pass."""
    producer_of: dict[str, str] = {k.name: SEED for k in seed_keys}
    for p in passes:
        for o in p.descriptor.produces:
            producer_of.setdefault(o.name, p.descriptor.id)

    nodes = [SEED] + [p.descriptor.id for p in passes]
    edges: list[tuple] = []
    for p in passes:
        for c in p.descriptor.consumes:
            producer = producer_of.get(c.name, SEED)
            edge = (producer, p.descriptor.id)
            if edge not in edges:
                edges.append(edge)
    return DependencyGraph(nodes=nodes, edges=edges)
