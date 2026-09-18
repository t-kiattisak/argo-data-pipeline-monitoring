# Kibana Observability & Dashboard Assets

โฟลเดอร์นี้บรรจุ Assets สำหรับ Kibana เพื่อนำเข้า (Import) และตั้งค่า Monitoring ได้ทันที

---

## สารบัญไฟล์:

1. **`dashboards/pipeline-dashboard-export.ndjson`**:
   - Dashboard สำเร็จรูป (Saved Objects)
   - ประกอบด้วย:
     - **Extracted Rows Metric**: ยอดรวมจำนวนแถวข้อมูล
     - **Stage Duration Trend**: กราฟแสดงเวลาที่ใช้ในแต่ละขั้นตอน (DB, CSV, S3, Webhook)
     - **Error Log Table**: ตารางค้นหา Log ที่ติด Error แบบเรียลไทม์
2. **`index-patterns/data-pipeline-index-pattern.json`**:
   - Index Pattern นิยาม Schema ฟิลด์ (`timestamp`, `row_count`, `duration_ms`, `stage`, `dataset`)
3. **`rules/kql-saved-queries.md`**:
   - รวมสูตร KQL (Kibana Query Language) สำหรับค้นหาข้อผิดพลาดและตั้ง Alerts (Zero rows check, Query timeout)

---

## วิธีการ Import เข้า Kibana:
1. เปิด Kibana Web UI (`http://kibana-host:5601`)
2. ไปที่เมนู **Stack Management** > **Saved Objects**
3. กดปุ่ม **Import** ด้านขวาบน
4. เลือกไฟล์ `dashboards/pipeline-dashboard-export.ndjson`
5. เปิดหน้า Dashboard: **`[DataOps] Batch Pipeline Observability Dashboard`**
