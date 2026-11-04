# Neighbourhood library — study-room booking (synthetic example)

This is a fictional project, written to show an EKP bundle at level L2.
People, data and figures are invented.

# EKP configuration — neighbourhood library

```yaml
# ekp-config
perimeter:
  - concept/
  - decisions/

modules: []

areas: [service-design, data]

extensions:
  constraint_type: "legal constraints are checked against every decision that collects data"

log: log.md
index:
  - decisions/_index.md
```

## Conventions (human/agent contract)

- **Ownership**: `research/` is a source and is never modified; the
  epistemic layer is written only through the `/wrap-up` gate; the index
  and the log are agent-maintained, never hand-edited.
- **Edges**: `derives_from` / `supersedes` / `resolves` only, path
  targets, stored downstream.
- **IDs**: `PREFIX-NNN`, progressive per category, assigned at wrap-up.
- **Language**: English.
