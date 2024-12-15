from dotenv import load_dotenv
from google.cloud import vision
import os
import json
from datetime import datetime
import logging
from typing import List, Dict, Any
import io

class VisionOCRProcessor:
    def __init__(self):
        """
        Initialize Vision OCR Processor
        """
        # โหลด environment variables
        load_dotenv()
        
        # ตั้งค่า logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('ocr_process.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # สร้าง Vision client with API key
        try:
            self.client = vision.ImageAnnotatorClient()  # เปลี่ยนเป็นใช้ API Key จาก environment
            self.logger.info("Vision client initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize Vision client: {e}")
            raise

    def process_image(self, image_path: str) -> Dict[str, Any]:
        """ประมวลผลรูปภาพเดี่ยว"""
        self.logger.info(f"Processing image: {image_path}")
        
        try:
            # อ่านไฟล์รูปภาพ
            with io.open(image_path, 'rb') as image_file:
                content = image_file.read()
            image = vision.Image(content=content)
            
            # เรียกใช้ Vision API
            response = self.client.document_text_detection(image=image)
            
            # สร้างผลลัพธ์
            result = {
                'filename': os.path.basename(image_path),
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
            self.logger.error(f"Error processing image {image_path}: {e}")
            raise

    def process_directory(self, input_dir: str, output_dir: str) -> None:
        """ประมวลผลทุกรูปในโฟลเดอร์"""
        # สร้างโฟลเดอร์ output
        os.makedirs(output_dir, exist_ok=True)
        
        # นามสกุลไฟล์ที่รองรับ
        valid_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp')
        
        # หารูปภาพทั้งหมดในโฟลเดอร์
        image_files = [
            f for f in os.listdir(input_dir) 
            if f.lower().endswith(valid_extensions)
        ]
        
        total_files = len(image_files)
        self.logger.info(f"Found {total_files} images to process")
        
        # ประมวลผลแต่ละรูป
        for i, filename in enumerate(image_files, 1):
            image_path = os.path.join(input_dir, filename)
            output_path = os.path.join(
                output_dir,
                f"{os.path.splitext(filename)[0]}_ocr.json"
            )
            
            try:
                print(f"Processing {i}/{total_files}: {filename}")
                result = self.process_image(image_path)
                
                # บันทึก JSON
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
                
                print(f"Saved results to: {output_path}")
                
            except Exception as e:
                print(f"Error processing {filename}: {e}")
                continue

def main():
    # กำหนดโฟลเดอร์ input และ output
    input_dir = "images"  # โฟลเดอร์ที่มีรูปภาพ
    output_dir = "ocr_results"  # โฟลเดอร์เก็บผล JSON
    
    try:
        processor = VisionOCRProcessor()
        processor.process_directory(input_dir, output_dir)
        print("\nProcessing completed!")
        print(f"Results saved in: {output_dir}")
        
    except Exception as e:
        print(f"Error occurred: {e}")

if __name__ == "__main__":
    main()
