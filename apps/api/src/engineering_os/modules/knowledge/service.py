"""Knowledge module — an internal semantic representation extracted from a project's artifacts.

Not a graph database; a structured model (Goal, Audience, Features, Tech, Topics, Risks, …) that
every downstream artifact (README now; more later) reads from. Extraction is deterministic and
content-aware, so synthesis reflects the *actual* artifacts and is testable without a network.
"""
import re
from dataclasses import dataclass, field

# Vocabulary we can detect in artifact text. Extend freely.
TECH = [
    "FastAPI", "Next.js", "React", "TypeScript", "Python", "Node.js", "Node", "PostgreSQL",
    "Redis", "Docker", "Tailwind", "SQLAlchemy", "Anthropic", "OpenAI", "Kotlin", "Flutter",
    "GitHub Actions", "WebSockets",
]
TOPICS = [
    "authentication", "authorization", "billing", "payments", "real-time", "websocket",
    "search", "notifications", "export", "dashboard", "analytics", "streaming", "agent",
    "llm", "ai", "versioning", "collaboration", "offline",
]


@dataclass
class KnowledgeGraph:
    title: str
    tagline: str
    problem: str
    solution: str
    features: list[str] = field(default_factory=list)
    tech_stack: list[str] = field(default_factory=list)
    topics: list[str] = field(default_factory=list)
    audience: str = ""
    roadmap: list[str] = field(default_factory=list)
    risks: list[str] = field(default_factory=list)
    architecture: str = ""
    sources: dict[str, list[str]] = field(default_factory=dict)


def _sections(md: str) -> dict[str, str]:
    out: dict[str, str] = {}
    current = "_preamble"
    buf: list[str] = []
    for line in md.splitlines():
        m = re.match(r"^#{1,3}\s+(.*)", line)
        if m:
            out[current.strip().lower()] = "\n".join(buf).strip()
            current = m.group(1)
            buf = []
        else:
            buf.append(line)
    out[current.strip().lower()] = "\n".join(buf).strip()
    return out


def _bullets(text: str) -> list[str]:
    return [ln.strip()[2:].strip() for ln in text.splitlines() if ln.strip().startswith("- ")]


class KnowledgeExtractor:
    def extract(self, title: str, idea: str, artifacts: dict[str, str]) -> KnowledgeGraph:
        vision = artifacts.get("vision", "")
        prd = artifacts.get("prd", "")
        combined = f"{idea}\n{vision}\n{prd}".lower()
        vs = _sections(vision)
        ps = _sections(prd)

        problem = vs.get("problem") or idea.strip()
        solution = vs.get("vision") or ""
        topics = [t for t in TOPICS if t in combined]
        base_features = (
            _bullets(ps.get("requirements", ""))
            or _bullets(ps.get("goals", ""))
            or _bullets(vs.get("what success looks like", ""))
        )
        # Detected topics are always surfaced as capabilities — the semantic guarantee holds
        # whether or not the PRD already lists features.
        topic_features = [f"{t.capitalize()} support" for t in topics]
        features = list(dict.fromkeys(base_features + topic_features))
        tagline = idea.strip().splitlines()[0].strip() if idea.strip() else title.strip()

        return KnowledgeGraph(
            title=title.strip(),
            tagline=tagline,
            problem=problem,
            solution=solution,
            features=features,
            tech_stack=[t for t in TECH if t.lower() in combined],
            topics=topics,
            audience=ps.get("users", "") or ps.get("target users", ""),
            roadmap=_bullets(ps.get("roadmap", "")),
            risks=_bullets(ps.get("risks", "")),
            architecture=vs.get("architecture", "") or ps.get("architecture", ""),
            sources={
                "Hero": ["vision"] if vision else [],
                "Problem": ["vision"] if vs.get("problem") else [],
                "Solution": ["vision"] if solution else [],
                "Features": ["prd"] if (ps.get("requirements") or ps.get("goals")) else (["vision"] if features else []),
                "Tech Stack": [t for t in ("vision", "prd") if t in artifacts],
                "Roadmap": ["prd"] if _bullets(ps.get("roadmap", "")) else [],
            },
        )
