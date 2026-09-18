# Documentation Index

Welcome to the **Argo Data Pipeline & Observability** project documentation (`argo-data-pipeline-monitoring`).

---

## สารบัญเอกสาร (Documentation Directory)

1. [ADR-001: Batch Data Extraction & Observability Architecture](ADR-001-pipeline-observability.md)
   - Architecture Decision Record สำหรับการออกแบบระบบ Data Extraction พร้อมระบบ Monitoring & Alerting
   - การเปรียบเทียบข้อดี/ข้อเสียของ Argo `onExit` vs Application try/catch

2. [ARCHITECTURE.md: System Architecture & Technical Specifications](ARCHITECTURE.md)
   - สถาปัตยกรรมระบบโดยละเอียด (High-Level Architecture + Sequence Diagram)
   - Generic Dataset Specifications (`DEVICE_TELEMETRY` และ `ORDER_EVENTS`)
   - มาตรฐานความปลอดภัย (SSE-KMS, Presigned URL TTL, API Gateway JWT)

3. [OBSERVABILITY_GUIDE.md: Observability & Monitoring Specification](OBSERVABILITY_GUIDE.md)
   - มาตรฐาน Structured JSON Logging สำหรับ Kibana / Elasticsearch
   - Argo Workflow `onExit` Email Alerting Spec
   - KQL Queries สำหรับการสร้าง Dashboard

4. [SKILLS_AND_COMPETENCIES.md: Engineering Skills Reference](SKILLS_AND_COMPETENCIES.md)
   - ทักษะสำคัญ: PostgreSQL JSONB Flattening, Boto3 S3/KMS, Argo Workflows, Centralized Logging
   - Production Readiness Checklist
