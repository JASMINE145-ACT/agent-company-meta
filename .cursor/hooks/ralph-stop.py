"""Ralph Loop stop hook — project copy (Windows + workspace discovery).

Reads `.cursor/ralph/scratchpad.md` and emits `followup_message` on stdout so
Cursor continues the agent loop after each turn.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from ralph_common import (
    claim_event,
    cleanup_state,
    emit_followup,
    log_debug,
    parse_scratchpad,
    ralph_state_dir,
    resolve_scratchpad,
)


def main() -> None:
    try:
        raw_bytes = sys.stdin.buffer.read()
    except AttributeError:
        raw_bytes = sys.stdin.read().encode("utf-8", errors="replace")
    raw_input = raw_bytes.decode("utf-8-sig", errors="replace")
    try:
        payload = json.loads(raw_input)
    except (json.JSONDecodeError, ValueError):
        payload = {}

    state_file = resolve_scratchpad(payload)
    if state_file is None or not state_file.is_file():
        return

    state_dir = ralph_state_dir(state_file)
    event_id = payload.get("generation_id") or payload.get("conversation_id")
    if not claim_event(state_dir, "stop", event_id):
        return

    done_flag = state_dir / "done"

    raw = state_file.read_text(encoding="utf-8-sig")
    data, prompt_text = parse_scratchpad(raw)
    if not data:
        print("Ralph loop: state file corrupted (no frontmatter). Stopping.", file=sys.stderr)
        cleanup_state(state_file, done_flag)
        return

    iteration = (data.get("iteration") or "").strip()
    max_iterations = (data.get("max_iterations") or "").strip()
    completion_promise = (data.get("completion_promise") or "").strip()

    if not iteration.isdigit():
        print(f"Ralph loop: state file corrupted (iteration: {iteration!r}). Stopping.", file=sys.stderr)
        cleanup_state(state_file, done_flag)
        return
    if not max_iterations.isdigit():
        print(f"Ralph loop: state file corrupted (max_iterations: {max_iterations!r}). Stopping.", file=sys.stderr)
        cleanup_state(state_file, done_flag)
        return

    it = int(iteration)
    mx = int(max_iterations)

    if done_flag.is_file():
        log_debug(f"Ralph loop: completion promise fulfilled at iteration {it}.")
        cleanup_state(state_file, done_flag)
        return

    if mx > 0 and it >= mx:
        log_debug(f"Ralph loop: max iterations ({mx}) reached.")
        cleanup_state(state_file, done_flag)
        return

    prompt_text = prompt_text.strip("\n")
    if not prompt_text:
        print("Ralph loop: no prompt text found in state file. Stopping.", file=sys.stderr)
        cleanup_state(state_file, done_flag)
        return

    next_iteration = it + 1
    new_raw = re.sub(
        r"^iteration:\s*\d+\s*$",
        f"iteration: {next_iteration}",
        raw,
        count=1,
        flags=re.MULTILINE,
    )
    state_file.write_text(new_raw, encoding="utf-8")

    if completion_promise and completion_promise.lower() != "null":
        header = (
            f"[Ralph loop iteration {next_iteration}. "
            f"To complete: output <promise>{completion_promise}</promise> ONLY when genuinely true.]"
        )
    else:
        header = f"[Ralph loop iteration {next_iteration}.]"

    emit_followup(f"{header}\n\n{prompt_text}")


if __name__ == "__main__":
    main()
