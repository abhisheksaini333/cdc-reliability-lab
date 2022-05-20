CREATE TABLE curated (
 event_id STRING, id BIGINT, device_id BIGINT, reading_value DOUBLE,
 unit STRING, site STRING, version BIGINT, op STRING, deleted INT,
 kafka_partition INT, kafka_offset BIGINT, source_ts_ms BIGINT, quality STRING
) WITH (
 'connector'='kafka', 'topic'='lab.curated', 'properties.bootstrap.servers'='kafka:9092',
 'format'='json', 'sink.delivery-guarantee'='at-least-once'
);
