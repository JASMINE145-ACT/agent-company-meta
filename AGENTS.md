<!-- TRELLIS:START -->
# Trellis Instructions

These instructions are for AI assistants in **agent-company-meta** (orchestration root).

**Product Trellis (full):** `platform/.trellis/` — specs, workflow, tasks, scripts.  
**Meta Trellis (light):** `.trellis/` — meta roadmap tasks only; specs point at platform.

- Meta workflow: `.trellis/workflow.md`
- Meta spec pointer: `.trellis/spec/index.md`
- Product entry: `platform/.trellis/spec/index.md`
- Product AGENTS: `platform/AGENTS.md`

Do **not** grow product layer specs under meta `.trellis/spec/`.

Meta mirrors Cursor/Codex Trellis agents & hooks for workspace root; **product gates live in `platform/`**.

<!-- TRELLIS:END -->

---

# agent-company-meta — AI assistant entry

This meta repo **orchestrates** Cursor/Trellis tooling. Product code lives in `platform/`.

- **Do not** treat `sample-ccb/` as platform source.
- **Do not** import `sample-ccb` from `platform/`.
- Product AGENTS: `platform/AGENTS.md`
- Stack authority: `platform/docs/platform-system-business-decoupling-optimization.md` §0.1

When working on product features, prefer opening the `platform` folder focus or follow `platform/AGENTS.md`.
