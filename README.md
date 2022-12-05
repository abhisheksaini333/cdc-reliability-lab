# CDC Reliability Lab

A reproducible PostgreSQL → Debezium → Kafka → Flink SQL → ClickHouse pipeline that measures source-to-serving correctness during mutations, duplicates, schema changes and process failures.

## What it demonstrates

- Snapshot-to-stream transition with inserts, updates, full-image deletes and Kafka tombstones.
- Device enrichment, temperature/unit validation, quarantine, and removal of stale values after invalid mutations.
- Immutable physical delivery history with deterministic logical current-state queries.
- Bounded Kafka export/replay, source reconciliation, checkpoint/savepoint recovery, and measured batch convergence.

## Run locally

Use Python 3.9–3.11, Docker Compose v2, and approximately 5 GB available to this stack. Older images require amd64 emulation on Apple Silicon; first startup and SQL compilation take longer there. Ports 4701–4705 bind loopback.

```sh
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python -m cdc_lab.cli init-env
python scripts/fetch_jars.py
python -m cdc_lab.cli start
python -m cdc_lab.cli reconcile
python -m cdc_lab.cli generate --count 100 --start 1000
python -m cdc_lab.cli metrics
```

Wait for serving convergence before interpreting a reconciliation mismatch as a defect. `reconcile` reports missing/extra/changed keys and exits nonzero while they differ. Credentials are generated into private `.env`; rendered SQL remains under ignored `.runtime`.

## Verify and operate

```sh
python -m unittest discover -s tests -v
python scripts/integration.py
python -m cdc_lab.cli benchmark --count 100 --rounds 3
python -m cdc_lab.cli savepoint
docker compose stop
```

Integration tests change only synthetic lab fixtures, restart dedicated components, and preserve named volumes. Run them in a disposable lab instance. They exercise real PostgreSQL, Kafka, Debezium, Flink and ClickHouse; unit tests provide fast independent contract checks.

See [measured verification](docs/verification.md).

Read [architecture and guarantees](docs/architecture.md), [recovery](docs/recovery.md), [bounded replay](docs/replay.md), [schema evolution](docs/schema-evolution.md), and [runtime versions](docs/versions.md). This is a single-node reliability lab: data equivalence and duplicate handling are measured, while HA, multi-partition ordering and production capacity are outside its proof.

An installed `cdc-lab` console command can be used from the checkout or with `CDC_LAB_ROOT=/absolute/path/to/cdc-reliability-lab`. Runtime SQL/configuration belongs to that checkout; the Python wheel contains the operator package.
