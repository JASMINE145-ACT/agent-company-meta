---
name: /trellis:plan-execution
id: trellis-plan-execution
category: Workflow
description: "Design Trellis task execution — workstream→tool mapping (Trellis/OpenSpec/ECC/Superpowers)"
---

Design a **phased execution plan** for the current or named Trellis task. **Planning only** — do not write application code until the user approves and says 执行 task / implement. **Design intent:** this command **composes real skills** from Trellis / OpenSpec / ECC / Superpowers — **load and run them in this session**, not only name them in `execution-plan.md`.

## Operating doctrine: Contract -> TDD -> Contract Verification

```text
Project layer: Contract-Driven
  Define the behavior contract(s) this task protects or changes.

Coding layer: TDD
  For each touched contract, write or identify RED/GREEN tests before implementation.

Acceptance layer: Contract Verification
  Verify the whole contract chain after implementation: code + tests + eval + UI/manual smoke where applicable.
```

Every execution plan MUST follow this three-layer discipline, planning work at the **behavior contract** level, not only at the file/workstream level. A valid plan answers:

1. **Which contract is touched?** Example: `WANd.LEARNING.IDLE.001`
2. **What behavior does the contract protect?**
3. **Which code paths implement it?**
4. **Which tests/evals/smokes prove it still holds?**
5. **What is the minimum TDD route for each implementation workstream?**

### Contract ID rules

- Prefer existing contract IDs from `.trellis/spec/**`, `.trellis/tasks/**`, eval cases, or runtime registries.
- If no ID exists, assign a provisional ID in the plan using this shape:
  - `WANd.<DOMAIN>.<BEHAVIOR>.001`
  - Examples: `WANd.TASKS.AGENT_RBAC.001`, `WANd.EMPLOYEE.PROFILE_CONTEXT.001`
- Record provisional IDs in `execution-plan.md`; if implementation makes the behavior permanent, update the relevant spec/registry during the spec-update gate.
- Every implementation row MUST include `touches: <contract-id>` or explicitly say `touches: docs-only/no-runtime-contract`.

Contract card / TDD row / Contract Verification gate templates: see SKILL.md §Operating doctrine (the only canonical copies).

## Load the skill (required)

Read and follow **in full** (canonical contract sections live in SKILL.md §Operating doctrine):

- `.cursor/skills/trellis-task-execution/SKILL.md`
- `.cursor/skills/trellis-task-execution/skill-selection.md` — **per-harness real-invocation mechanics, four-system verdict matrix, scenario F–L playbooks** (required whenever choosing between systems or classifying into F–L)
- `.cursor/skills/trellis-task-execution/examples.md` — when the task has multiple workstreams or two repos
  - Lite depth (single-workstream Scenario A/K): you may skip examples.md.

Phase-specific skills, load only when the scenario needs them (all at `.cursor/skills/<name>/SKILL.md`): **trellis-execute-plan** (approved plan execution / resume) · **trellis-contract-verify** (Contract Verification gate after implementation) · **trellis-debug-route** (Scenario C/F root-cause-first debugging) · **trellis-parallel-route** (Scenario D split, dispatch, and merge rules). Canonical cross-reference: `docs/ai-tools-reference.md` (§五 协作场景 · §八 验证门禁).

## Real invocation (three types — names are not invocations)

| Type | Meaning |
|------|---------|
| `Skill:` | Skill tool call — Trellis project skills, all `superpowers:*`, all `ecc:*` on Claude Code |
| `Agent:` | Subagent dispatch — trellis-research/implement/check, ecc reviewers/resolvers |
| `Read:` | Read SKILL.md **and follow its process to its artifact** — the only route for `openspec-*` on Claude Code |

On Claude Code, **never** write "if on disk" for Superpowers — it is a plugin, directly `Skill:`-invocable. **System ownership default rule:** Trellis is the spine; other systems provide invoked capabilities whose evidence is written back to the Trellis task. Ownership boundaries and same-capability verdicts come from skill-selection.md §一 / §二 (12 capabilities, fallback chains) — do not re-debate per task.

## Invoke skills by scenario (required — not plan text only)

After Step 1 scenario classification in `trellis-task-execution`, **before** writing `execution-plan.md`:

| Scenario | Must invoke **this session** |
|----------|------------------------------|
| **Any** | `Skill: trellis-before-dev` (or `Read:` on Cursor) → get_context + spec indexes for touched packages |
| **A** (clear PRD) | Above only; optional `Skill: trellis-brainstorm` if AC gaps found |
| **B** (large spec) | `Read: openspec-explore` → explore + `openspec list --json`; note whether `/opsx:propose` is next |
| **C** (bug) | `Skill: superpowers:systematic-debugging` **before any fix** |
| **D** (parallel) | `Skill: superpowers:dispatching-parallel-agents` + trellis §Step 6 merge owner |
| **E** (explore) | `Read: openspec-explore` **or** `Skill: trellis-brainstorm`; **stop** — no implementation plan until requirements clear |
| **F** (build failure) | `Agent: ecc:<lang>-build-resolver`; escalate to systematic-debugging after 2 failed rounds |
| **G** (refactor) | `Skill: superpowers:test-driven-development` (characterization safety net) + `Skill: ecc:refactor-clean` |
| **H** (security) | `Agent: security-reviewer` + `Skill: ecc:security-scan` — mandatory |
| **I** (performance) | `Agent: performance-optimizer` + measured baseline → `research/` |
| **J** (release) | `Read:` release spec + `Skill: ecc:verification-loop`; pre-package `git status/diff` |
| **K** (docs only) | `Agent: doc-updater` / `Skill: ecc:update-docs`; `Read: openspec-sync-specs` if deltas pending |
| **L** (research) | `Agent: trellis-research` → persist under `{task}/research/`; no code |
| **external-api / migration risk** | `Agent: trellis-research` → persist under `{task}/research/` |

**Evidence (required in plan or chat):** each row of the evidence block carries a type prefix (`Skill:` / `Agent:` / `Read:`) **plus** one-line output (spec paths, `research/foo.md`, test results, review verdict). A name without an invocation record = **invalid plan** — the rationalization table and red flags in skill-selection.md §四 apply. **Anti-pattern:** writing `Phase 0: /opsx:explore` without having executed explore steps in this session (unless user explicitly defers explore to a separate turn), or listing all four systems' candidates in one plan row instead of the matrix verdict + fallback.

## Input

The argument after the command is optional:

- *(empty)* — use active task from `python ./.trellis/scripts/task.py current --source`
- `07-02-mcp-health-coverage-expansion` — specific task dir under `.trellis/tasks/`
- A short feature name — find matching task dir first

## Required output

1. Phase -1 capability matrix (`available | unavailable | fallback`) and plan depth (`Lite | Standard | Full`)
2. Scenario classification (A–L) + workstream risk tags
3. **Contract map**: touched contract IDs, protected behavior, primary code, tests/evals/smokes
4. Phase 0–N workstream → tool table, including `touches`, `Risk`, `Required output`, and `Verification profile`
5. **TDD contract** per workstream: RED evidence, GREEN command, refactor guard
6. One verification profile (`Fast | Standard | UI | Release | Security | Cross-repo`) with a single **Contract Verification** gate chain
7. Parallel split + merge rules if applicable
8. Conditional recovery / re-approval rules
9. Manual steps (UI smoke for WanD/AionUI tasks)
10. `execution-plan.md` lint command/result: `python ./.trellis/scripts/lint_execution_plan.py .trellis/tasks/<task-dir>/execution-plan.md`

## Minimum execution-plan.md shape

The generated `execution-plan.md` MUST include these sections (full **Standard/Full** depth).  
**Lite depth:** use **Contract map (lite)** only — see `.cursor/skills/trellis-task-execution/SKILL.md` §Operating doctrine.

```markdown
## Skills invoked (this planning session)
| Invocation | Type | Evidence |
|------------|------|----------|
| trellis-before-dev | Read: | spec paths: ... |

## Progress snapshot
| Phase | State | Delivery / evidence |
|-------|-------|---------------------|
| Phase -1 | pending | capability matrix + lint pending |

## Contract map (lite)   <!-- Lite depth only; skip tables below -->
- **touches:** WANd.X.Y.001 | docs-only/no-runtime-contract
- **Behavior protected:** …
- **GREEN:** `exact command`
- **Manual smoke:** N/A | …

## Contract map            <!-- Standard / Full -->
| Contract | Behavior protected | Primary code | Tests / eval / smoke | Risk |
|----------|--------------------|--------------|----------------------|------|
| WANd.X.Y.001 | ... | ... | ... | ... |

## Workstreams
| Phase | Priority | Workstream | touches | Risk | Tool / agent | Files | Required output | Profile |
|-------|----------|------------|---------|------|--------------|-------|-----------------|---------|
| 1 | P0 | ... | WANd.X.Y.001 | ui | ... | ... | ... | UI |

## TDD contract
| Workstream | Contract | RED evidence | GREEN command | Refactor guard |
|------------|----------|--------------|---------------|----------------|
| ... | WANd.X.Y.001 | ... | ... | ... |

## Contract Verification
| Contract | Verification command / smoke | Required evidence | Status |
|----------|------------------------------|-------------------|--------|
| WANd.X.Y.001 | ... | command output / screenshot / eval result | pending |
| plan structure | `python ./.trellis/scripts/lint_execution_plan.py .trellis/tasks/<task-dir>/execution-plan.md` | PASS output | pending |
```

**Wait for user approval** before Phase 2 implementation.

## Quick triggers

| User says | Action |
|-----------|--------|
| 设计执行计划 | Run Steps 1–3 from skill |
| 执行 task | Load `trellis-execute-plan`; only after plan approved; enforce Contract Verification gate |
| 验证 / 完成了吗？ | Load `trellis-contract-verify`; update evidence before claiming completion |
| lint plan / 检查计划 | Run `/trellis:lint-plan` (command: see §Required output #10) |
| 可以并行吗？ | Load `trellis-parallel-route`; Scenario D table + merge rules |
| 用哪个 skill / 谁更好？ | skill-selection.md §二 verdict matrix — cite winner + fallback |
| 查 bug / 构建挂了 | Load `trellis-debug-route`; Scenario C/F playbook — diagnose first, fix second |
| 重构 / 清理 / 发版 / 只改文档 | Scenario G/J/K playbooks (skill-selection.md §三) |
