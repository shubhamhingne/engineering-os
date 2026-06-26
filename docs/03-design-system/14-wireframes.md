# 14 — Wireframes

Low-fidelity wireframes for the **MVP screens only**. ASCII layouts (version-controllable, no
Figma dependency). Each screen documents purpose, primary/secondary actions, and empty + error
states. High-fidelity mockups land in `design/mockups/` once these are approved.

Legend: `[ Button ]` action · `( field )` input · `‹icon›` · `▸` expandable.

## 1. Sign In
**Purpose:** authenticate. **Primary:** Continue with GitHub. **Secondary:** email sign-in.

```
                ┌──────────────────────────────┐
                │   ‹SH›  Engineering OS        │
                │   Idea → repository           │
                │                               │
                │   [ Continue with GitHub ]    │
                │   ──────── or ────────        │
                │   ( email )                   │
                │   ( password )                │
                │   [ Sign in ]                 │
                └──────────────────────────────┘
```
**Empty:** n/a. **Error:** "Invalid credentials" inline; "GitHub sign-in failed — try again."

## 2. Dashboard
**Purpose:** orient + resume. **Primary:** New project. **Secondary:** open recent, search.

```
┌────────┬─────────────────────────────────────────────┐
│Sidebar │ Home          ( search ⌘K )           ‹user› │
│• Home  ├─────────────────────────────────────────────┤
│• Proj ▸│ Recent projects        [ + New project ]     │
│• Set.  │ ┌─────────┐ ┌─────────┐ ┌─────────┐          │
│        │ │engine.. │ │salon-.. │ │…        │          │
│        │ │PRD ✓ ADR│ │Vision   │ │         │          │
│        │ └─────────┘ └─────────┘ └─────────┘          │
│        │ Activity: generated PRD · exported repo …    │
└────────┴─────────────────────────────────────────────┘
```
**Empty:** "No projects yet. Start from an idea." → [ New project ]. **Error:** load-failed banner + retry.

## 3. Project List
**Purpose:** browse/manage projects. **Primary:** New project. **Secondary:** sort, filter, open.

```
│ Projects                       ( filter )  [ + New ] │
│ ─────────────────────────────────────────────────── │
│ ‹folder› engineering-os   PRD·ADR·README  2h   ▸     │
│ ‹folder› salon-erp        Vision          1d   ▸     │
│ ‹folder› …                                            │
```
**Empty:** same as dashboard empty. **Error:** row-level "couldn't load" with retry.

## 4. Project Detail
**Purpose:** the project hub — artifacts, runs, repo. **Primary:** Generate next artifact.
**Secondary:** export repo, open artifact, view runs.

```
│ engineering-os                         [ Export repo ]│
│ Stage: Architecture ███░░  (3/9)                      │
│ Artifacts        Runs        Repository               │
│ ─────────────────────────────────────────────────────│
│ ‹file› Vision    v3  ✓        [ Open ]                │
│ ‹file› PRD       v2  ✓        [ Open ]                │
│ ‹file› ADR-0001  v1  ✓        [ Open ]                │
│ ‹file› README    —   [ Generate ]                     │
```
**Empty:** "No artifacts. Generate your first." → [ Generate Vision ]. **Error:** see generation errors.

## 5. Artifact Workspace
**Purpose:** read/edit an artifact. **Primary:** Generate / Save. **Secondary:** version history,
inspect, diff.

```
┌────────┬───────────────────────────────┬──────────────┐
│Sidebar │ PRD  ‹history› v2        [Save]│ Inspect      │
│        │ ───────────────────────────── │ prompt v4    │
│        │ # Overview                    │ model: …     │
│        │ Engineering OS is …           │ tokens 1,240 │
│        │ ## Goals                      │ cost  $0.03  │
│        │ - …                           │ 4.2s         │
│        │  (editable markdown, 16px)    │ [Regenerate] │
└────────┴───────────────────────────────┴──────────────┘
```
**Empty:** "Nothing generated yet." → [ Generate ]. **Error:** "Generation failed — draft safe." [Retry].

## 6. AI Generation Panel (within #5 / modal)
**Purpose:** run a generation with full provenance. **Primary:** Generate. **Secondary:** model
select, edit prompt.

```
│ Generate: PRD                                         │
│ Provider ( Anthropic ▾ )  Model ( … ▾ )  ~$0.03       │
│ ▸ Prompt (v4)  — inspectable/editable                 │
│ ─────────────────────────────────────────────────────│
│ ░ streaming … ## Overview Engineering OS is ▌ (cyan)  │
│ tokens 612 · 2.1s                         [ Stop ]    │
```
**Error:** inline "provider timeout" + [Retry] / switch model. **Loading:** streaming (no blank spinner).

## 7. Repository Export
**Purpose:** create the GitHub repo. **Primary:** Create repository. **Secondary:** edit name,
visibility.

```
│ Export to GitHub                                      │
│ Repo name ( engineering-os )   ( ● Public  ○ Private )│
│ Will include: README · LICENSE · .github standards ·  │
│               docs/ artifacts                          │
│ GitHub: ‹check› connected as @shubhamhingne           │
│                              [ Create repository ]     │
```
**Error:** "name exists" → rename; "GitHub expired" → [Reconnect]. **Success:** repo URL + [Open].

## 8. Settings
**Purpose:** providers + preferences. **Primary:** Connect provider. **Secondary:** disconnect,
density toggle.

```
│ Settings  ›  Providers                                │
│ ‹cpu› OpenAI       connected      [ Disconnect ]      │
│ ‹cpu› Anthropic    connected      [ Disconnect ]      │
│ ‹cpu› Gemini       —              [ Connect ]         │
│ Preferences:  Density ( Comfortable ▾ )               │
│ GitHub:  connected as @shubhamhingne  [ Disconnect ]  │
```
**Empty:** "No providers connected. Connect one to generate." **Error:** "Couldn't save key" + retry.

> Every screen reuses components from [07](07-component-library.md) — no new vocabulary invented.
