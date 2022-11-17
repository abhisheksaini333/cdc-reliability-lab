CREATE VIEW classified AS SELECT *,
 CASE
 WHEN op NOT IN ('r','c','u','d') THEN 'unsupported_operation'
 WHEN id IS NULL OR id <= 0 THEN 'invalid_id'
 WHEN device_id IS NULL OR device_id <= 0 THEN 'invalid_device_id'
 WHEN version IS NULL OR version < 0 THEN 'invalid_version'
 WHEN reading_value IS NULL OR CAST(reading_value AS STRING) IN ('NaN','Infinity','-Infinity') OR reading_value < -80 OR reading_value > 150 THEN 'invalid_value'
 WHEN unit IS NULL OR unit <> 'C' THEN 'unsupported_unit'
 WHEN site IS NULL THEN 'unknown_device'
 ELSE '' END AS quality
 FROM enriched;
