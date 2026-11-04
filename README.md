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
contested it; the decision was rewritten. A reviewer agent with access
only to constraints and decisions, not to the code, blocked an
implementation that violated them. This repository is the system, as it
stands, released together with the limits I know about. It accompanies
the talk *Progettare ad alta voce* (WUDRome 2026).

## Contents

| Path | What it is |
|------|-----------|
| [`SPEC.md`](SPEC.md) | The profile: conformance levels L0–L3, the seven categories and their lifecycles, three edge types, operations and layer contracts |
| [`templates/`](templates/) | One template per category, plus `SCHEMA_template.md`: the configuration block to paste into the project instruction file |
| [`commands/`](commands/) | `/state` (load where the reasoning stands) and `/wrap-up` (lint, propose, write only after confirmation), written as Claude Code commands |
| [`scripts/ekp_lint.py`](scripts/ekp_lint.py) | Deterministic linter for the checks a script can do. Read-only, Python 3 standard library only |
| [`examples/neighbourhood-library/`](examples/neighbourhood-library/) | A small synthetic bundle at level L2: a library redesigns how its study rooms are booked |

## Try it

```bash
# 1. look at the example and lint it
python3 scripts/ekp_lint.py examples/neighbourhood-library

# 2. in your project: create the two folders of the epistemic layer
mkdir -p concept/{gaps,assumptions,opportunities,hypotheses,constraints,insights} decisions

# 3. copy the linter, and the commands if you use Claude Code
mkdir -p scripts .claude/commands
cp path/to/ekp/scripts/ekp_lint.py scripts/
cp path/to/ekp/commands/*.md .claude/commands/
```

Then paste the block in `templates/SCHEMA_template.md` into your project's
instruction file (`CLAUDE.md`, `AGENTS.md` or equivalent) and start from
the templates. You don't need the whole thing on day one: level L0 costs
one `type:` field per file, L1 adds `id` and `status`, L2 adds the links.

The linter exits with 0 when the bundle is clean, 1 with warnings only,
2 with errors. Add `--json` for machine-readable output.

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
- **Discipline has a cost.** On a real bundle of 84 files, the linter
  found 47 errors and 64 warnings, and the computed index was sometimes
  out of date.

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
