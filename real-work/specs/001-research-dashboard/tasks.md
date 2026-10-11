# Research Dashboard Tasks

Status: Draft; uncompleted tasks are not authorization to execute.
Dependencies: Q-D1 gates application stack; Q-D2 gates real/private data.

## Setup

- [x] [D001] Scaffold the specification and plan in `specs/001-research-dashboard/`.
- [x] [D002] Add shared synthetic evidence contracts and tests in `contracts/` and `tests/test_feature_scaffolds.py`.
- [ ] [D003] Resolve Q-D1 and record the selected UI stack in `specs/001-research-dashboard/plan.md`.
- [ ] [D004] Initialize only the approved application dependencies under `src/dashboard/`.

## Foundation

- [ ] [D005] Implement case-scoped list/detail/run interfaces in `src/dashboard/repository/`; cover DASH-001 and DASH-008.
- [ ] [D006] Write positive fixture and wrong-case detail tests in `tests/dashboard/` before implementing the adapter.
- [ ] [D007] Add schema-error and service-unavailable handling in `src/dashboard/repository/`; cover DASH-006.

## Evidence Browsing

- [ ] [D008] Implement explicit case selection and evidence rows in `src/dashboard/ui/`; cover DASH-001 and DASH-002.
- [ ] [D009] Implement source/route filters, local-case text search, reset, and distinct empty states in `src/dashboard/ui/`; cover DASH-003 and DASH-006.
- [ ] [D010] Add filter and case-switch acceptance tests in `tests/dashboard/`.

## Provenance

- [ ] [D011] Add the provenance detail view with UTC retrieval time, jurisdiction state, checksum, and review label in `src/dashboard/ui/`; cover DASH-004.
- [ ] [D012] Add escaping, unsafe-link, and raw-path disclosure tests in `tests/dashboard/`; cover DASH-007.

## Collection Status

- [ ] [D013] Implement run outcomes, counts, and bounded diagnostics in `src/dashboard/ui/`; cover DASH-005.
- [ ] [D014] Test partial, failed, blocked, and zero-record outcomes in `tests/dashboard/`.

## Review

- [ ] [D015] Check keyboard controls and the documented fixture performance budget in `tests/dashboard/`; record results in `specs/001-research-dashboard/validation.md`.
- [ ] [D016] Resolve Q-D2 before implementing any real-data adapter in `src/dashboard/api/`.
- [ ] [D017] Document run commands and actual limits in `specs/001-research-dashboard/quickstart.md`; do not claim production readiness.
