#!/usr/bin/env python3
"""ekp_lint.py — deterministic lint for an EKP bundle (EKP v0.2, SPEC §8.5).

Read-only. Checks the scripted floor per conformance level:
  L0: YAML parses; `type` present and in the epistemic vocabulary.
  L1: `id` present/well-formed/unique; folder matches category; `status`
      valid for the category lifecycle.
  L2: edge targets exist (dangling -> warning); no bidirectional edges;
      edge targets are paths, not bare IDs; legacy edge fields flagged.
  Views: decision ids missing from the index (stale view -> warning).

Semantic judgment (duplicates, edge misclassification) is agent work and
is deliberately out of scope: scripts do bookkeeping, models do judgment.

Usage: python3 ekp_lint.py BUNDLE_ROOT [--json]
Exit code: 0 clean, 1 warnings only, 2 errors.
"""
import re, sys, json
from pathlib import Path

CATEGORIES = {
    "gap":        ("GAP", "concept/gaps",         ["open", "partial", "resolved"]),
    "assumption": ("ASS", "concept/assumptions",  ["open", "partially_validated", "validated", "invalidated"]),
    "opportunity":("OPP", "concept/opportunities",["unexplored", "exploring", "committed"]),
    "hypothesis": ("HYP", "concept/hypotheses",   ["untested", "supported", "refuted"]),
    "constraint": ("CON", "concept/constraints",  ["active", "removed"]),
    "insight":    ("INS", "concept/insights",     ["active"]),
    "decision":   ("DEC", "decisions",            ["open", "validated", "invalidated"]),
}
EDGE_FIELDS = ["derives_from", "supersedes", "resolves"]
LEGACY_EDGE_FIELDS = ["related_concept", "related_decisions", "resolved_by", "superseded_by", "validates", "triggers"]
ID_RE = re.compile(r"^(GAP|ASS|OPP|HYP|CON|INS|DEC)-\d{3}$")
BARE_ID_RE = re.compile(r"^(?:GAP|ASS|OPP|HYP|CON|INS|DEC)-\d{3}$")

def strip_comment(line):
    """Drop a YAML comment: `#` at line start or after whitespace, outside quotes."""
    quote = None
    for i, c in enumerate(line):
        if quote:
            if c == quote: quote = None
        elif c in "\"'":
            quote = c
        elif c == "#" and (i == 0 or line[i - 1] in " \t"):
            return line[:i].rstrip()
    return line

def parse_frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n?", text, re.S)
    if not m: return None
    d, key = {}, None
    for line in map(strip_comment, m.group(1).splitlines()):
        if re.match(r"^[A-Za-z_]+\s*:", line):
            key, _, val = line.partition(":")
            key = key.strip()
            val = val.strip()
            if val.startswith("[") and val.endswith("]"):
                d[key] = [x.strip() for x in val[1:-1].split(",") if x.strip()]
            else:
                d[key] = [val] if val else []
        elif key and line.strip().startswith("- "):
            d[key].append(line.strip()[2:].strip())
    return d

def first(fm, key):
    v = fm.get(key, [])
    return v[0] if v else ""

def main():
    root = Path(sys.argv[1])
    findings = []
    def err(level, path, msg): findings.append(("ERROR", level, str(path), msg))
    def warn(level, path, msg): findings.append(("WARNING", level, str(path), msg))

    files, ids = {}, {}
    perimeter = [p for pat in ("concept/*/*.md", "decisions/**/*.md")
                 for p in sorted(root.glob(pat)) if not p.name.startswith("_")]

    for p in perimeter:
        rel = p.relative_to(root).as_posix()
        fm = parse_frontmatter(p.read_text(errors="replace"))
        if fm is None:
            err("L0", rel, "no parseable YAML frontmatter"); continue
        files[rel] = fm
        t = first(fm, "type")
        if not t:
            err("L0", rel, "missing `type`"); continue
        if t not in CATEGORIES:
            err("L0", rel, f"`type: {t}` not in epistemic vocabulary {sorted(CATEGORIES)}")
            continue
        prefix, folder, lifecycle = CATEGORIES[t]
        fid = first(fm, "id")
        if not fid:
            err("L1", rel, "missing `id`")
        elif not ID_RE.match(fid):
            err("L1", rel, f"malformed id `{fid}` (expected PREFIX-NNN)")
        else:
            if fid in ids: err("L1", rel, f"duplicate id `{fid}` (also in {ids[fid]})")
            else: ids[fid] = rel
            if not fid.startswith(prefix):
                err("L1", rel, f"id prefix of `{fid}` does not match type `{t}` (expected {prefix}-NNN)")
        if not rel.startswith(folder + "/"):
            err("L1", rel, f"file not in folder matching category: expected under `{folder}/`")
        if t == "decision" and rel.count("/") > 1:
            warn("L1", rel, "decisions/ should be flat (v0.2): file is in a subfolder")
        status = first(fm, "status")
        if not status:
            err("L1", rel, "missing `status`")
        elif status != "superseded" and status not in lifecycle:
            # `superseded` is a universal terminal status (SPEC 4.2)
            err("L1", rel, f"`status: {status}` not in {t} lifecycle {lifecycle} (nor universal `superseded`)")
        for lf in LEGACY_EDGE_FIELDS:
            if fm.get(lf):
                warn("L2", rel, f"legacy edge field `{lf}` present (v0.2 vocabulary: {EDGE_FIELDS})")

    edge_pairs = set()
    for rel, fm in files.items():
        for field in EDGE_FIELDS:
            for target in fm.get(field, []):
                if not target: continue
                if BARE_ID_RE.match(target):
                    warn("L2", rel, f"`{field}: {target}` is a bare ID; targets must be root-relative paths")
                    tgt_rel = ids.get(target, "")
                else:
                    tgt_rel = target.lstrip("/")
                    if not (root / tgt_rel).exists():
                        warn("L2", rel, f"dangling edge `{field}: {target}` (target not found — may be not-yet-written knowledge)")
                src_id = first(fm, "id")
                tgt_id = first(files.get(tgt_rel, {}), "id") if tgt_rel else ""
                if src_id and tgt_id:
                    if (tgt_id, src_id) in edge_pairs:
                        err("L2", rel, f"bidirectional edge {src_id}<->{tgt_id}: edges are stored downstream only")
                    edge_pairs.add((src_id, tgt_id))

    idx = root / "decisions" / "_index.md"
    if idx.exists():
        idx_text = idx.read_text(errors="replace")
        for fid, rel in ids.items():
            if fid.startswith("DEC") and fid not in idx_text:
                warn("VIEWS", "decisions/_index.md", f"{fid} ({rel}) missing from index — stale view")

    errors = [f for f in findings if f[0] == "ERROR"]
    warnings = [f for f in findings if f[0] == "WARNING"]
    if "--json" in sys.argv:
        print(json.dumps({"files": len(files), "errors": errors, "warnings": warnings}, indent=1))
    else:
        print(f"# ekp_lint — {root.name}")
        print(f"Files in perimeter: {len(perimeter)} | Errors: {len(errors)} | Warnings: {len(warnings)}\n")
        for sev, level, path, msg in findings:
            print(f"- [{sev}/{level}] {path}: {msg}")
    sys.exit(2 if errors else (1 if warnings else 0))

if __name__ == "__main__":
    main()
