# Bounded replay

Use Python 3.9–3.11 with `pip install -r requirements.txt`. The Kafka client is pinned to 2.0.2.

```sh
python -m cdc_lab.cli export lab.curated artifacts/curated.json
python -m cdc_lab.cli replay artifacts/curated.json lab.curated
python -m cdc_lab.cli reconcile
```

Export captures partition high watermarks before reading and never commits consumer offsets. Each run has a unique `cdc-replay-*` group. It records topic, partition, offset, binary key/value, null tombstones and headers; output is capped at 10,000 records and 16 MiB, checksummed, private and nonoverwriting.

Replaying into `lab.curated` intentionally adds physical deliveries and tests idempotent current state. Export once, replay twice, wait for the observed raw count, compare canonical state hashes and reconcile. For isolated experiments, create an explicit `lab.replay.<name>` topic with the same partition count. Management/offset topics cannot be replay targets. Export source events into a separate archive if testing the Flink transform; preserve the device dimension for deterministic enrichment.

Do not infer absence of duplicates from equal row counts. The reconciliation command compares every canonical key and value, identifies missing/extra/changed rows, and exits nonzero on disagreement.

Kafka permits null header values, but kafka-python 2.0.2 cannot publish them. Export preserves those values; replay rejects the entire archive before sending any record rather than converting null to empty bytes. Binary non-null headers and null record values (tombstones) round-trip through this client.
