from http.server import BaseHTTPRequestHandler
import json
from vision_ocr_processor import VisionOCRProcessor
import base64

# Initialize OCR processor globally
ocr_processor = VisionOCRProcessor()

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/api/ocr/process':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode('utf-8'))
                
                if 'image' not in data:
                    raise ValueError("No image data provided")
                    
                image_bytes = base64.b64decode(data['image'])
                filename = data.get('filename', 'uploaded_image')
                
                result = ocr_processor.process_image_bytes(image_bytes, filename)
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                response = json.dumps({
                    'status': 'success',
                    'data': result,
                    'message': 'Image processed successfully'
                }).encode('utf-8')
                self.wfile.write(response)
                
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                error_response = json.dumps({
                    'status': 'error',
                    'message': str(e)
                }).encode('utf-8')
                self.wfile.write(error_response)

    def do_GET(self):
        if self.path == '/api/status':
            response_data = {
                'status': 'success',
                'data': {
                    'service': 'Vision OCR API',
                    'version': '1.0.0',
                    'status': 'active'
                }
            }
        elif self.path == '/api/formats':
            response_data = {
                'status': 'success',
                'data': {
                    'supported_formats': [
                        '.jpg',
                        '.jpeg',
                        '.png',
                        '.gif',
                        '.bmp',
                        '.webp'
                    ]
                }
            }
        else:
            response_data = {
                'message': 'Vision OCR API is running'
            }

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = json.dumps(response_data).encode('utf-8')
        self.wfile.write(response)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
