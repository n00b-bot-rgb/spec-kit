"""Positive and negative coverage for the scaffold validator."""

from __future__ import annotations

import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_SPEC = importlib.util.spec_from_file_location(
    "verify_workspace", ROOT / "scripts" / "verify_workspace.py"
)
assert MODULE_SPEC is not None and MODULE_SPEC.loader is not None
validator = importlib.util.module_from_spec(MODULE_SPEC)
MODULE_SPEC.loader.exec_module(validator)


class WorkspaceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.parent = Path(self.temp.name)
        self.root = self.parent / "real-work"
        shutil.copytree(
            ROOT, self.root, symlinks=True,
            ignore=shutil.ignore_patterns("__pycache__", ".venv"),
        )
        shutil.copytree(ROOT.parent / "workflows", self.parent / "workflows")

    def errors(self):
        return validator.validate_workspace(self.root)

    def test_valid_portable_copy(self):
        self.assertEqual(self.errors(), [])

    def test_missing_required_file(self):
        (self.root / "AGENTS.md").unlink()
        self.assertIn("Missing required file: AGENTS.md", self.errors())

    def test_self_test_preset_rejected(self):
        path = self.root / ".specify" / "presets" / ".registry"
        data = json.loads(path.read_text())
        data["presets"]["self-test"] = {"enabled": True}
        path.write_text(json.dumps(data))
        self.assertTrue(any("Unexpected presets inventory" in error for error in self.errors()))

    def test_malformed_json(self):
        path = self.root / ".specify" / "integration.json"
        path.write_text("{invalid")
        self.assertTrue(any("Invalid JSON" in error for error in self.errors()))

    def test_broken_skill_link(self):
        path = self.root / ".claude" / "skills" / "speckit-bug-assess" / "SKILL.md"
        path.unlink()
        path.symlink_to("missing.md")
        self.assertTrue(any("Broken skill symlink" in error for error in self.errors()))

    def test_absolute_escaping_link(self):
        path = self.root / ".claude" / "skills" / "speckit-bug-assess" / "SKILL.md"
        path.unlink()
        outside = self.parent / "outside.md"
        outside.write_text("outside")
        path.symlink_to(outside)
        self.assertTrue(any("Absolute skill symlink" in error for error in self.errors()))
        self.assertTrue(any("escapes workspace" in error for error in self.errors()))

    def test_machine_specific_workflow_source(self):
        path = self.root / ".specify" / "workflows" / "workflow-registry.json"
        data = json.loads(path.read_text())
        data["workflows"]["speckit"]["source"] = "/nonportable/workflows/speckit"
        path.write_text(json.dumps(data))
        self.assertIn("Nonportable workflow source: speckit", self.errors())

    def test_placeholder_constitution(self):
        path = self.root / ".specify" / "memory" / "constitution.md"
        path.write_text("# [PROJECT_NAME] Constitution")
        self.assertIn("Unfilled constitution placeholders", self.errors())

    def test_automatic_hooks_rejected(self):
        path = self.root / ".specify" / "extensions.yml"
        path.write_text(path.read_text().replace("auto_execute_hooks: false", "auto_execute_hooks: true"))
        self.assertIn("Automatic hooks must remain disabled in the starter", self.errors())


if __name__ == "__main__":
    unittest.main()
