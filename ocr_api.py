from datetime import datetime  # Add this for datetime
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from typing import List
import tempfile
import os
from pathlib import Path

# Import the VisionOCRProcessor class
from vision_ocr_processor import VisionOCRProcessor

app = FastAPI(
    title="Vision OCR API",
    description="Custom API for processing images using Google Cloud Vision OCR",
    version="1.0.0"
)

# Configure CORS
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# เพิ่ม CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ต้องมี route นี้สำหรับ Vercel
@app.get("/")
async def root():
    return {"message": "Hello World"}

# Initialize OCR processor
try:
    ocr_processor = VisionOCRProcessor()
except Exception as e:
    print(f"Failed to initialize OCR processor: {e}")
    raise

# Custom URL paths
API_V1_PREFIX = "/api/v1"
OCR_PREFIX = f"{API_V1_PREFIX}/ocr"

@app.get(f"{API_V1_PREFIX}/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "active",
        "service": "Vision OCR API",
        "version": "1.0.0"
    }

@app.post(f"{OCR_PREFIX}/process-image")
async def process_single_image(file: UploadFile = File(...)):
    """
    Process a single image file
    """
    try:
        if not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Please upload an image file."
            )
        
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_path = temp_file.name
        
        try:
            result = ocr_processor.process_image(temp_path)
            return JSONResponse(
                content={
                    "status": "success",
                    "data": result,
                    "message": "Image processed successfully"
                },
                status_code=200
            )
            
        finally:
            os.unlink(temp_path)
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing image: {str(e)}"
        )

@app.post(f"{OCR_PREFIX}/process-batch")
async def process_multiple_images(files: List[UploadFile] = File(...)):
    """
    Process multiple image files
    """
    try:
        results = []
        temp_files = []
        
        for file in files:
            if not file.content_type.startswith('image/'):
                continue
            
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                content = await file.read()
                temp_file.write(content)
                temp_files.append(temp_file.name)
        
        try:
            for temp_path in temp_files:
                result = ocr_processor.process_image(temp_path)
                results.append(result)
            
            return JSONResponse(
                content={
                    "status": "success",
                    "data": {
                        "total_processed": len(results),
                        "results": results
                    },
                    "message": "Batch processing completed"
                },
                status_code=200
            )
            
        finally:
            for temp_path in temp_files:
                try:
                    os.unlink(temp_path)
                except:
                    pass
                    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing images: {str(e)}"
        )

@app.get(f"{OCR_PREFIX}/formats")
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

@app.get(f"{API_V1_PREFIX}/status")
async def service_status():
    """Get detailed service status"""
    return {
        "status": "success",
        "data": {
            "service": "Vision OCR API",
            "version": "1.0.0",
            "status": "active",
            "timestamp": datetime.now().isoformat()
        }
    }

def start_server(host="0.0.0.0", port=8000):
    """Start the FastAPI server"""
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True
    )

if __name__ == "__main__":
    start_server()
