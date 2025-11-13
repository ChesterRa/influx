<!-- Generated on 2025-11-13T02:31:23+00:00 by por_subpor.py 0.1.1 -->

# T000001 - D1 — Schema validation + CI (M0) - Owner: peerB - Stage: proposed - Timebox: 0.5d

- Goal/Scope (<=3 lines):
  - Implement schema validation tool (tools/influx-validate) that validates JSONL records against schema/bigv.schema.json using jsonschema library
  - Fix schema to make `meta` required with critical sub-fields (`meta.score`, `meta.sources[>=1]`, `meta.last_refresh_at`, `provenance_hash`)
  - Create CI workflow (ci/validate.yml) that runs validator on data/latest/latest.jsonl.gz and fails PR if invalid
- Non-Goals (<=2 lines):
  - Collection tools (D2) - defer to next SUBPOR
  - Extensive schema documentation polish (already over-engineered per strategic review; focus on working validator)
- Deliverable & Interface (path/format/user-visible change):
  - tools/influx-validate: CLI tool (argparse) that validates JSONL against schema; exits 0 if valid, 1 if invalid with error details
  - schema/bigv.schema.json: Fixed schema with required `meta.score`, `meta.sources`, `meta.last_refresh_at`, `provenance_hash`
  - ci/validate.yml: GitHub Actions workflow that runs influx-validate on PRs
- Acceptance (3-5 observable items):
  [x] schema/bigv.schema.json validates correctly with jsonschema; `meta` and critical sub-fields are required
  [x] tools/influx-validate exists, runs jsonschema validation on JSONL input, checks manifest.json schema_version match
  [x] tools/influx-validate exits 0 on valid fixture (3 hardcoded JSON objects in test/fixtures/valid.jsonl), exits 1 on invalid fixture (test/fixtures/invalid.jsonl) with clear error message
  [x] ci/validate.yml workflow exists and runs influx-validate; simulate PR validation with manual smoke test
  [x] State DB schema fixed: `authors.last_active_at` allows NULL, `following.target_author_id` FK dropped (per Aux review MINOR findings)
- Probe (cheapest decisive): echo '{"id":"123","handle":"test","name":"Test","verified":"none","followers_count":50000,"lang_primary":"en","topic_tags":["ai"],"meta":{"score":75,"last_refresh_at":"2025-11-13T00:00:00Z","sources":[{"method":"manual","fetched_at":"2025-11-13T00:00:00Z","evidence":"test"}],"provenance_hash":"e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"}}' | python tools/influx-validate -s schema/bigv.schema.json && echo "PASS" || echo "FAIL"
- Kill Criteria (when to stop/pivot): If jsonschema library incompatible with schema draft-07 or validation logic requires >4 hours (timeout), pivot to simpler manual validation script
- Implementation Approach (<=3 bullets):
  - Fix schema FIRST: make `meta` required, add required sub-fields (`meta.score`, `meta.sources[>=1]`, `meta.last_refresh_at`, `provenance_hash`); validate with jsonschema library against test fixture
  - Implement influx-validate stub: argparse CLI, jsonschema validation, manifest check (schema_version, sha256), exit codes
  - Create CI workflow stub: GitHub Actions YAML, runs influx-validate on data/latest/latest.jsonl.gz, fails on non-zero exit
- Evidence (minimal refs):
  - tools/influx-validate: 252 lines Python CLI with jsonschema validation, manifest check, gzip support
  - cmd:python3 tools/influx-validate -s schema/bigv.schema.json test/fixtures/valid.jsonl :: ✓ PASS (3/3 records valid)
  - cmd:python3 tools/influx-validate -s schema/bigv.schema.json test/fixtures/invalid.jsonl :: ✓ FAIL (5 errors: missing meta, invalid handle pattern, invalid verified enum, missing sources, invalid provenance_hash)
  - probe test: echo '{"id":"123",...}' | python3 tools/influx-validate -s schema/bigv.schema.json :: ✓ Validation PASSED: 1/1 records valid
  - .github/workflows/validate.yml: GitHub Actions workflow with test fixtures validation + optional latest.jsonl.gz validation
  - schema/state_db.sql: authors.last_active_at now allows NULL (line 40), following.target_author_id FK dropped (line 123-124)
- Risks/Dependencies (1 line each):
  - Risk: jsonschema library version compatibility with draft-07 schema; mitigation: test early with probe fixture
  - Dependency: schema/bigv.schema.json must be fixed before validator can be tested; critical path blocker if schema changes required
- Next (single, decidable, <=30 minutes): Fix schema/bigv.schema.json to require `meta` and critical sub-fields per Aux review findings

## REV (append-only)
- 2025-11-13 02:40 | peerB | T000001 COMPLETED - validator (252 lines), test fixtures (3 valid + 5 invalid), CI workflow, State DB fixes per Aux review | tools/influx-validate, test/fixtures/{valid,invalid}.jsonl, .github/workflows/validate.yml, schema/state_db.sql:40,123-124

## Aux (tactical, when used)
- Offloaded micro-task(s): <one-liners> | why | how to verify

- Maintenance note: update this sheet before major steps; keep REV concise.

<!-- Generated on {{generated_on}} by {{tool}} {{tool_version}} ; template_sha1=9ead40e3dc96f80aa7cddce3ac0062ac8329f48d -->
