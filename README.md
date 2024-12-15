# Google Vision OCR API Documentation

## Overview
API สำหรับแปลงข้อความจากรูปภาพโดยใช้ Google Cloud Vision API รองรับการส่งข้อมูลได้ 3 รูปแบบ:
- Form-data (รูปภาพหลายไฟล์)
- URL ของรูปภาพ
- รูปภาพแบบ Base64

## Endpoint
```
POST https://google-vision-api.vercel.app/api/ocr/process-batch
```

## วิธีการใช้งาน

### 1. แบบ Form-data
เหมาะสำหรับการส่งไฟล์รูปภาพหลายไฟล์พร้อมกัน

**Headers:**
```
Content-Type: multipart/form-data
```

**Request Body:**
```
file1: [ไฟล์รูปภาพ 1]
file2: [ไฟล์รูปภาพ 2]
...
```

### 2. แบบ URL
สำหรับการส่ง URL ของรูปภาพที่ต้องการประมวลผล

**Headers:**
```
Content-Type: application/json
```


**Request Body:**
```json
{
    "images": [
        {
            "url": "https://example.com/image1.jpg",
            "filename": "image1.jpg"
        },
        {
            "url": "https://example.com/image2.png",
            "filename": "image2.png"
        },
        {
            "url": "https://example.com/image3.jpg",
            "filename": "image3.jpg"
        }
    ]
}
```

### 3. แบบ Base64
สำหรับการส่งรูปภาพในรูปแบบ Base64 string

**Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
    "images": [
        {
            "image": "BASE64_STRING",
            "filename": "image1.jpg"
        }
    ]
}
```

## Response Format
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
    ]
}
```

## Error Response
```json
{
    "status": "error",
    "message": "รายละเอียดข้อผิดพลาด"
}
```

## ข้อจำกัด
- รองรับไฟล์รูปภาพประเภท: JPG, JPEG, PNG, GIF, BMP, WEBP
- ขนาดไฟล์สูงสุด: 10MB ต่อไฟล์
- จำนวนไฟล์สูงสุดต่อการเรียก: 10 ไฟล์

## ตัวอย่างการใช้งาน

### Python
```python
import requests

# แบบ Form-data
files = {
    'file1': open('image1.jpg', 'rb'),
    'file2': open('image2.png', 'rb')
}
response = requests.post('https://google-vision-api.vercel.app/api/ocr/process-batch', files=files)

# แบบ URL
json_data = {
    "images": [
        {
            "url": "https://example.com/image1.jpg",
            "filename": "image1.jpg"
        }
    ]
}
response = requests.post('https://google-vision-api.vercel.app/api/ocr/process-batch', json=json_data)
```

### JavaScript
```javascript
// แบบ Form-data
const formData = new FormData();
formData.append('file1', file1);
formData.append('file2', file2);

fetch('https://google-vision-api.vercel.app/api/ocr/process-batch', {
    method: 'POST',
    body: formData
});

// แบบ URL
fetch('https://google-vision-api.vercel.app/api/ocr/process-batch', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        images: [
            {
                url: 'https://example.com/image1.jpg',
                filename: 'image1.jpg'
            }
        ]
    })
});
```

## หมายเหตุ
- API นี้ต้องการ API key ของ Google Cloud Vision
- ควรใช้ HTTPS ในการส่งข้อมูล
- ตรวจสอบขนาดและประเภทของไฟล์ก่อนส่ง