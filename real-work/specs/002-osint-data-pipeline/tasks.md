# OSINT Data Pipeline Tasks

Status: Draft; live collection requires separate approval.
Dependencies: Q-P1 gates storage; Q-P2/Q-P3 gate actual research data.

## Setup

- [x] [P001] Scaffold the specification and plan in `specs/002-osint-data-pipeline/`.
- [x] [P002] Add the v1 batch contract, synthetic artifacts, and offline validator under `contracts/` and `scripts/validate_evidence.py`.
- [x] [P003] Add positive and negative scaffold tests in `tests/test_feature_scaffolds.py`.
- [ ] [P004] Resolve Q-P1 and record the approved store/runner integration in `specs/002-osint-data-pipeline/plan.md`.

## Foundation

- [ ] [P005] Write bounded input, oversized artifact, and explicit-case tests in `tests/pipeline/test_importer.py`; cover PIPE-001, PIPE-003, and PIPE-005.
- [ ] [P006] Implement the offline importer interface in `src/pipeline/importer/`; no network collector or shell invocation.
- [ ] [P007] Define evidence-version, observation, and manifest persistence interfaces in `src/pipeline/storage/`; cover PIPE-002 and PIPE-004.

## Reliable Persistence

- [ ] [P008] Write unchanged-rerun, changed-content, case-separation, and rollback tests in `tests/pipeline/test_storage.py`.
- [ ] [P009] Implement transactional persistence and unique version identities in `src/pipeline/storage/`; cover PIPE-004 and PIPE-005.
- [ ] [P010] Implement accepted/rejected accounting and partial/failed run outcomes in `src/pipeline/importer/`; cover PIPE-006.
- [ ] [P011] Validate raw-file reads against the approved root and bounded size in `src/pipeline/importer/`; cover PIPE-002 and PIPE-005.

## Dashboard Integration

- [ ] [P012] Provide a case-scoped read adapter from `src/pipeline/storage/` to the shared contract; cover dashboard DASH-001 and PIPE-005.
- [ ] [P013] Test fixture import through dashboard list/detail/run queries in `tests/pipeline/`.

## Live-Source Gate

- [ ] [P014] Resolve Q-P2/Q-P3 and write the named-source scope and retention decision in `specs/002-osint-data-pipeline/source-approval.md`.
- [ ] [P015] Implement disabled-by-default source policy, identifier/jurisdiction rules, and secret-safe diagnostics in `src/pipeline/policy/`; cover PIPE-007 and PIPE-009.
- [ ] [P016] Test unauthorized hosts, embedded credentials, private addresses, redirects, and prohibited fallbacks in `tests/pipeline/`; cover PIPE-008.
- [ ] [P017] Add one approved private-runner adapter in `src/pipeline/adapters/` without copying private source or case records; cover PIPE-010.

## Review

- [ ] [P018] Record the 500-record offline baseline and actual command instructions in `specs/002-osint-data-pipeline/validation.md`.
- [ ] [P019] Review all outstanding gates and document limitations in `specs/002-osint-data-pipeline/quickstart.md`; do not enable live collection merely to complete a task.
