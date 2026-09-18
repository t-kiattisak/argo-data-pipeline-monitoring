# Engineering Skills & Competencies Reference

เอกสารนี้รวบรวมองค์ความรู้ ทักษะทางเทคนิค (Skills) และข้อควรระวังสำคัญสำหรับวิศวกรที่ดูแลระบบ **Upstream Data Pipeline & Observability** นี้

---

## 1. Core Technical Skills Breakdown

### A. Data Engineering & Database (Aurora PostgreSQL)
- **JSONB Querying & Flattening:** ความชำนาญการใช้ฟังก์ชัน JSONB ของ PostgreSQL เช่น `jsonb_extract_path_text()`, `->>`, `#>>` และ `jsonb_array_elements()` เพื่อแตก Nested Structure ออกเป็น Tabular Relational Model
- **Large Dataset Streaming:** การจัดการหน่วยความจำ (Memory Management) ไม่ให้เกิด `OOMKilled` ด้วยการใช้ Server-side Cursors (`named cursor` ใน `psycopg2` หรือ `yield_per` ใน SQLAlchemy) แทนการใช้ `fetchall()`
- **CSV Standards:** ความเข้าใจเรื่อง Encoding (`UTF-8 BOM` หรือ `utf-8-sig` เพื่อรองรับภาษาไทยในโปรแกรมภายนอก), การ Escaping quotes และ newlines (`quoting=csv.QUOTE_ALL`)

### B. Cloud Storage & Security (AWS S3 & KMS)
- **Server-Side Encryption with KMS (SSE-KMS):** การคอนฟิก `ServerSideEncryption='aws:kms'` และ `SSEKMSKeyId` ใน Boto3 SDK
- **Presigned URLs with Expiration:** การสร้าง Signed URL ที่มีอายุจำกัด (Time-to-Live) โดยใช้ `generate_presigned_url('get_object', Params=..., ExpiresIn=7200)`
- **Cloud Security IAM:** การใช้ AWS IRSA (IAM Roles for Service Accounts) บน EKS เพื่อหลีกเลี่ยงการเก็บ Long-lived Credentials ใน Container

### C. Workflow Orchestration (Argo Workflows & Events)
- **CronWorkflow Lifecycle:** การกำหนด Schedule Cron, Timezone (`Asia/Bangkok`), และการส่ง Parameters ข้าม Steps
- **Reliability & Fail-safe:** การใช้งาน `onExit` handler, `retryStrategy`, และ `activeDeadlineSeconds`
- **Argo Event Integration:** สถาปัตยกรรม Event-driven ข้ามระบบผ่าน Kong APIGW -> EventSource -> Sensor

### D. Modern Observability (Elasticsearch, Kibana, Alerting)
- **Structured JSON Logging:** การทำ Logging ตามมาตรฐาน 12-Factor App โดยส่งออกเป็น JSON ผ่าน `stdout`
- **Context Propagation:** การส่งต่อ Correlation ID (`batch_id`, `export_date`) ผ่านทุกลำดับของ Pipeline เพื่อความสะดวกในการ Filter ใน Kibana
- **Actionable Incident Alerting:** การออกแบบเนื้อหา Email Alert ให้กระชับ มีลิงก์ตรงไปยัง Dashboard เพื่อลด Mean Time to Resolution (MTTR)

---

## 2. Best Practices Checklist ก่อน Deploy ขึ้น Production

- [ ] **Database Connection:** ใช้ Connection Pool และตั้งค่า Timeout ที่เหมาะสมเพื่อป้องกัน Connection Leak
- [ ] **Data Volume Buffer:** ทดสอบ Query กับปริมาณข้อมูลจริง (เช่น 1,000,000 แถว) เพื่อดูพฤติกรรม RAM
- [ ] **KMS Access:** ตรวจสอบว่า IAM Role ของ Pod มีสิทธิ์ `kms:GenerateDataKey` และ `kms:Decrypt`
- [ ] **Log Sanitization:** ตรวจสอบว่าไม่มีข้อมูล PII (Personally Identifiable Information) เช่น เลขบัตรประชาชน หรือ Password หลุดไปใน Log
- [ ] **Alert Drill / Chaos Test:** ทดสอบปิด Database ชั่วคราว เพื่อดูว่า Argo `onExit` ส่ง Email แจ้งเตือนถูกต้องหรือไม่
