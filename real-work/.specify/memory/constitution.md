# Real Work Constitution

## Core Principles

### Specify before implementation

Describe each feature's purpose, scope, users, acceptance criteria, and exclusions
in a feature specification before implementation. Mark unresolved requirements
explicitly. Do not invent an application scope or technology stack.

### Verify deterministic behavior

Executable changes require positive and negative tests. Bug fixes require a
reproduction and regression coverage where feasible. Run focused checks first,
then relevant integration checks; report checks that were not run.

### Preserve provenance and existing work

Keep upstream source, licenses, and history intact. Work in focused feature
branches and keep application work inside this workspace. Disclose agent-authored
commits using the parent repository's contribution rules.

### Protect secrets and private information

Never commit credentials, private research records, local environment files, or
machine-specific overrides. Use environment variables or a secrets manager for
runtime credentials. Review staged content before publishing.

### Prefer small, reversible changes

Use the simplest design that satisfies the approved specification. Keep
dependencies explicit, document setup and validation, and obtain approval before
destructive changes, publication outside the approved repository, or payments.

## Development Workflow

Use the installed specification, planning, task, implementation, and review
commands from the workspace root. Review the specification before planning and
review the plan and tasks before implementation. The assessment and bug-fix
workflows are independent entry points, not required phases of every feature.

Automatic extension hooks are disabled initially. Invoke required extension
commands explicitly, or enable hooks only after reviewing their behavior. The Git
extension's auto-commit defaults remain disabled.

## Quality Gates

Before a feature is considered complete, its acceptance criteria must be checked,
relevant tests must pass, setup instructions must match the implementation, and
the diff must be reviewed for secrets and unrelated changes. Workspace checks
validate scaffolding only; they are not application tests or production approval.

## Governance

This is a starter constitution for the working project. Amend it as requirements
become concrete, record the reason and date, and align the affected specifications
and checks. No application feature or production deployment has been approved by
the creation of this scaffold.

Version: 0.1.0 | Ratified: 2026-10-07 | Last Amended: 2026-10-07
