# afterAgentResponse hook for Ralph Loop — writes .cursor/ralph/done on completion promise.
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from ralph_common import (
    claim_event,
    parse_scratchpad,
    ralph_state_dir,
    resolve_scratchpad,
    response_text_from_payload,
)


def main() -> None:
    try:
        raw_bytes = sys.stdin.buffer.read()
    except AttributeError:
        raw_bytes = sys.stdin.read().encode("utf-8", errors="replace")
    raw_in = raw_bytes.decode("utf-8-sig", errors="replace")
    try:
        hook = json.loads(raw_in)
    except json.JSONDecodeError:
        return

    response_text = response_text_from_payload(hook)
    if not response_text:
        return

    state_file = resolve_scratchpad(hook)
    if state_file is None or not state_file.is_file():
        return

    state_dir = ralph_state_dir(state_file)
    event_id = hook.get("generation_id") or hook.get("conversation_id")
    if not claim_event(state_dir, "capture", event_id):
        return

    done_flag = state_dir / "done"

    data, _ = parse_scratchpad(state_file.read_text(encoding="utf-8-sig"))
    if not data:
        return

    completion = (data.get("completion_promise") or "").strip()
    if not completion or completion.lower() == "null":
        return

    m = re.search(r"<promise>(.*?)</promise>", response_text, re.DOTALL | re.IGNORECASE)
    if not m:
        return

    inner = re.sub(r"\s+", " ", m.group(1).strip())
    if inner == completion:
        state_dir.mkdir(parents=True, exist_ok=True)
        done_flag.touch()


if __name__ == "__main__":
    main()
