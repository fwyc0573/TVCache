#!/usr/bin/env python3
"""Analyze P05 traces for ReJoin opportunity classes and small serial checks."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json
import math
import os
from pathlib import Path
import shutil
import statistics
import sys
import tarfile
import time

SCRIPT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPT_ROOT / "src"))
sys.path.insert(0, str(SCRIPT_ROOT / "scripts"))
from rejoin.schemas import digest_json
from rejoin.trace import load_jsonl


CLASSES = ("A", "B", "C", "U", "N")


def read_tasks(path: Path) -> list[str]:
    return [json.loads(line)["task_id"] for line in path.read_text().splitlines()
            if line.strip() and json.loads(line).get("include")]


def invocation(event) -> str:
    return digest_json({"tool": event.tool_name, "args": event.normalized_args, "cwd": event.cwd})


def effect(event) -> str:
    return digest_json({"result": event.result_digest, "exit_status": event.exit_status,
                        "changed_paths": event.workspace_changed_paths,
                        "mutates_declared": event.mutates_declared})


def prior_mutations(events: list, index: int) -> tuple:
    return tuple((event.tool_name, tuple(event.workspace_changed_paths), event.result_digest)
                 for event in events[:index] if event.workspace_changed_paths)


def prior_invocations(events: list, index: int) -> tuple[str, ...]:
    return tuple(invocation(event) for event in events[:index])


def divergent(recipient_events: list, recipient_index: int, donor_events: list, donor_index: int) -> bool:
    recipient_history = prior_mutations(recipient_events, recipient_index)
    donor_history = prior_mutations(donor_events, donor_index)
    return bool(recipient_history and donor_history and recipient_history != donor_history)


def classify(recipient_events: list, recipient_index: int, donor_events: list,
             donor_index: int) -> str:
    recipient = recipient_events[recipient_index]
    donor = donor_events[donor_index]
    if invocation(recipient) != invocation(donor):
        return "N"
    same_prefix = (prior_invocations(recipient_events, recipient_index) ==
                   prior_invocations(donor_events, donor_index))
    if same_prefix and recipient.workspace_before_digest == donor.workspace_before_digest:
        return "A"
    if (recipient.workspace_before_digest == donor.workspace_before_digest and
            effect(recipient) == effect(donor)):
        return "B"
    if (recipient.support_class == "S0" and donor.support_class == "S0" and
            effect(recipient) == effect(donor) and
            divergent(recipient_events, recipient_index, donor_events, donor_index)):
        return "C"
    if (recipient.support_class == "S1" and
            divergent(recipient_events, recipient_index, donor_events, donor_index)):
        return "U"
    return "N"


def donor_class(recipient_events: list, recipient_index: int, all_rollouts: dict[str, list],
                online: bool) -> tuple[str, dict | None]:
    recipient = recipient_events[recipient_index]
    candidates = []
    for rollout_id, donor_events in all_rollouts.items():
        if rollout_id == recipient.rollout_id:
            continue
        for donor_index, donor in enumerate(donor_events):
            if invocation(recipient) != invocation(donor):
                continue
            if online and donor.end_ns > recipient.start_ns:
                continue
            rank = {"A": 0, "B": 1, "C": 2, "U": 3, "N": 4}
            value = classify(recipient_events, recipient_index, donor_events, donor_index)
            candidates.append((rank[value], abs(donor.end_ns - recipient.start_ns), value,
                               rollout_id, donor_index))
    if not candidates:
        return "N", None
    _, _, value, rollout_id, donor_index = min(candidates)
    donor = all_rollouts[rollout_id][donor_index]
    return value, {"rollout_id": rollout_id, "seq": donor.seq, "end_ns": donor.end_ns}


def event_row(event, events: list, all_rollouts: dict[str, list], online: bool) -> dict:
    value, donor = donor_class(events, event.seq, all_rollouts, online)
    return {
        "task_id": event.task_id, "rollout_id": event.rollout_id, "seq": event.seq,
        "tool": event.tool_name, "support_class": event.support_class,
        "arguments": dict(event.normalized_args),
        "invocation_signature": invocation(event), "effect_signature": effect(event),
        "duration_ns": event.end_ns - event.start_ns,
        "prior_mutation_depth": sum(bool(item.workspace_changed_paths) for item in events[:event.seq]),
        "workspace_before_digest": event.workspace_before_digest,
        "workspace_after_digest": event.workspace_after_digest,
        "changed_paths": list(event.workspace_changed_paths), "class": value,
        "donor": donor,
    }


def aggregate(rows: list[dict], key: str = "class") -> dict:
    result = {value: {"calls": 0, "time_ns": 0} for value in CLASSES}
    for row in rows:
        bucket = result[row[key]]
        bucket["calls"] += 1
        bucket["time_ns"] += row["duration_ns"]
    total = sum(bucket["time_ns"] for bucket in result.values())
    for bucket in result.values():
        bucket["time_share"] = bucket["time_ns"] / total if total else 0.0
    return result


def svg_bar(path: Path, title: str, labels: list[str], values: list[float], unit: str) -> None:
    width, height = 900, 460
    margin_left, margin_bottom = 80, 90
    maximum = max(values, default=1.0) or 1.0
    bar_width = max(20, (width - margin_left - 30) / max(1, len(values)) - 18)
    colors = ["#4169e1", "#6a5acd", "#2e8b57", "#d2691e", "#808080", "#b22222", "#708090"]
    pieces = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">',
              f'<text x="{width/2}" y="28" text-anchor="middle" font-size="18">{title}</text>',
              f'<line x1="{margin_left}" y1="{height-margin_bottom}" x2="{width-20}" y2="{height-margin_bottom}" stroke="black"/>']
    for index, (label, value) in enumerate(zip(labels, values)):
        x = margin_left + 18 + index * ((width - margin_left - 30) / max(1, len(values)))
        bar_height = (height - margin_bottom - 60) * value / maximum
        y = height - margin_bottom - bar_height
        pieces.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_width:.1f}" height="{bar_height:.1f}" fill="{colors[index % len(colors)]}"/>')
        pieces.append(f'<text x="{x + bar_width/2:.1f}" y="{y-6:.1f}" text-anchor="middle" font-size="11">{value:.3g}</text>')
        pieces.append(f'<text x="{x + bar_width/2:.1f}" y="{height-52}" text-anchor="middle" font-size="12">{label}</text>')
    pieces.append(f'<text x="15" y="{height/2}" transform="rotate(-90 15 {height/2})" text-anchor="middle" font-size="12">{unit}</text>')
    pieces.append("</svg>\n")
    path.write_text("\n".join(pieces))


def run_serial_references(rows: list[dict], cloud_root: Path, tmp_root: Path, limit: int = 10) -> list[dict]:
    """Replay only the ten most expensive repeated signatures when feasible."""
    grouped = defaultdict(list)
    for row in rows:
        grouped[row["invocation_signature"]].append(row)
    ranked = sorted(((sum(item["duration_ns"] for item in items), signature, items)
                     for signature, items in grouped.items() if len(items) >= 2), reverse=True)
    try:
        from collect_p04 import prepare_filesystem, run_tool
    except ImportError:
        return [{"status": "unavailable", "reason": "collector import unavailable"}]
    results = []
    tmp_root.mkdir(parents=True, exist_ok=True)
    for total_ns, signature, items in ranked[:limit]:
        sample = items[0]
        archive = cloud_root / "rollouts/p05" / sample["run_id"] / sample["task_id"] / sample["rollout_id"] / "workspace.tar.gz"
        result = {"invocation_signature": signature, "task_id": sample["task_id"],
                  "tool": sample["tool"], "observed_calls": len(items),
                  "observed_total_ns": total_ns, "observed_median_ns": statistics.median(item["duration_ns"] for item in items),
                  "archive": str(archive)}
        if not archive.exists():
            result.update(status="unavailable", reason="workspace archive missing")
            results.append(result)
            continue
        rootfs = tmp_root / f"ref-{len(results):02d}"
        try:
            prepare_filesystem(rootfs)
            shutil.rmtree(rootfs / "app")
            with tarfile.open(archive, "r:gz") as bundle:
                bundle.extractall(rootfs)
            action = {"tool": sample["tool"], "arguments": sample["arguments"]}
            env = {"PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin"), "TMPDIR": "/tmp",
                   "XDG_CACHE_HOME": "/tmp/cache", "UV_CACHE_DIR": "/tmp/uv", "LANG": "C.UTF-8"}
            started = time.perf_counter_ns()
            tool_result = run_tool(action, rootfs, env)
            elapsed = time.perf_counter_ns() - started
            result.update(status="pass", serial_duration_ns=elapsed,
                          serial_exit_status=tool_result["exit_status"],
                          serial_result_digest=digest_json(tool_result["result"]),
                          concurrency_ratio=(statistics.median(item["duration_ns"] for item in items) / elapsed
                                              if elapsed else math.inf))
        except Exception as error:
            result.update(status="error", error=f"{type(error).__name__}: {error}")
        finally:
            shutil.rmtree(rootfs, ignore_errors=True)
        results.append(result)
    return results


def markdown(result: dict) -> str:
    lines = ["# P05 Opportunity Pilot", "", f"Run: `{result['run_id']}`", "",
             "## Scope and method", "",
             "The analyzer reloads every P05 JSONL trace, weights each call by `end_ns - start_ns`, and compares events across rollouts of the same task. A is prefix/history reuse, B is equal full workspace state with different history, C is a post-divergence S0 match with equal observed effect, U is a post-divergence repeated S1 call without a complete effect description, and N has no usable donor. Hindsight permits any donor in the batch; completed-donor online view requires donor completion before the recipient starts.", "",
             f"Collection concurrency recorded for this run: **{result['collection_concurrency']}**.", "",
             "## Hindsight class totals", "", "| Class | Calls | Time (s) | Time share |", "|---|---:|---:|---:|"]
    for value in CLASSES:
        bucket = result["hindsight"][value]
        lines.append(f"| {value} | {bucket['calls']} | {bucket['time_ns']/1e9:.3f} | {bucket['time_share']:.2%} |")
    lines += ["", "## Completed-donor online totals", "", "| Class | Calls | Time (s) | Time share |", "|---|---:|---:|---:|"]
    for value in CLASSES:
        bucket = result["online"][value]
        lines.append(f"| {value} | {bucket['calls']} | {bucket['time_ns']/1e9:.3f} | {bucket['time_share']:.2%} |")
    lines += ["", "## Per-task summary", "", "| Task | Calls | Tool time (s) | C calls | U calls | C+U time share | Verifier passes |", "|---|---:|---:|---:|---:|---:|---:|"]
    for row in result["per_task"]:
        lines.append(f"| {row['task_id']} | {row['calls']} | {row['time_ns']/1e9:.3f} | {row['C_calls']} | {row['U_calls']} | {row['CU_time_share']:.2%} | {row['verifier_passes']}/4 |")
    lines += ["", "## Pilot questions", "",
              f"- A: {result['hindsight']['A']['calls']} calls, {result['hindsight']['A']['time_ns']/1e9:.3f} s.",
              f"- B: {result['hindsight']['B']['calls']} calls, {result['hindsight']['B']['time_ns']/1e9:.3f} s.",
              f"- Post-divergence C: {result['hindsight']['C']['calls']} calls, {result['hindsight']['C']['time_ns']/1e9:.3f} s.",
              f"- U: {result['hindsight']['U']['calls']} calls, {result['hindsight']['U']['time_ns']/1e9:.3f} s.",
              f"- C+U share of observed tool time: {result['cu_time_share']:.2%}.",
              f"- Top-1 repeated signature share: {result['top_signature_share']:.2%}.",
              f"- Tasks with post-divergence C or U: {result['tasks_with_post_divergence_opportunity']}/{len(result['tasks'])}.",
              f"- Most common opportunity mutation depth: {result['opportunity_depth_mode']}.",
              f"- Opportunity time by support class: S0 {result['opportunity_by_support']['S0']['time_ns']/1e9:.3f} s; S1 {result['opportunity_by_support']['S1']['time_ns']/1e9:.3f} s.",
              "", "## Serial references", "", "The analyzer attempted serial reruns only for the ten most expensive repeated invocation signatures. These checks are calibration evidence for duration ordering; they do not change the A/B/C/U labels.", ""]
    for item in result["serial_references"]:
        lines.append(f"- `{item.get('task_id', '?')}` `{item.get('tool', '?')}`: {item.get('status')}" + (f", concurrent/serial median ratio {item['concurrency_ratio']:.2f}" if "concurrency_ratio" in item else ""))
    lines += ["", "## Figures", "", "- `figures/O1_class_time_share.svg` — A/B/C/U/N hindsight time share.", "- `figures/O2_opportunity_mutation_depth.svg` — C/U time by prior mutation depth.", "- `figures/O3_top_signature_concentration.svg` — repeated signature time concentration.", "", "## Interpretation limits", "", "These are opportunity measurements from one 10-task, four-rollout collection. C is an observed S0 effect match and still needs the P07 differential mechanism check. U is explicitly unsafe until a typed dependency/effect description is supplied. Verifier failures are retained as task outcomes and do not remove trace records.", ""]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cloud-root", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--collection-concurrency", type=int, default=4)
    parser.add_argument("--tmp-root", type=Path, default=Path("/data/ycfeng/tmp/p05-serial-reference"))
    args = parser.parse_args()
    tasks = read_tasks(args.manifest)
    all_events: list[dict] = []
    all_rows_hindsight, all_rows_online = [], []
    per_task = []
    verifier_passes = {}
    for task in tasks:
        rollouts = {}
        for index in range(4):
            directory = args.cloud_root / "rollouts/p05" / args.run_id / task / f"r{index}"
            events = load_jsonl(directory / "trace.jsonl")
            rollouts[f"r{index}"] = events
            summary = json.loads((directory / "COMPLETE.json").read_text())
            verifier_passes[task] = verifier_passes.get(task, 0) + int(summary.get("verifier_exit_code") == 0)
        for events in rollouts.values():
            for event in events:
                hindsight = event_row(event, events, rollouts, online=False)
                online = event_row(event, events, rollouts, online=True)
                hindsight["run_id"] = args.run_id
                online["run_id"] = args.run_id
                all_rows_hindsight.append(hindsight)
                all_rows_online.append(online)
    hindsight_total = aggregate(all_rows_hindsight)
    online_total = aggregate(all_rows_online)
    total_time = sum(row["duration_ns"] for row in all_rows_hindsight)
    cu_rows = [row for row in all_rows_hindsight if row["class"] in {"C", "U"}]
    grouped = defaultdict(list)
    for row in all_rows_hindsight:
        grouped[row["invocation_signature"]].append(row)
    top = []
    for signature, rows in grouped.items():
        if len(rows) < 2:
            continue
        top.append({"invocation_signature": signature, "tool": rows[0]["tool"],
                    "support_class": rows[0]["support_class"], "calls": len(rows),
                    "time_ns": sum(row["duration_ns"] for row in rows),
                    "task_ids": sorted({row["task_id"] for row in rows})})
    top.sort(key=lambda row: (-row["time_ns"], row["invocation_signature"]))
    for rank, row in enumerate(top, start=1):
        row["rank"] = rank
        row["time_share"] = row["time_ns"] / total_time if total_time else 0.0
    opportunity_depth = Counter(row["prior_mutation_depth"] for row in cu_rows)
    opportunity_by_support = {value: {"calls": 0, "time_ns": 0} for value in ("S0", "S1")}
    for row in cu_rows:
        bucket = opportunity_by_support[row["support_class"]]
        bucket["calls"] += 1
        bucket["time_ns"] += row["duration_ns"]
    per_task = []
    for task in tasks:
        rows = [row for row in all_rows_hindsight if row["task_id"] == task]
        task_time = sum(row["duration_ns"] for row in rows)
        per_task.append({"task_id": task, "calls": len(rows), "time_ns": task_time,
                         "C_calls": sum(row["class"] == "C" for row in rows),
                         "U_calls": sum(row["class"] == "U" for row in rows),
                         "CU_time_share": sum(row["duration_ns"] for row in rows if row["class"] in {"C", "U"}) / task_time if task_time else 0.0,
                         "verifier_passes": verifier_passes.get(task, 0)})
    result = {
        "run_id": args.run_id, "tasks": tasks, "rollouts": len(tasks) * 4,
        "collection_concurrency": args.collection_concurrency, "total_calls": len(all_rows_hindsight),
        "total_time_ns": total_time, "hindsight": hindsight_total, "online": online_total,
        "cu_time_share": sum(row["duration_ns"] for row in cu_rows) / total_time if total_time else 0.0,
        "tasks_with_post_divergence_opportunity": len({row["task_id"] for row in cu_rows}),
        "opportunity_depth": {str(key): value for key, value in sorted(opportunity_depth.items())},
        "opportunity_depth_mode": opportunity_depth.most_common(1)[0][0] if opportunity_depth else None,
        "opportunity_by_support": opportunity_by_support, "top_signatures": top[:10],
        "top_signature_share": top[0]["time_share"] if top else 0.0, "per_task": per_task,
        "serial_references": run_serial_references(all_rows_hindsight, args.cloud_root, args.tmp_root),
        "rows": {"hindsight": all_rows_hindsight, "online": all_rows_online},
    }
    report_dir = args.cloud_root / "reports/p05" / args.run_id
    figure_dir = report_dir / "figures"
    figure_dir.mkdir(parents=True, exist_ok=True)
    (report_dir / "opportunity_pilot.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    (report_dir / "opportunity_pilot.md").write_text(markdown(result))
    svg_bar(figure_dir / "O1_class_time_share.svg", "P05 hindsight class time share", list(CLASSES),
            [hindsight_total[value]["time_share"] * 100 for value in CLASSES], "percent")
    depth_labels = [str(key) for key in sorted(opportunity_depth)]
    svg_bar(figure_dir / "O2_opportunity_mutation_depth.svg", "C/U calls by prior mutation depth", depth_labels,
            [opportunity_depth[int(key)] for key in depth_labels], "calls")
    signature_labels = [f"#{row['rank']} {row['tool']}" for row in top[:10]]
    svg_bar(figure_dir / "O3_top_signature_concentration.svg", "Top repeated signature time (seconds)", signature_labels,
            [row["time_ns"] / 1e9 for row in top[:10]], "seconds")
    print(json.dumps({"run_id": args.run_id, "total_calls": len(all_rows_hindsight),
                      "total_time_ns": total_time, "cu_time_share": result["cu_time_share"],
                      "tasks_with_post_divergence_opportunity": result["tasks_with_post_divergence_opportunity"],
                      "top_signature_share": result["top_signature_share"],
                      "report": str(report_dir / "opportunity_pilot.md")}, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
