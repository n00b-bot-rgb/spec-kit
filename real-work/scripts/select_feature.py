#!/usr/bin/env python3
"""Select one scaffolded feature in ignored local Spec Kit state."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

FEATURES = {
    "research-dashboard": "specs/001-research-dashboard",
    "osint-data-pipeline": "specs/002-osint-data-pipeline",
}


def select_feature(root: Path, name: str) -> str:
    root = root.resolve()
    if name not in FEATURES:
        raise ValueError("Unknown scaffolded feature")
    relative = FEATURES[name]
    feature = (root / relative).resolve()
    state = root / ".specify"
    if not feature.is_relative_to(root) or not state.resolve().is_relative_to(root):
        raise ValueError("Feature or state path escapes workspace")
    if not state.is_dir():
        raise ValueError("Not a Spec Kit workspace")
    if not all((feature / filename).is_file() for filename in ("spec.md", "plan.md", "tasks.md")):
        raise ValueError("Feature must contain spec.md, plan.md, and tasks.md")
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=state, delete=False) as handle:
            temporary = Path(handle.name)
            json.dump({"feature_directory": relative}, handle, indent=2)
            handle.write("\n")
        temporary.replace(state / "feature.json")
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    return relative


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("feature", choices=sorted(FEATURES))
    args = parser.parse_args()
    try:
        relative = select_feature(Path(__file__).resolve().parents[1], args.feature)
    except ValueError as exc:
        parser.exit(1, f"ERROR: {exc}\n")
    print(f"Selected {relative}")
    print("Next: launch Claude Code here; review the spec and plan before /speckit-implement.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
