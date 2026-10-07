# OSINT Data Pipeline Implementation Plan

Status: Draft proposal; storage and private-runner integration need review.
Scope: offline import first; no live collection during scaffolding.

## Technical Context

The first implemented scaffold component is an offline evidence-contract
validator, not a fetcher or database. Python is used only for these local tools.
The feature's service/storage choices remain open until Q-P1 is resolved.

Use an adapter around the existing private OSINT runner if approved. Keep its
collector configuration and Makefile as the regular command surface; do not
start a competing scheduler or vendor its private implementation into this fork.

## Architecture

```text
approved local batch + artifacts
             |
     size and case limits
             |
  schema + provenance/hash validation
             |
  normalization and version identity
             |
 case-scoped evidence store + observation log
             |
       run manifest
             |
 dashboard read adapter / report consumer
```

Live sources later enter through an explicit source-policy boundary before
collection. Source approval, URL/redirect handling, rate limits, and secrets are
separate from evidence validation.

## Shared Data Model

- **Evidence version:** Deterministic record ID derived from
  `[case_id, source_id, identifier, content_sha256]`, not title or retrieval time.
- **Observation:** A run's retrieval event for a record version. Reimports can
  record an observation without adding another evidence version.
- **Run:** Source/case pair, lifecycle status, timestamps, reconciled counts, and
  bounded diagnostics.
- **Artifact:** Relative reference below the configured storage root; validate
  traversal, symlink escape, and SHA-256 before acceptance.
- **Jurisdiction:** County value plus `known`, `unknown`, or `not_applicable`
  state. Resolve jurisdiction where publisher rules require it.

The fixture batch represents records accepted in the included runs. It is not a
historical database snapshot or a request to collect those source URLs.

## Decisions

- **Offline by default:** Synthetic local input only in the first milestone.
- **No source autoenable:** Any new real source starts disabled.
- **Transactional import:** Write an evidence version and its observation
  consistently; reject invalid records without losing run accounting.
- **Idempotent persistence:** Store uniqueness on case/source/identifier/hash;
  retain changed content separately.
- **Private storage:** Real artifacts belong outside Git-tracked directories.
  Approve retention and permissions before importing actual case records.
- **Bounded errors:** Store useful reasons without credentials, response bodies,
  unrelated personal data, or uncontrolled exception dumps.

## File Boundaries

```text
src/pipeline/
  importer/         Bounded offline import and manifest accounting
  storage/          Case-scoped evidence versions and observation persistence
  policy/           Disabled-by-default live source admission, later milestone
  adapters/         Approved private-runner bridge, later milestone
tests/pipeline/
  test_importer.*   Limits, hashes, identity, retries, and partial outcomes
  test_storage.*    Transaction failures, uniqueness, version/case separation
```

Concrete database drivers and service manifests wait for Q-P1. Shared schema and
fixture checks are implemented under `scripts/` and `tests/test_feature_scaffolds.py`.

## Delivery Sequence

Review the contract and Q-P1, add bounded importer/storage interfaces, write
failure tests, then implement offline persistence and repeated import behavior.
Expose read-only case-scoped results to the dashboard. Resolve Q-P2/Q-P3 before
adding a real source or retaining actual evidence.

## Tests and Gates

Positive tests cover valid imports, reproducible checksums, changed content,
same-source records in separate cases, and manifest accounting.

Negative tests cover missing provenance, mismatched hashes, malformed input,
unknown case IDs, traversal/symlink escape, oversized inputs, rollback failure,
duplicate identities, and injected diagnostic text. Network tests must use
mocked/local fixtures and verify that no live request occurs in offline mode.

Do not mark URL/DNS/redirect safeguards complete because a JSON Schema passes.
Implement and review those controls before any live adapter can be enabled.
