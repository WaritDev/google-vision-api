# 1. ทดสอบแบบ Form-data
Method: POST
URL: https://google-vision-api.vercel.app/api/ocr/process-batch
Headers:
  Content-Type: multipart/form-data
Body:
  - เลือก form-data
  - เพิ่มไฟล์:
    Key: file1  Type: File  Value: [เลือกไฟล์ image1.jpg]
    Key: file2  Type: File  Value: [เลือกไฟล์ image2.png]

# 2. ทดสอบแบบ URL
Method: POST 
URL: https://google-vision-api.vercel.app/api/ocr/process-batch
Headers:
  Content-Type: application/json
Body (raw JSON):
{
    "images": [
        {
            "url": "https://example.com/image1.jpg",
            "filename": "image1.jpg"
        }
    ]
}

# 3. ทดสอบแบบ Base64
Method: POST
URL: https://google-vision-api.vercel.app/api/ocr/process-batch  
Headers:
  Content-Type: application/json
Body (raw JSON):
{
    "images": [
        {
            "image": "BASE64_STRING",
            "filename": "image1.jpg"
        }
    ]
}