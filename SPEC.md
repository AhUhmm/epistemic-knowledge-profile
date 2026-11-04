# EKP — Epistemic Knowledge Profile

**Version 0.2 — Draft**
**An epistemic profile of the Open Knowledge Format (OKF).**

EKP is a *profile* of OKF: every EKP-conformant file is also a valid OKF
concept document. EKP does not replace OKF — it constrains the space OKF
deliberately leaves open, adding the small set of conventions needed to
capture not just *what is known* but the *epistemic status* of knowledge
and the *reasoning trail* that produced it.

Where OKF describes the **state** of assets for exchange, EKP describes
the **process and certainty** of knowledge for reasoning. OKF is the
transport layer; EKP is the method layer that sits on top of it.

> **Changes from v0.1** — informed by a field audit of a real bundle
> (77 files, 200 edges) and by the LLM Wiki pattern (Karpathy, 2026):
> `type` is now the bare epistemic category and `area` carries domain
> semantics (§3, §4.1); `decisions/` is flat — decision subtypes are
> removed (§4.1); a seventh category `insight` is added (§4.1);
> the edge vocabulary is fixed at three types with path targets, and
> back-references are computed, never stored (§5); `semantic_tags` is
> tolerated at every level, required only at L3 (§6); a new section
> defines operations and layer contracts (§8).

---

## 1. Motivation

OKF is built for the data-catalog case: a concept is an asset (a table,
a metric) and everything in a bundle reads as settled fact. Design and
product reasoning is different — most of what it captures is provisional:
gaps, assumptions, hypotheses, constraints, decisions that may expire.
OKF has no vocabulary for uncertainty, no lifecycle, no review triggers.

EKP adds exactly those, and nothing more, while staying OKF-conformant so
that any OKF consumer (e.g. a static graph visualizer) can still read an
EKP bundle without understanding the extensions.

### The design question EKP answers

*How much frontmatter is necessary and how much is noise?*

EKP's answer: **necessity is a function of the scale you operate at.**
A solo human–agent session needs almost nothing beyond OKF. A team at
scale needs the full graph and semantic layer. EKP makes this explicit
through **conformance levels** — you adopt the level your use demands and
no more.

---

## 2. Conformance levels

| Level | Name | Adds | Use it when |
|-------|------|------|-------------|
| **L0** | OKF base | `type` + parseable YAML | You only need interchange/visualization |
| **L1** | EKP core | `id`, `status`, epistemic `type` vocabulary | Solo human–agent sessions; agents reason over status |
| **L2** | EKP graph | typed, single-direction relationships | Multi-artifact projects; you need the reasoning trail |
| **L3** | EKP team | `semantic_tags` + identity resolution | Teams; you need overlap & dependency detection |

A file declares nothing about its level: the level is a property of the
*bundle's discipline*, not of the file. A consumer that understands only
L1 must ignore L2/L3 fields gracefully (OKF permissive-consumption rule).

**Field-cost principle.** A field belongs in the frontmatter only if it
must be *queryable without opening the body*. Test each field: would a
human or agent ever filter or route on it without reading the document?
If no, it is body content or noise. `status` passes ("show me open
assumptions"); `rationale` correctly lives in the body.

**Falsifiability principle.** A field that no rule ever branches on is
decoration. `risk: medium` earns its place only if something behaves
differently when `risk: high`. Otherwise move it to prose or drop it.

---

## 3. Level 0 — OKF base

Every EKP file is a UTF-8 markdown file with a YAML frontmatter block and
a markdown body. The single OKF-required field:

- `type` — in EKP, the **bare epistemic category**: `gap`, `assumption`,
  `opportunity`, `hypothesis`, `constraint`, `insight`, `decision`.
  The value is deliberately free of domain semantics: what *kind of
  knowledge* a file is (epistemic) and what *it is about* (semantic)
  are different axes and must not share a field. Domain semantics live
  in `area` and `tags` (§4.3). The bare value is still a valid,
  self-explanatory OKF type.

  `type` intentionally duplicates the folder (§4.1): the folder is local
  navigation, `type` is what survives when the file travels outside the
  tree — an exported OKF bundle, a single file cited on its own.

OKF-recommended fields, all optional but encouraged:

- `title`, `description`, `tags`, `timestamp` (ISO 8601).
- `resource` — canonical URI of the asset the concept describes or is
  anchored to. **This is EKP's artifact-anchoring primitive**: point a
  decision at the wireframe, Storybook story, PR, issue tracker item, or
  dataset it informs. Operational links (e.g. a Linear issue) belong
  here, not in the epistemic edge fields.

---

## 4. Level 1 — EKP core

L1 adds the epistemic spine. Two required fields beyond OKF:

- `id` — stable addressing primitive, `PREFIX-NNN` (see §4.1). Required
  for cross-referencing; do not derive it from the filename.
- `status` — the epistemic lifecycle value (see §4.2). This is the single
  highest-value field: it is what lets an agent treat a file as a
  criterion rather than as prose.

### 4.1 Epistemic type vocabulary

Seven single-valued, mutually-exclusive categories. **The category is
the folder.** Because a unit is exactly one category, encoding it in the
filesystem is sound.

| Category | Prefix | Folder | Answers |
|----------|--------|--------|---------|
| Gap | `GAP` | `concept/gaps/` | "we don't know / haven't decided X" |
| Assumption | `ASS` | `concept/assumptions/` | "we treat X as true to proceed" |
| Opportunity | `OPP` | `concept/opportunities/` | "we could do X if…" |
| Hypothesis | `HYP` | `concept/hypotheses/` | "if X then Y" / "X is feasible & valuable" |
| Constraint | `CON` | `concept/constraints/` | "we cannot do X because…" |
| Insight | `INS` | `concept/insights/` | "we have learned X from evidence" |
| Decision | `DEC` | `decisions/` | "we commit to X" |

**Insight vs assumption.** They can look alike once an assumption is
validated. The distinction is genetic: an assumption is born as a bet and
is later verified; an insight is born *from* evidence (research, data,
observation). A validated assumption stays an assumption with
`status: validated` — it does not convert into an insight.

**Decisions have no subtypes.** `decisions/` is a flat folder. What were
subtypes in earlier systems (strategy, architecture, research-insight)
are either semantic classification — the `area` field (§4.3) — or a
category of their own (`insight`). Human per-area browsing is served by
the computed index (§5.4), not by subfolders.

Any *other* organizing axis — area, cluster, feature, sprint, domain —
MUST be a metadata field, never a folder. The filesystem encodes one
axis (epistemic category); everything else is queryable metadata. This
is OKF's location-vs-category decoupling applied deliberately.

### 4.2 Status lifecycles

Status is the only mandatory epistemic field. Each category has its own
small lifecycle:

- **Gap** — `open → partial → resolved`
- **Assumption** — `open → partially_validated → validated → invalidated`
- **Opportunity** — `unexplored → exploring → committed`
- **Hypothesis** — `untested → supported → refuted`
- **Constraint** — `active → removed`
- **Insight** — `active`
- **Decision** — `open → validated → invalidated`

**`superseded` is a universal terminal status**, valid for every
category in addition to its lifecycle. It pairs with the `supersedes`
edge (§5.2): when a new node replaces an old one, the old node moves to
`superseded` regardless of where it was in its lifecycle — field use
showed this happens to hypotheses too (replaced before ever being
tested). The lifecycle wording is deliberate and should not drift:
a hypothesis is *supported*, never "validated" — the term encodes that
evidence backs it without settling it.

**Status transitions are the events worth logging.** Every transition is
appended to the bundle log (§8.4). When the validation or invalidation
of a concept item produces a commitment, that commitment is a *new
decision* linked with `derives_from` — the concept file records only its
own status change.

### 4.3 The `area` field

Optional, project-defined, single-valued: the macro semantic division a
project wants to browse decisions and concept items by — e.g.
`strategy`, `architecture`, `service-design`. Applicable to any of the
seven categories.

The vocabulary is **open**: values are introduced as the need arises,
with no enum and no required declaration. Declaring the values in use in
the bundle schema (§8.1) is good hygiene, not a requirement. Drift is
self-announcing — since the only thing that branches on `area` is the
computed index, two near-identical groups in the view are immediately
visible; linters MAY flag near-duplicate area values.

`area` passes the falsifiability principle because the computed index
groups on it. It is a field precisely because it is a *semantic* axis:
folders are reserved for the epistemic one.

---

## 5. Level 2 — EKP graph

L2 makes the reasoning trail traceable. It is the differentiator OKF
cannot express: OKF links are untyped edges with the relationship implied
in prose; EKP edges are typed and directed.

### 5.1 The graph is not a pipeline

The frequent pattern gap → opportunity → hypothesis → constraint →
decision → resource is a *pattern, not a rule*. EKP encodes no ordering
and no canonical sequence. Field evidence confirms this: in the audited
bundle, hypothesis→gap and gap→hypothesis edges coexist, and decisions
open new gaps. The typed edges form whatever graph emerges. Do not model
a sequence; model relationships.

### 5.2 Edge vocabulary

Exactly three edge types. Each is directed and stored downstream (§5.3).

- `derives_from` — this node was built on the listed nodes. The primary
  edge: field audit showed ~75–80% of all typed relationships in real
  use are derivations (a hypothesis derived from an assumption, a
  decision derived from a constraint).
- `supersedes` — this node replaces the listed node (lifecycle edge).
- `resolves` — this **decision** settles the listed gap(s). Distinct
  from derivation: a decision may resolve a gap it does not derive from.

Edge targets are **root-relative file paths**, one per target:

```yaml
# in decisions/DEC-014.md  (downstream node stores the edges)
derives_from:
  - concept/constraints/CON-003_context-window.md
  - concept/assumptions/ASS-005_blind-review.md
resolves:
  - concept/gaps/GAP-002_eval-criteria.md
supersedes: decisions/DEC-009_code-aware-review.md
```

Paths (rather than bare IDs) keep the graph procedurally navigable —
any consumer can follow an edge with no ID-resolution index — and match
OKF's resource-addressing style.

**What is deliberately not an edge.** Symmetric affinity ("these items
belong to the same theme") is not a relationship type. Field audit showed
that most apparently-mutual links are directional derivations stored
twice; the genuinely symmetric residue is co-membership in a cluster.
Express it with a shared tag (e.g. `tags: [orca-method]`), never with an
untyped `relates_to` edge. If a link has no direction, it is not an edge.

### 5.3 Single-direction rule

To halve maintenance and make inconsistency impossible, **each edge is
stored on exactly one node — the downstream one.** A decision records
what it derives from and what it resolves; the upstream gap or
constraint stores NO forward link. Back-references are *computed* by
querying who points at a node, never stored in the upstream file.

The consumption need that forward links used to serve — reducing an
agent's search surface, walking from an artifact back to the gaps that
informed it — is served by the computed index (§5.4), not by duplicated
storage.

### 5.4 The index is a routing file

Each bundle maintains an `_index.md` (per layer or unified) that is a
**computed view, never a source of truth**: regenerated from frontmatter
by the maintenance operations (§8), read first by agents to route
queries without opening file bodies. It materializes what storage
deliberately omits — back-references, per-`area` groupings, per-status
listings. If the index and a file disagree, the file wins and the index
is stale (a lint finding, §8.5).

### 5.5 Edge tolerance and immutability

- Consumers MUST tolerate a dangling edge (OKF rule): a missing target is
  not malformed, it may be not-yet-written knowledge. Linters SHOULD
  surface dangling edges as warnings, not errors.
- Edges are **append-only provenance**. A status change (e.g. a decision
  becoming `superseded`) NEVER deletes the edges behind it. The trail
  remains as historical record even when the node is no longer active.

---

## 6. Level 3 — EKP team

At team scale the graph alone is necessary but not sufficient: two people
will file the same gap under different IDs, and the graph cannot see the
overlap. L3 adds the layer that makes overlap and dependency detection
possible.

- `semantic_tags` — **required at L3, optional and tolerated at every
  lower level.** Concepts a reader who does not know the file's content
  would search for. NOT repetitions of the literal `tags`. These are the
  substrate for identity resolution.
- **Identity resolution** — a consumption-time process (semantic
  similarity over `semantic_tags` + `description` + body) that flags
  candidate duplicates and near-duplicates *before* dependency analysis.
  EKP specifies the inputs, not the algorithm.

Rationale for the level gating: `semantic_tags` cost authoring effort for
a consumer that does not exist in solo use. Below L3 the field is
permitted so producers can seed it and observe whether anything ever
branches on it — the falsifiability principle applied empirically. OKF
compliance is unaffected either way: consumers preserve unknown keys.

---

## 7. Optional domain extensions

Activated per domain, never required by the core. Each must satisfy the
falsifiability principle (something must branch on it):

- `risk: high | medium | low` — only if a rule acts on it (e.g. high-risk
  assumptions block a release gate).
- `test_method` / `evaluation_path` — for hypotheses with a defined
  verification route.
- `constraint_type: technical | business | legal | accessibility`.
- `cluster` — thematic grouping (a tag-like field, never a folder).

Producers MAY add any further keys; consumers MUST preserve unknown keys
when round-tripping and MUST NOT reject files with unrecognized fields.

---

## 8. Operations and layer contracts

EKP bundles live inside a larger knowledge layout. This section fixes
the operational discipline; it adapts the three-layer wiki pattern
(sources / wiki / schema) to the epistemic domain.

### 8.1 Layers and ownership

| Layer | Contents | Owner | Write discipline |
|-------|----------|-------|------------------|
| **Sources** | raw material: transcripts, briefs, research inputs | human | **immutable** — agents read, never modify |
| **Domain documents** | elaborated research, models, specs, deliverables | human + agent | free structure; referenced from EKP files **in the body or via `resource` only**, never in edge fields |
| **Epistemic layer** | `concept/` + `decisions/` (the EKP bundle) | co-owned | agent proposes, **human confirms before any durable write** (the gate) |
| **Schema** | the project instruction file + templates | co-evolved | changed deliberately, documented |
| **Views** | `_index.md`, computed back-references | agent | regenerated, never hand-edited |

The machine-readable part of the schema is a fenced YAML block
(`# ekp-config`) inside the project instruction file — see
`templates/SCHEMA_template.md`. It declares the bundle perimeter, the
active modules (§8.3), the `area` values in use (§4.3), the active
domain extensions with the rule that branches on each (§7), and the
locations of log and indexes. Commands and linters parse this block;
everything else in the instruction file is prose for the agent.

The confirmation gate is a deliberate divergence from the wiki pattern
(where the agent owns its layer entirely): epistemic commitments are
exactly the writes that must not happen without human judgment.
Session outputs never enter the epistemic layer ungated.

### 8.2 The three operations

- **Ingest** — extract candidate items and status transitions from a
  work session or source; propose them through the gate; write confirmed
  files; regenerate views; append to the log.
- **Query** — read the index first, drill into files only as needed,
  answer with `id`-cited references. Never scan bodies to route.
- **Lint** — verify bundle health. Deterministic checks are scripted
  (§8.5); semantic judgment (is this edge really a derivation?) is
  agent work under the gate. Lint runs at minimum at every ingest;
  bundles that grow stale between sessions should also run it on a
  schedule.

Scripts do the bookkeeping; the model does the judgment. Neither
substitutes the other.

### 8.3 Session commands

The reference implementation ships the operations as two commands with
a modular design mirroring the conformance levels:

- **core** — pure two-layer management, no session-continuity duties:
  `/state` = query — load the epistemic profile state and give the
  session visibility on the conceptual level; `/wrap-up` = lint +
  ingest + views + log.
- **continuity module** — session-continuity lives entirely here:
  handover notes, "last point / next step" briefing, start-of-work
  confirmation (project-specific; may alias `/state` + briefing as
  `/resume`).
- **integrations module** — issue trackers, transcript pipelines,
  semantic indexes (environment-specific).

Core is required for EKP maintenance; modules are optional and
**activated by declaration** in the bundle schema (e.g.
`modules: [continuity, integrations]`). Absent declaration, commands
run core only — activation is a checkable fact, not an inference the
agent makes per session. The core
deliberately describes *where the reasoning stands*, never what to do
next: work direction is the user's (or the continuity module's).
Stripping ritual to the core is what makes the system adoptable outside
its original domain.

### 8.4 The log

`log.md`, append-only, one line per event, grep-parseable prefix:

```
## [2026-07-23] status | ASS-001 open→validated | evidence: user interviews R4
## [2026-07-23] create | DEC-034 derives_from ASS-001
## [2026-07-23] lint   | 1 dangling edge (GAP-002→DEC-004), 0 errors
```

The log records events; files record state; the index records views.
None duplicates another.

### 8.5 Deterministic lint checks

The scripted floor, per level:

- **L0** — YAML parses; `type` present and in vocabulary (§4.1).
- **L1** — `id` present, well-formed, unique; folder matches category;
  `status` valid for the category's lifecycle (§4.2).
- **L2** — edge targets exist (dangling → warning); no forward links
  stored upstream; no edge stored in both directions; edge targets are
  paths, not bare IDs.
- **Views** — index entries agree with file frontmatter (stale index →
  warning).

Everything else — duplicate concepts, misclassified edges, stale claims —
is judgment-lint, proposed by the agent and confirmed through the gate.

---

## 9. Body conventions

The body is argumentative, not merely descriptive (the EKP difference from
OKF's schema/examples bodies). Conventional headings by category:

- **Decision** — `## Decision`, `## Rationale`, `## Implications`,
  `## Review triggers`.
- **Gap** — `## Description`, `## Context and impact`, `## Review trigger`.
- **Assumption** — `## Assumption`, `## Current basis`,
  `## How to validate`, `## Review trigger`.
- **Hypothesis** — `## Hypothesis`, `## Rationale`,
  `## Verification method`, `## Collected evidence`.
- **Constraint** — `## Constraint`, `## Origin`, `## Impact on design`,
  `## Review conditions`.
- **Insight** — `## Insight`, `## Evidence`, `## Implications`,
  `## Review trigger`.

`## Review trigger(s)` matters most: it is the body section that, with
`status`, turns a file into an actionable criterion and makes staleness
explicit. OKF has no equivalent.

---

## 10. Conformance checklist

A bundle is **EKP-conformant at level N** if:

**L0** — every file in the bundle perimeter has parseable YAML with a
`type` from the vocabulary (§4.1). Files outside the perimeter (sources,
domain documents) are exempt; the perimeter is `concept/` + `decisions/`.

**L1** — every file additionally has `id` and a `status` drawn from its
category's lifecycle (§4.2); each file sits in the folder matching its
epistemic category (§4.1); `decisions/` is flat.

**L2** — edges use only the three types (§5.2) with path targets;
relationships are stored downstream only (§5.3); no edge is duplicated
in both directions; edges are append-only; indexes are computed views
(§5.4).

**L3** — every file has non-empty `semantic_tags` distinct from `tags`.

Consumers MUST treat all other guidance as soft, and MUST NOT reject a
bundle for missing optional fields, unknown types, unknown keys, dangling
edges, or a higher level than they understand.

---

## 11. Minimal example (L2)

```markdown
---
type: decision
id: DEC-014
title: Eval gate with blind reviewers over constraint/decision files
description: A solution's acceptance criteria are the constraint and decision files, judged by reviewer agents with no access to the implementation.
status: validated
timestamp: 2026-06-18T10:00:00Z
area: architecture
tags: [eval, multi-agent, governance]
resource: https://github.com/your-org/your-project/pull/42
supersedes: decisions/DEC-009_code-aware-review.md
derives_from:
  - concept/constraints/CON-003_context-window.md
  - concept/constraints/CON-007_falsifiable-constraints.md
  - concept/assumptions/ASS-005_blind-review.md
---

## Decision
Reviewer agents judge the solution using only the constraint and decision
files as a rubric, without seeing the code produced by the developer agents.

## Rationale
A reviewer that sees the implementation validates the code's internal
coherence, not its fidelity to intent. Blind to the code and anchored to
the architectural constraints (CON-003), the reviewer judges only "does
this violate a constraint or contradict a decision?". In first real use
this caught two serious architectural violations a code-aware review had
passed.

## Implications
- Enables reproducible quality gates independent of the solution's author.
- Requires every relevant constraint to be stated falsifiably (CON-007).
- Blocks solutions that pass functional tests but violate an untested
  constraint.

## Review triggers
- If the constraint count exceeds the reviewer's context window → switch
  to cluster-based selective retrieval instead of full load.
- If reviewers start producing false positives → check whether a
  constraint went stale and should move to `status: superseded`.
```

---

## 12. Relationship to OKF, restated

OKF achieves interoperability by leaving epistemic status, lifecycle, and
review triggers *out*. That those had to be omitted to be universal is
precisely the evidence that they are domain-specific value, not universal
overhead. EKP adds them back as a profile, for the reasoning-capture
domain OKF deliberately does not serve — without breaking OKF consumption.

---

## Appendix A — Glossary

| Term | Definition | Ref |
|------|------------|-----|
| **Profile** | A constrained subset of a broader format: every EKP file is also a valid OKF file | §12 |
| **Bundle** | The set of files under the epistemic perimeter (`concept/` + `decisions/`) managed with EKP discipline | §10 |
| **Perimeter** | The folders whose files must conform; declared in `ekp-config`. Sources and domain documents are outside it | §10, §8.1 |
| **Conformance level (L0–L3)** | How much discipline a bundle adopts; a property of the bundle, not of any file | §2 |
| **Epistemic category** | One of seven kinds of knowledge unit (gap, assumption, opportunity, hypothesis, constraint, insight, decision); the value of `type` and the file's folder | §4.1 |
| **`area`** | Optional single-valued field for a project's macro semantic division (e.g. strategy, architecture); open vocabulary | §4.3 |
| **Lifecycle / `status`** | The small ordered set of states a category moves through; the highest-value field for agent reasoning | §4.2 |
| **`superseded`** | Universal terminal status, valid for every category; pairs with the `supersedes` edge | §4.2 |
| **Edge** | A typed, directed relationship stored in frontmatter: `derives_from`, `supersedes`, or `resolves` | §5.2 |
| **Single-direction rule** | Every edge is stored only on the downstream node; upstream files hold no forward links | §5.3 |
| **Back-reference** | The reverse reading of an edge ("derived by", "resolved by"); always computed into views, never stored | §5.3, §5.4 |
| **Dangling edge** | An edge whose target file does not exist; tolerated (may be not-yet-written knowledge), flagged as a warning | §5.5 |
| **Index (`_index.md`)** | A computed routing view over the bundle: per-status listings, per-area groupings, back-references. Never a source of truth | §5.4 |
| **Log (`log.md`)** | Append-only, grep-parseable record of epistemic events (creations, status transitions, lint runs) | §8.4 |
| **Schema** | The project instruction file + templates: conventions, ownership contracts, and the machine-readable `ekp-config` block | §8.1 |
| **`ekp-config`** | The fenced YAML block in the instruction file declaring perimeter, modules, areas, extensions, log/index locations | §8.1 |
| **Module** | Optional command behavior (continuity, integrations) activated only by declaration in `ekp-config` | §8.3 |
| **Gate** | The confirmation step: the agent proposes, the human approves before any durable write to the epistemic layer | §8.1, §8.2 |
| **Ingest / Query / Lint** | The three operations: gated writing of session knowledge; routed reading of state; health verification | §8.2 |
| **`resource`** | OKF field carrying the URI of the artifact a unit is anchored to (wireframe, PR, issue, dataset) | §3 |
| **`semantic_tags`** | Search-oriented concepts distinct from literal `tags`; substrate for identity resolution; required only at L3 | §6 |
| **Identity resolution** | Consumption-time detection of duplicate/near-duplicate units across authors | §6 |
| **Review trigger** | The body section stating what would make a unit stale or reopen it; with `status`, what makes a file actionable | §9 |
| **Field-cost principle** | A field earns frontmatter placement only if queryable-without-opening-the-body is needed | §2 |
| **Falsifiability principle** | A field earns existence only if some rule branches on it | §2 |

---
*EKP v0.2 — drafted 2026-07-23. Supersedes v0.1 (2026-06-18). A profile
of OKF v0.1. v0.2 changes are grounded in a field audit of a live design
bundle (77 files, 200 edges) and in the LLM Wiki pattern.*
