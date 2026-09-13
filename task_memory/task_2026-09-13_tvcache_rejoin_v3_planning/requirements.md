## Modification History

| Date       | Summary of Changes |
| ---------- | ------------------ |
| 2026-09-13 | Created task record for converting the v3 ReJoin research plan into durable planning documents. |
| 2026-09-13 | Follow-up request authorized execution of the recorded plan, starting at P00 and continuing through the ready packets. |

# Requirements

## Original Request

充分分析并理解 `draft-plan/TVCache_ReJoin_Codex_Plan_v3_ZH.md`，基于该文档把计划落成新的 `task_memory/` 文档。本阶段只做 planning，不实现代码或运行研究实验。

## Follow-up Request

用户在 2026-09-13 明确要求“开始执行”。因此本任务从 planning-only 转入执行阶段，先按 P00 baseline 和 P01 cursor reproducer 开始，再进入 P02 harness；保留原 v3 的停止条件和延期事项。

## Scope Decisions

- Source of truth: `draft-plan/TVCache_ReJoin_Codex_Plan_v3_ZH.md` in the current worktree.
- The same-named files under `draft-plan/legacy/` are legacy reference material only, as stated by `draft-plan/legacy/AGENTS.md`.
- Deliver a new task directory with durable requirements, findings, execution plan, progress, and design records.
- Preserve the source plan's early-stage scope: Phase 1 opportunity measurement, then the smallest Phase 2 guarded memoizer mechanism proof.
- Do not modify TVCache serving code or start GPU jobs before the M0/M1 gates authorize that work.
- CPU tests, research harness code, trace collection, and task-memory evidence are now in scope when required by P00–P05.

## Latest follow-up

用户已提供第一版 W1 filesystem task selection 和 candidate manifest，并指定下一步为：checkout/pin Terminal-Bench source；构建十个 task image 并填 runtime digest；验证 verifier；实现 seven S0 plus one S1 tool surface；使用四个 task 启动 P04 smoke。当前主机缺少 container runtime，因此 image build 和 in-container verifier 执行需在 runtime 可用后继续。

## Acceptance Criteria

- The new task directory is present under `task_memory/`.
- The source plan is analyzed into structured findings with goals, exclusions, evidence classes, workloads, metrics, gates, risks, and open decisions.
- A step-by-step execution plan is recorded with dependencies and explicit verification points.
- Progress records the source path, repository pin, and any unresolved input or design questions.
- All planning documents have a modification history and use clear English technical terms where needed.
