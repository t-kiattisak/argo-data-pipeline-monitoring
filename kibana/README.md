# Kibana Observability & Dashboard Assets

This directory contains pre-configured assets for Elasticsearch and Kibana to facilitate immediate log visualization and monitoring.

---

## Directory Contents:

1. **`dashboards/pipeline-dashboard-export.ndjson`**:
   - Pre-built Saved Object dashboard ready for direct import into Kibana.
   - Includes:
     - **Extracted Rows Metric**: Aggregated throughput across datasets.
     - **Stage Duration Trend**: Historical latency tracking per stage (`EXTRACT_DB`, `WRITE_CSV`, `UPLOAD_S3`, `POST_WEBHOOK`).
     - **Error Log Table**: Real-time listing of pipeline errors and stack traces.

2. **`index-patterns/data-pipeline-index-pattern.json`**:
   - Field schema definitions mapping numeric metrics (`row_count`, `duration_ms`) and categorical dimensions (`stage`, `dataset`).

3. **`rules/kql-saved-queries.md`**:
   - Standard Kibana Query Language (KQL) formulas for diagnosing failures, zero-row anomalies, and latency spikes.

---

## Import Instructions:
1. Open the Kibana Web UI (`http://localhost:5601`).
2. Navigate to **Stack Management** > **Saved Objects**.
3. Click the **Import** button in the top-right corner.
4. Select `dashboards/pipeline-dashboard-export.ndjson`.
5. Open the newly imported dashboard: **`[DataOps] Batch Pipeline Observability Dashboard`**.
