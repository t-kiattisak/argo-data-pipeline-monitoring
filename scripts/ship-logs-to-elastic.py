import json
import os
import sys
import urllib.request

ES_URL = "http://localhost:9200/pipeline-logs/_doc"

# Feed our pipeline logs directly to Elasticsearch
sample_logs = [
    {"timestamp": "2026-09-18T01:00:00.120Z", "level": "INFO", "service": "batch-data-extractor", "dataset": "system", "stage": "PIPELINE_START", "batch_id": "b-9001", "export_date": "2026-09-17", "message": "Pipeline started for 2026-09-17"},
    {"timestamp": "2026-09-18T01:00:05.340Z", "level": "INFO", "service": "batch-data-extractor", "dataset": "DEVICE_TELEMETRY", "stage": "EXTRACT_DB", "batch_id": "b-9001", "export_date": "2026-09-17", "row_count": 2, "duration_ms": 31, "message": "Successfully extracted 2 rows from PostgreSQL"},
    {"timestamp": "2026-09-18T01:00:06.100Z", "level": "INFO", "service": "batch-data-extractor", "dataset": "DEVICE_TELEMETRY", "stage": "UPLOAD_S3", "batch_id": "b-9001", "export_date": "2026-09-17", "duration_ms": 15, "file_size_bytes": 730, "s3_key": "datasets/DEVICE_TELEMETRY/2026-09-17.csv", "message": "Uploaded to MinIO/S3 successfully"},
    {"timestamp": "2026-09-18T01:00:10.500Z", "level": "INFO", "service": "batch-data-extractor", "dataset": "ORDER_EVENTS", "stage": "EXTRACT_DB", "batch_id": "b-9001", "export_date": "2026-09-17", "row_count": 2, "duration_ms": 25, "message": "Successfully extracted 2 rows from PostgreSQL"},
    {"timestamp": "2026-09-18T01:00:11.200Z", "level": "INFO", "service": "batch-data-extractor", "dataset": "ORDER_EVENTS", "stage": "UPLOAD_S3", "batch_id": "b-9001", "export_date": "2026-09-17", "duration_ms": 12, "file_size_bytes": 622, "s3_key": "datasets/ORDER_EVENTS/2026-09-17.csv", "message": "Uploaded to MinIO/S3 successfully"},
    {"timestamp": "2026-09-18T01:00:12.000Z", "level": "INFO", "service": "batch-data-extractor", "dataset": "system", "stage": "PIPELINE_SUCCESS", "batch_id": "b-9001", "export_date": "2026-09-17", "message": "Batch extraction completed successfully"}
]

for item in sample_logs:
    req = urllib.request.Request(ES_URL, data=json.dumps(item).encode("utf-8"), headers={"Content-Type": "application/json"})
    urllib.request.urlopen(req)

print("Ingested logs into Elasticsearch index 'pipeline-logs' successfully.")
