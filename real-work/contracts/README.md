# Evidence Contract v1

`research-batch.schema.json` defines the shared dashboard/pipeline boundary.
`fixtures/sample-batch.json` contains three fictional records across two cases,
plus partial, successful, and failed run examples. Its URLs are labels only:
the validator never fetches them.

## Record identity and provenance

A record version is identified by `case_id`, `source_id`, publisher `identifier`,
and SHA-256 of the raw bytes. Its display ID is `rec_` plus the first 16 hexadecimal
characters of SHA-256 over UTF-8 compact JSON of that four-element list, using
unescaped Unicode. The full four-element tuple is the persistence uniqueness
key; do not rely solely on the shortened display ID as a database constraint.

Changing retrieval time does not change a record version. A later implementation
must store repeated retrievals in a separate observation log. Changing content
creates a new version; matching content in a different case stays separate.

Run IDs in a batch must be unique. Each included record belongs to one included
run with the same case and source, and each run's accepted count matches its
included records. This is an import-output batch, not a historical snapshot.

## Run Lifecycle and Input Rules

Queued means processing has not started: `started_at` and `finished_at` are
null, all counts are zero, no accepted records belong to the run, and
`failure_reason` is null. Every other state requires a UTC `started_at`.
Running may report partial progress but has no `finished_at`; terminal states
require a finish timestamp not earlier than the start.

Succeeded has no rejected items or failure reason. Partial has both accepted and
rejected items and explains the failure. Failed and blocked accept no evidence
and require a reason. Counts and included accepted records must still reconcile.

Constrained IDs, checksums, timestamps, and URL labels are full-string values;
line terminators cannot be appended to an otherwise valid match. No identifier
is silently stripped or rewritten. The schema's end assertion prevents a
trailing newline from exploiting a permissive end-of-line anchor.

Credential screening normalizes case, hyphens, underscores, and whitespace in
query/fragment parameter names, including common token, client-secret, API-key,
and signature aliases. Explicit ports must parse and lie in 1–65535. This is
conservative screening of known credential-key names, not proof that arbitrary
URL text is secret-free and not permission to fetch any URL; publisher-specific
admission and network rules remain separate.

## Local validation

```bash
.venv/bin/python scripts/validate_evidence.py
```

The validator checks the schema, known credential parameters in source labels, identities,
run relationships/counts/statuses, timestamp ordering, relative artifact paths,
and actual SHA-256 values. It limits batch JSON to 10 MiB and fixture artifact
reads to 1 MiB each. Those are scaffold validation limits, not source collection
permissions or a guarantee against every resource attack.

Only `raw/` paths below the chosen artifact root are allowed; traversal and
escaping symlinks are rejected. The default root is `contracts/fixtures/`.
Synthetic fixtures and checks do not authorize any real collection, and this
tool is not a network policy engine, a persistence importer, or a UI.

## Contract changes

Update both feature plans when changing fields or meaning. Keep test fixtures
synthetic, preserve case boundaries, and add negative tests before admitting
new input forms.
