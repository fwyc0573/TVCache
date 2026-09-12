"""Exercise real VideoAgent HTTP tools and record their results and durations."""

import argparse
import json
import os
from pathlib import Path
import time
from uuid import uuid4

import httpx


def main(args):
    manifest = json.loads(args.manifest.read_text())
    sandbox_id = "tool-smoke-" + uuid4().hex
    result = {"sandbox_id": sandbox_id, "video_id": manifest["video_id"], "calls": []}
    started = False

    def record_call(client, endpoint, body):
        before = time.monotonic()
        response = client.post(args.sandbox_url + endpoint, json=body)
        row = {"endpoint": endpoint, "command": body.get("command"),
               "status_code": response.status_code,
               "seconds": time.monotonic() - before, "body": response.json()}
        result["calls"].append(row)
        args.output.write_text(json.dumps(result, indent=2) + "\n")
        print(json.dumps(row), flush=True)
        response.raise_for_status()
        assert row["body"]["success"] is True, row
        return row["body"]

    with httpx.Client(timeout=httpx.Timeout(1800, connect=10)) as client:
        try:
            record_call(client, "/start", {"sandbox_id": sandbox_id})
            started = True
            commands = [
                ("load_video_into_sandbox", manifest["video_id"] + ".mp4"),
                ("preprocess", ""),
                ("caption_retrieval", "(0, 1)"),
                ("segment_localization", "a person painting a picture"),
                ("visual_question_answering", "('What is the person doing?', 0)"),
            ]
            for command, argument in commands:
                body = record_call(client, "/execute", {
                    "sandbox_id": sandbox_id, "command": command, "argument": argument,
                })
                assert isinstance(body["result"], str) and body["result"].strip(), body
                if command == "visual_question_answering":
                    assert "Segment description:" in body["result"], body
                    assert "Answer to the question:" in body["result"], body
        finally:
            if started:
                record_call(client, "/stop", {
                    "sandbox_id": sandbox_id, "operation_id": uuid4().hex,
                })
                remaining = Path(os.environ["VIDEO_AGENT_SANDBOX_DIR"]) / sandbox_id
                assert not remaining.exists(), remaining
    result["status"] = "PASS"
    args.output.write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--sandbox-url", default="http://127.0.0.1:5000")
    main(parser.parse_args())
