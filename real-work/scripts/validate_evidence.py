#!/usr/bin/env python3
"""Validate a bounded local evidence batch; never fetch URLs or persist records."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from datetime import datetime
from pathlib import Path, PurePosixPath
from urllib.parse import parse_qs, urlsplit

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
MAX_BATCH_BYTES = 10 * 1024 * 1024
MAX_ARTIFACT_BYTES = 1024 * 1024
SECRET_QUERY_KEYS = {"token", "key", "apikey", "api_key", "auth", "authorization", "password", "secret"}


def record_id(case_id: str, source_id: str, identifier: str, checksum: str) -> str:
    encoded = json.dumps(
        [case_id, source_id, identifier, checksum],
        ensure_ascii=False, separators=(",", ":"),
    ).encode("utf-8")
    return "rec_" + hashlib.sha256(encoded).hexdigest()[:16]


def load_batch(path: Path) -> dict:
    with path.open("rb") as handle:
        content = handle.read(MAX_BATCH_BYTES + 1)
    if len(content) > MAX_BATCH_BYTES:
        raise ValueError("Batch exceeds 10 MiB validation limit")
    return json.loads(content)


def validate_batch(batch: dict, artifact_root: Path) -> list[str]:
    schema = json.loads((ROOT / "contracts" / "research-batch.schema.json").read_text())
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = [
        f"schema:{'/'.join(map(str, error.absolute_path))}: violates {error.validator}"
        for error in validator.iter_errors(batch)
    ]
    if errors:
        return errors
    timestamps = [record["retrieved_at"] for record in batch["records"]]
    timestamps += [run["started_at"] for run in batch["runs"]]
    timestamps += [run["finished_at"] for run in batch["runs"] if run["finished_at"] is not None]
    for timestamp in timestamps:
        try:
            datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        except ValueError:
            errors.append("Invalid UTC timestamp")
    if errors:
        return errors
    artifact_root = artifact_root.resolve()
    runs = {}
    counts: Counter = Counter()
    ids = set()
    identities = set()
    for run in batch["runs"]:
        if run["run_id"] in runs:
            errors.append("Duplicate run ID")
        runs[run["run_id"]] = run
    for record in batch["records"]:
        identity = tuple(record[key] for key in ("case_id", "source_id", "identifier", "content_sha256"))
        if record["record_id"] in ids or identity in identities:
            errors.append("Duplicate evidence version")
        ids.add(record["record_id"])
        identities.add(identity)
        if record["record_id"] != record_id(*identity):
            errors.append("Record ID does not match version identity")
        run = runs.get(record["run_id"])
        if not run or any(record[key] != run[key] for key in ("case_id", "source_id")):
            errors.append("Record/run case or source mismatch")
        counts[record["run_id"]] += 1
        try:
            url = urlsplit(record["source_url"])
            if not url.hostname or url.scheme != "https":
                errors.append("Invalid HTTPS source URL")
            if url.username or url.password or any(
                key.lower() in SECRET_QUERY_KEYS
                for key in parse_qs(url.query, keep_blank_values=True)
            ):
                errors.append("Credential-bearing source URL")
        except ValueError:
            errors.append("Invalid HTTPS source URL")
        relative = PurePosixPath(record["raw_artifact"])
        if relative.is_absolute() or ".." in relative.parts or "\\" in record["raw_artifact"]:
            errors.append("Unsafe raw artifact path")
            continue
        try:
            artifact = (artifact_root / str(relative)).resolve(strict=True)
            if not artifact.is_relative_to(artifact_root) or not artifact.is_file():
                errors.append("Raw artifact escapes root or is not a file")
                continue
            with artifact.open("rb") as handle:
                raw = handle.read(MAX_ARTIFACT_BYTES + 1)
            if len(raw) > MAX_ARTIFACT_BYTES:
                errors.append("Raw artifact exceeds 1 MiB validation limit")
            elif hashlib.sha256(raw).hexdigest() != record["content_sha256"]:
                errors.append("Raw artifact checksum mismatch")
        except (OSError, RuntimeError):
            errors.append("Raw artifact unavailable")
    for run in batch["runs"]:
        accepted, rejected, attempted = (run[key] for key in ("accepted_count", "rejected_count", "attempted_count"))
        if accepted + rejected != attempted or counts[run["run_id"]] != accepted:
            errors.append("Run counts do not reconcile")
        terminal = run["status"] not in ("queued", "running")
        if terminal != (run["finished_at"] is not None):
            errors.append("Run lifecycle timestamps do not match status")
        if run["finished_at"] is not None:
            started = datetime.fromisoformat(run["started_at"].replace("Z", "+00:00"))
            finished = datetime.fromisoformat(run["finished_at"].replace("Z", "+00:00"))
            if finished < started:
                errors.append("Run finished before it started")
        if run["status"] == "succeeded" and (rejected or run["failure_reason"] is not None):
            errors.append("Succeeded run contains failure")
        if run["status"] == "partial" and not (accepted and rejected and run["failure_reason"]):
            errors.append("Partial run must explain mixed outcomes")
        if run["status"] in ("failed", "blocked") and (accepted or not run["failure_reason"]):
            errors.append("Failed or blocked run must explain zero accepted evidence")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("batch", nargs="?", type=Path, default=ROOT / "contracts/fixtures/sample-batch.json")
    parser.add_argument("--artifact-root", type=Path, default=ROOT / "contracts/fixtures")
    args = parser.parse_args()
    try:
        errors = validate_batch(load_batch(args.batch), args.artifact_root)
    except (OSError, ValueError):
        print("FAIL: input or contract could not be loaded; no records persisted")
        return 1
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print("PASS: local evidence schema, identity, provenance, artifacts, and run accounting")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
