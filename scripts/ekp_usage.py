#!/usr/bin/env python3
"""ekp_usage.py — deterministic token accounting for EKP operations.

Appends one grep-parseable `usage` line per session to the bundle log:

  ## [2026-11-13] usage | session 7b5e2508 | ops: /wrap-up×1 | tokens: 124.3k in / 8.1k out / 1.2M cache-read | model: claude-…

No model is involved: the numbers come from the session transcript's
usage records (the JSONL file Claude Code writes under ~/.claude/projects/).
Scripts do the bookkeeping; this is bookkeeping.

Designed to run as a Claude Code SessionEnd hook — add to the adopting
project's .claude/settings.json:

    {"hooks": {"SessionEnd": [{"hooks": [
        {"type": "command", "command": "python3 scripts/ekp_usage.py"}]}]}}

Behavior:
- The log path comes from --log, else from the `log:` entry of the
  `# ekp-config` block in CLAUDE.md / AGENTS.md, else `log.md` — all
  relative to --root (default: the hook's cwd). If the log file does not
  exist the script exits 0 without writing, so the hook is safe to
  configure even in projects without an EKP bundle.
- Idempotent per session: if the log already carries this session's line
  with the same totals, nothing is appended. If the totals grew (resumed
  session), a new line is appended — the log is append-only, latest wins.
- `ops` counts the EKP commands seen in the session (/state, /wrap-up,
  /resume); `-` when none ran.
- Always exits 0 in hook mode: accounting must never block a session.

Usage:
  python3 ekp_usage.py                                   # as a hook (JSON on stdin)
  python3 ekp_usage.py --transcript T.jsonl [--root DIR] [--log PATH] [--dry-run]
"""
import json, re, sys
from datetime import date
from pathlib import Path

EKP_OPS = {"/state", "/wrap-up", "/resume"}
COMMAND_RE = re.compile(r"<command-name>([^<]+)</command-name>")


def summarize(transcript_path):
    """Sum usage records and count EKP command invocations in a transcript."""
    tot = {"in": 0, "out": 0, "cache_read": 0, "cache_create": 0}
    models, ops = {}, {}
    for line in Path(transcript_path).read_text(errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except ValueError:
            continue
        msg = obj.get("message") or {}
        usage = msg.get("usage")
        if obj.get("type") == "assistant" and usage:
            tot["in"] += usage.get("input_tokens") or 0
            tot["out"] += usage.get("output_tokens") or 0
            tot["cache_read"] += usage.get("cache_read_input_tokens") or 0
            tot["cache_create"] += usage.get("cache_creation_input_tokens") or 0
            if msg.get("model"):
                # A session can touch several models (subagents, fast mode);
                # the reported one is whichever produced the most output.
                models[msg["model"]] = models.get(msg["model"], 0) + (usage.get("output_tokens") or 0)
        if obj.get("type") == "user":
            # Only the text the user typed: tool results also travel as
            # `user` entries and may quote command tags verbatim.
            content = msg.get("content")
            texts = [content] if isinstance(content, str) else \
                    [b.get("text", "") for b in content or [] if isinstance(b, dict) and b.get("type") == "text"]
            for name in COMMAND_RE.findall("\n".join(texts)):
                if name in EKP_OPS:
                    ops[name] = ops.get(name, 0) + 1
    return tot, models, ops


def fmt(n):
    if n >= 1_000_000: return f"{n / 1_000_000:.1f}M"
    if n >= 1_000: return f"{n / 1_000:.1f}k"
    return str(n)


def usage_line(day, session, tot, models, ops):
    ops_s = ", ".join(f"{k}×{v}" for k, v in sorted(ops.items())) or "-"
    model = max(models, key=models.get) if models else "-"
    return (f"## [{day}] usage | session {session} | ops: {ops_s} | "
            f"tokens: {fmt(tot['in'])} in / {fmt(tot['out'])} out / "
            f"{fmt(tot['cache_read'])} cache-read | model: {model}")


def find_log(root):
    """The log declared in the ekp-config block (SPEC §8.1), else log.md."""
    for name in ("CLAUDE.md", "AGENTS.md"):
        p = root / name
        if p.exists():
            m = re.search(r"```yaml\s*\n#\s*ekp-config(.*?)```", p.read_text(errors="replace"), re.S)
            if m:
                lm = re.search(r"^log:\s*(\S+)", m.group(1), re.M)
                if lm:
                    return root / lm.group(1)
    return root / "log.md"


def arg(flag):
    return sys.argv[sys.argv.index(flag) + 1] if flag in sys.argv else None


def main():
    transcript, session_id, hook_mode = arg("--transcript"), None, False
    root = Path(arg("--root") or ".")
    if not transcript:
        if sys.stdin.isatty():
            sys.exit(__doc__.strip())
        hook_mode = True
        try:
            data = json.load(sys.stdin)
            transcript = data.get("transcript_path")
            session_id = data.get("session_id")
            if "--root" not in sys.argv and data.get("cwd"):
                root = Path(data["cwd"])
        except ValueError:
            print("ekp_usage: no valid hook JSON on stdin", file=sys.stderr)
            sys.exit(0)
    if not transcript or not Path(transcript).exists():
        print(f"ekp_usage: transcript not found: {transcript}", file=sys.stderr)
        sys.exit(0 if hook_mode else 1)

    session = (session_id or Path(transcript).stem)[:8]
    tot, models, ops = summarize(transcript)
    line = usage_line(date.today().isoformat(), session, tot, models, ops)

    log_arg = arg("--log")
    log = Path(log_arg) if log_arg else find_log(root)
    if log_arg and not log.is_absolute():
        log = root / log
    if "--dry-run" in sys.argv:
        print(line)
        print(f"(dry run — would append to {log})")
        return
    if not log.exists():
        print(f"ekp_usage: no log at {log}; nothing written", file=sys.stderr)
        sys.exit(0)
    body = line.partition("] ")[2]  # idempotency ignores the date
    if any(ln.rstrip().endswith(body) for ln in log.read_text(errors="replace").splitlines()):
        return
    with log.open("a") as f:
        f.write(line + "\n")
    print(f"appended to {log}: {line}")


if __name__ == "__main__":
    main()
