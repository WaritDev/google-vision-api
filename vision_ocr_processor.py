from dotenv import load_dotenv
from google.cloud import vision
from google.oauth2 import service_account
import os
import json
from datetime import datetime
import logging
from typing import List, Dict, Any
import io
import sys

class VisionOCRProcessor:
    def __init__(self):
        """
        Initialize Vision OCR Processor
        """
        # โหลด environment variables
        load_dotenv()
        
        # ตั้งค่า logging ใหม่ให้ใช้แค่ StreamHandler
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # สร้าง Vision client
        try:
            if os.getenv('VERCEL'):
                # สำหรับ Vercel environment
                credentials_json = os.getenv('GOOGLE_CLOUD_CREDENTIALS')
                if not credentials_json:
                    raise ValueError("Missing GOOGLE_CLOUD_CREDENTIALS")
                
                credentials_dict = json.loads(credentials_json)
                credentials = service_account.Credentials.from_service_account_info(credentials_dict)
                self.client = vision.ImageAnnotatorClient(credentials=credentials)
            else:
                # สำหรับ local development
                self.client = vision.ImageAnnotatorClient()
            
            self.logger.info("Vision client initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize Vision client: {e}")
            raise

    async def process_image_bytes(self, image_bytes: bytes, filename: str = "uploaded_image") -> Dict[str, Any]:
        """ประมวลผลรูปภาพจาก bytes (สำหรับ API endpoint)"""
        self.logger.info(f"Processing image: {filename}")
        
        try:
            # สร้าง Vision Image object จาก bytes
            image = vision.Image(content=image_bytes)
            
            # เรียกใช้ Vision API
            response = self.client.document_text_detection(image=image)
            
            # สร้างผลลัพธ์
            result = {
                'filename': filename,
                'timestamp': datetime.now().isoformat(),
                'text': response.full_text_annotation.text if response.full_text_annotation else '',
                'blocks': []
            }
            
            # ดึงข้อมูลแต่ละ block
            if response.full_text_annotation:
                for page in response.full_text_annotation.pages:
                    for block in page.blocks:
                        block_info = {
                            'text': '',
                            'confidence': block.confidence,
                            'bounds': {
                                'x1': block.bounding_box.vertices[0].x,
                                'y1': block.bounding_box.vertices[0].y,
                                'x2': block.bounding_box.vertices[2].x,
                                'y2': block.bounding_box.vertices[2].y
                            }
                        }
                        
                        # รวมข้อความใน block
                        words = []
                        for paragraph in block.paragraphs:
                            for word in paragraph.words:
                                word_text = ''.join([
                                    symbol.text for symbol in word.symbols
                                ])
                                words.append(word_text)
                        block_info['text'] = ' '.join(words)
                        
                        result['blocks'].append(block_info)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error processing image {filename}: {e}")
            raise
