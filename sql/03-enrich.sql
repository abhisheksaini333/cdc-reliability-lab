CREATE TABLE devices_lookup (
 id BIGINT, site STRING, PRIMARY KEY (id) NOT ENFORCED
) WITH (
 'connector'='jdbc', 'url'='jdbc:postgresql://postgres:5432/lab',
 'table-name'='devices', 'username'='lab', 'password'='${POSTGRES_PASSWORD}',
 'lookup.max-retries'='3'
);
CREATE VIEW enriched AS SELECT n.*, d.site FROM normalized AS n
 LEFT JOIN devices_lookup FOR SYSTEM_TIME AS OF n.processing_time AS d ON n.device_id=d.id;
