from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import numpy as np
import base64
from io import BytesIO
from PIL import Image

app = Flask(__name__)
CORS(app)

class ToothMeasurement:
    def __init__(self, mm_per_pixel=0.15, magnification=1.25):
        self.mm_per_pixel = mm_per_pixel
        self.magnification = magnification
    
    def calculate(self, points):
        """Calculate measurements from 4 points"""
        pm_width_px = np.sqrt((points[1][0] - points[0][0])**2 + (points[1][1] - points[0][1])**2)
        pr_width_px = np.sqrt((points[3][0] - points[2][0])**2 + (points[3][1] - points[2][1])**2)
        
        pm_width_mm = (pm_width_px * self.mm_per_pixel) / self.magnification
        pr_width_mm = (pr_width_px * self.mm_per_pixel) / self.magnification
        difference = pm_width_mm - pr_width_mm
        
        return {
            'primary_molar_width_mm': round(pm_width_mm, 2),
            'premolar_width_mm': round(pr_width_mm, 2),
            'difference_mm': round(abs(difference), 2),
            'within_normal_range': 2.0 <= abs(difference) <= 2.8
        }

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'mode': 'manual_selection'})

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.json
        points = data.get('points')  # [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
        
        if not points or len(points) != 4:
            return jsonify({'error': 'Need exactly 4 points'}), 400
        
        calculator = ToothMeasurement()
        results = calculator.calculate(points)
        
        return jsonify(results)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)
