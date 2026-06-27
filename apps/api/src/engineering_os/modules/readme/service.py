"""README module — synthesizes a README from the project's KnowledgeGraph (not concatenation).

Every section carries provenance (which artifacts it derived from), and the result is scored for
completeness. This is the "three layers" standard: prompt/knowledge → reasoning metadata
(provenance + score) → artifact (the README).
"""
from ..knowledge.service import KnowledgeExtractor, KnowledgeGraph

# (section, weight, present?) — weights sum to 100.
_CHECKS: list[tuple[str, int]] = [
    ("Hero", 10),
    ("Problem", 15),
    ("Solution", 10),
    ("Features", 20),
    ("Architecture", 10),
    ("Tech Stack", 10),
    ("Getting Started", 10),
    ("Roadmap", 5),
    ("Screenshots", 5),
    ("License", 5),
]


def _present(graph: KnowledgeGraph) -> dict[str, bool]:
    return {
        "Hero": bool(graph.title),
        "Problem": bool(graph.problem),
        "Solution": bool(graph.solution or graph.tagline),
        "Features": bool(graph.features),
        "Architecture": bool(graph.architecture),
        "Tech Stack": bool(graph.tech_stack),
        "Getting Started": True,
        "Roadmap": bool(graph.roadmap),
        "Screenshots": False,  # no images captured yet
        "License": True,
    }


class ReadmeService:
    def __init__(self) -> None:
        self._extractor = KnowledgeExtractor()

    def _graph(self, title: str, idea: str, artifacts: dict[str, str]) -> KnowledgeGraph:
        return self._extractor.extract(title, idea, artifacts)

    def _score(self, graph: KnowledgeGraph) -> tuple[int, list[str]]:
        present = _present(graph)
        score = sum(w for name, w in _CHECKS if present[name])
        missing = [name for name, _ in _CHECKS if not present[name]]
        return score, missing

    def _render(self, g: KnowledgeGraph) -> str:
        out: list[str] = [f"# {g.title}", "", f"> {g.tagline}", ""]
        out += ["## Problem", g.problem or "_TBD_", ""]
        out += ["## Solution", g.solution or g.tagline, ""]
        out += ["## Features"]
        out += [f"- {f}" for f in g.features] if g.features else ["- _TBD_"]
        out += ["", "## Architecture", g.architecture or "See [`docs/`](docs/) for architecture and ADRs.", ""]
        out += ["## Tech Stack", " · ".join(g.tech_stack) if g.tech_stack else "_TBD_", ""]
        out += ["## Getting Started", "```bash", "git clone <repo> && cd <repo>", "# install and run — see docs/", "```", ""]
        out += ["## Roadmap"]
        out += [f"- {r}" for r in g.roadmap] if g.roadmap else ["- _TBD_"]
        out += ["", "## Documentation", "See [`docs/`](docs/).", ""]
        out += ["## Contributing", "Contributions welcome — see CONTRIBUTING.", ""]
        out += ["## License", "MIT.", ""]
        return "\n".join(out)

    def synthesize(self, title: str, idea: str, artifacts: dict[str, str]) -> tuple[str, dict, int, list[str]]:
        graph = self._graph(title, idea, artifacts)
        content = self._render(graph)
        score, missing = self._score(graph)
        provenance = {
            **{k: v for k, v in graph.sources.items() if v},
            "Getting Started": ["template"],
            "Documentation": ["template"],
            "Contributing": ["template"],
            "License": ["template"],
        }
        return content, provenance, score, missing

    def assess(self, title: str, idea: str, artifacts: dict[str, str]) -> tuple[int, list[str], dict]:
        graph = self._graph(title, idea, artifacts)
        score, missing = self._score(graph)
        provenance = {k: v for k, v in graph.sources.items() if v}
        return score, missing, provenance
