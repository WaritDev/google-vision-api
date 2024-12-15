import json
import os
import io
import logging
from datetime import datetime
from typing import Dict, Any
from google.cloud import vision
from google.oauth2 import service_account
from dotenv import load_dotenv

class VisionOCRProcessor:
    def __init__(self):
        """Initialize Vision OCR Processor"""
        load_dotenv()
        
        # ตั้งค่า logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # ดึง credentials จาก environment variable
        credentials_json = os.getenv('GOOGLE_CLOUD_CREDENTIALS')
        
        if not credentials_json:
            raise ValueError("GOOGLE_CLOUD_CREDENTIALS not found in environment variables")
            
        try:
            credentials_dict = json.loads(credentials_json)
            credentials = service_account.Credentials.from_service_account_info(
                credentials_dict
            )
            self.client = vision.ImageAnnotatorClient(credentials=credentials)
            self.logger.info("Vision client initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Vision client: {e}")
            raise

    async def process_image_bytes(self, image_bytes: bytes, filename: str) -> Dict[str, Any]:
        """Process image from bytes"""
        self.logger.info(f"Processing image: {filename}")
        
        try:
            image = vision.Image(content=image_bytes)
            response = self.client.document_text_detection(image=image)
            
            result = {
                'filename': filename,
                'timestamp': datetime.now().isoformat(),
                'text': response.full_text_annotation.text if response.full_text_annotation else '',
                'blocks': []
            }
            
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
