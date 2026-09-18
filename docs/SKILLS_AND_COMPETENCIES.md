# Engineering Skills & Competencies Reference

This document compiles core technical skills, operational principles, and production readiness checks for maintaining this data pipeline platform.

---

## 1. Technical Competencies Breakdown

### A. Data Engineering & Relational Databases (PostgreSQL / Aurora)
- **JSONB Querying & Flattening:** Advanced use of PostgreSQL JSONB operators (`->>`, `#>>`, `jsonb_extract_path_text`) to transform nested event logs into standardized relational tabular structures.
- **Large Dataset Streaming:** Memory management to prevent `OOMKilled` container failures using server-side cursors (`named cursor` in `psycopg2` or `yield_per` in SQLAlchemy).
- **CSV Standardization:** Adherence to RFC 4180 formatting with UTF-8 BOM encoding for multilingual data interoperability and strict quoting (`csv.QUOTE_ALL`).

### B. Cloud Storage & Data Protection (AWS S3 / KMS / MinIO)
- **Server-Side Encryption (SSE-KMS):** Proper configuration of encryption headers (`aws:kms`) and KMS Key ARNs via the Boto3 SDK.
- **Restricted Time-to-Live Presigned URLs:** Generating secure, time-bounded access links (`ExpiresIn=7200`) to decouple storage access from consuming downstream systems.
- **Identity & Access Management:** Utilizing AWS IRSA (IAM Roles for Service Accounts) in Kubernetes to prevent long-lived credentials within container runtimes.

### C. Workflow Orchestration (Kubernetes & Argo Workflows)
- **CronWorkflow Management:** Defining cron expressions, handling timezone configurations (`Asia/Bangkok`), and managing parameter propagation.
- **Fault Tolerance & Reliability:** Implementing `retryStrategy` with exponential backoff, deadline guards (`activeDeadlineSeconds`), and `onExit` lifecycle triggers.
- **Modular Workflow Templates:** Designing reusable `WorkflowTemplate` and `ClusterWorkflowTemplate` definitions to promote cross-team standardization.

### D. Modern Observability (Elasticsearch, Kibana, Centralized Logging)
- **Structured JSON Logging:** Implementing Twelve-Factor App principles by emitting standardized JSON lines directly to `stdout`.
- **Distributed Context Propagation:** Attaching consistent tracing fields (`batch_id`, `export_date`, `stage`) to facilitate querying across large-scale log indexes.
- **Actionable Alerting Design:** Constructing concise alert templates enriched with deep links to Kibana queries to accelerate Mean Time to Resolution (MTTR).

---

## 2. Production Readiness Checklist

- [ ] **Connection Pooling:** Validate that database connections are managed safely and closed properly.
- [ ] **Volume Testing:** Execute load testing against high record volumes (e.g., 1M+ rows) to verify container memory limits.
- [ ] **KMS Access Verification:** Ensure that the Kubernetes ServiceAccount has permissions for `kms:GenerateDataKey` and `kms:Decrypt`.
- [ ] **PII Data Sanitization:** Verify that no Personally Identifiable Information (passwords, citizen IDs) is emitted in log outputs.
- [ ] **Alerting Drills:** Simulate intentional database failures to confirm automated trigger of Argo `onExit` email alerts.
