# agent-company-meta

Workspace / orchestration layer for the **Agent-native company** product (not CCB-Wanding).

```text
L1 product semantics  →  platform/
L2 Rudder-class CP    →  (future, under platform/control-plane)
L3 package platform   →  platform/
L4 sample vertical    →  sample-ccb/  (read-only submodule → claude-code-best)
```

## Open in Cursor

Open this folder or `agent-company-meta.code-workspace`.

## Where to commit

| Repo | Path | Commit what |
|------|------|-------------|
| **meta** | `D:\Projects\agent-company-meta` (this root, excluding nested repos) | workspace, `.cursor`, `.agents`, meta `.trellis`, submodule **pointer** only |
| **platform** | `platform/` | new product code, specs, docs, scripts |
| **sample-ccb** | `sample-ccb/` | **Do not commit product work here.** Read-only sample. Bump submodule pointer in meta only when intentionally refreshing the sample pin. |

## sample-ccb is read-only

After bootstrap / before handoff:

```powershell
git -C sample-ccb status --short   # MUST be empty
```

Do not edit WanD business code inside `sample-ccb/`. Extract later into `platform/packages/com.wanding.trade/` (separate task).

### Submodule URL

MVP uses **local path** clone of `D:\Projects\claude-code-best`.

To switch to a remote later, edit `.gitmodules` and run:

```powershell
git submodule sync --recursive
git submodule update --init --recursive
```

## Boundary checks (platform)

```powershell
cd platform
node scripts/check-no-sample-import.mjs
node scripts/check-no-wanding-core-terms.mjs
```

## Triple git status checklist

```powershell
git -C D:\Projects\agent-company-meta status --short
git -C D:\Projects\agent-company-meta\platform status --short
git -C D:\Projects\agent-company-meta\sample-ccb status --short
```

## Runtime

**No app runtime yet** (no Node app server / Electron product shell required for this bootstrap). Tooling scripts and docs only.

## Authority docs

See `platform/docs/` and `platform/docs/source-map.md`.
