"""Shared helpers for Ralph Loop project hooks."""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path


def log_debug(message: str) -> None:
    if os.environ.get("RALPH_DEBUG", "").strip().lower() in {"1", "true", "yes"}:
        print(message, file=sys.stderr, flush=True)


def normalise_root(raw: str) -> Path:
    raw = raw.replace("\\", "/")
    if raw.startswith("file://"):
        raw = raw[7:]
    if re.match(r"^/[a-zA-Z]:/", raw):
        raw = raw[1:]
    return Path(raw)


def parse_scratchpad(content: str) -> tuple[dict[str, str] | None, str]:
    text = content.lstrip("\ufeff").replace("\r\n", "\n")
    lines = text.split("\n")
    if not lines or lines[0] != "---":
        return None, ""
    fm_lines: list[str] = []
    i = 1
    while i < len(lines):
        if lines[i] == "---":
            break
        fm_lines.append(lines[i])
        i += 1
    else:
        return None, ""
    body = "\n".join(lines[i + 1 :])
    data: dict[str, str] = {}
    for line in fm_lines:
        if ":" not in line:
            continue
        k, _, v = line.partition(":")
        k, v = k.strip(), v.strip()
        if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
            v = v[1:-1]
        data[k] = v
    return data, body


def candidate_workspace_roots(payload: dict | None = None) -> list[str]:
    roots: list[str] = []
    seen: set[str] = set()
    payload = payload or {}

    def add(raw: str | None) -> None:
        if not raw or not str(raw).strip():
            return
        s = str(raw).strip()
        if s not in seen:
            seen.add(s)
            roots.append(s)

    for r in payload.get("workspace_roots") or []:
        add(r)
    add(payload.get("workspace_root"))
    add(os.environ.get("CURSOR_PROJECT_DIR"))
    try:
        add(str(Path.cwd().resolve()))
    except OSError:
        pass
    return roots


def find_scratchpad_in_roots(workspace_roots: list[str]) -> Path | None:
    for raw in workspace_roots:
        p = normalise_root(raw) / ".cursor" / "ralph" / "scratchpad.md"
        if p.is_file():
            return p
    return None


def find_scratchpad_upwards(start: Path, *, max_up: int = 32) -> Path | None:
    cur = start.resolve()
    for _ in range(max_up):
        candidate = cur / ".cursor" / "ralph" / "scratchpad.md"
        if candidate.is_file():
            return candidate
        parent = cur.parent
        if parent == cur:
            break
        cur = parent
    return None


def resolve_scratchpad(payload: dict | None = None) -> Path | None:
    found = find_scratchpad_in_roots(candidate_workspace_roots(payload))
    if found is not None:
        return found
    hook_dir = Path(__file__).resolve().parent
    for start in (Path.cwd(), hook_dir, hook_dir.parent.parent):
        try:
            p = find_scratchpad_upwards(start)
        except OSError:
            p = None
        if p is not None:
            log_debug(f"ralph-loop: scratchpad via upward search {p}")
            return p
    return None


def ralph_state_dir(scratchpad: Path) -> Path:
    return scratchpad.parent


def claim_event(state_dir: Path, prefix: str, event_id: str | None) -> bool:
    """Return True if this hook invocation should run (first claimant)."""
    if not event_id:
        return True
    safe = re.sub(r"[^\w.-]+", "_", event_id)[:120]
    lock = state_dir / f".{prefix}-{safe}"
    try:
        lock.touch(exist_ok=False)
        return True
    except FileExistsError:
        log_debug(f"ralph-loop: skip duplicate {prefix} for {event_id}")
        return False


def cleanup_state(state_file: Path, done_flag: Path) -> None:
    state_dir = state_file.parent
    state_file.unlink(missing_ok=True)
    done_flag.unlink(missing_ok=True)
    for lock in state_dir.glob(".*"):
        name = lock.name
        if name.startswith(".stop-") or name.startswith(".capture-"):
            lock.unlink(missing_ok=True)


def response_text_from_payload(payload: dict) -> str:
    for key in ("text", "response", "message", "content", "assistant_message"):
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            return value
    return ""


def emit_followup(followup: str) -> None:
    print(json.dumps({"followup_message": followup}, ensure_ascii=False), flush=True)
