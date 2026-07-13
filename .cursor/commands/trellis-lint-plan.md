---
name: /trellis:lint-plan
id: trellis-lint-plan
category: Workflow
description: "Lint a Trellis execution-plan.md for required contract/TDD/verification structure"
---

Run:

```bash
python ./.trellis/scripts/lint_execution_plan.py .trellis/tasks/<task-dir>/execution-plan.md
```

If no task is named, resolve the current task first with:

```bash
python ./.trellis/scripts/task.py current --source
```

Fix structural failures before asking for approval, executing a phase, or claiming completion.
