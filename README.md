# Google Vision OCR API

## 📝 รายละเอียด
API สำหรับแปลงข้อความจากรูปภาพโดยใช้ Google Cloud Vision API รองรับการส่งข้อมูล 3 รูปแบบ:
- Form-data Images Array (รูปภาพหลายไฟล์)

## 🔗 Endpoint
```
POST https://google-vision-api.vercel.app/api/ocr/process-batch
```

## 📌 ข้อจำกัด
- รองรับไฟล์: JPG, JPEG, PNG, GIF, BMP, WEBP
- ขนาดไฟล์สูงสุด: 10MB ต่อไฟล์
- จำนวนไฟล์สูงสุด: 10 ไฟล์ต่อการเรียก

## 🚀 วิธีการใช้งาน
API นี้ต้องใช้ API Key ในการเข้าถึง โดยส่งผ่าน Header

```http
Secret-Key: your-api-key-here
```
### Form-data
```http
POST /api/ocr/process-batch
Content-Type: multipart/form-data

images[]: [ไฟล์รูปภาพ 1]
images[]: [ไฟล์รูปภาพ 2]
...

```
```http
หรือ
POST /api/ocr/process-batch
Content-Type: multipart/form-data

images[0]: [ไฟล์รูปภาพ 1]
images[1]: [ไฟล์รูปภาพ 2]
...
```

## 📋 Response Format
### Success Response
```json
{
    "status": "success",
    "results": [
        {
            "filename": "image1.jpg",
            "status": "success",
            "data": {
                "filename": "image1.jpg",
                "timestamp": "2024-12-15T22:37:00.000Z",
                "text": "ข้อความที่พบในรูปภาพ",
                "blocks": [
                    {
                        "text": "ข้อความในบล็อก",
                        "confidence": 0.99,
                        "bounds": {
                            "x1": 100,
                            "y1": 200,
                            "x2": 300,
                            "y2": 400
                        }
                    }
                ]
            }
        }
    ],
    "message": "Processed 1 images"
}
```

### Error Response
```json
{
    "status": "error",
    "message": "รายละเอียดข้อผิดพลาด"
}
```

## 💻 ตัวอย่างการใช้งาน

### Python
```python
import requests

files = [
    ('images[]', ('image1.jpg', open('image1.jpg', 'rb'))),
    ('images[]', ('image2.jpg', open('image2.jpg', 'rb')))
]
response = requests.post(
    'https://google-vision-api.vercel.app/api/ocr/process-batch',
    files=files
)
```

### JavaScript
```javascript
const formData = new FormData();
formData.append('images[]', file1);
formData.append('images[]', file2);

await fetch('https://google-vision-api.vercel.app/api/ocr/process-batch', {
    method: 'POST',
    body: formData
});
```

## ⚠️ Error Codes
| Status Code | Description |
|-------------|-------------|
| 400 | Bad Request - ข้อมูลไม่ถูกต้องหรือไม่ครบถ้วน |
| 413 | Payload Too Large - ขนาดไฟล์เกินกำหนด |
| 415 | Unsupported Media Type - รูปแบบไฟล์ไม่รองรับ |
| 429 | Too Many Requests - จำนวนการเรียกเกินกำหนด |
| 500 | Internal Server Error - เกิดข้อผิดพลาดภายในเซิร์ฟเวอร์ |

## 📝 หมายเหตุ
- ใช้ HTTPS เท่านั้นในการส่งข้อมูล
- ตรวจสอบขนาดและประเภทของไฟล์ก่อนส่ง