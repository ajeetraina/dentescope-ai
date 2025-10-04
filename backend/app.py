from flask import Flask, request, jsonify
from flask_cors import CORS
from dental_width_analyzer import DentalWidthAnalyzer
import base64
import requests
from io import BytesIO
import cv2
import numpy as np
import os

app = Flask(__name__)
CORS(app)

# Use the downloaded model (change this after training)
MODEL_PATH = os.environ.get('MODEL_PATH', '../models/yolov8n.pt')
analyzer = DentalWidthAnalyzer(model_path=MODEL_PATH)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'model': MODEL_PATH})

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.json
        image_url = data.get('image_url')
        
        # Download image
        response = requests.get(image_url)
        image = cv2.imdecode(
            np.frombuffer(response.content, np.uint8), 
            cv2.IMREAD_COLOR
        )
        
        # Save temporarily
        temp_path = f'/tmp/{data.get("image_path", "temp.jpg")}'
        cv2.imwrite(temp_path, image)
        
        # Analyze
        results = analyzer.analyze(temp_path, output_path='/tmp/annotated.jpg')
        
        # Read annotated image and convert to base64
        with open('/tmp/annotated.jpg', 'rb') as f:
            annotated_base64 = base64.b64encode(f.read()).decode('utf-8')
        
        return jsonify({
            'results': results['results'],
            'total_pairs_detected': results['total_pairs_detected'],
            'annotated_image_base64': annotated_base64
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=True)
