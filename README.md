I'll guide you through using Postman to test your API step by step:

1. **First, start your API server:**
```bash
python -m uvicorn ocr_api:app --reload
```
You should see it running on `http://127.0.0.1:8000` or `http://localhost:8000`

2. **Open Postman and Create New Request:**
   1. Click "New" or "+" button
   2. Choose "HTTP Request"

3. **Test Health Check Endpoint (GET):**
   1. Select `GET` method from dropdown
   2. Enter URL: `http://localhost:8000/api/v1/health`
   3. Click "Send"
   ![Postman GET](https://i.imgur.com/example1.png)

4. **Test OCR Single Image (POST):**
   1. Select `POST` method
   2. Enter URL: `http://localhost:8000/api/v1/ocr/process-image`
   3. Go to "Body" tab
   4. Select "form-data"
   5. Add key "file"
   6. Click the dropdown on right side of "file" key and select "File"
   7. Upload an image file
   8. Click "Send"

Visual Guide for Single Image Upload:
```
┌─────────────────────────────────────────────┐
│ POST http://localhost:8000/api/v1/ocr/process-image
├─────────────────────────────────────────────┤
│ Body > form-data                            │
│ ┌─────┬─────────┬──────────────────────┐   │
│ │ KEY │ TYPE    │ VALUE                │   │
│ ├─────┼─────────┼──────────────────────┤   │
│ │file │ File 📎 │ [Select Files]       │   │
│ └─────┴─────────┴──────────────────────┘   │
└─────────────────────────────────────────────┘
```

5. **Test Multiple Images (POST):**
   1. Select `POST` method
   2. Enter URL: `http://localhost:8000/api/v1/ocr/process-batch`
   3. Go to "Body" tab
   4. Select "form-data"
   5. Add multiple keys named "files"
   6. Set each to File type
   7. Upload different images
   8. Click "Send"

Visual Guide for Multiple Images:
```
┌─────────────────────────────────────────────┐
│ POST http://localhost:8000/api/v1/ocr/process-batch
├─────────────────────────────────────────────┤
│ Body > form-data                            │
│ ┌──────┬─────────┬──────────────────────┐  │
│ │ KEY  │ TYPE    │ VALUE                │  │
│ ├──────┼─────────┼──────────────────────┤  │
│ │files │ File 📎 │ [image1.jpg]         │  │
│ │files │ File 📎 │ [image2.jpg]         │  │
│ └──────┴─────────┴──────────────────────┘  │
└─────────────────────────────────────────────┘
```

6. **Check Supported Formats (GET):**
   1. Select `GET` method
   2. Enter URL: `http://localhost:8000/api/v1/ocr/formats`
   3. Click "Send"

7. **View API Documentation:**
   - Open browser and go to: `http://localhost:8000/docs`
   - Or: `http://localhost:8000/redoc`

8. **Troubleshooting:**

If you get errors:
- Check Headers:
```
Accept: application/json
Content-Type: multipart/form-data
```

- Verify file types are supported
- Check file size isn't too large
- Ensure API server is running

9. **Save Requests:**
- Click "Save" button to save requests
- Create a collection for your OCR API
- Name requests meaningfully

10. **Example Collection Structure:**
```
OCR API Collection
├── Health Check (GET)
├── Process Single Image (POST)
├── Process Multiple Images (POST)
└── Get Supported Formats (GET)
```

Remember:
- Keep API server running while testing
- Use valid image files
- Check response codes and messages
- Images should be in supported formats (jpg, png, etc.)
