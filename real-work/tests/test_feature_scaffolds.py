"""Offline contract and feature-selection tests, including rejected inputs."""

from __future__ import annotations

import copy
import importlib.util
import json
import shutil
import socket
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]


def load_module(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


evidence = load_module("validate_evidence")
selector = load_module("select_feature")
SAMPLE = json.loads((ROOT / "contracts/fixtures/sample-batch.json").read_text())


class ContractTests(unittest.TestCase):
    def setUp(self):
        self.batch = copy.deepcopy(SAMPLE)
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "fixtures"
        shutil.copytree(ROOT / "contracts/fixtures", self.root)

    def errors(self):
        return evidence.validate_batch(self.batch, self.root)

    def test_schema_is_valid(self):
        schema = json.loads((ROOT / "contracts/research-batch.schema.json").read_text())
        Draft202012Validator.check_schema(schema)

    def test_valid_batch_without_network(self):
        with patch.object(socket.socket, "connect", side_effect=AssertionError("Network forbidden")):
            self.assertEqual(self.errors(), [])

    def test_missing_provenance(self):
        del self.batch["records"][0]["identifier"]
        self.assertTrue(any("required" in error for error in self.errors()))

    def test_wrong_schema_version(self):
        self.batch["schema_version"] = "2.0"
        self.assertTrue(any("const" in error for error in self.errors()))

    def test_checksum_mismatch(self):
        (self.root / "raw/publisher-report.txt").write_text("Changed fixture bytes")
        self.assertIn("Raw artifact checksum mismatch", self.errors())

    def test_case_path_traversal(self):
        self.batch["records"][0]["case_id"] = "../demo-beta"
        self.assertTrue(any("pattern" in error for error in self.errors()))

    def test_raw_path_traversal(self):
        self.batch["records"][0]["raw_artifact"] = "raw/../../outside.txt"
        self.assertIn("Unsafe raw artifact path", self.errors())

    def test_escaping_raw_symlink(self):
        outside = Path(self.temp.name) / "outside.txt"
        outside.write_text("Outside root")
        path = self.root / "raw/publisher-report.txt"
        path.unlink()
        path.symlink_to(outside)
        self.assertIn("Raw artifact escapes root or is not a file", self.errors())

    def test_oversized_artifact(self):
        (self.root / "raw/publisher-report.txt").write_bytes(b"x" * (evidence.MAX_ARTIFACT_BYTES + 1))
        self.assertIn("Raw artifact exceeds 1 MiB validation limit", self.errors())

    def test_cross_case_run(self):
        self.batch["records"][0]["run_id"] = "run_beta_success"
        self.assertIn("Record/run case or source mismatch", self.errors())

    def test_duplicate_evidence(self):
        self.batch["records"].append(copy.deepcopy(self.batch["records"][0]))
        self.assertIn("Duplicate evidence version", self.errors())

    def test_duplicate_run(self):
        self.batch["runs"].append(copy.deepcopy(self.batch["runs"][0]))
        self.assertIn("Duplicate run ID", self.errors())

    def test_counts_reconcile(self):
        self.batch["runs"][0]["attempted_count"] = 4
        self.assertIn("Run counts do not reconcile", self.errors())

    def test_failure_not_labeled_success(self):
        self.batch["runs"][0]["status"] = "succeeded"
        self.assertIn("Succeeded run contains failure", self.errors())

    def test_county_known_requires_value(self):
        self.batch["records"][0]["jurisdiction"]["county_status"] = "known"
        self.assertTrue(any("type" in error for error in self.errors()))

    def test_invalid_calendar_date(self):
        self.batch["records"][0]["retrieved_at"] = "2026-02-30T12:00:00Z"
        self.assertTrue(self.errors())

    def test_embedded_credentials_rejected(self):
        self.batch["records"][0]["source_url"] = "https://user:password@example.org/report"
        self.assertTrue(self.errors())

    def test_query_credential_redacted(self):
        self.batch["records"][0]["source_url"] = "https://example.org/report?token=never-print-this"
        errors = self.errors()
        self.assertIn("Credential-bearing source URL", errors)
        self.assertNotIn("never-print-this", " ".join(errors))

    def test_credential_aliases_are_rejected_without_values(self):
        for key in (
            "access_token", "ACCESS_TOKEN", "access-token", "client_secret",
            "CLIENT-SECRET", "Api_Key", "X-Api-Key", "refresh_token",
            "id_token", "X-Amz-Signature", "sig",
        ):
            with self.subTest(key=key):
                self.batch["records"][0]["source_url"] = (
                    f"https://example.org/report?{key}=SYNTHETIC_SECRET_VALUE"
                )
                errors = self.errors()
                self.assertIn("Credential-bearing source URL", errors)
                self.assertNotIn("SYNTHETIC_SECRET_VALUE", " ".join(errors))

    def test_encoded_credential_query_key_rejected(self):
        self.batch["records"][0]["source_url"] = (
            "https://example.org/report?access%5Ftoken=SYNTHETIC_SECRET_VALUE"
        )
        self.assertIn("Credential-bearing source URL", self.errors())

    def test_fragment_credential_rejected_without_value(self):
        self.batch["records"][0]["source_url"] = (
            "https://example.org/report#access_token=SYNTHETIC_SECRET_VALUE"
        )
        errors = self.errors()
        self.assertIn("Credential-bearing source URL", errors)
        self.assertNotIn("SYNTHETIC_SECRET_VALUE", " ".join(errors))

    def test_noncredential_query_and_anchor_allowed(self):
        self.batch["records"][0]["source_url"] = (
            "https://example.org/report?record_id=REPORT-001&page=1#methods"
        )
        self.assertEqual(self.errors(), [])

    def test_invalid_url_ports_rejected(self):
        for port in ("not-a-port", "-1", "65536", "0"):
            with self.subTest(port=port):
                self.batch["records"][0]["source_url"] = (
                    f"https://example.org:{port}/report"
                )
                self.assertIn("Invalid HTTPS source URL", self.errors())

    def test_valid_explicit_url_ports_allowed(self):
        for port in ("443", "8443"):
            with self.subTest(port=port):
                self.batch["records"][0]["source_url"] = (
                    f"https://example.org:{port}/report"
                )
                self.assertEqual(self.errors(), [])

    def test_safe_id_control_characters_rejected(self):
        schema = json.loads((ROOT / "contracts/research-batch.schema.json").read_text())
        validator = Draft202012Validator(schema["$defs"]["safeId"])
        for value in ("demo-alpha\n", "demo-alpha\r", "demo-alpha\t", "demo-alpha\0"):
            with self.subTest(value=repr(value)):
                self.assertFalse(validator.is_valid(value))

    def test_newline_case_id_rejected_with_consistent_references(self):
        for record in self.batch["records"]:
            if record["case_id"] == "demo-alpha":
                record["case_id"] += "\n"
                record["record_id"] = evidence.record_id(
                    record["case_id"], record["source_id"],
                    record["identifier"], record["content_sha256"],
                )
        for run in self.batch["runs"]:
            if run["case_id"] == "demo-alpha":
                run["case_id"] += "\n"
        self.assertTrue(any("pattern" in error for error in self.errors()))

    def test_full_string_patterns_reject_trailing_newline(self):
        schema = json.loads((ROOT / "contracts/research-batch.schema.json").read_text())
        fields = schema["$defs"]["record"]["properties"]
        checks = (
            ("record_id", fields["record_id"], SAMPLE["records"][0]["record_id"]),
            ("checksum", fields["content_sha256"], SAMPLE["records"][0]["content_sha256"]),
            ("url", fields["source_url"], "https://example.org/report"),
            ("timestamp", schema["$defs"]["utcTimestamp"], "2026-01-01T12:00:00Z"),
        )
        for label, field_schema, valid_value in checks:
            with self.subTest(field=label):
                validator = Draft202012Validator(field_schema)
                self.assertTrue(validator.is_valid(valid_value))
                self.assertFalse(validator.is_valid(valid_value + "\n"))

    def make_queued_run(self):
        run = self.batch["runs"][0]
        self.batch["records"] = [
            record for record in self.batch["records"]
            if record["run_id"] != run["run_id"]
        ]
        run.update(
            status="queued", started_at=None, finished_at=None,
            attempted_count=0, accepted_count=0, rejected_count=0,
            failure_reason=None,
        )
        return run

    def test_legacy_queued_run_with_completed_records_rejected(self):
        self.batch["runs"][0].update(status="queued", finished_at=None)
        self.assertTrue(self.errors())

    def test_unstarted_empty_queued_run_allowed(self):
        self.make_queued_run()
        self.assertEqual(self.errors(), [])

    def test_queued_run_with_start_timestamp_rejected(self):
        run = self.make_queued_run()
        run["started_at"] = "2026-01-01T12:00:00Z"
        self.assertTrue(self.errors())

    def test_queued_run_with_processed_evidence_rejected(self):
        run = self.make_queued_run()
        self.batch["records"].append(copy.deepcopy(SAMPLE["records"][0]))
        run.update(attempted_count=1, accepted_count=1)
        self.assertIn("Queued run must be unprocessed and have no failure", self.errors())

    def test_queued_run_with_failure_reason_rejected(self):
        run = self.make_queued_run()
        run["failure_reason"] = "Synthetic error"
        self.assertIn("Queued run must be unprocessed and have no failure", self.errors())

    def test_running_run_can_report_progress(self):
        self.batch["runs"][0].update(status="running", finished_at=None)
        self.assertEqual(self.errors(), [])

    def test_running_run_requires_start_timestamp(self):
        self.batch["runs"][0].update(
            status="running", started_at=None, finished_at=None,
        )
        self.assertTrue(self.errors())

    def test_terminal_run_requires_finish_timestamp(self):
        self.batch["runs"][0]["finished_at"] = None
        self.assertIn("Run lifecycle timestamps do not match status", self.errors())

    def test_terminal_run_cannot_finish_before_start(self):
        self.batch["runs"][0]["finished_at"] = "2025-12-31T12:00:00Z"
        self.assertIn("Run finished before it started", self.errors())

    def test_ids_are_case_scoped(self):
        first, third = self.batch["records"][0], self.batch["records"][2]
        self.assertEqual(first["content_sha256"], third["content_sha256"])
        self.assertNotEqual(first["record_id"], third["record_id"])

    def test_retrieval_does_not_change_version_id(self):
        first = self.batch["records"][0]
        original = evidence.record_id(first["case_id"], first["source_id"], first["identifier"], first["content_sha256"])
        first["retrieved_at"] = "2026-01-02T12:00:00Z"
        updated = evidence.record_id(first["case_id"], first["source_id"], first["identifier"], first["content_sha256"])
        self.assertEqual(original, updated)

    def test_changed_content_changes_version_id(self):
        first = self.batch["records"][0]
        updated = evidence.record_id(first["case_id"], first["source_id"], first["identifier"], "0" * 64)
        self.assertNotEqual(first["record_id"], updated)

    def test_oversized_batch_file(self):
        path = self.root / "oversized.json"
        path.write_bytes(b"x" * (evidence.MAX_BATCH_BYTES + 1))
        with self.assertRaisesRegex(ValueError, "10 MiB"):
            evidence.load_batch(path)

    def test_oversized_record_array(self):
        self.batch["records"] = [self.batch["records"][0]] * 2001
        self.assertTrue(any("maxItems" in error for error in self.errors()))


class FeatureSelectionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "workspace"
        self.root.mkdir()
        (self.root / ".specify").mkdir()
        shutil.copytree(ROOT / "specs", self.root / "specs")

    def test_select_dashboard(self):
        selected = selector.select_feature(self.root, "research-dashboard")
        self.assertEqual(selected, "specs/001-research-dashboard")
        state = json.loads((self.root / ".specify/feature.json").read_text())
        self.assertEqual(state["feature_directory"], selected)

    def test_switch_to_pipeline(self):
        selector.select_feature(self.root, "research-dashboard")
        selector.select_feature(self.root, "osint-data-pipeline")
        state = json.loads((self.root / ".specify/feature.json").read_text())
        self.assertEqual(state["feature_directory"], "specs/002-osint-data-pipeline")

    def test_unknown_feature_leaves_state_untouched(self):
        with self.assertRaises(ValueError):
            selector.select_feature(self.root, "../../unknown")
        self.assertFalse((self.root / ".specify/feature.json").exists())

    def test_missing_plan_leaves_state_untouched(self):
        (self.root / "specs/001-research-dashboard/plan.md").unlink()
        with self.assertRaises(ValueError):
            selector.select_feature(self.root, "research-dashboard")
        self.assertFalse((self.root / ".specify/feature.json").exists())

    def test_escaping_feature_symlink(self):
        path = self.root / "specs/001-research-dashboard"
        shutil.rmtree(path)
        path.symlink_to(self.root.parent)
        with self.assertRaisesRegex(ValueError, "escapes"):
            selector.select_feature(self.root, "research-dashboard")


if __name__ == "__main__":
    unittest.main()
