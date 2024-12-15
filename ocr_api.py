from http.server import BaseHTTPRequestHandler
import json
import base64
import cgi
import urllib.request
import os
from vision_ocr_processor import VisionOCRProcessor

ocr_processor = VisionOCRProcessor()

class handler(BaseHTTPRequestHandler):
    SUPPORTED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff', '.tif', '.pdf'}

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
        for field in form.keys():
            if not form[field].filename:
                continue

            filename = form[field].filename
            if not self.is_supported_format(filename):
                results.append({
                    'filename': filename,
                    'status': 'error',
                    'message': 'Unsupported file format'
                })
                continue

            try:
                file_data = form[field].file.read()
                result = self.process_image(file_data, filename)
                results.append({
                    'filename': filename,
                    'status': 'success',
                    'data': result
                })
            except Exception as e:
                results.append({
                    'filename': filename,
                    'status': 'error',
                    'message': str(e)
                })
        return results

    def process_json_data(self, data: dict) -> list:
        results = []
        for image_data in data.get('images', []):
            filename = image_data.get('filename', 'uploaded_image')
            try:
                if 'url' in image_data:
                    with urllib.request.urlopen(image_data['url']) as response:
                        image_bytes = response.read()
                elif 'image' in image_data:
                    image_bytes = base64.b64decode(image_data['image'])
                else:
                    raise ValueError("No image data or URL provided")

                result = self.process_image(image_bytes, filename)
                results.append({
                    'filename': filename,
                    'status': 'success',
                    'data': result
                })
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
            else:
                content_length = int(self.headers.get('Content-Length', 0))
                post_data = json.loads(self.rfile.read(content_length).decode('utf-8'))
                results = self.process_json_data(post_data)

            self.send_json_response({
                'status': 'success',
                'data': results,
                'message': f'Processed {len(results)} images'
            })

        except Exception as e:
            self.send_json_response({
                'status': 'error',
                'message': str(e)
            }, 500)

    def do_GET(self):
        endpoints = {
            '/api/status': {
                'status': 'success',
                'data': {
                    'service': 'Vision OCR API',
                    'version': '1.0.0',
                    'status': 'active'
                }
            },
            '/api/formats': {
                'status': 'success',
                'data': {
                    'supported_formats': list(self.SUPPORTED_EXTENSIONS)
                }
            }
        }
        
        response_data = endpoints.get(self.path, {
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
