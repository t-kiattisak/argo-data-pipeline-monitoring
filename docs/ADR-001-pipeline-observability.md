# ADR-001: Batch Data Extraction & Observability Architecture (PostgreSQL to S3)

## Status
Accepted

## Date
2026-09-18

## Context & Problem Statement
The platform requires an automated daily batch pipeline to extract high-volume JSONB telemetry and transactional event logs from a transactional database (PostgreSQL / Aurora), flatten the documents into standardized CSV formats, upload them to secure object storage (AWS S3) using server-side encryption (SSE-KMS), and notify downstream systems via an API Gateway using signed JWT webhooks every day at 01:00 (Asia/Bangkok).

**Problem:**
Without dedicated monitoring and observability, batch failures (e.g., query timeouts, network partitions, expired tokens, or S3 upload errors) would result in silent failures, delaying downstream business analytics and reporting.

---

## Decision Drivers
1. **Zero Silent Failures:** Instant alerting on execution failures at the orchestrator level.
2. **Kibana / Elasticsearch Compatibility:** Seamless integration with standard centralized logging aggregators.
3. **Contextual & Actionable Alerts:** Notifications must contain error traces, duration, affected dataset, and deep links to dashboards.
4. **Zero Proprietary / Internal Leaks:** Generic domain modeling suitable for public open-source demonstration and reference implementations.

---

## Considered Options

### 1. Alerting Strategy
- **Option 1A: In-app try/catch notification (Python)**
  - *Cons:* Fails silently if the container is OOMKilled, evicted, or times out at the Kubernetes level.
- **Option 1B: Argo Workflow `onExit` Handler**
  - *Pros:* Decoupled from application runtime; guaranteed execution regardless of pod exit status (`Failed`, `Errored`).
  - *Decision:* **Option 1B (Argo `onExit` Email Notification)**.

### 2. Logging Strategy
- **Option 2A: Plain text console prints**
  - *Cons:* Unstructured, difficult to filter or build metrics around in Kibana.
- **Option 2B: Structured JSON Logging (JSONL)**
  - *Pros:* Native ingestion into Elasticsearch/OpenSearch; enables metric extraction and rapid querying.
  - *Decision:* **Option 2B (Structured JSON Logging)**.

---

## Decision Outcome

### Pipeline Flow
1. **Trigger:** Argo CronWorkflow runs daily at `01:00 AM (Asia/Bangkok)`.
2. **Extraction:** Python 3.12 extracts semi-structured JSONB events:
   - `DEVICE_TELEMETRY` (Device metrics, battery, network status)
   - `ORDER_EVENTS` (E-commerce order events and status transitions)
3. **Transformation & Export:** Formats data into RFC 4180 CSV (`UTF-8 BOM`, `QUOTE_ALL`).
4. **Storage:** Uploads to S3 with `SSE-KMS` and creates a 2-hour Presigned URL.
5. **Dispatch:** Notifies downstream via API Gateway using a JWT-signed Webhook.
6. **Observability:**
   - Emits structured JSON logs to stdout for Fluentbit/Elasticsearch.
   - Argo `onExit` hook fires an alert email with run context if execution fails.

---

## Consequences
- **Positive:** Resilient alerting against container-level faults, quick Mean Time to Resolution (MTTR), zero risk of exposing confidential company data.
- **Trade-offs:** Requires standard SMTP relay or SES credentials configured in the cluster.
