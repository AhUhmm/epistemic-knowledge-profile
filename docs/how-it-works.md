# How EKP works

This page explains EKP without assuming you write code. It covers what
the files are, how they connect, what happens during a working session,
and which parts are checked automatically. The precise rules are in the
[specification](../SPEC.md); this page is the way in.

## The idea in one paragraph

A project makes many choices, and each one rests on something: a fact,
a guess, a limit, a question still open. Usually only the choice gets
written down, and over time nobody remembers why it was made or how sure
anyone was. EKP writes down the reasoning too, one short file per piece,
and links the pieces together. People can read it, and so can the AI
agents that work on the project with them.

## Seven kinds of note

Every note is one of seven kinds. Each kind answers a different
question, and each has a small set of states it can be in.

| Kind | The question it answers | Example states |
|------|-------------------------|----------------|
| **Gap** | What don't we know yet? | open → resolved |
| **Assumption** | What are we taking for granted? | open → validated or invalidated |
| **Insight** | What have we learned? | active |
| **Opportunity** | What could we do? | unexplored → exploring → committed |
| **Hypothesis** | What do we think will happen, and can we test it? | untested → supported or refuted |
| **Constraint** | What limits must every solution respect? | active → removed |
| **Decision** | What did we choose, and why? | open → validated or invalidated |

Any note can also end up **superseded**: replaced by a newer one, but
kept, so the old reasoning stays readable.

## What's in a project

A project that uses EKP has a few extra folders and files. Each has an
owner, and the owner decides who may write there.

```mermaid
flowchart TB
    subgraph YOU["Yours"]
        SRC["Your sources<br/>interviews, briefs, data<br/><i>never changed by the agent</i>"]
        CFG["Project settings<br/>a short block in CLAUDE.md"]
    end
    subgraph SHARED["Shared: written only after you say yes"]
        NOTES["The notes<br/>concept/ and decisions/"]
    end
    subgraph AUTO["Kept up to date automatically"]
        IDX["The index<br/>a summary of every note"]
        LOG["The log<br/>a diary of what changed"]
    end
    subgraph KIT["The EKP kit, copied at install"]
        TPL["templates/<br/>one blank form per kind"]
        SCR["scripts/<br/>checks and summaries"]
        CMD["commands<br/>/state and /wrap-up"]
    end
    SRC -- "evidence" --> NOTES
    TPL -- "new notes start from these" --> NOTES
    NOTES -- "summarised into" --> IDX
    NOTES -- "every change recorded in" --> LOG
    CFG -. "tells the agent where things are" .-> NOTES
```

- **The notes** are the heart of it. `concept/` holds the first six
  kinds, one subfolder each. `decisions/` holds the decisions.
- **The index** is a summary page, so nobody has to open every note to
  see where things stand. A script rebuilds it; nobody edits it by hand.
- **The log** is a diary: one line for every note created and every
  change of state, with the date. Lines are only ever added.
- **The kit** is what you copy from this repository when you install
  EKP: blank forms, scripts and two commands.

## How notes connect

Notes point to each other in only three ways:

- **built on**: this note came from that one;
- **resolves**: this decision answers that gap;
- **replaces**: this note takes the place of that one.

The link is always written in the newer note, pointing back at the older
one. The older note never has to be edited when something new builds on
it. The index works out the reverse reading for you ("what was built on
this?").

Here is the example in [`examples/neighbourhood-library`](../examples/neighbourhood-library/),
a library deciding how its study rooms are booked:

```mermaid
flowchart RL
    GAP1["GAP-001<br/>When do rooms run out?<br/><b>resolved</b>"]
    ASS1["ASS-001<br/>Students book a day ahead<br/><b>invalidated</b>"]
    CON1["CON-001<br/>Store only the card number<br/><b>active</b>"]
    DEC1["DEC-001<br/>All rooms booked online<br/><b>superseded</b>"]
    INS1["INS-001<br/>Two thirds are walk-ins<br/><b>active</b>"]
    HYP1["HYP-001<br/>Same-day rooms help<br/><b>supported</b>"]
    OPP1["OPP-001<br/>Screen at the entrance<br/><b>exploring</b>"]
    DEC2["DEC-002<br/>Two rooms ahead, two on the day<br/><b>validated</b>"]
    GAP2["GAP-002<br/>Unused same-day slots?<br/><b>open</b>"]

    DEC1 -- "built on" --> ASS1
    DEC1 -- "built on" --> CON1
    INS1 -- "built on" --> GAP1
    HYP1 -- "built on" --> INS1
    OPP1 -- "built on" --> INS1
    DEC2 -- "built on" --> HYP1
    DEC2 -- "built on" --> CON1
    DEC2 -- "resolves" --> GAP1
    DEC2 -- "replaces" --> DEC1
    GAP2 -- "built on" --> DEC2
```

Read it as a story. The library assumed students book ahead (ASS-001)
and decided to put every room online (DEC-001). Front-desk records showed
that most requests are walk-ins (INS-001), so the assumption turned out
wrong. A pilot supported keeping some rooms for the same day (HYP-001),
and a new decision replaced the first one (DEC-002). That decision
answered the original question (GAP-001) and raised a new one (GAP-002).
DEC-001 is still there, marked superseded: anyone can see what was tried
and why it changed.

## A working session

You work with an AI agent as usual. EKP adds two moments: one at the
start and one at the end.

```mermaid
sequenceDiagram
    actor You
    participant Agent
    participant Notes as Notes, index and log
    Note over You,Notes: Start: /state
    Agent->>Notes: reads the index and the latest log lines
    Agent->>You: here is where the reasoning stands
    Note over You,Agent: You work: discuss, research, design
    Note over You,Notes: End: /wrap-up
    Agent->>Notes: runs the automatic checks
    Agent->>You: proposes new notes, changes of state, links
    You->>Agent: yes / no / change this (the gate)
    Agent->>Notes: writes only what you confirmed
    Agent->>Notes: rebuilds the index, adds lines to the log
```

The most important step is **the gate**. The agent never adds or changes
a note on its own: it proposes, you decide. A note is a commitment ("we
believe this", "we chose this"), and commitments need a person behind
them.

## Commands, scripts and hooks: who does what

EKP splits the work between judgment and bookkeeping. Judgment
(is this really an insight? is this decision still sound?) belongs to
you and the agent. Bookkeeping (are the files well formed? is the index
current?) is done by small programs that give the same answer every
time, whatever model is running.

```mermaid
flowchart LR
    subgraph J["Judgment"]
        YOU2["You<br/>confirm at the gate"]
        AG["The agent<br/>follows the commands"]
    end
    subgraph D["Bookkeeping: same answer every time"]
        LINT["ekp_lint.py<br/>checks the notes"]
        INDEX["ekp_index.py<br/>rebuilds the index"]
        USAGE["ekp_usage.py<br/>records session cost"]
    end
    CMDS["/state and /wrap-up<br/><i>commands</i>"] --> AG
    AG -- "runs" --> LINT
    AG -- "runs" --> INDEX
    HOOK["end of session<br/><i>hook</i>"] -- "runs, no agent involved" --> USAGE
    AG -- "proposes" --> YOU2
```

- **A command** is a written procedure the agent follows when you type
  it, like `/wrap-up`. It's a recipe: the agent reads it and does the
  steps, using its judgment where the recipe asks for it. (Some tools
  call these *skills*; the idea is the same.)
- **A script** is a small program. It doesn't interpret anything: given
  the same files, it always gives the same result. EKP has three: the
  checker, the index builder and the usage counter.
- **A hook** is a rule in your AI tool's settings: "when this happens,
  run that". It fires on its own, without the agent deciding. EKP
  currently offers one, optional: at the end of each session, add a line
  to the log with what the session cost. A second one is planned
  ([#20](https://github.com/AhUhmm/epistemic-knowledge-profile/issues/20)): check every note right after it's written.

The split matters because an agent can be wrong, or skip a step. The
scripts are the floor that holds anyway.

## Project settings

Each project has a short settings block in its instruction file
(`CLAUDE.md`, or `AGENTS.md` for other tools). It starts with
`# ekp-config`. The blank version is in
[`templates/SCHEMA_template.md`](../templates/SCHEMA_template.md).

| Setting | What it says | Who reads it today | Safe to change? |
|---------|--------------|--------------------|-----------------|
| `ekp_version` | Which EKP release the project was installed from | People, when upgrading | Yes: update it when you upgrade |
| `perimeter` | Which folders hold the notes | The agent only | **No**: the scripts look in `concept/` and `decisions/` regardless ([#19](https://github.com/AhUhmm/epistemic-knowledge-profile/issues/19)) |
| `modules` | Optional extras that are switched on | The agent | Yes |
| `areas` | The topics you group notes by, e.g. strategy, research | The agent | Yes: add new ones freely |
| `extensions` | Extra fields your project adds, and the rule that uses each | The agent | Yes, as long as each has a rule |
| `log` | Where the log file is | The agent and the usage counter | **No**: the checker still reads `log.md` |
| `index` | Where the index file is | The agent | **No**: the scripts use `decisions/_index.md` |

Until [#19](https://github.com/AhUhmm/epistemic-knowledge-profile/issues/19) is solved, keep the folder and file
locations as they are, and change the rest freely.

## Words used on this page

- **Bundle**: all the notes of one project, with their index and log.
- **Note** (in the specification: *item* or *unit*): one file, one piece
  of reasoning.
- **Link** (in the specification: *edge*): built on, resolves, replaces.
- **State** (in the specification: *status*): where a note is in its
  life, e.g. open or validated.
- **The gate**: the moment you confirm what the agent proposes. Nothing
  is written without it.
