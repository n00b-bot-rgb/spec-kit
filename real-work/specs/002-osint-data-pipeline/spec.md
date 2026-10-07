# OSINT Data Pipeline Specification

Status: Draft scaffold; review before implementation.
Feature: `002-osint-data-pipeline`
Requested: 2026-10-07
Dependency: shared evidence contract v1; feeds the dashboard through a read-only
adapter, not through duplicated collection logic.

## Problem Statement

A researcher needs collected public records normalized into a case-separated
evidence store without losing the source, retrieval route, identifier, or checksum.
The user requested a pipeline feature. This scaffold must integrate with the
existing runner rather than inventing a second orchestrator; no throughput or
quality baseline has been measured.

## Goals

- Import a bounded synthetic batch without network access or credentials.
- Preserve verifiable provenance and explicit review state for every accepted
  record.
- Make repeated imports idempotent while retaining changed content as a new
  record version and separating cases.
- Report accepted, rejected, blocked, and failed outcomes rather than silently
  treating missing evidence as a successful absence finding.

## Non-Goals

- Rebuilding the current collector runner, Airflow, event bus, or database stack.
- Active exploitation, credential guessing, exfiltration, device/phone location
  tracking, or monitoring live cameras.
- Commercial people-search scraping or login-walled social collection.
- Automatic identity linking, bulk person enrichment, or copying private case
  anchors into this public project.
- Enabling real collectors, schedules, paid APIs, or external AI providers merely
  by installing the feature.

## User Stories

- **US1, trusted import:** As a researcher, I want a bounded import with complete
  provenance so I can inspect and verify the source afterward.
- **US2, reliable reruns:** As a researcher, I want unchanged evidence deduplicated
  without merging cases or discarding changed source content.
- **US3, explicit gaps:** As a researcher, I want collection failures and access
  gaps recorded so I can choose an authorized follow-up route.

## Requirements

- **PIPE-001, P0, US1:** Accept an explicit case ID and a configured local batch
  path. Given a synthetic batch, when imported offline, then no external request
  is made and records are assigned only to the explicitly permitted case.
- **PIPE-002, P0, US1:** Require source ID, source URL, route, publisher identifier,
  UTC retrieval time, jurisdiction state, raw artifact reference, and SHA-256.
  Given a missing required field or a checksum mismatch, then reject the record
  with a bounded reason and do not expose it as valid evidence.
- **PIPE-003, P0, US1:** Bound each input batch to a proposed maximum of 2,000
  records and 10 MiB serialized JSON, with bounded artifact reads. Reject an
  over-limit batch before persistence. This cap is a proposed MVP constraint,
  not permission to collect 2,000 records from any publisher.
- **PIPE-004, P0, US2:** Identify a record version by case, source, publisher
  identifier, and content checksum. Given an unchanged rerun, then no duplicate
  evidence version is added; given changed content, then retain both versions
  with their retrieval history. Record retry observations separately.
- **PIPE-005, P0, US2:** Keep storage and queries case-scoped. Given the same
  identifier and content in two authorized cases, then the records remain
  separate. Reject case-path traversal and artifact paths escaping the approved
  storage root.
- **PIPE-006, P0, US3:** Emit a run manifest with status, counts, timestamps, and
  bounded diagnostic text. Counts must reconcile. Mixed valid/invalid input
  produces partial status; invalid input never becomes a success with a hidden
  failure.
- **PIPE-007, P0:** Keep live sources disabled until a source ID, route, access
  basis, scope, and limits are reviewed. Prefer publisher bulk exports/open GIS,
  then documented APIs, official records, records requests, and lastly public
  pages. Do not bypass access restrictions.
- **PIPE-008, P0:** Before enabling any live adapter, block embedded credentials,
  unauthorized hosts, private/link-local/loopback fetch targets, unsafe redirects,
  arbitrary shell execution, and credential-bearing fallback URLs. Respect
  publisher restrictions and rate limits. An offline fixture validator is not
  the implementation of these live-network safeguards.
- **PIPE-009, P0:** Where a record depends on county/jurisdiction, resolve it
  before building publisher-specific identifiers. Unknown and not-applicable are
  distinct states; never infer a jurisdiction or rewrite an identifier silently.
- **PIPE-010, P1:** Add a reviewed adapter to the existing private runner and
  preserve its command surface. No private source code or case data is copied
  into the public Spec Kit fork.
- **PIPE-011, P2:** Add optional enrichment/ranking only after source import and
  provenance controls pass, with separate model/data-sharing approval.

## Success Metrics

These are proposed acceptance targets, not measured operational results:

- All valid synthetic records are accepted with reproducible artifact checksums.
- All deliberately invalid provenance/case/path fixtures are rejected.
- Reimporting the same batch adds zero duplicate evidence versions.
- All run counts reconcile and partial/failed outcomes remain visible.
- Zero network calls occur in the offline importer acceptance tests.
- Proposed offline baseline exercise: ingest 500 synthetic records and record
  time, memory, and environment; set an operational target after measurement.

## Open Questions

- **Q-P1, owner user, blocking before persistence:** Approve the existing runner
  integration point and either a temporary local store or direct use of its
  current storage. The scaffold uses fixtures only.
- **Q-P2, owner user, blocking before real collection:** Which named source,
  research case, route, and scope are authorized?
- **Q-P3, owner user, blocking before retaining real artifacts:** Choose storage
  location, access controls, retention, deletion, and backup rules.
- **Q-P4, owner implementer/user, non-blocking for fixtures:** Confirm publisher-
  specific identifier and jurisdiction rules for the first approved source.

## Definition of Done

An approved bounded importer and store satisfy the positive/negative tests,
repeat imports are idempotent, source changes preserve history, and the dashboard
can read case-scoped results. Live collection is a separate approved milestone.
The current scaffold is not an operational collector or a production pipeline.
