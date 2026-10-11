"""Check CI admission, read-only permissions, coverage, and checkout guidance."""

from __future__ import annotations

import copy
import re
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_PATH = ROOT.parent / ".github/workflows/workspace.yml"
REQUIRED_COMMANDS = (
    "uv pip install --python .venv/bin/python -r requirements-dev.txt",
    "uvx ruff@0.15.0 check scripts tests",
    ".venv/bin/python scripts/verify_workspace.py",
    ".venv/bin/python scripts/validate_evidence.py",
    ".venv/bin/python -m unittest discover -s tests -v",
)


def workflow_errors(workflow):
    """Return missing guarantees for this narrowly scoped workspace workflow."""
    errors = []
    if workflow.get("permissions") != {"contents": "read"}:
        errors.append("Permissions must be read-only contents")
    triggers = workflow.get("on", {})
    for event in ("pull_request", "push"):
        paths = triggers.get(event, {}).get("paths", [])
        required_paths = (
            "real-work/**", ".github/workflows/workspace.yml",
            "workflows/**", "pyproject.toml",
        )
        if not all(path in paths for path in required_paths):
            errors.append(f"Missing workspace admission for {event}")
    branches = triggers.get("push", {}).get("branches", [])
    if branches != ["main", "feat/research-dashboard-osint-pipeline"]:
        errors.append("Unexpected push branch scope")
    job = workflow.get("jobs", {}).get("workspace", {})
    if job.get("defaults", {}).get("run", {}).get("working-directory") != "real-work":
        errors.append("Incorrect workspace working directory")
    versions = job.get("strategy", {}).get("matrix", {}).get("python-version")
    if versions != ["3.11", "3.14"]:
        errors.append("Missing minimum/current Python coverage")
    commands = "\n".join(step.get("run", "") for step in job.get("steps", []))
    for command in REQUIRED_COMMANDS:
        if command not in commands:
            errors.append(f"Missing command: {command}")
    for step in job.get("steps", []):
        if "uses" in step and not re.search(r"@[0-9a-f]{40}\Z", step["uses"]):
            errors.append("Action must be pinned to a commit")
    return errors


class WorkspaceCITests(unittest.TestCase):
    def setUp(self):
        # BaseLoader preserves GitHub's YAML 1.2 "on" key as a string.
        self.workflow = yaml.load(
            WORKFLOW_PATH.read_text(encoding="utf-8"), Loader=yaml.BaseLoader,
        )

    def test_workflow_covers_workspace(self):
        self.assertEqual(workflow_errors(self.workflow), [])

    def test_missing_test_command_is_detected(self):
        workflow = copy.deepcopy(self.workflow)
        workflow["jobs"]["workspace"]["steps"] = [
            step for step in workflow["jobs"]["workspace"]["steps"]
            if "unittest" not in step.get("run", "")
        ]
        self.assertTrue(any("unittest" in error for error in workflow_errors(workflow)))

    def test_missing_validator_is_detected(self):
        workflow = copy.deepcopy(self.workflow)
        workflow["jobs"]["workspace"]["steps"] = [
            step for step in workflow["jobs"]["workspace"]["steps"]
            if "validate_evidence.py" not in step.get("run", "")
        ]
        self.assertTrue(any("validate_evidence.py" in error for error in workflow_errors(workflow)))

    def test_missing_lint_is_detected(self):
        workflow = copy.deepcopy(self.workflow)
        workflow["jobs"]["workspace"]["steps"] = [
            step for step in workflow["jobs"]["workspace"]["steps"]
            if "ruff@" not in step.get("run", "")
        ]
        self.assertTrue(any("ruff@" in error for error in workflow_errors(workflow)))

    def test_paths_excluding_workspace_are_detected(self):
        workflow = copy.deepcopy(self.workflow)
        workflow["on"]["pull_request"]["paths"] = ["docs/**"]
        self.assertIn(
            "Missing workspace admission for pull_request", workflow_errors(workflow),
        )

    def test_unexpected_push_branch_is_detected(self):
        workflow = copy.deepcopy(self.workflow)
        workflow["on"]["push"]["branches"].append("unrelated-branch")
        self.assertIn("Unexpected push branch scope", workflow_errors(workflow))

    def test_write_permission_is_detected(self):
        workflow = copy.deepcopy(self.workflow)
        workflow["permissions"]["contents"] = "write"
        self.assertIn("Permissions must be read-only contents", workflow_errors(workflow))

    def test_unpinned_action_is_detected(self):
        workflow = copy.deepcopy(self.workflow)
        workflow["jobs"]["workspace"]["steps"][0]["uses"] = "actions/checkout@main"
        self.assertIn("Action must be pinned to a commit", workflow_errors(workflow))

    def test_root_working_directory_is_detected(self):
        workflow = copy.deepcopy(self.workflow)
        workflow["jobs"]["workspace"]["defaults"]["run"]["working-directory"] = "."
        self.assertIn("Incorrect workspace working directory", workflow_errors(workflow))

    def test_fresh_checkout_explicitly_selects_feature_branch(self):
        for filename in ("README.md", "START-HERE.md"):
            with self.subTest(filename=filename):
                text = (ROOT / filename).read_text(encoding="utf-8")
                self.assertIn(
                    "git clone --branch feat/research-dashboard-osint-pipeline --single-branch",
                    text,
                )

    def test_startup_guide_uses_published_branch_not_original_patch(self):
        text = (ROOT / "START-HERE.md").read_text(encoding="utf-8")
        self.assertIn("git switch --track origin/feat/research-dashboard-osint-pipeline", text)
        self.assertNotIn("changes are not on GitHub", text)
        self.assertNotIn("git am /path/to/research-features-scaffold.patch", text)


if __name__ == "__main__":
    unittest.main()
