EXECUTE STATEMENT SET
BEGIN
 INSERT INTO curated SELECT event_id,id,device_id,reading_value,unit,site,version,op,deleted,
 kafka_partition,kafka_offset,source_ts_ms FROM classified WHERE quality='';
 INSERT INTO quarantine SELECT event_id,id,device_id,reading_value,unit,COALESCE(site,''),version,op,deleted,
 kafka_partition,kafka_offset,source_ts_ms,quality FROM classified WHERE quality<>'';
END;
