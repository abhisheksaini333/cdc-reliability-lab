# Schema evolution

`python -m cdc_lab.cli schema` validates the live PostgreSQL contract. Adding nullable columns is compatible: Debezium emits the new field and the explicit Flink row type ignores unknown fields. Run `migrations/001-add-note.sql` then mutate a reading and reconcile.

Changing `value` from double precision to text is incompatible. The schema gate rejects this before deployment; strict JSON decoding also fails the Flink task if unplanned incompatible data arrives. Do not enable ignore-parse-errors to conceal it. Restore the source contract, or deploy a reviewed new pipeline and topic contract. Preserve the failed offset and inspect the source event before any offset decision.

PostgreSQL DDL checks can be performed inside a transaction and rolled back. The integration scenario verifies the incompatible type using PostgreSQL itself and checks the schema gate, then rolls back before resuming writes.
