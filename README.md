# EKP — Epistemic Knowledge Profile

A way to write down not only what a project has decided, but how sure it
is, what it is assuming, and what would make it change its mind — in plain
markdown files that people and agents can both read.

EKP is a profile of Google's [Open Knowledge Format (OKF)](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md):
every EKP file is also a valid OKF document. It adds what OKF leaves out on
purpose — epistemic status, a lifecycle, typed links between items, and
review triggers.

[Italiano più sotto](#in-italiano).

## Why it exists

I started it as a personal tool. Working with agents, I was taking many
more decisions in much less time, and losing the thread: what I had
chosen, what was still open, how sure I was, where I wanted to go. The
system mirrors the categories I already used to organise project
knowledge — gaps, assumptions, insights, opportunities, hypotheses,
constraints and decisions — linked to each other and to the conditions
that should reopen them.

On two projects it left my head and became a shared working constraint.
A colleague read one of my decisions, checked it against the code and
contested it; a new decision superseded it. The contested one was not
deleted — it stays in the bundle as `superseded`, with the disagreement
on record. That is deliberate: kept disagreements and superseded
decisions strengthen the decisions that replaced them, because the new
one carries the trace of what it had to answer. A reviewer agent with
access only to constraints and decisions, not to the code, blocked an
implementation that violated them. This repository is the system, as it
stands, released together with the limits I know about. It accompanies
the talk *Progettare ad alta voce* (WUDRome 2026).

The talk leaves two questions open, and this repo inherits them: a
system like this seems to offer affordances for contestation — it opens
surfaces where decisions can be challenged. Does it, really? And how do
those surfaces extend to the people the decisions fall on, who have no
access to the bundle?

## Contents

| Path | What it is |
|------|-----------|
| [`SPEC.md`](SPEC.md) | The profile: conformance levels L0–L3, the seven categories and their lifecycles, three edge types, operations and layer contracts |
| [`templates/`](templates/) | One template per category, plus `SCHEMA_template.md`: the configuration block to paste into the project instruction file |
| [`commands/`](commands/) | `/state` (load where the reasoning stands) and `/wrap-up` (lint, propose, write only after confirmation), written as Claude Code commands |
| [`scripts/ekp_lint.py`](scripts/ekp_lint.py) | Deterministic linter for the checks a script can do. Read-only, Python 3 standard library only |
| [`scripts/ekp_index.py`](scripts/ekp_index.py) | Regenerates the computed index from frontmatter: per-status listings, back-references, Mermaid graph. `--check` verifies staleness without writing |
| [`scripts/ekp_usage.py`](scripts/ekp_usage.py) | Deterministic token accounting: appends one `usage` line per session to the log, from the session transcript. Runs as a Claude Code `SessionEnd` hook |
| [`tests/`](tests/) | Contract tests for the scripts (`python3 -m unittest discover -s tests`): the example bundle must lint clean, a dirty fixture must trigger every finding class |
| [`examples/neighbourhood-library/`](examples/neighbourhood-library/) | A small synthetic bundle at level L2: a library redesigns how its study rooms are booked |

## The system at a glance

Five layers, each with an owner and a write discipline (SPEC §8.1). The
epistemic layer is the only co-owned one: the agent proposes, the human
confirms — that confirmation step is **the gate**.

```mermaid
flowchart LR
    subgraph H["owned by the human"]
        SRC["sources/<br/>transcripts, briefs<br/><i>immutable</i>"]
    end
    subgraph C["co-owned — written only through the gate"]
        EPI["epistemic layer<br/>concept/ + decisions/"]
    end
    subgraph A["maintained by the agent, computed by scripts"]
        IDX["_index.md<br/><i>computed view</i>"]
        LOG["log.md<br/><i>append-only events</i>"]
    end
    SCHEMA["schema<br/>ekp-config block in CLAUDE.md"]
    SRC -- "evidence (read-only)" --> EPI
    EPI -- "ekp_index.py" --> IDX
    EPI -- "events, lint runs, usage" --> LOG
    SCHEMA -. "declares perimeter,<br/>modules, areas" .-> EPI
```

The two operations route through those layers. Scripts do the
bookkeeping (lint floor, views, token accounting); the model does the
judgment; nothing durable is written without a yes:

```mermaid
sequenceDiagram
    participant U as human
    participant M as agent
    participant B as bundle
    Note over M,B: /state — query
    M->>B: read _index.md + log tail (never file bodies)
    M->>U: where the reasoning stands
    Note over U,B: /wrap-up — lint + ingest
    M->>B: ekp_lint.py — deterministic floor
    M->>U: proposal: new items, transitions, edges
    U->>M: confirm / reject / amend (the gate)
    M->>B: write confirmed files
    M->>B: ekp_index.py — regenerate views
    M->>B: append events to log.md
    Note over B: session end — ekp_usage.py hook<br/>appends one usage line, no model involved
```

Relationships are three typed edges, always stored on the downstream
node; the upstream file holds no forward link, and the index computes
the reverse reading (SPEC §5). The graph they form is whatever emerges —
EKP encodes no pipeline and no canonical ordering:

```mermaid
flowchart LR
    NEW["new node"] -- "derives_from" --> UP["the node it was built on"]
    DEC["decision"] -- "resolves" --> GAP["gap"]
    REPL["replacing node"] -- "supersedes" --> OLD["old node → status: superseded"]
```

## Try it

```bash
# 1. look at the example and lint it
python3 scripts/ekp_lint.py examples/neighbourhood-library

# 2. in your project: create the two folders of the epistemic layer
mkdir -p concept/{gaps,assumptions,opportunities,hypotheses,constraints,insights} decisions

# 3. copy the scripts, and the commands if you use Claude Code
mkdir -p scripts .claude/commands
cp path/to/ekp/scripts/*.py scripts/
cp path/to/ekp/commands/*.md .claude/commands/
```

Then paste the block in `templates/SCHEMA_template.md` into your project's
instruction file (`CLAUDE.md`, `AGENTS.md` or equivalent) and start from
the templates. You don't need the whole thing on day one: level L0 costs
one `type:` field per file, L1 adds `id` and `status`, L2 adds the links.

The linter exits with 0 when the bundle is clean, 1 with warnings only,
2 with errors. Add `--json` for machine-readable output.

To also record what each session costs, add the usage hook to the
project's `.claude/settings.json` — it appends one line per session to
`log.md`, computed from the transcript, no model involved:

```json
{"hooks": {"SessionEnd": [{"hooks": [
    {"type": "command", "command": "python3 scripts/ekp_usage.py"}]}]}}
```

### Without the system

Three gestures you can try on Monday, with no files and no agents:
separate what you know from what you are assuming; for every decision,
write down why you took it, how sure you are and what would make you
change your mind; and put it where others — people and agents — read it.

## Known limits

- **It records when and where an idea was born, not who proposed it.**
  Ideas from people have a name; ideas from an agent don't. Confirming is
  not writing, and responsibility without provenance can't be verified.
  The next version should separate who answers for an item from where it
  comes from. This is [issue #1](../../issues/1).
- **To contest a decision you have to be able to read it.** A bundle
  helps only where the people affected can open it. Even inside a team,
  access is fragile.
- **The categories measure certainty and direction, not who a choice is
  good for, or at whose expense.** They are all written in the first
  person plural. The system doesn't say who is left out of that "we".

Try it on your projects and tell me where it doesn't hold. Issues are
the right place, in English or in Italian.

## Licence

Text — the specification, templates, commands, documentation and
example — is released under [CC BY 4.0](LICENSE). Code in `scripts/` is
released under the [MIT licence](LICENSE-CODE).

---

## In italiano

EKP è un modo per scrivere non solo che cosa ha deciso un progetto, ma
quanto ne è sicuro, che cosa sta assumendo e che cosa gli farebbe
cambiare idea. Sono file markdown che leggono sia le persone sia gli
agenti. Accompagna il talk *Progettare ad alta voce* (WUDRome 2026).

La specifica, i template e l'esempio sono in inglese. Le categorie sono
sette: gap, assunzioni, insight, opportunità, ipotesi, constraint e
decisioni. Ognuna ha un ciclo di vita, e le relazioni tra elementi
sono di tre tipi: *deriva da*, *sostituisce*, *risolve*.

Per cominciare:

1. Guardate l'esempio in `examples/neighbourhood-library/` e lanciate il
   linter: `python3 scripts/ekp_lint.py examples/neighbourhood-library`.
2. Nel vostro progetto, create le cartelle `concept/` e `decisions/`,
   incollate il blocco di `templates/SCHEMA_template.md` nel file di
   istruzioni (`CLAUDE.md` o equivalente) e partite dai template.
3. Non serve tutto subito. Il livello L0 chiede solo il campo `type`;
   L1 aggiunge `id` e `status`; L2 i collegamenti.

I limiti che conosco sono elencati sopra, in *Known limits*. Il primo,
chi ha proposto cosa, è già la [issue #1](../../issues/1).

Provatelo sui vostri progetti e ditemi dove non regge. Le issue vanno
bene anche in italiano.
