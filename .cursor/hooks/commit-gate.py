#!/usr/bin/env python3
"""Cursor beforeShellExecution hook: commit-evidence gate.

Denies `git commit` when there is an active Trellis task and no verification
evidence has been recorded for it. See `.trellis/scripts/common/commit_gate.py`
for the shared decision logic (same module is reused by the Claude Code
adapter). Mirrors the stdin-parsing / env-escape-hatch style of
`.cursor/hooks/inject-shell-session-context.py`.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

DIR_WORKFLOW = ".trellis"


def _string_value(value: Any) -> str | None:
    if isinstance(value, str):
        stripped = value.strip()
        return stripped or None
    return None


def _find_trellis_root(start: Path) -> Path | None:
    current = start.resolve()
    while True:
        if (current / DIR_WORKFLOW).is_dir():
            return current
        if current == current.parent:
            return None
        current = current.parent


def _allow() -> None:
    print(json.dumps({"permission": "allow"}, ensure_ascii=False))


def main() -> int:
    if os.environ.get("TRELLIS_HOOKS") == "0" or os.environ.get("TRELLIS_DISABLE_HOOKS") == "1":
        return 0

    try:
        hook_input = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, ValueError):
        hook_input = {}
    if not isinstance(hook_input, dict):
        hook_input = {}

    command = _string_value(hook_input.get("command")) or ""
    if not command:
        _allow()
        return 0

    cwd_value = _string_value(hook_input.get("cwd")) or os.getcwd()
    root = _find_trellis_root(Path(cwd_value))
    if root is None:
        _allow()
        return 0

    scripts_dir = root / DIR_WORKFLOW / "scripts"
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))
    try:
        from common.commit_gate import evaluate_commit_gate  # type: ignore[import-not-found]
    except Exception as exc:
        print(
            f"[commit-gate] failed to import commit_gate, fail-open: {exc!r}",
            file=sys.stderr,
        )
        _allow()
        return 0

    decision, reason = evaluate_commit_gate(command, cwd_value, hook_input, "cursor", root)

    if decision == "deny":
        message = reason or "Trellis commit gate: evidence missing."
        print(
            json.dumps(
                {"permission": "deny", "userMessage": message, "agentMessage": message},
                ensure_ascii=False,
            )
        )
        return 0

    _allow()
    return 0


if __name__ == "__main__":
    sys.exit(main())
