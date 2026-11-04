# Log — neighbourhood library

<!-- Append-only, one line per event (SPEC §8.4). -->

## [2026-03-02] create | GAP-001 When do study rooms run out?
## [2026-03-02] create | ASS-001 Students book rooms at least a day ahead
## [2026-03-05] create | CON-001 Bookings store only the library card number
## [2026-03-06] create | DEC-001 derives_from ASS-001, CON-001
## [2026-03-20] create | INS-001 derives_from GAP-001 | evidence: front-desk logs, 412 requests
## [2026-03-20] status | ASS-001 open→invalidated | evidence: INS-001
## [2026-03-21] create | HYP-001 derives_from INS-001
## [2026-04-10] status | HYP-001 untested→supported | evidence: two-week pilot
## [2026-04-12] create | OPP-001 derives_from INS-001
## [2026-04-14] create | DEC-002 derives_from HYP-001, CON-001; resolves GAP-001; supersedes DEC-001
## [2026-04-14] status | DEC-001 validated→superseded
## [2026-04-14] status | GAP-001 open→resolved
## [2026-04-14] status | DEC-002 open→validated
## [2026-04-15] create | GAP-002 derives_from DEC-002
## [2026-04-15] lint   | 0 errors, 0 warnings
