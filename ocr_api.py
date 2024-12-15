from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
from datetime import datetime
from typing import List
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vision_ocr_processor import VisionOCRProcessor

app = FastAPI(
    title="Vision OCR API",
    description="Custom API for processing images using Google Cloud Vision OCR",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OCR processor
try:
    ocr_processor = VisionOCRProcessor()
except Exception as e:
    print(f"Failed to initialize OCR processor: {e}")
    raise

@app.get("/")
async def root():
    """Root endpoint for Vercel"""
    return {"message": "Vision OCR API is running"}

@app.post("/api/ocr/process")
async def process_image(file: UploadFile = File(...)):
    """Process a single image file"""
    try:
        if not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Please upload an image file."
            )
        
        # Read file content
        content = await file.read()
        
        # Process image bytes directly
        result = await ocr_processor.process_image_bytes(content, file.filename)
        
        return JSONResponse(
            content={
                "status": "success",
                "data": result,
                "message": "Image processed successfully"
            },
            status_code=200
        )
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing image: {str(e)}"
        )

@app.get("/api/formats")
async def supported_formats():
    """Get supported image formats"""
    return {
        "status": "success",
        "data": {
            "supported_formats": [
                ".jpg",
                ".jpeg",
                ".png",
                ".gif",
                ".bmp",
                ".webp"
            ]
        }
    }

@app.get("/api/status")
async def service_status():
    """Get service status"""
    return {
        "status": "success",
        "data": {
            "service": "Vision OCR API",
            "version": "1.0.0",
            "status": "active",
            "timestamp": datetime.now().isoformat()
        }
    }

# Handler for Vercel
handler = Mangum(app)
