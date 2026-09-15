## Modification History

| Date       | Summary of Changes |
| ---------- | ------------------ |
| 2026-09-13 | Created task record for converting the v3 ReJoin research plan into durable planning documents. |
| 2026-09-13 | Follow-up request authorized execution of the recorded plan, starting at P00 and continuing through the ready packets. |
| 2026-09-15 | Recorded the CPU-master Docker limitation and the approved GPU-worker build and verifier route for P03. |
| 2026-09-15 | Added cloud persistence and authorized P04 smoke when existing resources settle required inputs. |

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

用户已提供第一版 W1 filesystem task selection 和 candidate manifest，并指定下一步为：checkout/pin Terminal-Bench source；构建十个 task image 并填 runtime digest；验证 verifier；实现 seven S0 plus one S1 tool surface；使用四个 task 启动 P04 smoke。CPU master 没有可用 Docker runtime，因此已按用户建议通过 H200 GPU worker 的 StepBPS build path 完成 image 构建，并在同一 image 中运行 verifier。

## Latest execution update

- P03 source revision is pinned at `d28711d0da2675d0bb1d56de45ae5df6082438a3`.
- Ten selected task images have successful StepBPS build records, registry manifest digests, and H200 worker verifier evidence.
- The four P04 smoke tasks are ready to run; no provider rollout has started yet.

## Acceptance Criteria

- [Original Request] 将需要复用的 task/image/rollout 等持久化保存到云卷 ycfeng 目录下，为当前任务建立分类目录；运行生成的大型持久产物也写入该目录。
- [Original Request] 调查 P04 是否仍有必须由用户提供的数据或关键决策；有则列出讨论，没有则直接执行 P04 smoke。
- Cloud writes use StepMind Python RJobBackend with the declared JuiceFS mount, only below `/mnt/codesign-exp/ycfeng`. Worker caches stay on temporary local storage. Upload source, complete image data, and selected evidence; exclude credentials.
- P04 uses the four recorded tasks with four independent rollouts each, fixed provider settings, real tools, persisted traces, workspace artifacts, and verifier results. Existing provider resources should be checked before requesting new information.

- The new task directory is present under `task_memory/`.
- The source plan is analyzed into structured findings with goals, exclusions, evidence classes, workloads, metrics, gates, risks, and open decisions.
- A step-by-step execution plan is recorded with dependencies and explicit verification points.
- Progress records the source path, repository pin, and any unresolved input or design questions.
- All planning documents have a modification history and use clear English technical terms where needed.
