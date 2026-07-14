# Org Tree 拓宽设计 — 选中态覆盖层（方案 A）

> 日期：2026-07-14 · 状态：approved · 范围：`platform/control-plane/ui`
> 对应契约：`platform/.trellis/spec/product/org-structure.md`

## 背景与理念

组织树已实现「宪法与经营治理并进同一棵树」：

```text
公司宪法（宪 · 非 Agent，唯一根）
  └─ 治理席位（治）
       └─ COO 下挂能力部门（部）→ Agent（A）
```

本轮在**不动这一理念**的前提下做三类拓宽：树的可视化、查看级交互、理念文档化。
数据仍为只读静态 seed，无持久化、无后端。

## 核心决策：Contract Team 以覆盖层上树（方案 A）

Contract Team **永远不是树节点**。右侧面板选中某 Team 时树进入聚焦态：

- 非成员节点变暗（opacity ≈ 0.35）；
- 成员节点高亮描边；Owner 加 STO 徽章；
- 从 Owner 向每个其他成员画虚线（SVG dashed）；
- 取消选中即完全还原。

否决的替代方案：B（Team 作临时节点挂 COO 下）违背「临时不入树」不变量；C（双视图切换）是分裂而非拓宽，YAGNI。

## 可视化拓宽

1. **泳道**：画布内、节点之下渲染四条全宽色带（宪/治/部/A）+ 左侧层标签，由 `layerLanes(flatNodes)` 从实际节点坐标按 kind 推导，随 pan/zoom 联动。
2. **平台基座**：平台组件从 header 标签条移入画布，画在 Agent 泳道之下、与树同宽的基座条（组件为条内芯片），无连线，表达「所有 Agent 站在平台上」。header 原平台条删除。

## 查看级交互

- 单一选中态：`{ type: 'node' | 'team', id } | null`；点树上卡片选节点，点 Team 列表选团队，点画布空白清除。
- 右侧栏拆两区：上 `DetailPanel`（宪法条款 / 席位职责+seat / 部门使命+编制 / Agent 头衔+状态+所属 Team 反查；Team 选中时显示契约详情），下 `ContractTeamPanel` 改为可点击列表。
- 属于 active Team 的 Agent 卡片显示小角标。

## 模型层（纯函数，全部可测）

- 新 `model/orgSelectors.ts`：`teamMembershipByAgent(org)`、`teamFocus(org, teamId) → { ownerId, memberIds } | null`（未知 id 返回 null）、`nodeDetails(org, nodeId) → 判别联合 | null`、`OrgSelection` 类型。
- `model/layout.ts` 追加：`layerLanes(flat) → { id, label, yTop, yBottom }[]`、`overlayEdges(flat, focus) → { owner, member }[]`。
- `orgTypes` / `seedOrg` / `orgView` 零改动。

## 测试（先写测试）

- `orgSelectors.test.ts`：membership 反查、focus owner∈members、未知 id null、details 各 kind 分支。
- `layout.test.ts` 追加：四泳道顺序宪→治→部→A、互不重叠、覆盖各自节点；overlayEdges 边数 = 成员数−1、无 focus 为空。
- `orgView.test.ts` 追加：树中无 platform kind 节点、无 Contract Team id（INV-4/5 锚点）。

## 验收

`npm test` + `npm run build` 通过；`/org` 页手动确认：四泳道、基座条、Team 聚焦态（高亮/STO/虚线）、节点详情面板、pan/zoom/fit 全部联动。
