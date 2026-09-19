# Decoupled Observability Architecture via Apache Kafka

This architecture specification details how the data pipeline acts as a **Log Producer**, publishing structured telemetry and operational events to **Apache Kafka** before asynchronous ingestion into **Elasticsearch & Kibana**.

---

## 1. High-Throughput Decoupled Architecture

```mermaid
flowchart LR
    subgraph Pipeline["Data Pipeline (Producer)"]
        Extractor["Python 3.12 Extractor"]
        KafkaHandler["KafkaLoggingHandler<br/>(Fire & Forget)"]
        StdoutHandler["StdoutHandler<br/>(Console JSONL)"]
        
        Extractor --> StdoutHandler
        Extractor --> KafkaHandler
    end

    subgraph KafkaCluster["Buffer & Streaming Layer (Apache Kafka)"]
        Topic[("Topic: data-pipeline-logs<br/>Partitions: 3 / Replication: 2")]
    end

    subgraph IngestionWorker["Log Ingestion Layer (Consumer)"]
        Consumer["Logstash / Vector / Fluentbit<br/>(Kafka Consumer Group)"]
    end

    subgraph Analytics["Search & Observability"]
        Elasticsearch[("Elasticsearch Index:<br/>pipeline-logs-YYYY.MM.DD")]
        Kibana["Kibana Dashboards"]
    end

    KafkaHandler -->|Async Produce (<5ms)| Topic
    Topic -->|Pull in Batches| Consumer
    Consumer -->|Bulk Indexing (_bulk)| Elasticsearch
    Elasticsearch --> Kibana
```

---

## 2. Core Architectural Advantages

1. **Near-Zero Pipeline Overhead:**
   - Emitting HTTP requests to Elasticsearch directly incurs 50–200ms latency per request.
   - Producing to a Kafka topic via `acks=0` (or `acks=1` with background queueing) takes **< 3ms**, ensuring the data extraction workload is never bottlenecked by the logging system.

2. **Backpressure Buffer & Surge Protection:**
   - In peak batch processing (e.g., millions of records), logging spikes cannot overwhelm the Elasticsearch cluster.
   - Kafka absorbs the burst, allowing Logstash or Vector consumers to ingest at a controlled, steady pace.

3. **High Availability & Zero Log Loss:**
   - If Elasticsearch undergoes maintenance or experiences downtime, messages safely accumulate in Kafka without failing the pipeline.
   - Once Elasticsearch recovers, consumers replay and ingest uncommitted offsets.

---

## 3. Producer Configuration in Python

The pipeline uses `KafkaLoggingHandler` inside `src/logger.py`:

```python
# Enable in .env:
KAFKA_ENABLED=true
KAFKA_BOOTSTRAP_SERVERS="kafka-broker.streaming.svc.cluster.local:9092"
KAFKA_LOG_TOPIC="data-pipeline-logs"
```

### Event Payload Emitted to Kafka:
```json
{
  "timestamp": "2026-09-19T01:05:23.142Z",
  "level": "INFO",
  "service": "batch-data-extractor",
  "dataset": "DEVICE_TELEMETRY",
  "stage": "EXTRACT_DB",
  "batch_id": "00bf24e1-00f5-495a-95e7-32318fb992c7",
  "export_date": "2026-09-18",
  "row_count": 54200,
  "duration_ms": 320,
  "message": "Successfully extracted 54200 rows from PostgreSQL"
}
```

---

## 4. Consumer Configuration Sample (Logstash Pipeline)

To consume events from the Kafka topic into Elasticsearch:

```ruby
input {
  kafka {
    bootstrap_servers => "kafka:9092"
    topics => ["data-pipeline-logs"]
    codec => "json"
    group_id => "logstash-kibana-indexer"
    auto_offset_reset => "earliest"
  }
}

output {
  elasticsearch {
    hosts => ["http://elasticsearch:9200"]
    index => "pipeline-logs-%{+YYYY.MM.dd}"
  }
}
```
