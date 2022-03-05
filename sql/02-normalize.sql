CREATE VIEW normalized AS SELECT
 CASE WHEN op='d' THEN `before`.id ELSE `after`.id END AS id,
 CASE WHEN op='d' THEN `before`.device_id ELSE `after`.device_id END AS device_id,
 CASE WHEN op='d' THEN `before`.`value` ELSE `after`.`value` END AS reading_value,
 CASE WHEN op='d' THEN `before`.unit ELSE `after`.unit END AS unit,
 source.lsn AS version, op, CASE WHEN op='d' THEN 1 ELSE 0 END AS deleted,
 CONCAT('lab:public:readings:', CAST(source.lsn AS STRING), ':', op, ':',
 CAST(CASE WHEN op='d' THEN `before`.id ELSE `after`.id END AS STRING)) AS event_id,
 kafka_partition, kafka_offset, ts_ms AS source_ts_ms, processing_time
 FROM source_events WHERE op IS NOT NULL;
