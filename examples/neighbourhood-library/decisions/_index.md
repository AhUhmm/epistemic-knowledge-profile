# Index (computed view)

<!-- Regenerated at wrap-up from frontmatter (scripts/ekp_index.py).
Never edit by hand: if this file and a source file disagree, the
source file wins (SPEC §5.4). -->

## Decisions by status

| ID | Title | Status | Area |
|----|-------|--------|------|
| DEC-002 | Two rooms bookable ahead, two only on the day | validated | service-design |
| DEC-001 | All rooms bookable online, up to seven days ahead | superseded | service-design |

## Concept items by status

| ID | Title | Status |
|----|-------|--------|
| GAP-002 | What happens to same-day slots nobody takes? | open |
| OPP-001 | A screen at the entrance showing live room availability | exploring |
| HYP-001 | Holding back rooms for same-day use reduces turn-aways | supported |
| CON-001 | Bookings store only the library card number | active |
| INS-001 | Two thirds of room requests are walk-ins | active |
| GAP-001 | When do study rooms run out? | resolved |
| ASS-001 | Students book rooms at least a day ahead | invalidated |

## By area

- **data** — CON-001
- **service-design** — GAP-001, GAP-002, ASS-001, OPP-001, HYP-001, INS-001, DEC-001, DEC-002

## Back-references (computed, never stored upstream)

- GAP-001 — derived by INS-001; resolved by DEC-002
- ASS-001 — derived by DEC-001
- HYP-001 — derived by DEC-002
- CON-001 — derived by DEC-001, DEC-002
- INS-001 — derived by OPP-001, HYP-001
- DEC-001 — superseded by DEC-002
- DEC-002 — derived by GAP-002

## Graph (computed)

```mermaid
graph LR
  GAP_001["GAP-001"]
  GAP_002["GAP-002"]
  ASS_001["ASS-001"]
  OPP_001["OPP-001"]
  HYP_001["HYP-001"]
  CON_001["CON-001"]
  INS_001["INS-001"]
  DEC_001["DEC-001"]
  DEC_002["DEC-002"]
  GAP_002 -- derives_from --> DEC_002
  OPP_001 -- derives_from --> INS_001
  HYP_001 -- derives_from --> INS_001
  INS_001 -- derives_from --> GAP_001
  DEC_001 -- derives_from --> ASS_001
  DEC_001 -- derives_from --> CON_001
  DEC_002 -- resolves --> GAP_001
  DEC_002 -- derives_from --> HYP_001
  DEC_002 -- derives_from --> CON_001
  DEC_002 -- supersedes --> DEC_001
  classDef terminal stroke-dasharray: 4 4,opacity:0.6;
  class ASS_001,DEC_001,GAP_001 terminal;
```
