# Example bundle — neighbourhood library

A synthetic EKP bundle at level L2: a neighbourhood library redesigns how
its four study rooms are booked. Nothing here comes from a real project.

What to look at:

1. **A decision built on an assumption that fails.** `DEC-001` derives
   from `ASS-001` (people book ahead). Research (`INS-001`) shows most
   requests are walk-ins; `ASS-001` becomes `invalidated`.
2. **A decision that replaces another without deleting it.** `DEC-002`
   `supersedes` `DEC-001`. `DEC-001` keeps its edges: the record of why it
   was taken stays.
3. **A decision that resolves a gap and opens another.** `DEC-002`
   `resolves` `GAP-001`; `GAP-002` `derives_from` `DEC-002`.
4. **A constraint as a criterion.** `CON-001` (card number only) is
   stated so that a reviewer, human or agent, can check any solution
   against it.
5. **Views and log.** `decisions/_index.md` computes the back-references;
   `log.md` records every status transition.

Run the linter from the repository root:

```bash
python3 scripts/ekp_lint.py examples/neighbourhood-library
```
