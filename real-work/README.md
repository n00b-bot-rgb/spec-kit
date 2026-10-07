# Spec Kit Real Work Workspace

This is the working project inside the Spec Kit fork. It preserves the toolkit
source at the repository root while keeping application specifications, code,
and tests separate. No application feature has been selected or implemented yet.

## Setup

Use Python 3.11 or newer, Git, and uv. Install Claude Code separately if you want
to execute the generated coding-agent skills; installing Specify does not install
or authenticate Claude Code.

From a fresh checkout:

```bash
git clone https://github.com/n00b-bot-rgb/spec-kit.git
cd spec-kit
uv tool install .
export PATH="$(uv tool dir --bin):$PATH"
cd real-work
python3 scripts/verify_workspace.py
python3 -m unittest discover -s tests -v
specify preset list
specify extension list
specify workflow list
```

If Specify is already installed and you intend to replace it with this checkout,
use `uv tool install --force .` from the repository root. This replaces the
existing Specify tool installation. The generated integration and installed
packages are already committed; do not rerun `specify init --force`.

## Installed components

- **Integration:** Claude Code skills with Bash scripts.
- **Presets:** `lean` and `constitution-sync`, both at priority 10. Constitution
  sync wraps the constitution command, while Lean supplies the shorter core
  workflow commands.
- **Extensions:** `agent-context`, `assess`, `bug`, `git`, `github`, and `selftest`.
  The `selftest` extension is a retained diagnostic utility, not the removed
  `self-test` preset. Running it is optional.
- **Workflows:** `speckit`, `assess`, and `bugfix`. All three are installed.
  Their related bundle contents were installed directly rather than through
  bundle registrations.
- **Removed presets:** `self-test` and the example scaffold whose installed ID
  was `my-preset`. Their source examples remain in the parent toolkit.

Automatic extension hooks are disabled for this starting configuration, and
auto-commit defaults remain disabled. These settings do not prevent explicitly
invoked workflows or agent commands from performing actions; review their steps.

## Start real work

Open Claude Code from `real-work/`, not the parent toolkit directory. Read the
constitution and choose a focused feature before starting implementation.

1. Create a Git feature branch, for example `git switch -c feat/first-feature`.
2. Run `/speckit-specify` with the feature description. Lean asks for a feature
   directory; use a path such as `specs/001-first-feature`.
3. Review `spec.md`, then run `/speckit-plan` and review `plan.md`.
4. Run `/speckit-tasks`, review the tasks, then `/speckit-implement`.
5. Run the feature's tests and applicable review commands before publishing.

The generated Claude skills use hyphenated invocation names. CLI artifact IDs
can use dot-separated names; these are different naming surfaces.

For an uncertain idea, start with `/speckit-assess-intake`. For a reproducible bug,
start with `/speckit-bug-assess`. The GitHub task-to-issues command creates remote
issues when executed; review the intended repository and payload first.

## Layout

```text
real-work/
  .claude/skills/          Generated Claude commands and relative symlinks
  .specify/               Installed packages, templates, and workflow state
  .specify/memory/         Starter constitution
  specs/                  Reviewed feature specifications
  src/                    Future application code
  tests/                  Workspace checks and future application tests
  scripts/                Local scaffold verification
  AGENTS.md               Working-project instructions
  CLAUDE.md               Claude entry-point instructions
```

Run CLI commands from this directory. From elsewhere, explicitly set
`SPECIFY_INIT_DIR` to the absolute `real-work` directory to target this project.
The workflow sources use paths relative to this workspace, and the generated
skill symlinks resolve within it.

## Validation and limits

`scripts/verify_workspace.py` checks installed component inventories, source
paths, JSON syntax, required skill files, safe hook defaults, authored
constitution text, and skill symlink portability. The unittest suite exercises
both valid and deliberately invalid workspace fixtures.

These are scaffolding checks only. They do not execute Claude, validate an
application feature, authenticate GitHub on another machine, or demonstrate
production readiness. Keep environment files, credentials, private research data,
and local feature-pointer state out of repository history.
