from google.cloud import vision
from google.oauth2 import service_account
import os
import json
import logging
from typing import Dict, Any
from datetime import datetime

class VisionOCRProcessor:
    def __init__(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        self.client = self._initialize_client()

    def _initialize_client(self) -> vision.ImageAnnotatorClient:
        try:
            if os.getenv('VERCEL'):
                credentials_json = os.getenv('GOOGLE_CLOUD_CREDENTIALS')
                if not credentials_json:
                    raise ValueError("Missing GOOGLE_CLOUD_CREDENTIALS")
                
                credentials = service_account.Credentials.from_service_account_info(
                    json.loads(credentials_json)
                )
                return vision.ImageAnnotatorClient(credentials=credentials)
            return vision.ImageAnnotatorClient()
            
        except Exception as e:
            self.logger.error(f"Vision client initialization failed: {e}")
            raise

    def _extract_block_info(self, block) -> Dict[str, Any]:
        return {
            'text': ' '.join([
                ''.join([symbol.text for symbol in word.symbols])
                for paragraph in block.paragraphs
                for word in paragraph.words
            ]),
            'confidence': block.confidence,
            'bounds': {
                'x1': block.bounding_box.vertices[0].x,
                'y1': block.bounding_box.vertices[0].y,
                'x2': block.bounding_box.vertices[2].x,
                'y2': block.bounding_box.vertices[2].y
            }
        }

    def process_image_bytes(self, image_bytes: bytes, filename: str = "uploaded_image") -> Dict[str, Any]:
        self.logger.info(f"Processing image: {filename}")
        
        try:
            response = self.client.document_text_detection(
                image=vision.Image(content=image_bytes)
            )
            
            full_text = response.full_text_annotation
            result = {
                'filename': filename,
                'timestamp': datetime.now().isoformat(),
                'text': full_text.text if full_text else '',
                'blocks': []
            }
            
            if full_text:
                result['blocks'] = [
                    self._extract_block_info(block)
                    for page in full_text.pages
                    for block in page.blocks
                ]
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error processing {filename}: {e}")
            raise
