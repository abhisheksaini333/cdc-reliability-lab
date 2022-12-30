# Verification evidence

The application was exercised against the pinned PostgreSQL, Debezium/Kafka, Flink and ClickHouse containers. The machine-readable [validation summary](validation-summary.json) records the scope and measured results.

| Check | Result |
|---|---|
| Deterministic Python contracts/operator tests | 63 passed |
| Initial snapshot and insert/update/delete transitions | Source and served keys/values equal |
| Invalid latest reading and subsequent repair | Stale served row removed, repaired row restored |
| Repeated bounded Kafka replay | Physical deliveries increased; current-state digest unchanged |
| Task-manager restart | Checkpoints resumed and source state converged |
| Connect and ClickHouse outages | Mutations made during each outage converged after restart |
| Savepoint stop/restore through CLI | Restored state confirmed by Flink; 313 source/served rows equal |
| Additive schema change | New nullable field tolerated and changed value served |
| Incompatible PostgreSQL type | Rejected by live schema contract gate, then transaction rolled back |
| NaN and positive/negative infinity | Quarantined through the actual Flink path; valid repair served |
| Kafka binary headers and null record values | Actual export/publication roundtrip preserved bytes |
| Bootstrap and installed CLI | New state-volume ownership and external-directory console use verified |

Three measured batches of 100 mutations converged in **1.733, 2.403 and 2.053 seconds**, approximately **57.71, 41.61 and 48.70 records/second**, including source writes and polling. The nearest-rank batch p50 was **2.053 seconds** and p95 **2.403 seconds**. These are three synthetic local samples under amd64 container emulation, not production capacity estimates. Acknowledgment requires new logical CDC events plus full source/serving equivalence, including repeated runs with unchanged values.

Recovery cases were run on the actual services. The final numeric-classifier change was rechecked with NaN/infinity traffic, completed checkpoints, a fresh benchmark, and another savepoint stop/restore on the final SQL graph. Failed startup, checkpoint-permission, SQL-client and parser runs were retained during development; the run harness writes private nonoverwriting failure evidence under ignored `artifacts/`.

Local fixes included bounded Kafka admin JVMs, adequate coordinator heap, Flink 1.14 statement-set syntax, ClickHouse aggregate alias handling, state-volume ownership, canonical savepoint URIs, compact transactional schema JSON, bounded SQL planner resources, and nonfinite quality handling. These failures are why unit tests alone are not treated as proof of a running CDC pipeline.

To repeat the checks, follow the README and run `python scripts/integration.py`; the configured manual integration workflow runs the same stack. The report does not claim hosted CI execution, production HA, multi-partition ordering, or null-header publication through the pinned Kafka client.

The integration job streams scenario and benchmark JSON into its log, including completed scenarios from a failed run. Download the job log with `gh run view RUN_ID --log > acceptance.log` to preserve hosted evidence. Full local reports remain under ignored `artifacts/`; the workflow does not depend on an artifact upload service.

Startup prepares the private runtime bind directory before Docker starts, so a fresh nonroot Linux checkout retains permission to write its generated SQL. The startup-order, ownership and symlink checks are covered by deterministic tests; the existing full-stack measurements above precede this filesystem-only startup fix.
