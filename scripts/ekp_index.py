#!/usr/bin/env python3
"""ekp_index.py — regenerate the computed index of an EKP bundle (SPEC §5.4).

The index is a routing view, never a source of truth. This script computes
it deterministically from frontmatter — per-status listings, per-`area`
groupings, computed back-references, and a Mermaid rendering of the graph —
so the agent's wrap-up keeps only the judgment work. It never reads bodies.

Read-only on the bundle except for the index file it writes.
Python 3 standard library only.

Usage: python3 ekp_index.py BUNDLE_ROOT [--out PATH] [--check]
  --out PATH   index path relative to BUNDLE_ROOT (default: decisions/_index.md)
  --check      write nothing; exit 1 if the existing index is stale/missing
"""
import sys
from pathlib import Path

# Importing ekp_lint would leave scripts/__pycache__/ in the user's project.
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ekp_lint import parse_frontmatter, first, CATEGORIES, EDGE_FIELDS, BARE_ID_RE

# Routing order: items needing attention first, terminal states last.
STATUS_RANK = {
    "open": 0, "unexplored": 0, "untested": 0,
    "partial": 1, "partially_validated": 1, "exploring": 1,
    "supported": 2,
    "active": 3, "validated": 3, "committed": 3,
    "resolved": 4, "removed": 4, "refuted": 4,
    "invalidated": 5,
    "superseded": 6,
}
PREFIX_ORDER = ["GAP", "ASS", "OPP", "HYP", "CON", "INS", "DEC"]
BACKREF_VERB = {"derives_from": "derived by", "resolves": "resolved by",
                "supersedes": "superseded by"}
TERMINAL = {"superseded", "invalidated", "refuted", "removed", "resolved"}


def id_key(fid):
    prefix, _, num = fid.partition("-")
    order = PREFIX_ORDER.index(prefix) if prefix in PREFIX_ORDER else 99
    return (order, int(num) if num.isdigit() else 0)


def sort_key(item):
    fid, fm = item
    return (STATUS_RANK.get(first(fm, "status"), 9), id_key(fid))


def load_bundle(root):
    files = {}
    for pat in ("concept/*/*.md", "decisions/**/*.md"):
        for p in sorted(root.glob(pat)):
            if p.name.startswith("_"):
                continue
            fm = parse_frontmatter(p.read_text(errors="replace"))
            if fm and first(fm, "id"):
                files[p.relative_to(root).as_posix()] = fm
    return files


def build_index(root, files):
    ids = {first(fm, "id"): rel for rel, fm in files.items()}
    by_id = {first(fm, "id"): fm for fm in files.values()}

    decisions = sorted(((i, fm) for i, fm in by_id.items() if first(fm, "type") == "decision"), key=sort_key)
    concepts = sorted(((i, fm) for i, fm in by_id.items() if first(fm, "type") != "decision"), key=sort_key)

    # Edges: (downstream id, field, upstream id) — resolved from path or legacy bare ID.
    path_to_id = {rel: fid for fid, rel in ids.items()}
    edges = []
    for rel, fm in files.items():
        src = first(fm, "id")
        for field in EDGE_FIELDS:
            for target in fm.get(field, []):
                tgt = target if BARE_ID_RE.match(target) else path_to_id.get(target.lstrip("/"), "")
                if src and tgt in by_id:
                    edges.append((src, field, tgt))

    # Back-references materialize here what storage deliberately omits:
    # edges live only on the downstream node (SPEC §5.3), the index gives
    # the upstream node its reverse reading.
    backrefs = {}
    for src, field, tgt in edges:
        backrefs.setdefault(tgt, {}).setdefault(BACKREF_VERB[field], []).append(src)

    name = root.resolve().name.replace("-", " ")
    out = [f"# Index — {name} (computed view)", "",
           "<!-- Regenerated at wrap-up from frontmatter (scripts/ekp_index.py).",
           "Never edit by hand: if this file and a source file disagree, the",
           "source file wins (SPEC §5.4). -->", ""]

    out += ["## Decisions by status", "", "| ID | Title | Status | Area |", "|----|-------|--------|------|"]
    out += [f"| {i} | {first(fm, 'title')} | {first(fm, 'status')} | {first(fm, 'area')} |" for i, fm in decisions]

    out += ["", "## Concept items by status", "", "| ID | Title | Status |", "|----|-------|--------|"]
    out += [f"| {i} | {first(fm, 'title')} | {first(fm, 'status')} |" for i, fm in concepts]

    areas = {}
    for i, fm in sorted(by_id.items(), key=lambda kv: id_key(kv[0])):
        if first(fm, "area"):
            areas.setdefault(first(fm, "area"), []).append(i)
    out += ["", "## By area", ""]
    out += [f"- **{area}** — {', '.join(ids_)}" for area, ids_ in sorted(areas.items())]

    out += ["", "## Back-references (computed, never stored upstream)", ""]
    for tgt in sorted(backrefs, key=id_key):
        parts = [f"{verb} {', '.join(sorted(srcs, key=id_key))}"
                 for verb in ("derived by", "resolved by", "superseded by")
                 for srcs in [backrefs[tgt].get(verb)] if srcs]
        out.append(f"- {tgt} — {'; '.join(parts)}")

    out += ["", "## Graph (computed)", "", "```mermaid", "graph LR"]
    # Mermaid reserves `-` for edge syntax, so node ids use `_` and the
    # bracket label carries the real id.
    mid = lambda fid: fid.replace("-", "_")
    for i, fm in sorted(by_id.items(), key=lambda kv: id_key(kv[0])):
        out.append(f"  {mid(i)}[\"{i}\"]")
    for src, field, tgt in sorted(edges, key=lambda e: (id_key(e[0]), id_key(e[2]))):
        out.append(f"  {mid(src)} -- {field} --> {mid(tgt)}")
    terminal = [mid(i) for i, fm in by_id.items() if first(fm, "status") in TERMINAL]
    if terminal:
        out += ["  classDef terminal stroke-dasharray: 4 4,opacity:0.6;",
                f"  class {','.join(sorted(terminal))} terminal;"]
    out += ["```", ""]
    return "\n".join(out)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        sys.exit(__doc__.strip())
    root = Path(args[0])
    rel_out = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else "decisions/_index.md"
    out_path = root / rel_out

    text = build_index(root, load_bundle(root))
    current = out_path.read_text(errors="replace") if out_path.exists() else None
    if "--check" in sys.argv:
        if current == text:
            print(f"ok: {rel_out} is up to date")
            sys.exit(0)
        print(f"stale: {rel_out} does not match frontmatter — regenerate with ekp_index.py")
        sys.exit(1)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(text)
    print(f"wrote {out_path} ({len(text.splitlines())} lines)")


if __name__ == "__main__":
    main()
