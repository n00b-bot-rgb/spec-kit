# Working Project Instructions

This directory is the application workspace, not the implementation of the
Specify CLI. Read `.specify/memory/constitution.md` and the relevant feature
specification before making changes. Consult the parent `AGENTS.md` and
`CONTRIBUTING.md` for repository-wide rules and commit disclosure.

## Scope and layout

Put application code under `src/`, feature documents under `specs/`, and checks
under `tests/`. Do not modify the parent toolkit as a side effect of application
work. No application stack or first feature has been selected yet.

## Execution

Run Spec Kit commands from this directory. When running from elsewhere, export
`SPECIFY_INIT_DIR` with this directory's absolute path. Preserve relative skill
symlinks and their installed extension targets when copying the workspace.

Automatic extension hooks and auto-commit are disabled. Do not enable them or
create remote issues, pushes, deployments, or destructive changes without
authorization for the specific action.

## Verification

Run the local checks before committing workspace configuration:

```bash
python3 scripts/verify_workspace.py
python3 -m unittest discover -s tests -v
```

Add appropriate application tests as features are implemented. State exactly
which checks ran and which agent or integration paths were not exercised.
