# Kibana Saved Queries & Alert Rules (KQL)

Standard query patterns for use in Kibana Discover, Dashboard filters, and Alerting Rules (Watcher / Alerting Framework).

---

## 1. High-Severity Operational Alerts

### A. Critical Failures & Unhandled Exceptions
- **KQL Query:**
  ```kql
  service: "batch-data-extractor" and level: ("ERROR" or "CRITICAL")
  ```
- **Recommended Action:** Immediate notification to on-call engineering.

### B. Zero-Row Anomaly (Extraction returns 0 rows)
- **KQL Query:**
  ```kql
  service: "batch-data-extractor" and stage: "EXTRACT_DB" and row_count: 0
  ```
- **Description:** Alerts when the source table contains no records for the given date partition.

---

## 2. Latency & SLA Monitoring

### A. Slow Database Query (> 30 seconds)
- **KQL Query:**
  ```kql
  service: "batch-data-extractor" and stage: "EXTRACT_DB" and duration_ms > 30000
  ```

### B. Slow S3 / MinIO Upload (> 60 seconds)
- **KQL Query:**
  ```kql
  service: "batch-data-extractor" and stage: "UPLOAD_S3" and duration_ms > 60000
  ```

---

## 3. Execution Tracing

### Filter by Specific Batch ID:
```kql
batch_id: "your-uuid-here"
```

### Filter by Target Export Date:
```kql
service: "batch-data-extractor" and export_date: "2026-09-17"
```
