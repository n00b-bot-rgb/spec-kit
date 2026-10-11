# Research Dashboard Specification

Status: Draft scaffold; review before implementation.
Feature: `001-research-dashboard`
Requested: 2026-10-07
Dependency: shared evidence contract v1; live pipeline integration is not required
for the first fixture-driven milestone.

## Problem Statement

An independent researcher needs one place to inspect collected documents,
understand their provenance, and see incomplete or failed collection runs.
The user requested a research dashboard; time spent on today's workflow and its
error rate have not been measured, so this spec does not claim a baseline benefit.

## Goals

- Complete case selection, filtering, and evidence inspection without leaving
  the dashboard in a synthetic acceptance session.
- Show provenance for every displayed record, with missing values explicit.
- Prevent cross-case disclosure in every data query and evidence view.
- Distinguish partial, failed, and blocked collection from a successful empty
  result. Never infer "no record exists" from an empty collection.

## Non-Goals

- Live collection, scheduler controls, arbitrary URL fetching, or scraping.
- People-search dossiers, device tracking, live camera monitoring, or exploit
  tools.
- Automatic identity resolution, AI-generated findings, or credibility claims.
- Public hosting of real research data, multiuser collaboration, or a production
  security claim.
- Maps, relationship graphs, bulk exports, and complex ranking in the first MVP.

## User Stories

- **US1, evidence browsing:** As a researcher, I want to select a case and filter
  its records so that unrelated matters do not enter my review.
- **US2, provenance inspection:** As a researcher, I want the original source,
  retrieval date, identifier, route, and checksum so I can verify a finding.
- **US3, collection gaps:** As a researcher, I want run outcomes and failure
  reasons so I know what remains unresolved.

## Requirements

- **DASH-001, P0, US1:** Display an explicit selected case; scope record, detail,
  and run data to that case. Case identifiers are exact values, not fuzzy matches.
  Given two fixture cases, when case Alpha is selected, then no Beta record or
  run is returned or rendered, including a guessed detail ID.
- **DASH-002, P0, US1:** List title, source, UTC retrieval time, and review status.
  Given valid fixture records, when the list loads, then every row displays these
  fields without treating "unreviewed" as verified.
- **DASH-003, P0, US1:** Filter by source and route; search title, summary, and
  publisher identifier within the selected case. Given no matches, when filters
  are applied, then show "No matches in this view," retain the filters, and offer
  reset. Do not silently clear filters or change cases.
- **DASH-004, P0, US2:** Detail view shows source URL, route, publisher identifier,
  county or "not applicable/unknown," retrieved-at timestamp, checksum, and
  review status. Given a missing county, then do not imply that a jurisdiction
  was resolved.
- **DASH-005, P0, US3:** Display run status, attempted/accepted/rejected counts,
  start/end timestamps, and bounded diagnostic text. Given a partial run or a
  failed run with zero accepted records, then show that status rather than a
  success or a conclusive absence finding. Given a queued run with null start
  time and zero counts, then show "Not started," not a fabricated start time.
- **DASH-006, P0:** Handle loading, empty-case, filtered-empty, schema error, and
  service-unavailable states separately. Reject invalid contract payloads instead
  of rendering them as valid evidence.
- **DASH-007, P0:** Render collected text as text, not executable HTML. Source
  links must reject script URLs and embedded credentials; raw-file access must
  never expose arbitrary filesystem paths.
- **DASH-008, P0:** The first milestone works entirely with committed synthetic
  fixtures and requires no secrets or network collector.
- **DASH-009, P1:** Persist local filter preferences per case and show a
  chronological retrieval timeline without conflating it with event occurrence.
- **DASH-010, P2:** Add map views only for reviewed, explicitly geographic records,
  after a separate scope and privacy review.

## Success Metrics

These are proposed acceptance targets, not measured production results:

- All three core user stories pass on the fixture dataset.
- Zero cross-case records returned in negative tests, including detail lookups.
- All displayed fixture records have usable provenance in their detail view.
- All failed/partial fixture runs are correctly labeled.
- Proposed performance budget: filter 500 synthetic records in under 1 second on
  the documented development machine. Measure and record the environment before
  judging the target; no current latency baseline exists.

## Open Questions

- **Q-D1, owner user, blocking before UI implementation:** Approve a proposed
  local-only web UI and framework, including whether to use a Python API
  framework such as FastAPI, or select a desktop/terminal alternative.
- **Q-D2, owner user, blocking before non-synthetic data:** Will this run only on
  localhost or require a private authenticated deployment? Vercel's Python
  runtime is a candidate only; the hosting destination and authentication
  boundary remain unapproved.
- **Q-D3, owner user, non-blocking for fixtures:** Which first real research case
  and source are authorized? No actual case data is included.

## Definition of Done

The accepted specification and plan are implemented, case-boundary and malicious
text tests pass, all UI states are covered, and setup instructions are reproducible.
The current scaffold does not satisfy this definition: application work remains.
