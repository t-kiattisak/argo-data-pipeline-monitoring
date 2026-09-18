# System Architecture & Technical Specifications

This document provides a technical deep dive into the **Batch Data Pipeline & Observability** platform, designed to extract semi-structured event logs from PostgreSQL and ingest them into Cloud/Local Object Storage (S3 / MinIO).

---

## 1. High-Level Architecture

```mermaid
flowchart TD
    subgraph K8s["Kubernetes Cluster (Argo Workflows)"]
        Cron["Argo CronWorkflow<br/>(Daily 01:00 Bangkok)"]
        
        subgraph ExtractorPod["Pod: Generic Extractor (Python 3.12)"]
            Main["main.py"]
            DB["PostgreSQL Client<br/>(psycopg2 / SQLAlchemy)"]
            CSV["CSV Formatter<br/>(UTF-8 BOM, QUOTE_ALL)"]
            S3Client["S3 Uploader<br/>(boto3, SSE-KMS)"]
            Webhook["API Gateway Webhook Client<br/>(requests, JWT Bearer)"]
            LogEngine["Structured JSON Logger<br/>(stdout)"]
        end
        
        subgraph Handlers["Workflow Lifecycle Handlers"]
            OnExit{"onExit Trigger"}
            EmailPod["Pod: Mail Notifier<br/>(SMTP / SES Relay)"]
        end
    end

    subgraph Storage["Cloud / Local Storage"]
        PG[("PostgreSQL Database<br/>JSONB event_records")]
        S3Bucket[("S3 / MinIO Bucket")]
        KMS["KMS Encryption Key"]
    end

    subgraph Gateway["Edge / API Gateway"]
        APIGW["API Gateway<br/>JWT Auth Verification"]
        EventSink["Downstream Event Broker"]
    end

    subgraph Observability["Observability Platform"]
        Fluentbit["Fluentbit / Log Agent"]
        Elasticsearch[("Elasticsearch")]
        Kibana["Kibana Dashboard"]
    end

    %% Cron and Pipeline flow
    Cron --> ExtractorPod
    Main --> DB
    DB --> PG
    PG --> DB
    DB --> CSV
    CSV --> S3Client
    S3Client --> S3Bucket
    S3Bucket -.-> KMS
    Main --> Webhook
    Webhook --> APIGW
    APIGW --> EventSink

    %% Logging & Observability
    ExtractorPod -.-> Fluentbit
    Fluentbit --> Elasticsearch
    Elasticsearch --> Kibana

    %% Failure / Exit Handling
    ExtractorPod --> OnExit
    OnExit --> EmailPod
    EmailPod --> AlertRecipients["Data Engineering / SRE Team"]
```

---

## 2. Sequence Flow

```mermaid
sequenceDiagram
    autonumber
    participant Cron as Argo CronWorkflow
    participant App as Python 3.12 Extractor
    participant DB as PostgreSQL
    participant S3 as AWS S3 (KMS)
    participant APIGW as API Gateway
    participant Mail as Email Notifier (onExit)

    Note over Cron: Daily 01:00 Asia/Bangkok
    Cron->>App: Launch Pod (EXPORT_DATE)

    rect rgb(240, 248, 255)
        Note over App,S3: Stage 1: Device Telemetry Dataset
        App->>DB: Query JSONB flatten (DEVICE_TELEMETRY)
        DB-->>App: Extracted Columns ResultSet
        App->>App: Format CSV (UTF-8 BOM, QUOTE_ALL)
        App->>S3: PutObject (SSE-KMS)
        App->>S3: Generate Presigned URL (2h expiry)
        App-->>App: Emit Stage Metric (JSON log)
    end

    rect rgb(245, 255, 245)
        Note over App,S3: Stage 2: Order Events Dataset
        App->>DB: Query JSONB flatten (ORDER_EVENTS)
        DB-->>App: Extracted Columns ResultSet
        App->>App: Format CSV (UTF-8 BOM, QUOTE_ALL)
        App->>S3: PutObject (SSE-KMS)
        App->>S3: Generate Presigned URL (2h expiry)
        App-->>App: Emit Stage Metric (JSON log)
    end

    rect rgb(255, 250, 240)
        Note over App,APIGW: Stage 3: Downstream Webhook Notification
        App->>APIGW: POST /events/v1/batch-completed (JWT Bearer)
        APIGW-->>App: 200 OK
        App-->>App: Emit Success JSON log
    end

    alt Any Stage Fails (DB / S3 / APIGW / OOM)
        App--xCron: Exit non-zero
        Cron->>Mail: Trigger onExit Handler
        Mail-->>Mail: Send Email Alert with Dashboard Link & Error Context
    end
```

---

## 3. Generic Dataset Specifications

To safeguard intellectual property, this demonstration implements standardized telemetry and e-commerce models:

### Dataset 1: `DEVICE_TELEMETRY`
- **Source:** PostgreSQL table (`iot_device_events`, JSONB column: `payload`)
- **Extracted Columns:**
  1. `event_id` (UUID / String)
  2. `device_id` (String)
  3. `timestamp` (Timestamp ISO-8601)
  4. `battery_level` (Decimal)
  5. `temperature_c` (Decimal)
  6. `firmware_version` (String)
  7. `signal_strength_dbm` (Integer)
  8. `cpu_usage_pct` (Decimal)
  9. `memory_usage_pct` (Decimal)
  10. `operating_mode` (String)
  11. `network_type` (String)
  12. `ip_address` (String)
  13. `status` (String)
  14. `created_at` (Timestamp)
  15. `export_date` (Date YYYY-MM-DD)
  16. `batch_id` (String)

### Dataset 2: `ORDER_EVENTS`
- **Source:** PostgreSQL table (`store_order_events`, JSONB column: `payload`)
- **Extracted Columns:**
  1. `order_id` (String)
  2. `customer_id` (String)
  3. `event_timestamp` (Timestamp ISO-8601)
  4. `event_type` (String: CREATED, PAID, SHIPPED, CANCELLED)
  5. `currency` (String)
  6. `total_amount` (Decimal)
  7. `discount_amount` (Decimal)
  8. `item_count` (Integer)
  9. `payment_method` (String)
  10. `shipping_carrier` (String)
  11. `delivery_country` (String)
  12. `created_at` (Timestamp)
  13. `export_date` (Date YYYY-MM-DD)
  14. `batch_id` (String)

---

## 4. Security & Compliance
1. **At-Rest Encryption:** Files stored in S3 enforce server-side encryption via `aws:kms`.
2. **In-Transit Encryption:** All transport layers enforce TLS 1.3.
3. **Restricted Time-to-Live (TTL):** Presigned S3 URLs expire after 2 hours (`ExpiresIn=7200`).
4. **Data Sanitization:** Strict avoidance of proprietary corporate identifiers and business rules.
