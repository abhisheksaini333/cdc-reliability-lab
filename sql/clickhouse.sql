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
CREATE VIEW IF NOT EXISTS lab.current_readings AS
 SELECT id, tupleElement(latest,1) AS device_id,tupleElement(latest,2) AS reading_value,
 tupleElement(latest,3) AS unit,tupleElement(latest,4) AS site,tupleElement(latest,6) AS version
 FROM (SELECT id,argMax(tuple(device_id,reading_value,unit,site,deleted,version),tuple(version,deleted,event_id)) AS latest
 FROM lab.raw_events GROUP BY id) WHERE tupleElement(latest,5)=0;
CREATE VIEW IF NOT EXISTS lab.unique_events AS SELECT event_id,argMax(id,version) AS id,
 max(version) AS version,count() AS deliveries FROM lab.raw_events GROUP BY event_id;
CREATE TABLE IF NOT EXISTS lab.quarantine_events (
 event_id String, id Int64, device_id Int64, reading_value Float64, unit String, site String,
 version Int64, op String, deleted Int32, kafka_partition Int32, kafka_offset Int64, source_ts_ms Int64,
 quality String, received_at DateTime64(3) DEFAULT now64(3)
) ENGINE=MergeTree ORDER BY (quality,id,version);
CREATE TABLE IF NOT EXISTS lab.quarantine_queue (
 event_id String, id Int64, device_id Int64, reading_value Float64, unit String, site String,
 version Int64, op String, deleted Int32, kafka_partition Int32, kafka_offset Int64, source_ts_ms Int64, quality String
) ENGINE=Kafka SETTINGS kafka_broker_list='kafka:9092', kafka_topic_list='lab.quarantine',
 kafka_group_name='clickhouse-quarantine-v1', kafka_format='JSONEachRow', kafka_num_consumers=1,
 kafka_max_block_size=100, kafka_flush_interval_ms=500;
CREATE MATERIALIZED VIEW IF NOT EXISTS lab.ingest_quarantine TO lab.quarantine_events AS SELECT *,now64(3) AS received_at FROM lab.quarantine_queue;
