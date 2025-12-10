# 📋 SecOps Demo Workflow Guide

คู่มือการใช้งาน n8n Workflow สำหรับ SecOps Demo - Automated Vulnerability Detection

## 🎯 ภาพรวม Workflow

Workflow นี้จะทำการ:
1. รับคำสั่งจาก Line OA Webhook
2. สแกน Port ด้วย Nmap
3. ส่งผลลัพธ์ไปให้ Nuclei สแกนช่องโหว่
4. ใช้ AI (OpenAI) วิเคราะห์ผลลัพธ์จาก Nuclei
5. ตรวจสอบช่องโหว่ด้วย curl command
6. ส่งแจ้งเตือนไปยัง Line Notify

## 📥 การ Import Workflow

1. เปิด n8n UI ที่ `http://localhost:5678`
2. คลิก **Workflows** → **Import from File**
3. เลือกไฟล์ `secops-workflow.json`
4. Workflow จะถูก import เข้ามาในระบบ

## ⚙️ การตั้งค่า (Configuration)

### 1. Line OA Webhook

- Node: **Line OA Webhook**
- Path: `secops-scan` (สามารถแก้ไขได้)
- Webhook URL จะแสดงใน node หลังจาก Activate workflow
- ใช้ URL นี้ในการตั้งค่า Line OA Webhook

### 2. OpenAI API

- Node: **6. AI Analyst**
- ต้องสร้าง Credential สำหรับ OpenAI API:
  1. คลิกที่ node **6. AI Analyst**
  2. คลิก **Create New Credential**
  3. เลือก **OpenAI API**
  4. ใส่ API Key ของ OpenAI
  5. บันทึก

### 3. Line Notify Token

- Node: **8. Line Notify Alert**
- ต้องตั้งค่า Environment Variable:
  1. ใน n8n Settings → Environment Variables
  2. เพิ่ม `LINE_NOTIFY_TOKEN` = Token จาก Line Notify
  3. หรือแก้ไข node โดยตรงใน Authorization header

**วิธีสร้าง Line Notify Token:**
1. ไปที่ https://notify-bot.line.me/
2. Login ด้วย Line Account
3. คลิก **My page** → **Generate token**
4. เลือก Group หรือ Chat ที่ต้องการส่งข้อความ
5. Copy Token ที่ได้มา

### 4. Target Configuration

- Target URL ถูกตั้งค่าเป็น `http://victim-app` (ตาม docker-compose network)
- หากต้องการเปลี่ยน target สามารถแก้ไขใน node **2. Parse Ports**

## 🔄 Workflow Flow

```
Line OA Webhook
    ↓
1. Nmap Port Scan (สแกน Port ที่เปิด)
    ↓
2. Parse Ports (แยก Port และสร้าง URL)
    ↓
3. Nuclei Scan (สแกนช่องโหว่แต่ละ Port)
    ↓
4. Parse Nuclei Output (แปลง JSON output)
    ↓
5. Prepare AI Input (เตรียมข้อมูลสำหรับ AI)
    ↓
6. AI Analyst (OpenAI วิเคราะห์ช่องโหว่)
    ↓
Parse AI Response (แปลงผลลัพธ์จาก AI)
    ↓
Check Vulnerability Found (ตรวจสอบว่าพบช่องโหว่หรือไม่)
    ↓
    ├─ Yes → 7. Validation Loop (รัน curl command)
    │           ↓
    │           Check Curl Result (ตรวจสอบ HTTP status code)
    │           ↓
    │           ├─ 200 → 8. Line Notify Alert (ส่งแจ้งเตือน)
    │           └─ 404 → False Positive (ไม่ส่งแจ้งเตือน)
    │
    └─ No → Safe Status (ไม่พบช่องโหว่)
```

## 🧪 การทดสอบ

### 1. ทดสอบ Webhook

```bash
curl -X POST http://localhost:5678/webhook/secops-scan \
  -H "Content-Type: application/json" \
  -d '{"test": "scan"}'
```

### 2. ทดสอบด้วย Line OA

ตั้งค่า Webhook URL ใน Line OA Developer Console:
- Webhook URL: `http://your-domain:5678/webhook/secops-scan`
- หรือใช้ Cloudflare Tunnel URL หากตั้งค่าไว้

### 3. ตรวจสอบ Logs

ดู execution logs ใน n8n UI:
- ไปที่ **Executions** tab
- ดูรายละเอียดแต่ละ step

## 🔧 การแก้ไขปัญหา (Troubleshooting)

### ปัญหา: Nmap ไม่พบ Port

- ตรวจสอบว่า victim-app container กำลังรันอยู่
- ทดสอบด้วย: `docker exec -it n8n-secops nmap -p 80,8080 victim-app`

### ปัญหา: Nuclei ไม่พบช่องโหว่

- อัปเดต Nuclei templates: `nuclei -update-templates`
- ตรวจสอบว่า victim-app มีไฟล์ `.env` ที่เปิดเผยอยู่

### ปัญหา: OpenAI ไม่ตอบกลับ

- ตรวจสอบ API Key ถูกต้อง
- ตรวจสอบว่ามี Credit ใน OpenAI Account
- ดู error logs ใน n8n Executions

### ปัญหา: Line Notify ไม่ส่งข้อความ

- ตรวจสอบ LINE_NOTIFY_TOKEN ถูกต้อง
- ทดสอบ Token ด้วย curl:
  ```bash
  curl -X POST https://notify-api.line.me/api/notify \
    -H "Authorization: Bearer YOUR_TOKEN" \
    -F "message=Test message"
  ```

## 📝 หมายเหตุ

- Workflow นี้ใช้สำหรับ **การศึกษาและ Demo เท่านั้น**
- อย่าใช้กับระบบจริงโดยไม่ได้รับอนุญาต
- ตรวจสอบให้แน่ใจว่า target เป็นระบบที่คุณมีสิทธิ์ทดสอบ

## 🔗 Resources

- [n8n Documentation](https://docs.n8n.io/)
- [Nuclei Documentation](https://docs.nuclei.sh/)
- [Nmap Documentation](https://nmap.org/book/)
- [Line Notify API](https://notify-bot.line.me/doc/en/)

