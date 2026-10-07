# Feature Specifications

Create a separate directory for each approved feature, such as
`001-first-feature/`. Keep its specification, implementation plan, and task list
together so they can be reviewed against the resulting code.

Two draft features are available:

- `001-research-dashboard/`: a case-isolated evidence browser, provenance details,
  and collection-run status, initially using synthetic fixtures.
- `002-osint-data-pipeline/`: a bounded, provenance-preserving importer with case
  separation and disabled-by-default future collection adapters.

Each contains `spec.md`, `plan.md`, and `tasks.md`. Review the open questions and
approval gates before implementation. Both consume the versioned evidence
contract under `../contracts/`; the dashboard can start with fixtures without
waiting for live collection.
