#!/usr/bin/env python3
"""ekp_lint.py — deterministic lint for an EKP bundle (EKP v0.2, SPEC §8.5).

Read-only. Checks the scripted floor per conformance level:
  L0: YAML parses; `type` present and in the epistemic vocabulary.
  L1: `id` present/well-formed/unique; folder matches category; `status`
      valid for the category lifecycle.
  L2: edge targets exist (dangling -> warning); no bidirectional edges;
      edge targets are paths, not bare IDs; legacy edge fields flagged;
      `resolves` stored on a non-decision (error) or settling a non-gap
      (warning).
  Views: ids missing from the index, and index statuses that disagree
      with file frontmatter (stale view -> warning).
  Log: `create` events whose id has no file, and file statuses that
      differ from the last logged transition (-> warning).

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
ID_RE = re.compile(r"^(GAP|ASS|OPP|HYP|CON|INS|DEC)-\d{3,}$")
BARE_ID_RE = re.compile(r"^(?:GAP|ASS|OPP|HYP|CON|INS|DEC)-\d{3,}$")
ANY_ID_RE = re.compile(r"(?:GAP|ASS|OPP|HYP|CON|INS|DEC)-\d+")

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

def unquote(s):
    if len(s) >= 2 and s[0] == s[-1] and s[0] in "\"'":
        return s[1:-1]
    return s

def parse_frontmatter(text):
    """Hand-rolled YAML subset parser: the scripts must run on a bare
    Python 3 with no PyYAML. It covers exactly what EKP frontmatter uses —
    scalars, inline lists, dash lists — and nothing nested."""
    m = re.match(r"^---\n(.*?)\n---\n?", text, re.S)
    if not m: return None
    d, key = {}, None
    for line in map(strip_comment, m.group(1).splitlines()):
        if re.match(r"^[A-Za-z_]+\s*:", line):
            key, _, val = line.partition(":")
            key = key.strip()
            val = val.strip()
            if val.startswith("[") and val.endswith("]"):
                d[key] = [unquote(x.strip()) for x in val[1:-1].split(",") if x.strip()]
            else:
                d[key] = [unquote(val)] if val else []
        elif key and line.strip().startswith("- "):
            d[key].append(unquote(line.strip()[2:].strip()))
    return d

def first(fm, key):
    v = fm.get(key, [])
    return v[0] if v else ""

def perimeter(root):
    """The files under the bundle perimeter (SPEC §10), `_`-prefixed views excluded."""
    return [p for pat in ("concept/*/*.md", "decisions/**/*.md")
            for p in sorted(Path(root).glob(pat)) if not p.name.startswith("_")]

def lint(root):
    """Lint the bundle at `root`; return findings as (severity, level, path, message)."""
    root = Path(root)
    findings = []
    def err(level, path, msg): findings.append(("ERROR", level, str(path), msg))
    def warn(level, path, msg): findings.append(("WARNING", level, str(path), msg))

    # --- Per-file checks (L0 vocabulary, L1 id/folder/status) ---
    files, ids = {}, {}
    for p in perimeter(root):
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

    # --- Edge checks (L2): vocabulary, path targets, single direction ---
    edge_pairs = set()
    for rel, fm in files.items():
        t = first(fm, "type")
        if fm.get("resolves") and t in CATEGORIES and t != "decision":
            err("L2", rel, f"`resolves` stored on a {t}: SPEC §5.2 reserves it for decisions")
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
                if field == "resolves" and tgt_rel in files:
                    tt = first(files[tgt_rel], "type")
                    if tt and tt in CATEGORIES and tt != "gap":
                        warn("L2", rel, f"`resolves` target `{target}` is a {tt}; SPEC §5.2 defines resolves as settling gaps")
                src_id = first(fm, "id")
                tgt_id = first(files.get(tgt_rel, {}), "id") if tgt_rel else ""
                if src_id and tgt_id:
                    if (tgt_id, src_id) in edge_pairs:
                        err("L2", rel, f"bidirectional edge {src_id}<->{tgt_id}: edges are stored downstream only")
                    edge_pairs.add((src_id, tgt_id))

    # --- Views: the index must agree with frontmatter (SPEC §8.5).
    # Presence of concept items is checked only when the index has a
    # concept section: a decisions-only index is legitimate (§5.4).
    idx = root / "decisions" / "_index.md"
    if idx.exists():
        idx_text = idx.read_text(errors="replace")
        lists_concept = "## Concept items" in idx_text
        idx_status = {}
        for m in re.finditer(r"^\|\s*(" + ANY_ID_RE.pattern + r")\s*\|(.+)$", idx_text, re.M):
            cells = [c.strip() for c in m.group(2).strip().strip("|").split("|")]
            if len(cells) >= 2:
                idx_status[m.group(1)] = cells[1]
        for fid, rel in ids.items():
            if (fid.startswith("DEC") or lists_concept) and fid not in idx_text:
                warn("VIEWS", "decisions/_index.md", f"{fid} ({rel}) missing from index — stale view")
            st = first(files[rel], "status")
            if fid in idx_status and st and idx_status[fid] != st:
                warn("VIEWS", "decisions/_index.md",
                     f"index lists {fid} as `{idx_status[fid]}` but file says `{st}` — stale view")

    # --- Log vs files: the log records events, files record state (§8.4);
    # they must not contradict each other. Only the LAST transition per id
    # is compared, since earlier ones are legitimately outdated history.
    logf = root / "log.md"
    if logf.exists():
        log_text = logf.read_text(errors="replace")
        for m in re.finditer(r"^##\s*\[[^\]]+\]\s*create\s*\|\s*(" + ANY_ID_RE.pattern + r")", log_text, re.M):
            if m.group(1) not in ids:
                warn("LOG", "log.md", f"{m.group(1)} created in log but has no file in the bundle")
        last = {}
        for m in re.finditer(r"^##\s*\[[^\]]+\]\s*status\s*\|\s*(" + ANY_ID_RE.pattern +
                             r")\s+(\S+?)\s*(?:→|->)\s*(\S+)", log_text, re.M):
            last[m.group(1)] = m.group(3)
        for fid, to in last.items():
            if fid in ids:
                st = first(files[ids[fid]], "status")
                if st and st != to:
                    warn("LOG", "log.md", f"last logged transition moves {fid} to `{to}` but file says `{st}`")

    return findings

def main():
    root = Path(sys.argv[1])
    findings = lint(root)
    n_files = len(perimeter(root))
    errors = [f for f in findings if f[0] == "ERROR"]
    warnings = [f for f in findings if f[0] == "WARNING"]
    if "--json" in sys.argv:
        print(json.dumps({"files": n_files, "errors": errors, "warnings": warnings}, indent=1))
    else:
        print(f"# ekp_lint — {root.name}")
        print(f"Files in perimeter: {n_files} | Errors: {len(errors)} | Warnings: {len(warnings)}\n")
        for sev, level, path, msg in findings:
            print(f"- [{sev}/{level}] {path}: {msg}")
    sys.exit(2 if errors else (1 if warnings else 0))

if __name__ == "__main__":
    main()
