SET 'execution.checkpointing.interval' = '5s';
SET 'execution.checkpointing.mode' = 'EXACTLY_ONCE';
SET 'parallelism.default' = '1';
SET 'pipeline.name' = 'cdc-reliability-lab';
CREATE TABLE source_events (
 `before` ROW<id BIGINT, device_id BIGINT, `value` DOUBLE, unit STRING>,
 `after` ROW<id BIGINT, device_id BIGINT, `value` DOUBLE, unit STRING>,
 op STRING,
 source ROW<lsn BIGINT, ts_ms BIGINT>,
 ts_ms BIGINT,
 kafka_partition INT METADATA FROM 'partition' VIRTUAL,
 kafka_offset BIGINT METADATA FROM 'offset' VIRTUAL,
 processing_time AS PROCTIME()
) WITH (
 'connector'='kafka', 'topic'='lab.public.readings',
 'properties.bootstrap.servers'='kafka:9092', 'properties.group.id'='flink-live-v1',
 'scan.startup.mode'='earliest-offset', 'format'='json', 'json.fail-on-missing-field'='false',
 'json.ignore-parse-errors'='false'
);
