# Kibana Saved Queries & Alert Rules (KQL)

รวม Query มาตรฐานสำหรับนำไปใส่ใน Kibana Discover, Dashboard filters, หรือสร้าง Alerting Rules ใน Kibana Watcher / Alerting Framework

---

## 1. Top Severity Alerts (ข้อผิดพลาดวิกฤต)

### A. Critical Failures & Unhandled Exceptions
- **Query (KQL):**
  ```kql
  service: "batch-data-extractor" and level: ("ERROR" or "CRITICAL")
  ```
- **Action:** ส่งเข้า On-Call Team ทันที

### B. Zero Rows Anomaly (ดึงข้อมูลได้ 0 แถว ผิดปกติ)
- **Query (KQL):**
  ```kql
  service: "batch-data-extractor" and stage: "EXTRACT_DB" and row_count: 0
  ```
- **Description:** แจ้งเตือนเมื่อ Table ต้นทางไม่มีข้อมูลใหม่ในรอบวัน หรือเงื่อนไข Date partition ผิดพลาด

---

## 2. Performance & SLA Monitoring

### A. Slow Database Query (> 30 วินาที)
- **Query (KQL):**
  ```kql
  service: "batch-data-extractor" and stage: "EXTRACT_DB" and duration_ms > 30000
  ```

### B. Slow S3 / MinIO Upload (> 60 วินาที)
- **Query (KQL):**
  ```kql
  service: "batch-data-extractor" and stage: "UPLOAD_S3" and duration_ms > 60000
  ```

---

## 3. Dataset Tracing (ค้นหาประวัติตามรอบการรัน)

### ค้นหาด้วย Batch ID:
```kql
batch_id: "your-uuid-here"
```

### ค้นหาข้อมูลของ Export Date เฉพาะวัน:
```kql
service: "batch-data-extractor" and export_date: "2026-09-17"
```
