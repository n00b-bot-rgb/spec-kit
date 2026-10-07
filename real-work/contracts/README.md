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

## Local validation

```bash
.venv/bin/python scripts/validate_evidence.py
```

The validator checks the schema, credential-free source labels, identities,
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
