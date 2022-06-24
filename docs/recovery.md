# Recovery runbook

1. Capture `docker compose ps`, `python -m cdc_lab.cli metrics`, and `/jobs/overview` from `http://127.0.0.1:4704` before changing processes.
2. For a failed task manager, inspect the Flink exception and completed checkpoint count. Restart only `taskmanager`; wait for RUNNING and a new completed checkpoint, then reconcile.
3. For a connector outage, preserve `connect-offsets` and PostgreSQL `lab_slot`. Restart Connect and check both connector and task state. Source mutations made during the outage must converge after restart.
4. For a ClickHouse outage, retain its named volume and Kafka groups. Restart ClickHouse and reconcile, accounting for duplicate raw deliveries.
5. Before a planned pipeline change, create a savepoint. Stop the old job and submit using the returned `file:///state/savepoints/...` path. Require Flink's `latest.restored` checkpoint evidence and source equivalence.
6. A coordinator restart is not high availability: this standalone lab has no replicated job graph store. Resubmit from a reviewed savepoint. Never claim task-manager checkpoint recovery proves coordinator failover.

Use `docker compose stop` to pause the lab. `docker compose down` removes only this project's containers/network and retains volumes. Removing volumes destroys the source and offset history and is only appropriate for an explicitly disposable fresh run. Never delete offsets as a substitute for diagnosing a failed record.

Published ports bind loopback. Keep `.env`, `.runtime`, source exports and volume snapshots private. The database fixtures are synthetic. Retain failed integration output before retrying; record the fix and verify the original failed scenario.
