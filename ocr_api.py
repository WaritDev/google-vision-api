from http.server import BaseHTTPRequestHandler
import json
from vision_ocr_processor import VisionOCRProcessor
import base64
import cgi
import urllib.request
import os
import mimetypes

# Initialize OCR processor globally
ocr_processor = VisionOCRProcessor()

class handler(BaseHTTPRequestHandler):
    SUPPORTED_FORMATS = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
    
    def is_supported_format(self, filename):
        ext = os.path.splitext(filename)[1].lower()
        return ext in self.SUPPORTED_FORMATS
    
    def get_image_from_url(self, url):
        try:
            with urllib.request.urlopen(url) as response:
                content_type = response.headers.get('Content-Type', '')
                if not content_type.startswith('image/'):
                    raise ValueError("URL does not point to an image")
                
                ext = mimetypes.guess_extension(content_type)
                if ext not in self.SUPPORTED_FORMATS:
                    raise ValueError(f"Image format {ext} not supported")
                
                return response.read()
        except Exception as e:
            raise ValueError(f"Failed to fetch image from URL: {str(e)}")

    def do_POST(self):
        if self.path == '/api/ocr/process-batch':
            try:
                # Check if the request is multipart/form-data
                content_type = self.headers.get('Content-Type', '')
                
                results = []
                
                if content_type.startswith('multipart/form-data'):
                    # Handle form-data
                    form = cgi.FieldStorage(
                        fp=self.rfile,
                        headers=self.headers,
                        environ={'REQUEST_METHOD': 'POST'}
                    )
                    
                    # Process uploaded files
                    for field in form.keys():
                        if form[field].filename:
                            filename = form[field].filename
                            if not self.is_supported_format(filename):
                                results.append({
                                    'filename': filename,
                                    'status': 'error',
                                    'message': f'Unsupported file format'
                                })
                                continue
                            
                            file_data = form[field].file.read()
                            result = ocr_processor.process_image_bytes(file_data, filename)
                            results.append({
                                'filename': filename,
                                'status': 'success',
                                'data': result
                            })
                
                else:
                    # Handle JSON request (base64 images or URLs)
                    content_length = int(self.headers.get('Content-Length', 0))
                    post_data = self.rfile.read(content_length)
                    data = json.loads(post_data.decode('utf-8'))
                    
                    if 'images' not in data:
                        raise ValueError("No images data provided")
                    
                    for image_data in data['images']:
                        try:
                            filename = image_data.get('filename', 'uploaded_image')
                            
                            if 'url' in image_data:
                                # Process image URL
                                image_bytes = self.get_image_from_url(image_data['url'])
                            elif 'image' in image_data:
                                # Process base64 image
                                image_bytes = base64.b64decode(image_data['image'])
                            else:
                                raise ValueError("No image data or URL provided")
                            
                            result = ocr_processor.process_image_bytes(image_bytes, filename)
                            results.append({
                                'filename': filename,
                                'status': 'success',
                                'data': result
                            })
                        except Exception as img_error:
                            results.append({
                                'filename': filename,
                                'status': 'error',
                                'message': str(img_error)
                            })
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                response = json.dumps({
                    'status': 'success',
                    'data': results,
                    'message': f'Processed {len(results)} images'
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
