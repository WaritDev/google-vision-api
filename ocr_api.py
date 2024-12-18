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

    def process_form_data(self, form) -> list:
        results = []
        processed_count = 0
        
        image_fields = []
        for key in form.keys():
            if key.startswith('images['):
                image_fields.append(form[key])
        
        if len(image_fields) > self.MAX_IMAGES:
            return [{
                'status': 'error',
                'message': f'Maximum number of images exceeded. Limit is {self.MAX_IMAGES} images per request.'
            }]

        for field in image_fields:
            if not field.filename:
                continue

            filename = field.filename
            if not self.is_supported_format(filename):
                results.append({
                    'filename': filename,
                    'status': 'error',
                    'message': 'Unsupported file format'
                })
                continue

            try:
                file_data = field.file.read()
                if not self.check_file_size(file_data):
                    results.append({
                        'filename': filename,
                        'status': 'error',
                        'message': f'File size exceeds maximum limit of {self.MAX_FILE_SIZE/(1024*1024)}MB'
                    })
                    continue

                result = self.process_image(file_data, filename)
                results.append({
                    'filename': filename,
                    'status': 'success',
                    'data': result
                })
                processed_count += 1
            except Exception as e:
                results.append({
                    'filename': filename,
                    'status': 'error',
                    'message': str(e)
                })

        return results

    def do_POST(self):
        if self.path != '/api/ocr/process-batch':
            return self.send_json_response({'status': 'error', 'message': 'Invalid endpoint'}, 404)

        try:
            content_type = self.headers.get('Content-Type', '')
            
            if content_type.startswith('multipart/form-data'):
                form = cgi.FieldStorage(
                    fp=self.rfile,
                    headers=self.headers,
                    environ={'REQUEST_METHOD': 'POST'}
                )
                results = self.process_form_data(form)
                
                self.send_json_response({
                    'status': 'success',
                    'results': results,
                    'message': f'Processed {len(results)} images'
                })
            else:
                content_length = int(self.headers.get('Content-Length', 0))
                post_data = json.loads(self.rfile.read(content_length).decode('utf-8'))
                results = self.process_json_data(post_data)
                
                self.send_json_response({
                    'status': 'success',
                    'results': results,
                    'message': f'Processed {len(results)} images'
                })

        except Exception as e:
            self.send_json_response({
                'status': 'error',
                'message': str(e)
            }, 500)
        
        response_data = endpats.get(self.path, {
            'status': 'error',
            'message': 'Endpoint not found'
        })
        
        self.send_json_response(response_data, 404 if response_data['status'] == 'error' else 200)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
