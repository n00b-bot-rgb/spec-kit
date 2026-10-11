# Research Dashboard Implementation Plan

Status: Draft proposal; UI stack and deployment require review.
Scope: fixture-driven dashboard first; read-only pipeline integration later.

## Technical Context

The shared JSON Schema and fixture batch live under `contracts/`. Python tools
validate the scaffold contract offline. No UI framework has been installed.

Proposed application direction: a local web UI with a small read-only API adapter.
React/TypeScript and a Python/FastAPI adapter are candidates, not approved
dependencies. Resolve Q-D1 before creating their manifests. A fixture adapter
keeps the first UI milestone independent of the real collection runner.

## Architecture

```text
synthetic fixture -> contract validation -> case-scoped repository
                                             |
                         case-filtered list/detail/run adapter
                                             |
                         dashboard list, provenance drawer, run panel
```

The case-scoped repository API takes `case_id` for every list, detail, and run
operation. Do not fetch all cases and rely on client-side filtering as a security
boundary. A local fixture demo is not sufficient access control for production;
authentication and authorization gate any private network deployment.

## Deployment Candidate: Vercel Python Runtime

Vercel is an unapproved candidate for a future hosted API milestone, not a
deployment decision. Its Python runtime supports ASGI and WSGI applications,
including FastAPI. If approved, the API would expose a top-level `app` handler
through a supported Python entrypoint or a `tool.vercel.entrypoint` setting in
`pyproject.toml`; Python dependencies and the supported interpreter version
would also need to be explicit.

Vercel routes requests to the function, and a frontend could be combined with
the backend through Services if that deployment model is approved. Python
bundles include files reachable at build time without automatic tree-shaking, so
any eventual configuration should exclude unnecessary tests and static assets
and keep runtime dependencies and the bundle within platform limits.

This option does not change the fixture-first, local milestone. Before adding
Vercel configuration or deploying, resolve Q-D1 and Q-D2, approve the framework,
hosting mode, authentication boundary, and data classification, and confirm
that only synthetic data is used unless private-data controls are separately
approved. A successful platform build would not establish production readiness.

## Decisions

- **Contract first:** Consume v1 evidence records and run manifests; do not
  introduce a second schema in UI component state.
- **Read-only MVP:** No collector-start, arbitrary fetch, deletion, or source-
  enable buttons.
- **Synthetic defaults:** The initial data path points to fixtures. Real records
  remain outside the public repository and require a separate approved adapter.
- **Conservative presentation:** Retrieval time is not event time. An unreviewed
  record is not a verified claim. An empty dataset is not proof of absence.
- **UI proposal:** A restrained dark theme, clear source/status labels, and
  keyboard-accessible controls. Visual direction is a proposal, not a delivered UI.

## File Boundaries

```text
src/dashboard/
  repository/       Case-scoped read interface and fixture adapter
  api/              Optional read-only service adapter after stack approval
  ui/               Case selector, list, filter controls, detail, run states
tests/dashboard/
  test_repository.* Case isolation, filters, and guessed-detail boundaries
  test_views.*      UI states, text escaping, keyboard behavior
```

Extensions are illustrative until stack approval determines file suffixes and
test tools. Existing shared contract checks are in `tests/test_feature_scaffolds.py`.

## Delivery Sequence

Review the spec and Q-D1, implement the fixture repository, then implement list
and detail views. Add collection-run states before wiring real pipeline results.
Resolve Q-D2 before any non-local or non-synthetic deployment. If Vercel is
approved, add and validate its Python function configuration as a separate
deployment milestone; do not treat configuration validation as deployment
authorization.

## Tests and Gates

- Positive: filter known fixtures, open provenance, display partial and failed runs.
- Negative: wrong case/detail combinations, malformed payloads, malicious text,
  unsupported links, missing fields, service errors, and empty-filter states.
- Gate: approve UI framework before dependency installation.
- Gate: approve authentication and data handling before real research data.
- Gate: approve an explicit destination before any public or remote deployment.
- Gate: approve Vercel, the ASGI/WSGI entrypoint, Python version, and bundle
  contents before adding platform-specific runtime configuration.

## Integration

The pipeline supplies batches matching `contracts/research-batch.schema.json`.
A fixture repository can be swapped for a private adapter without changing the
display model. Do not expose the raw artifact storage root through the API.
