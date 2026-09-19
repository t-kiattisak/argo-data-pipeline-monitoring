# Documentation Index

Welcome to the **Argo Data Pipeline & Observability** project documentation (`argo-data-pipeline-monitoring`).

---

## Documentation Table of Contents

1. [ADR-001: Batch Data Extraction & Observability Architecture](ADR-001-pipeline-observability.md)
   - Architecture Decision Record for batch pipeline design with integrated monitoring and alerting.
   - Comparative analysis: Argo `onExit` vs. Application-level try/catch.

2. [ARCHITECTURE.md: System Architecture & Technical Specifications](ARCHITECTURE.md)
   - Detailed system architecture (High-Level Architecture flowchart and Sequence Diagrams).
   - Generic dataset specifications (`DEVICE_TELEMETRY` and `ORDER_EVENTS`).
   - Security standards (SSE-KMS, Presigned URL TTL, API Gateway JWT).

3. [OBSERVABILITY_GUIDE.md: Observability & Monitoring Specification](OBSERVABILITY_GUIDE.md)
   - Structured JSON Logging standard for Elasticsearch / Kibana.
   - Argo Workflow `onExit` email alerting specifications and incident runbook.
   - Standard KQL queries for building monitoring dashboards.

4. [SKILLS_AND_COMPETENCIES.md: Engineering Skills Reference](SKILLS_AND_COMPETENCIES.md)
   - Key technical competencies: PostgreSQL JSONB flattening, Boto3 S3/KMS, Argo Workflows, Centralized Logging.
   - Production readiness deployment checklist.

5. [KAFKA_OBSERVABILITY_ARCHITECTURE.md: Decoupled Observability via Apache Kafka](KAFKA_OBSERVABILITY_ARCHITECTURE.md)
   - High-throughput decoupled logging architecture using Apache Kafka as a message broker buffer.
   - Producer implementation details, backpressure handling, and Logstash consumer pipelines.
