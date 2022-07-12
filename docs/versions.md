# Runtime and upstream attribution

The application and fixtures are original. Dependencies retain their upstream licenses; jar/container binaries are downloaded and are not committed.

| Component | Pin | Upstream |
|---|---|---|
| PostgreSQL | 13.5 | https://www.postgresql.org/docs/13/logical-replication.html |
| Debezium | 1.8.0.Final | https://debezium.io/releases/1.8/ |
| Kafka inside Debezium image | 3.0.0 | https://kafka.apache.org/30/documentation/ |
| Flink | 1.14.2, Scala 2.12, Java 11 | https://nightlies.apache.org/flink/flink-docs-release-1.14/ |
| ClickHouse | 21.8.12.29 | https://github.com/ClickHouse/ClickHouse/releases/tag/v21.8.12.29-lts |
| PostgreSQL JDBC | 42.3.1 | https://jdbc.postgresql.org/ |
| kafka-python | 2.0.2 | https://github.com/dpkp/kafka-python/tree/2.0.2 |

The Flink Kafka and JDBC jars match the runtime's 1.14.2/Scala 2.12 ABI. `infra/flink/artifacts.json` records exact URLs and SHA256; the fetcher refuses different bytes. Images are architecture-specific where required; Docker Desktop on Apple Silicon uses amd64 emulation for the older Java/ClickHouse components. The actual Kafka broker reports 3.0.0 through Connect's management API.

The SQL client uses `BEGIN STATEMENT SET; ... END;`, the supported 1.14 syntax. ClickHouse ingestion uses Kafka engines and materialized views, with query-time `argMax` projection. No Kafka Connect ClickHouse sink is required.

Dependency upgrades need a fresh snapshot/mutation/replay/checkpoint/savepoint acceptance run. This release keeps the assembled baseline fixed so that recovery results apply to one tested combination.
