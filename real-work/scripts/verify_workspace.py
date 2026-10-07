#!/usr/bin/env python3
"""Validate the configured workspace without running an agent or remote action."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

EXPECTED_PRESETS = {"lean", "constitution-sync"}
EXPECTED_EXTENSIONS = {"agent-context", "assess", "bug", "git", "github", "selftest"}
EXPECTED_WORKFLOWS = {"speckit", "assess", "bugfix"}
REQUIRED_SKILLS = {
    "speckit-specify",
    "speckit-plan",
    "speckit-tasks",
    "speckit-implement",
    "speckit-constitution",
    "speckit-assess-intake",
    "speckit-bug-assess",
}


def validate_workspace(root: Path) -> list[str]:
    """Return actionable errors; do not modify files or execute tools."""
    root = root.resolve()
    errors: list[str] = []
    for path in (
        "README.md",
        "AGENTS.md",
        "CLAUDE.md",
        "specs/README.md",
        "src/README.md",
        ".specify/memory/constitution.md",
        ".specify/extensions.yml",
    ):
        if not (root / path).is_file():
            errors.append(f"Missing required file: {path}")

    registries = (
        (".specify/presets/.registry", "presets", EXPECTED_PRESETS, "preset.yml"),
        (".specify/extensions/.registry", "extensions", EXPECTED_EXTENSIONS, "extension.yml"),
        (".specify/workflows/workflow-registry.json", "workflows", EXPECTED_WORKFLOWS, "workflow.yml"),
    )
    for relative, key, expected, manifest in registries:
        try:
            data = json.loads((root / relative).read_text(encoding="utf-8"))
            entries = data[key]
            if not isinstance(entries, dict):
                raise ValueError(f"{key} must be an object")
        except (OSError, ValueError, KeyError, TypeError) as exc:
            errors.append(f"Invalid registry {relative}: {exc}")
            continue
        if set(entries) != expected:
            errors.append(f"Unexpected {key} inventory: {sorted(entries)}")
        for name, entry in entries.items():
            if not isinstance(entry, dict):
                errors.append(f"Invalid {key} entry: {name}")
                continue
            if not (root / ".specify" / key / name / manifest).is_file():
                errors.append(f"Missing {key} manifest: {name}")
            if key != "workflows" and entry.get("enabled") is not True:
                errors.append(f"Disabled {key} entry: {name}")
            if key == "workflows":
                source = entry.get("source")
                if not isinstance(source, str) or Path(source).is_absolute():
                    errors.append(f"Nonportable workflow source: {name}")
                elif not (root / source / manifest).is_file():
                    errors.append(f"Missing workflow source: {name}")

    specify = root / ".specify"
    if specify.is_dir():
        for path in specify.rglob("*.json"):
            try:
                json.loads(path.read_text(encoding="utf-8"))
            except (OSError, ValueError) as exc:
                errors.append(f"Invalid JSON {path.relative_to(root)}: {exc}")
    skills = root / ".claude" / "skills"
    for name in sorted(REQUIRED_SKILLS):
        if not (skills / name / "SKILL.md").is_file():
            errors.append(f"Missing required skill: {name}")
    if skills.is_dir():
        for path in skills.rglob("*"):
            if path.is_symlink():
                if Path(path.readlink()).is_absolute():
                    errors.append(f"Absolute skill symlink: {path.relative_to(root)}")
                if not path.exists():
                    errors.append(f"Broken skill symlink: {path.relative_to(root)}")
                if not path.resolve().is_relative_to(root):
                    errors.append(f"Skill symlink escapes workspace: {path.relative_to(root)}")
        for name in ("speckit-wrap-test", "speckit-myext-myextcmd"):
            if (skills / name).exists():
                errors.append(f"Leftover example skill: {name}")

    constitution = root / ".specify" / "memory" / "constitution.md"
    if constitution.is_file():
        content = constitution.read_text(encoding="utf-8")
        if re.search(r"\[(?:PROJECT_NAME|PRINCIPLE_\d+_\w+|CONSTITUTION_VERSION)\]", content):
            errors.append("Unfilled constitution placeholders")
        if "preset:self-test" in content or "Constitution (Self-Test Preset)" in content:
            errors.append("Self-test constitution still active")
    config = root / ".specify" / "extensions.yml"
    if config.is_file():
        content = config.read_text(encoding="utf-8")
        if not re.search(r"^\s+auto_execute_hooks:\s+false\s*$", content, re.MULTILINE):
            errors.append("Automatic hooks must remain disabled in the starter")
    return errors


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    errors = validate_workspace(root)
    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print("PASS: workspace inventory, constitution, JSON, sources, hooks, and skills")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
