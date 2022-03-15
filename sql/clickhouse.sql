CREATE DATABASE IF NOT EXISTS lab;
CREATE TABLE IF NOT EXISTS lab.raw_events (
 event_id String, id Int64, device_id Int64, reading_value Float64, unit String, site String,
 version Int64, op String, deleted Int32, kafka_partition Int32, kafka_offset Int64, source_ts_ms Int64,
 received_at DateTime64(3) DEFAULT now64(3)
) ENGINE=MergeTree ORDER BY (id,version,event_id);
CREATE TABLE IF NOT EXISTS lab.curated_queue (
 event_id String, id Int64, device_id Int64, reading_value Float64, unit String, site String,
 version Int64, op String, deleted Int32, kafka_partition Int32, kafka_offset Int64, source_ts_ms Int64
) ENGINE=Kafka SETTINGS kafka_broker_list='kafka:9092', kafka_topic_list='lab.curated',
 kafka_group_name='clickhouse-curated-v1', kafka_format='JSONEachRow', kafka_num_consumers=1,
 kafka_max_block_size=100, kafka_flush_interval_ms=500;
CREATE MATERIALIZED VIEW IF NOT EXISTS lab.ingest_curated TO lab.raw_events AS SELECT *,now64(3) AS received_at FROM lab.curated_queue;
