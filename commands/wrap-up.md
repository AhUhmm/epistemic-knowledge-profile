---
description: "Ingest operation with lint gate: propose epistemic updates, write only after explicit confirmation, regenerate views, append to log. Core is layer management only; continuity and integrations are optional modules."
---

# /wrap-up — core (lint + ingest)

Run at the end of the session. **Write no file until the user confirms
explicitly.** Ownership contract: the agent proposes, the human decides —
session output never enters the epistemic layer ungated.

## 0 — Lint (deterministic pass, read-only)

Run `scripts/ekp_lint.py` on the bundle. Report findings before
proposing anything:

```
## Lint — [today]
Errors:   [malformed YAML, bad id, status outside lifecycle, folder/type mismatch]
Warnings: [dangling edges, upstream forward links, bidirectional edges, stale index entries]
```

Errors must be resolved (or explicitly deferred by the user) before
ingest. Judgment-lint findings (suspected duplicates, edges that don't
look like derivations) go into the proposal below as [FLAG] items.

## 1 — Session recognition

Analyze the session and identify:

- **A. New decisions** — explicit or implicit commitments.
- **B. New concept items** — gaps, assumptions, opportunities,
  hypotheses, constraints, insights that emerged without commitment.
- **C. Status transitions** — existing items whose lifecycle moved
  (assumption validated, gap resolved, hypothesis supported…).
- **D. New edges** — derivations, resolutions, supersessions. Stored
  downstream only, as root-relative paths.

## 2 — Proposal (the gate)

```
## Candidate decisions
[NEW]    DEC-XXX — [title] | area: [..] | derives_from: [..] | resolves: [..] | confidence: high/med/low
[UPDATE] DEC-XXX — [status transition or edge append, with reason]
[DISCARD] [what is not a decision, and why]

## Candidate concept items
[NEW]    [PREFIX]-XXX — [title] | type: [category] | derives_from: [..] | confidence: high/med/low
[UPDATE] [ID] — [status transition, with evidence]

## Flags (judgment-lint)
[FLAG] [suspected duplicate / misclassified edge / stale claim]
```

Ask for explicit confirmation. Do not proceed without an affirmative
answer. Items can be confirmed selectively.

## 3 — Write confirmed files

1. Assign progressive IDs (check the highest existing ID per prefix —
   from the index, verified against the filesystem).
2. Write files from `templates/` into the folder matching their `type`
   (`concept/<category>/`, flat `decisions/`).
3. Edges: downstream only, path targets. Never add a forward link to an
   upstream file. Never delete an existing edge (append-only provenance).
4. Status transitions: update `status` in place; touch nothing else in
   the frontmatter.

## 4 — Regenerate views

Rebuild `_index.md` from frontmatter (script-assisted where available):
per-status listings, per-`area` groupings, computed back-references
("derived by", "resolved by", "superseded by"). The index is a routing
file — if step 3 changed anything, the index must be regenerated in the
same wrap-up.

## 5 — Append to the log

One line per event in `log.md`, append-only, grep-parseable:

```
## [YYYY-MM-DD] create | DEC-XXX [title]
## [YYYY-MM-DD] status | ASS-XXX open→validated | [evidence in brief]
## [YYYY-MM-DD] lint   | [N errors, N warnings]
```

## 6 — Close

```
## Wrap-up complete — [today]
Epistemic layer: [N created / N updated / none]
Views: [regenerated / unchanged]
Log: [N events appended]
```

---

## Module hooks (conditional)

A module runs only if the bundle schema declares it active (e.g.
`modules: [continuity]` in the project instruction file). No
declaration means core only — skip silently, ask nothing.

**continuity** (if declared) — session-continuity duties live entirely
here: write `_handover/HANDOVER_[YYYY-MM-DD]_[slug].md` (last point,
done, open, suggested next step, files touched) and add a "next session
starts from" line to the close.

**integrations** (if declared) — update issue-tracker status, comment
issues referenced by new decisions (cite IDs), run the semantic
re-index on changed files, process session transcripts.
