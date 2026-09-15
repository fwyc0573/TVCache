#!/usr/bin/env python3
"""Reload cloud P04 artifacts and evaluate the recorded smoke checks."""

import argparse
from collections import Counter
import json
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from rejoin.schemas import digest_json
from rejoin.trace import load_jsonl

TASKS = ("wasm-pipeline", "polyglot-c-py", "multi-source-data-merger", "recover-accuracy-log")


def check(root: Path, run_id: str) -> dict:
    root = root.resolve()
    if not root.is_relative_to("/mnt/codesign-exp/ycfeng"):
        raise ValueError("Read only the personal cloud directory")
    records, problems = [], []
    for task in TASKS:
        for index in range(4):
            directory = root / "rollouts/p04" / run_id / task / f"r{index}"
            try:
                summary = json.loads((directory / "COMPLETE.json").read_text())
                events = load_jsonl(directory / "trace.jsonl")
                assert summary["task_id"] == task and summary["rollout_id"] == f"r{index}"
                assert summary["tool_calls"] == len(events)
                assert all(e.run_id == run_id and e.task_id == task and e.rollout_id == f"r{index}"
                           for e in events)
                assert not events or events[0].seq == 0
                for artifact in ("workspace.tar.gz", "workspace.initial.json", "workspace.final.json",
                                 "verifier.log", "verifier.xml", "provider.jsonl"):
                    assert (directory / artifact).stat().st_size > 0, artifact
                raw = [json.loads(line) for line in (directory / "trace.jsonl").read_text().splitlines()]
                for record in raw:
                    assert digest_json(record["tool_result"]) == record["result_digest"]
                    assert record["provider"]["response_id"]
                suites = ET.parse(directory / "verifier.xml").getroot().iter("testsuite")
                counts = Counter()
                for suite in suites:
                    counts.update({name: int(suite.attrib.get(name, 0))
                                   for name in ("tests", "failures", "errors", "skipped")})
                summary.update(trace_reload_count=len(events), verifier_counts=dict(counts),
                               has_mutation=any(e.workspace_changed_paths for e in events),
                               mutation_calls=sum(bool(e.workspace_changed_paths) for e in events),
                               class_calls=dict(Counter(e.support_class for e in events)),
                               support_classes=sorted({e.support_class for e in events}),
                               trajectory=digest_json([[e.tool_name, e.normalized_args] for e in events]))
                records.append(summary)
            except (OSError, ValueError, AssertionError, KeyError, ET.ParseError) as error:
                problems.append(f"{task}/r{index}: {type(error).__name__}: {error}")
    diverse = {task: len({r["trajectory"] for r in records if r["task_id"] == task}) for task in TASKS}
    classes = sorted({value for row in records for value in row["support_classes"]})
    checks = {
        "all_16_reload": len(records) == 16 and not problems,
        "majority_at_least_4_calls": sum(r["tool_calls"] >= 4 for r in records) > 8,
        "real_mutations": any(r["has_mutation"] for r in records),
        "each_task_has_divergence": all(value >= 2 for value in diverse.values()),
        "both_support_classes": classes == ["S0", "S1"],
        "no_collection_errors": len(records) == 16 and all(r["termination"] != "collection_error" for r in records),
    }
    return {"status": "PASS" if all(checks.values()) else "FAIL", "run_id": run_id,
            "checks": checks, "problems": problems, "records": records,
            "total_calls": sum(r["tool_calls"] for r in records),
            "at_least_4_calls": sum(r["tool_calls"] >= 4 for r in records),
            "mutation_rollouts": sum(r["has_mutation"] for r in records),
            "verifier_passes": sum(r["verifier_exit_code"] == 0 for r in records),
            "invalid_or_early": sum(r["termination"] != "final_answer" for r in records),
            "unique_trajectories": diverse, "support_classes": classes}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--cloud-root", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    report = check(args.cloud_root, args.run_id)
    args.report.write_text(json.dumps(report, indent=2) + "\n")
    args.report.chmod(0o666)
    cloud_report = args.cloud_root / "reports" / (args.run_id + ".smoke.json")
    cloud_report.write_text(json.dumps(report, indent=2) + "\n")
    lines = ["## Modification History", "", "| Date | Summary of Changes |",
             "| --- | --- |", "| 2026-09-15 | Generated from reloaded P04 cloud artifacts. |",
             "", "# P04 smoke results", "", f"Run: `{args.run_id}`. Smoke status: **{report['status']}**.",
             "", "| Task | Rollout | Calls | Mutation calls | S0 | S1 | Verifier exit | Termination |",
             "| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |"]
    for row in report["records"]:
        lines.append(f"| {row['task_id']} | {row['rollout_id']} | {row['tool_calls']} | "
                     f"{row['mutation_calls']} | {row['class_calls'].get('S0', 0)} | "
                     f"{row['class_calls'].get('S1', 0)} | {row['verifier_exit_code']} | {row['termination']} |")
    lines += ["", f"Total calls: {report['total_calls']}. Verifier passes: {report['verifier_passes']}/16. "
              f"Invalid or early termination: {report['invalid_or_early']}.", "", "Smoke checks:", ""]
    lines += [f"- {key}: {'PASS' if value else 'FAIL'}" for key, value in report["checks"].items()]
    lines += ["", "These are collection checks. Opportunity classification and reuse benefit belong to P05."]
    markdown = "\n".join(lines) + "\n"
    args.report.with_suffix(".md").write_text(markdown)
    args.report.with_suffix(".md").chmod(0o666)
    cloud_report.with_suffix(".md").write_text(markdown)
    print(json.dumps({key: value for key, value in report.items() if key != "records"}))
    raise SystemExit(report["status"] != "PASS")
