# Why model software-project generation as semantic compilation

*A design paper. It does not describe a product; it argues a position: that generating engineering
artifacts from a project is better modeled as **compilation over a typed semantic model** than as
**orchestration of prompts**. The argument stands on its own — the implementation
([specification](20-compiler-specification.md), [invariants](19-compiler-invariants.md),
[history](../../ARCHITECTURE_HISTORY.md)) is evidence, not the subject.*

---

## 1. The problem with prompt-centric generators

The obvious way to turn a project idea into a README, some ADRs, and a scaffold is to ask a language
model for each, in sequence, threading earlier outputs into later prompts. It works in a demo. It
degrades as a system, for reasons that are structural rather than incidental:

- **The output is the only state.** Knowledge lives in generated *text*. To use "the tech stack" in
  three documents, you re-derive it from prose three times — and the three can disagree. There is no
  object that *is* the tech stack.
- **Nothing is verifiable.** A document→model→document step has no intermediate you can assert on. You
  can test that *a* README came back; you cannot test that it mentions the authentication the project
  actually requires. Bugs are semantic and invisible.
- **Change is all-or-nothing.** With no model of what each artifact depends on, every regeneration is a
  full re-run. "Only the idea's wording changed — rebuild just what that affects" is unanswerable.
- **Provenance is gone.** Why is this section here? Which input produced it? A prompt chain cannot say;
  the reasoning evaporated into the text.
- **AI defines the architecture.** When prompts *are* the system, an opaque, non-deterministic stage
  sits at the center, and every property you might want — reproducibility, testability, incremental
  rebuilds — has to be bolted onto something that resists all of them.

These are not prompt-quality problems. A better prompt produces better prose with the same structural
deficits. The missing thing is not a better generator. It is a **model**.

## 2. The missing abstraction: typed semantic models

The fix is to stop treating the project as text and start treating it as **structured knowledge**.
Before any artifact is written, extract typed, versioned models:

- a **knowledge model** — the project's topics and technologies;
- a **decision model** — the architectural decisions those imply;
- an **explanation model** — for each entity, its evidence, the artifacts it shaped, and a confidence.

Now "the tech stack" is an object, not a phrase. It is computed once and *projected* into every
artifact. Extraction is deterministic where it can be, which means it is **testable**: *idea mentions
authentication ⇒ the knowledge model contains it ⇒ the README's features include it.* That is a unit
test, not a vibe check. The text becomes a rendering of the model, and the model becomes the thing
worth getting right.

Once the representation is a typed model rather than prose, a sequence of questions answers itself —
and they turn out to be exactly the questions a compiler asks.

## 3. The compiler analogy

A compiler takes source and produces a binary through *phases* over *typed intermediate
representations*, with a dependency graph, caching, and reproducible builds. Map that onto project
generation and every phase has a counterpart:

```
source            →  Project (title, idea, sources)
parse / semantic  →  KnowledgeGraph, DecisionGraph, ExplanationGraph
IR                →  the typed CompilerContext (a symbol table of typed slots)
optimization plan →  ExecutionPlan (what to run, given what changed)
codegen           →  renderers → an ArtifactBundle
link / emit       →  publishers → a destination (ZIP, GitHub, …)
build log         →  CompilationReport
build id          →  BuildManifest
```

The analogy is not decoration; it is a *design constraint*. It says new capability should arrive as a
**phase in a pipeline**, not a feature in a monolith — and it imports fifty years of answers to the
exact questions prompt chains fail: how to validate before running, cache by content, rebuild only
what changed, and reproduce a result. The word *compiler* is chosen in deliberate contrast: this is
not a template engine (it builds a semantic model, not substitutions) and not a prompt workflow (every
transformation has a typed contract; AI, if present, is one implementation of one phase).

## 4. The evolution of the architecture

The model was not designed up front; it was *discovered*, one constraint at a time, and the path is
itself an argument that the abstractions were load-bearing. The throughline: **every new capability
became an explicit typed model before it became code**, and **correctness moved earlier** at each step.

Semantics were separated from documents (the knowledge model), representation from transport
(renderers vs publishers), and content was hashed so rebuilds could be incremental. Transformations
were unified under a typed **pass** contract; explainability became a first-class output. Identity was
added *around* the compiler, never inside it — the compiler never learns who the user is. The context
became a typed **symbol table** validated at startup, so an ill-formed pipeline fails at construction.
The compiler learned to **fingerprint itself**, then to **plan** — executing only the work a change
implies — and finally to give each compilation an **immutable identity**. The full account is in the
[architecture history](../../ARCHITECTURE_HISTORY.md).

One observation summarizes the result better than any feature list: across the additions of
authentication, repository synchronization, caching, and dependency-driven execution, the
**fingerprint of the existing pipeline never changed**, because none of those releases modified the
existing passes. New capability *composed in*; it did not ripple out. That is architectural stability
made observable — and it is the property a prompt chain can never have, because a prompt chain has no
contract to leave unchanged.

## 5. The invariants that keep it coherent

What stops a growing system from sliding back into an ad-hoc pile is a small set of **invariants** —
rules every change must preserve or amend explicitly. They are grouped by concern
([full list](19-compiler-invariants.md)); the load-bearing ones:

- **The compiler never knows the user.** It receives a project and produces facts, so it runs
  unchanged in a CLI, CI, a batch job, or a test. Identity wraps it.
- **The pipeline is provably well-formed before it runs**, and **every produced slot has exactly one
  producer** — ownership of state is unambiguous, checked at startup.
- **Cacheable ⇒ deterministic**, **execution is topological and minimal**, **plans are
  side-effect-free** — execution is predictable and reproducible.
- **Every run is fingerprinted**; **every compilation has one immutable manifest**; **equivalent
  artifacts imply equivalent manifests** — identity is well-defined and separates *what was produced*
  from *how it ran*.

These are not comments. They are demonstrated over randomly generated pipelines by a property-based
suite, and a change either preserves all of them or amends one in a dated decision record. Invariants
are how the architecture stays an architecture.

## 6. What the model enables

Because the representation is a typed model rather than text, capabilities that are out of reach for a
prompt chain become straightforward — most of them *fall out* of the structure rather than being added:

- **Incremental compilation.** Content hashes + a dependency graph mean a change recompiles only its
  forward closure. Change the idea's wording and only the affected artifacts rebuild.
- **Explainability.** Every entity carries its evidence, the artifacts it produced, and the decisions
  it relates to — provenance as a queryable output, not a guess.
- **Reproducibility.** A run records the compiler configuration that produced it; the same inputs under
  the same compiler yield the same artifacts and the same semantic identity.
- **Immutable build identity.** A tiny, content-addressed manifest answers "exactly what compilation is
  this?" — the reference object for audit, provenance, and replay.
- **Transport-independent publication.** Publication state is modeled separately from any provider, so
  "what's on the remote, and what's pending?" is answerable, and a second provider is a new adapter.

None of these required a cleverer model call. They required the *model*.

## 7. What remains open

The specification defines a compiler; whether the model is as strong as it looks is an empirical
question, and three are worth stating honestly:

- **Pass substitutability.** Can a deterministic and an LLM implementation satisfy the *same* pass
  contract? If yes — even only for some passes, even only under constrained prompting — then AI is an
  interchangeable implementation, and the architecture absorbs it without bending. Success is measured
  by substitutability under the contract, not by output quality.
- **Implementation-independent identity.** If a Python, a Rust, and a cloud implementation produced the
  *same* manifest for the same project, that would demonstrate the strongest claim available: the
  **specification**, not any implementation, defines the compiler.
- **Reproducible workspaces.** If a manifest can reconstruct an entire engineering workspace, it is a
  reproducibility primitive, not merely an audit record.

Each is answerable without changing the specification. That is the point of having one.

---

### Closing

The transferable idea here is not README generation or GitHub publishing. It is this: **project
knowledge is a semantic model, engineering artifacts are compiled views over it, and planning,
execution, identity, and publication are separate concerns that each deserve a typed contract.** Model
the problem that way and correctness becomes something you can encode, validate, and test — rather than
something you hope a prompt returned. That reframing is useful even to someone who never runs this code.
