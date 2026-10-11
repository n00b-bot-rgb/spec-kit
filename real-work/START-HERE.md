# Start Your Research Features with Spec Kit

Two draft features are scaffolded: `001-research-dashboard` and
`002-osint-data-pipeline`. Both have a specification, implementation plan, and
task checklist. The dashboard starts with synthetic data; the pipeline starts
with offline import. No UI, importer/store, or live collector is implemented yet.

## Where the scaffold lives

The scaffold is published on GitHub branch
`feat/research-dashboard-osint-pipeline` and is under review in
[pull request #1](https://github.com/n00b-bot-rgb/spec-kit/pull/1).
While the PR is unmerged, use this branch rather than the default `main` branch.

For a fresh checkout:

```bash
git clone --branch feat/research-dashboard-osint-pipeline --single-branch \
  https://github.com/n00b-bot-rgb/spec-kit.git
cd spec-kit
```

For an existing checkout with no local branch of that name:

```bash
cd /path/to/spec-kit
git status --short
# Continue only if the working tree is clean.
git fetch origin
git switch --track origin/feat/research-dashboard-osint-pipeline
```

If the local branch already exists and the working tree is clean:

```bash
git switch feat/research-dashboard-osint-pipeline
git pull --ff-only origin feat/research-dashboard-osint-pipeline
```

Stop on divergence instead of force-resetting existing work. None of these
checkout paths merges the feature branch into `main`.

The earlier `research-features-scaffold.patch` is a historical copy of the
initial scaffold; it does not include the follow-up fixes. Do not apply it on top
of the published branch. The branch checkout is the current source of truth.

```text
real-work/
  START-HERE.md
  specs/001-research-dashboard/{spec,plan,tasks}.md
  specs/002-osint-data-pipeline/{spec,plan,tasks}.md
  contracts/research-batch.schema.json
  contracts/fixtures/sample-batch.json
  contracts/fixtures/raw/
  scripts/select_feature.py
  scripts/validate_evidence.py
  src/dashboard/README.md
  src/pipeline/README.md
  tests/test_feature_scaffolds.py
```

The JSON contract and artifacts are synthetic. The source URLs are labels,
not enabled sources. The private OSINT runner's code and real research records
have not been copied into the public Spec Kit fork.

## Prepare the local workspace

From a checkout containing this branch:

```bash
cd /path/to/spec-kit
git switch feat/research-dashboard-osint-pipeline

# Install this checkout's Specify CLI if it is not already installed.
uv tool install .
export PATH="$(uv tool dir --bin):$PATH"

cd real-work
uv venv .venv
uv pip install --python .venv/bin/python -r requirements-dev.txt
python3 scripts/verify_workspace.py
.venv/bin/python scripts/validate_evidence.py
.venv/bin/python -m unittest discover -s tests -v
uvx ruff@0.15.0 check scripts tests
```

If Specify is already installed and you want to replace it with this checkout,
use `uv tool install --force .` from the repository root, not `real-work/`.
Install and authenticate Claude Code separately. Do not run `specify init --force`
over this configured workspace.

## Start the research dashboard

The feature selector writes `.specify/feature.json`, which is local and
gitignored. It does not create a branch, call an agent, publish changes, or run
collection. Select the dashboard before launching the agent:

```bash
cd /path/to/spec-kit/real-work
python3 scripts/select_feature.py research-dashboard
claude
```

In Claude Code, enter:

```text
/speckit-specify Review and refine the existing research-dashboard draft.
Use specs/001-research-dashboard. Preserve its requirement IDs, provenance
requirements, case isolation, and fixture-first scope. Ask about blocking
questions before choosing a UI framework or implementing anything.
```

When the Lean specify command asks for a feature directory, answer:

```text
specs/001-research-dashboard
```

The spec already exists, so this is a review/refinement pass, not a request to
discard it. Review the resulting changes before continuing:

```text
/speckit-plan Review the existing dashboard plan. Resolve Q-D1 with me,
keep the first milestone local and synthetic, and do not install application
dependencies until I approve the framework.

/speckit-tasks Reconcile the existing dashboard checklist with the reviewed
plan. Preserve task IDs and make the stack/data/deployment approval gates
explicit. Do not execute implementation tasks yet.
```

After approving the spec, plan, and task scope, request:

```text
/speckit-implement Implement only the approved fixture-driven dashboard
milestone. Do not add real collectors, publish a site, enable automatic hooks,
or connect real case data.
```

The implementation command delegates work to the coding agent. A terminal
`specify` command alone does not implement the application.

## Start the OSINT pipeline

Exit or pause the current agent session first so it does not retain the wrong
feature scope. Select the second feature, then launch Claude from this directory:

```bash
python3 scripts/select_feature.py osint-data-pipeline
claude
```

Start with:

```text
/speckit-specify Review and refine specs/002-osint-data-pipeline.
Preserve the shared evidence contract, bounded offline import, provenance,
case separation, changed-content history, and disabled live sources.
```

When asked for the directory, answer `specs/002-osint-data-pipeline`. Review it,
then use:

```text
/speckit-plan Review the existing pipeline plan. Ask me to resolve Q-P1
before choosing persistence or touching the private runner. Keep live collection
and real artifacts out of this milestone.

/speckit-tasks Reconcile the existing pipeline tasks with the reviewed plan.
Keep source approval, retention, and network safeguards as explicit gates.
```

After those reviews, request implementation of the approved offline importer
milestone only. Do not enable live sources as a shortcut for testing.

## Check Spec Kit wiring

This checkout uses hyphenated Claude skill names, such as `/speckit-specify`,
not the dot-separated slash-command spelling used in some other integrations.
CLI inventory names use dots:

```bash
specify artifact info command:speckit.specify --json
specify preset list
specify workflow list

# Validate the selected feature's existing files without invoking an agent.
bash .specify/scripts/bash/check-prerequisites.sh \
  --json --require-spec --require-tasks --include-tasks
```

Keep terminal commands and agent slash commands separate. Run terminal commands
from `real-work/`; from elsewhere set `SPECIFY_INIT_DIR` explicitly.

## Recommended order and review gates

Review the shared contract first. Develop the dashboard's fixture views and the
pipeline's offline importer independently, then connect them through a case-scoped
read adapter. Only afterward consider one explicitly authorized real source.

UI framework and persistence are draft decisions. Local synthetic tests are not
proof of production authorization, application security, or successful collection.
Automatic extension hooks remain disabled. Do not push, deploy, create issues,
or enable live collection without approval for that specific action.

## Scaffold validation

The initial scaffold passed 37 workspace/contract/selector tests and 56 focused
upstream tests. The follow-up adds regression and CI-wiring tests; consult
`VALIDATION.md` for the latest local results and PR #1 for hosted checks.

The dedicated workspace CI runs on relevant pull requests and pushes to `main`
or the feature branch, using Python 3.11 and 3.14 on Ubuntu. It checks the new
Python files, both validators, and the workspace tests rather than relying on
the parent toolkit's test-discovery paths.

These results verify the scaffold only. No UI, persistent importer, live source,
Claude model execution, or full upstream test-suite run is claimed.
