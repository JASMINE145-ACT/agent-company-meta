---
iteration: 5
max_iterations: 10
completion_promise: "BACKEND_SPEC_COMPLETE"
---

Continue building `.trellis/spec/backend/` — each iteration:

1. Read existing backend docs; find gaps, contradictions, or unverified claims
2. Verify paths/behavior against claude-code-B, ccb-installer, mcp_servers, python, live D:\CCB-Wanding
3. Improve docs: reconcile source vs dist-patch reality ($buildMcp), cross-link integration/frontend
4. Add missing smoke commands (test-native-acp-agent.mjs etc.), update index.md
5. Mark [VERIFY] only where genuinely unconfirmed

P2 done: deploy script, AGENTS.md, guides/outline. P3: source-migration-mcp.md, integration/frontend cross-links. Open runtime: route-b-status § Open (AionUI E2E, execute migration).

Output <promise>BACKEND_SPEC_COMPLETE</promise> only when docs are internally consistent, cross-linked, and spot-checked against repo.
