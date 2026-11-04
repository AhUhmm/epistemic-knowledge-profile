# EKP configuration — [PROJECT_NAME]

<!-- Paste this section into the project instruction file (CLAUDE.md or
equivalent). It is the bundle schema (SPEC §8.1): the single place where
the bundle declares its perimeter, active modules, area vocabulary, and
domain extensions. Commands and the linter read the fenced YAML block
below — keep it as the first ```yaml block after this heading. -->

```yaml
# ekp-config
perimeter:
  - concept/
  - decisions/

modules: []            # activate by declaration, e.g. [continuity, integrations]
                       # no declaration = commands run core only (SPEC §8.3)

areas: []              # open vocabulary (SPEC §4.3): list the values in use
                       # as hygiene, e.g. [strategy, architecture]. Not an enum —
                       # new values may be introduced as the need arises.

extensions: {}         # optional domain extensions in use (SPEC §7).
                       # Each entry names the field and the rule that branches
                       # on it — a field nothing branches on is decoration:
                       #   risk: "high blocks the release gate"
                       #   hypothesis_type: "behavioral | functional — selects the verification route"
                       #   constraint_type: "technical | business | legal | accessibility"

log: log.md            # append-only event log (SPEC §8.4)
index:
  - decisions/_index.md   # computed views, regenerated at wrap-up (SPEC §5.4)
```

## Conventions (human/agent contract)

- **Ownership** (SPEC §8.1): sources are immutable; the epistemic layer
  is written only through the wrap-up gate; views and log are
  agent-maintained, never hand-edited.
- **Edges** (SPEC §5): `derives_from` / `supersedes` / `resolves` only,
  path targets, stored downstream; back-references are computed into the
  index.
- **IDs**: `PREFIX-NNN`, progressive per category, assigned at wrap-up.
- [Project-specific conventions: language, naming, references to domain
  documents and deliverables.]
