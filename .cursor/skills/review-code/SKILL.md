---
name: review-code
description: Launch project code-reviewer with Layer A gates. Use after code changes, before tests.
---

# Review Code (platform code-reviewer)

Use when the user or Trellis gate requires **code-reviewer** on this repo.

## Launch

Exactly one `code-reviewer` subagent:

- `subagent_type: "code-reviewer"`
- `readonly: true`
- `run_in_background: false` unless user asks for background

Project agent: `.cursor/agents/code-reviewer.md`  
Canonical identity: `.cursor/rules/code-reviewer-agent.mdc`

## Prompt shape

```text
Full Repository Path: <absolute path to platform repo>
Diff: branch changes | uncommitted changes
Change Description: <optional — per-file bullets>
Custom Instructions: <only if user gave extra focus>
```

## Gate order

```text
code-reviewer PASS (Layer A; Layer B = N/A)
  → boundary scripts / unit tests
  → trellis docs / check.jsonl
```

## Spec pointers

- Layer A: `.trellis/spec/code-review-layer-a.md`
- Boundary smokes:

```powershell
node scripts/check-no-sample-import.mjs
node scripts/check-no-wanding-core-terms.mjs
```
