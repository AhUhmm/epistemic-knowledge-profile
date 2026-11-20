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

An action an upgrade needs that isn't a breaking change (for example,
regenerating the index once) is listed under **Upgrade notes**. On
upgrade, a bundle applies every Breaking item and every upgrade note in
the entries newer than its `ekp_version` (SPEC §8.1).

Each release is an annotated git tag `vX.Y.Z` on the commit that closes
its entry. This file and the tags are the only places that carry the
version: the specification, templates and scripts don't repeat it.

A project records the version it was installed from with
`git -C path/to/ekp describe --tags --always` (see the README). Between
releases this prints something like `v0.2.0-9-g<hash>`, which still pins
the exact commit, as long as it was installed from a tag or from `main`.

## [Unreleased]

### Changed
- README "system at a glance": the diagrams say who runs the scripts
  (the agent, at wrap-up), that the gate is a working agreement, and that
  the usage hook is optional, Claude Code only, and counts tokens.

## [0.3.1] - 2026-11-20

Installation fixes from the first real install of 0.3.0 (#22, step 1),
and documentation. No change to the format.

### Upgrade notes
- Regenerate the index once: `python3 scripts/ekp_index.py .`. Its title
  line changes, so `--check` reports it stale until you do.

### Added
- An **Upgrade notes** section in changelog entries, for actions an
  upgrade needs that aren't breaking. SPEC §8.1's upgrade rule now covers
  them alongside Breaking items.
- `docs/how-it-works.md`: EKP explained for non-technical readers, with
  diagrams of the project layout, the links between notes (on the
  example bundle), a working session, and who checks what.
- Install step 6: check the install (folders, lint, index,
  `ekp_version`).

### Changed
- Install steps state the Python version (3.9 or later), put a
  `.gitkeep` in every layer folder so git keeps them while empty, and say
  exactly what to copy from `SCHEMA_template.md` and which placeholders
  to replace.
- The install commands set the two folder paths once and `cd`
  explicitly, so the block works when pasted, even with spaces in paths.
- The README warns about file clashes before the copy step, and explains
  how to merge the usage hook into existing settings, including an
  existing `SessionEnd` entry.

### Fixed
- `ekp_index.py` no longer leaves `scripts/__pycache__/` in the project.
- The index title no longer contains the bundle folder's name, so a
  clone in a differently named folder no longer fails `--check`.

## [0.3.0] - 2026-11-19

### Added
- `scripts/ekp_index.py`: the computed index is built from frontmatter
  deterministically (per-status listings, per-area groupings,
  back-references, Mermaid graph). `--check` reports a stale index.
- `scripts/ekp_usage.py`: a SessionEnd hook that appends a usage line to
  the bundle log, computed from the Claude Code transcript (#8). Repeats
  with unchanged totals are skipped; a resumed session appends its
  updated totals, and the latest line wins.
- Linter: `resolves` on a non-decision or settling a non-gap, index
  statuses compared against frontmatter, log cross-checks (#9).
- `tests/`: contract tests for lint, index and usage, with a clean
  example and a dirty fixture.
- SPEC §1 opens with the founding question. README: "system at a
  glance" diagrams.
- This changelog, and a single versioning scheme.
- `ekp_version` in the `ekp-config` block: the EKP version a bundle was
  installed from (#17). SPEC §8.1 states the upgrade rule that uses it.

### Changed
- Install steps copy `templates/`, which `/wrap-up` needs (#17).
- `/wrap-up` stops when a template is missing instead of improvising
  the frontmatter (#17).
- Install step 4 creates `log.md` and the first index, which `/state`
  reads on the first session. The version is captured with
  `describe --tags --always`, with a fallback for ZIP downloads.
- SPEC §8.1 and the schema template say what actually reads
  `ekp-config`: the scripts read only `log` so far (see #19).
- Version numbers removed from SPEC and scripts. Lint messages cite
  SPEC sections instead.

### Fixed
- The linter header names the bundle when run on `.`.
- Quoted frontmatter values are unquoted before checking.
- IDs and bare-ID references accept three or more digits (`DEC-1000`),
  not exactly three.
- `--json` reports the same `files` count as the text output: every file
  in the perimeter, including those whose frontmatter can't be read.
- SPEC §8.5 lists the checks the linter runs, and says precisely what
  each one covers.

### Removed
- The Italian section of the README.

## [0.2.0] - 2026-11-04

First public release. Tagged retroactively: the tag points to the
release commit, and this entry was written afterwards. Informed by a
field audit of a real bundle (77 files, 200 edges) and by the LLM Wiki pattern (Karpathy, 2026).

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

[Unreleased]: https://github.com/AhUhmm/epistemic-knowledge-profile/compare/v0.3.1...HEAD
[0.3.1]: https://github.com/AhUhmm/epistemic-knowledge-profile/compare/v0.3.0...v0.3.1
[0.3.0]: https://github.com/AhUhmm/epistemic-knowledge-profile/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/AhUhmm/epistemic-knowledge-profile/releases/tag/v0.2.0
