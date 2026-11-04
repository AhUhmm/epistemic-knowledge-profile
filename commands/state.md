---
description: "Query operation: load the epistemic profile state and give the session visibility on the conceptual level. Pure layer management — no session-continuity duties."
---

# /state — core (query)

Loads the current state of the epistemic layer at the start of a session
(or on demand, whenever the conceptual picture needs refreshing). It
routes through views and the log — it never opens file bodies to route,
and drills into individual files only where the state brief requires it.

## 1 — Load the schema

Read the project instruction file (CLAUDE.md or equivalent) if not
already in context. It declares the bundle perimeter, the `area` values
in use, and which optional modules are active.

## 2 — Route through the views

1. Read `decisions/_index.md` (and `concept/_index.md` if present).
   These are computed views: items by status, per-area groupings,
   computed back-references.
2. Read the tail of `log.md`:
   `grep "^## \[" log.md | tail -10`
   The last epistemic events (creations, status transitions, lint
   results) — without opening any file.

## 3 — Present the epistemic state

```
## Epistemic state — [today]

**Recent events:** [from the log tail: last transitions and creations]

**Open by category:** [counts: N gaps open, N assumptions unvalidated,
N hypotheses untested, N decisions with pending review triggers]

**Items awaiting input:**
- [ID] — [the pending review trigger or open question]

**Health:** [lint findings from the last wrap-up, if any]
```

The state brief describes *where the reasoning stands*, not what to do
next: work direction belongs to the user (or to the continuity module,
if active).

---

## Module hooks (conditional)

A module runs only if the bundle schema declares it active (e.g.
`modules: [continuity]` in the project instruction file). No
declaration means core only — skip silently, ask nothing.

**continuity** (if declared) — session-continuity duties live entirely
here: read the most recent handover in `_handover/`, add "last point"
and "suggested next step" to the brief, and hold the start of work for
the user's confirmation. Projects using this module may alias the
combined operation as `/resume`.

**integrations** (if declared) — fetch active issues from the declared
tracker, match `PREFIX-NNN` references against open items, flag issues
blocked by pending review triggers.
