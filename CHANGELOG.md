# Changelog

All notable changes to EKP are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## Versioning

One version number covers the whole repo: the specification, the
templates, the commands and the scripts. They implement the same
contract, so they are released together. Separate numbers would need a
compatibility table that nobody would keep up to date.

Versions follow [Semantic Versioning](https://semver.org/), read as the
version of a **format**:

- **MAJOR**: a bundle that conformed to the previous version no longer
  does and needs a migration (a renamed field, a removed category, a
  changed edge vocabulary).
- **MINOR**: new capabilities that existing bundles can ignore (a new
  script, a new optional field, a new lint check that only warns).
- **PATCH**: fixes and documentation, with no change to the contract.

Until 1.0, the format is still settling: a breaking change bumps MINOR
and is listed under **Breaking** in its entry.

Each release is an annotated git tag `vX.Y.Z` on the commit that closes
its entry. This file and the tags are the only places that carry the
version: the specification, templates and scripts don't repeat it.

A project records the version it was installed from with
`git -C path/to/ekp describe --tags` (see the README). Between releases
this prints something like `v0.2.0-9-gc5e1b23`, which still pins the
exact commit.

## [Unreleased]

### Added
- `scripts/ekp_index.py`: the computed index is built from frontmatter
  deterministically (per-status listings, per-area groupings,
  back-references, Mermaid graph). `--check` reports a stale index.
- `scripts/ekp_usage.py`: a SessionEnd hook that appends one usage line
  per session to the bundle log, computed from the Claude Code
  transcript (#8).
- Linter: `resolves` on a non-decision or settling a non-gap, index
  statuses compared against frontmatter, log cross-checks (#9).
- `tests/`: contract tests for lint, index and usage, with a clean
  example and a dirty fixture.
- SPEC §1 opens with the founding question. README: "system at a
  glance" diagrams.
- This changelog, and a single versioning scheme.
- `ekp_version` in the `ekp-config` block: the EKP version a bundle was
  installed from (#17).

### Changed
- Install steps copy `templates/`, which `/wrap-up` needs (#17).
- `/wrap-up` stops when a template is missing instead of improvising
  the frontmatter (#17).
- Version numbers removed from SPEC and scripts. Lint messages cite
  SPEC sections instead.

### Removed
- The Italian section of the README.

## [0.2.0] - 2026-11-04

First public release. Informed by a field audit of a real bundle
(77 files, 200 edges) and by the LLM Wiki pattern (Karpathy, 2026).

### Breaking
- `type` is now the bare epistemic category. `area` carries domain
  semantics (SPEC §3, §4.1).
- `decisions/` is flat: decision subtypes are removed (§4.1).
- The edge vocabulary is fixed at three types (`derives_from`,
  `supersedes`, `resolves`) with path targets. Back-references are
  computed, never stored (§5).

### Added
- A seventh category, `insight` (§4.1).
- Operations and layer contracts (§8): `/state` and `/wrap-up`,
  `ekp-config` bundle schema, linter `ekp_lint.py`.
- Synthetic example bundle `examples/neighbourhood-library`.

### Changed
- `semantic_tags` is tolerated at every level, required only at L3 (§6).

## 0.1.0 - 2026-06-18

Initial draft of the specification. Not published in this repository.

[Unreleased]: ../../compare/v0.2.0...HEAD
[0.2.0]: ../../releases/tag/v0.2.0
