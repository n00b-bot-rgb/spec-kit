# Workspace Validation

Validation was performed on 2026-10-07 in the Computer sandbox. These results
cover the configured workspace, feature scaffolds, and selected upstream behavior,
not implemented application features or a live Claude session.

## Research-feature scaffold revision

- A dedicated workspace virtualenv was created and `requirements-dev.txt` was
  installed successfully.
- The workspace validator and offline evidence validator both passed.
- The workspace unittest suite now has 37 passing tests: 9 workspace tests and
  28 evidence-contract/feature-selector tests.
- The 56 focused upstream tests listed below were rerun and passed.
- Both dashboard and pipeline feature selections passed
  `.specify/scripts/bash/check-prerequisites.sh --json --require-spec
  --require-tasks --include-tasks`.
- The dashboard was left as the selected local feature. Its pointer is gitignored.
- The UI, persistence importer, live collector, and complete agent workflow
  remain unimplemented/unexecuted. The total is 93 focused passing tests, not
  application end-to-end coverage.

## Original workspace checks

- `python3 scripts/verify_workspace.py`: passed workspace inventory,
  constitution, JSON, workflow source-path, hook-default, and skill checks.
- `python3 -m unittest discover -s tests -v`: 9 tests passed. Coverage includes
  a portable workspace copy and rejection of missing instructions, self-test
  preset registration, malformed JSON, broken or escaping skill links,
  machine-specific workflow sources, constitution placeholders, and enabled
  automatic hooks.
- Parent repository `.venv/bin/python -m pytest
  tests/specify_cli/presets/test_registry.py
  tests/test_constitution_template_sync_report.py
  tests/test_agent_config_consistency.py -q`: 56 tests passed.
- `specify artifact list --json`: successfully enumerated 57 artifacts.
- `specify preset list`: only `constitution-sync` and `lean` were installed.
- `specify workflow list`: `speckit`, `assess`, and `bugfix` were installed.
- `git diff --check`: passed.
- A clean local Git clone passed the workspace validator and all 9 workspace
  tests, and the CLI again enumerated 57 artifacts.
- Staged-file screening found no matching credential patterns, sensitive
  credential filenames, or sandbox-specific absolute paths.

## Limits

The full upstream test suite was not run. No Claude model invocation, complete
SDD workflow, application implementation, remote issue creation, or production
deployment was exercised. Local configuration validation and credential-pattern
screening do not constitute a full security audit.

## AI assistance

Perplexity Computer using Claude Opus 5.5 acted autonomously on the user's request
to clean, scaffold, validate, and push the project. The repository operator did
not perform a line-by-line review before the agent-authored commit.
