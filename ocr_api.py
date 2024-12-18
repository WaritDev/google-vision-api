from http.server import BaseHTTPRequestHandler
import json
import cgi
from tokenize import endpats
import os
from vision_ocr_processor import VisionOCRProcessor

ocr_processor = VisionOCRProcessor()

class handler(BaseHTTPRequestHandler):
    SUPPORTED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
    MAX_IMAGES = 10
    MAX_FILE_SIZE = 10 * 1024 * 1024

    def check_file_size(self, file_data: bytes) -> bool:
        return len(file_data) <= self.MAX_FILE_SIZE

    def is_supported_format(self, filename: str) -> bool:
        return os.path.splitext(filename.lower())[1] in self.SUPPORTED_EXTENSIONS
    
    def process_image(self, image_bytes: bytes, filename: str) -> dict:
        return ocr_processor.process_image_bytes(image_bytes, filename)

    def send_json_response(self, data: dict, status_code: int = 200):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def process_form_data(self, form):
        results = []
        
        image_fields = []
        for key in form.keys():
            if key.startswith('images'):
                field = form[key]
                if isinstance(field, list):
                    image_fields.extend([f for f in field if hasattr(f, 'filename')])
                elif hasattr(field, 'filename'):
                    image_fields.append(field)
                    
        if len(image_fields) > self.MAX_IMAGES:
            return [{
                'status': 'error',
                'message': f'Maximum number of images exceeded. Limit is {self.MAX_IMAGES}'
            }]

        for field in image_fields:
            try:
                result = self.process_single_file(field)
                results.append(result)
            except Exception as e:
                results.append({
                    'filename': field.filename,
                    'status': 'error',
                    'message': str(e)
                })

        return results
    
    def process_single_file(self, field):
        print(f"Processing file: {field.filename}")
        print(f"Field type: {type(field)}")
        print(f"Content type: {field.type}")
        
        if not self.is_supported_format(field.filename):
            print(f"Unsupported format: {field.filename}")
            return {
                'filename': field.filename,
                'status': 'error',
                'message': 'Unsupported file format'
            }

        file_data = field.file.read()
        print(f"File size: {len(file_data)} bytes")

        result = self.process_image(file_data, field.filename)
        return {
            'filename': field.filename,
            'status': 'success',
            'data': result
        }

    def do_POST(self):
        if self.path != '/api/ocr/process-batch':
            return self.send_json_response({
                'status': 'error',
                'message': 'Invalid endpoint'
            }, 404)

        try:
            content_type = self.headers.get('Content-Type', '')
            
            if content_type.startswith('multipart/form-data'):
                form = cgi.FieldStorage(
                    fp=self.rfile,
                    headers=self.headers,
                    environ={'REQUEST_METHOD': 'POST'}
                )
                results = self.process_form_data(form)
                
                return self.send_json_response({
                    'status': 'success',
                    'results': results,
                    'message': f'Processed {len(results)} images'
                })
            else:
                content_length = int(self.headers.get('Content-Length', 0))
                post_data = json.loads(self.rfile.read(content_length).decode('utf-8'))
                results = self.process_json_data(post_data)
                
                return self.send_json_response({
                    'status': 'success',
                    'results': results,
                    'message': f'Processed {len(results)} images'
                })

        except Exception as e:
            return self.send_json_response({
                'status': 'error',
                'message': str(e)
            }, 500)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
