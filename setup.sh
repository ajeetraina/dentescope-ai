#!/bin/bash

# Dental Width Detection System - Complete Setup Script
# This script creates all necessary files and directory structure

set -e

echo "🦷 Setting up Dental Width Detection System..."
echo "================================================"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Create directory structure
echo -e "${BLUE}Creating directory structure...${NC}"
mkdir -p {backend,frontend/src/components,frontend/src/api,supabase/functions/analyze-dental,models,dataset/{images/{train,val,test},labels/{train,val,test}},scripts,docs}

# ============================================
# PYTHON BACKEND FILES
# ============================================

echo -e "${BLUE}Creating Python backend files...${NC}"

# Main analyzer class
cat > backend/dental_width_analyzer.py << 'EOF'
import cv2
import numpy as np
from ultralytics import YOLO
from typing import List, Dict, Tuple
import json

class DentalWidthAnalyzer:
    def __init__(self, model_path: str = 'models/best.pt'):
        """Initialize the Dental Width Analyzer"""
        self.model = YOLO(model_path)
        self.magnification_factor = 1.25
        self.mm_per_pixel = 0.12
        
        self.colors = {
            'primary_molar': (255, 0, 0),
            'premolar': (0, 255, 0),
            'measurement_line': (0, 0, 255),
            'text_bg': (200, 200, 200)
        }
    
    def preprocess_image(self, image_path: str) -> np.ndarray:
        """Enhanced preprocessing for panoramic radiographs"""
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(img)
        
        denoised = cv2.fastNlMeansDenoising(enhanced, None, h=10, 
                                            templateWindowSize=7, 
                                            searchWindowSize=21)
        
        normalized = cv2.normalize(denoised, None, 0, 255, cv2.NORM_MINMAX)
        rgb_image = cv2.cvtColor(normalized, cv2.COLOR_GRAY2RGB)
        
        return rgb_image
    
    def detect_teeth(self, image: np.ndarray, conf_threshold: float = 0.25) -> List[Dict]:
        """Detect teeth in the image"""
        results = self.model.predict(
            image,
            conf=conf_threshold,
            iou=0.45,
            imgsz=640,
            verbose=False
        )
        
        detections = []
        for r in results:
            boxes = r.boxes
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                conf = float(box.conf[0].cpu().numpy())
                cls = int(box.cls[0].cpu().numpy())
                class_name = self.model.names[cls]
                
                detections.append({
                    'bbox': [int(x1), int(y1), int(x2), int(y2)],
                    'confidence': conf,
                    'class_id': cls,
                    'class_name': class_name
                })
        
        return detections
    
    def measure_width(self, bbox: List[int]) -> float:
        """Calculate mesiodistal width with magnification correction"""
        x1, y1, x2, y2 = bbox
        pixel_width = x2 - x1
        width_mm = (pixel_width * self.mm_per_pixel) / self.magnification_factor
        return width_mm
    
    def categorize_teeth(self, detections: List[Dict]) -> Dict:
        """Separate primary molars and premolars"""
        categories = {
            'primary_molars': [],
            'premolars': []
        }
        
        for det in detections:
            if any(term in det['class_name'].lower() for term in ['primary', 'deciduous', 'e', 'j']):
                categories['primary_molars'].append(det)
            elif any(term in det['class_name'].lower() for term in ['premolar', 'bicuspid']):
                categories['premolars'].append(det)
        
        return categories
    
    def match_pairs(self, primary_molars: List[Dict], premolars: List[Dict]) -> List[Tuple]:
        """Match primary molars with their corresponding premolars"""
        pairs = []
        
        for pm in primary_molars:
            pm_center_x = (pm['bbox'][0] + pm['bbox'][2]) / 2
            pm_center_y = (pm['bbox'][1] + pm['bbox'][3]) / 2
            
            min_dist = float('inf')
            best_match = None
            
            for pr in premolars:
                pr_center_x = (pr['bbox'][0] + pr['bbox'][2]) / 2
                pr_center_y = (pr['bbox'][1] + pr['bbox'][3]) / 2
                
                dist = np.sqrt((pm_center_x - pr_center_x)**2 + 
                             (pm_center_y - pr_center_y)**2)
                
                if dist < min_dist:
                    min_dist = dist
                    best_match = pr
            
            if best_match:
                pairs.append((pm, best_match))
        
        return pairs
    
    def draw_annotations(self, image: np.ndarray, pair: Tuple, difference: float) -> np.ndarray:
        """Draw annotations like the example image"""
        annotated = image.copy()
        primary_molar, premolar = pair
        
        pm_bbox = primary_molar['bbox']
        cv2.rectangle(annotated, 
                     (pm_bbox[0], pm_bbox[1]), 
                     (pm_bbox[2], pm_bbox[3]), 
                     self.colors['primary_molar'], 3)
        
        pr_bbox = premolar['bbox']
        cv2.rectangle(annotated, 
                     (pr_bbox[0], pr_bbox[1]), 
                     (pr_bbox[2], pr_bbox[3]), 
                     self.colors['premolar'], 3)
        
        pm_center_y = (pm_bbox[1] + pm_bbox[3]) // 2
        pm_center_x = (pm_bbox[0] + pm_bbox[2]) // 2
        cv2.circle(annotated, (pm_center_x, pm_center_y + 100), 40, 
                  self.colors['measurement_line'], 3)
        
        pr_center_y = (pr_bbox[1] + pr_bbox[3]) // 2
        pr_center_x = (pr_bbox[0] + pr_bbox[2]) // 2
        cv2.circle(annotated, (pr_center_x, pr_center_y + 100), 40, 
                  self.colors['measurement_line'], 3)
        
        line_y = min(pm_bbox[1], pr_bbox[1]) + 50
        cv2.line(annotated, 
                (pm_center_x, line_y), 
                (pr_center_x, line_y), 
                self.colors['measurement_line'], 2)
        
        mid_x = (pm_center_x + pr_center_x) // 2
        text = f"Delta {difference:.2f}mm"
        
        (text_w, text_h), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)
        cv2.rectangle(annotated, 
                     (mid_x - text_w//2 - 10, line_y - text_h - 20),
                     (mid_x + text_w//2 + 10, line_y - 5),
                     self.colors['text_bg'], -1)
        
        cv2.putText(annotated, text, 
                   (mid_x - text_w//2, line_y - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, 
                   self.colors['measurement_line'], 2)
        
        return annotated
    
    def analyze(self, image_path: str, output_path: str = 'result.jpg') -> Dict:
        """Complete analysis pipeline"""
        processed_image = self.preprocess_image(image_path)
        original_image = cv2.imread(image_path)
        
        detections = self.detect_teeth(processed_image)
        categories = self.categorize_teeth(detections)
        pairs = self.match_pairs(
            categories['primary_molars'],
            categories['premolars']
        )
        
        results = []
        annotated_image = original_image.copy()
        
        for primary_molar, premolar in pairs:
            pm_width = self.measure_width(primary_molar['bbox'])
            pr_width = self.measure_width(premolar['bbox'])
            difference = pm_width - pr_width
            
            annotated_image = self.draw_annotations(
                annotated_image,
                (primary_molar, premolar),
                difference
            )
            
            results.append({
                'primary_molar': {
                    'class': primary_molar['class_name'],
                    'width_mm': round(pm_width, 2),
                    'confidence': round(primary_molar['confidence'], 2)
                },
                'premolar': {
                    'class': premolar['class_name'],
                    'width_mm': round(pr_width, 2),
                    'confidence': round(premolar['confidence'], 2)
                },
                'difference_mm': round(difference, 2),
                'within_normal_range': 2.0 <= difference <= 2.8
            })
        
        cv2.imwrite(output_path, annotated_image)
        
        return {
            'results': results,
            'output_image': output_path,
            'total_pairs_detected': len(results)
        }
EOF

# Flask API
cat > backend/app.py << 'EOF'
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

analyzer = DentalWidthAnalyzer(model_path='models/best.pt')

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy'})

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
    app.run(host='0.0.0.0', port=port)
EOF

# Requirements
cat > backend/requirements.txt << 'EOF'
flask==3.0.0
flask-cors==4.0.0
opencv-python==4.8.1.78
numpy==1.24.3
ultralytics==8.0.200
torch==2.1.0
torchvision==0.16.0
requests==2.31.0
pillow==10.1.0
EOF

# Dockerfile
cat > backend/Dockerfile << 'EOF'
FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "app.py"]
EOF

# ============================================
# FRONTEND FILES
# ============================================

echo -e "${BLUE}Creating frontend files...${NC}"

# React Component
cat > frontend/src/components/DentalAnalyzer.tsx << 'EOF'
import React, { useState } from 'react';
import { Upload, Activity, CheckCircle, AlertTriangle, Download } from 'lucide-react';

export default function DentalAnalyzer() {
  const [image, setImage] = useState<string | null>(null);
  const [results, setResults] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [annotatedImage, setAnnotatedImage] = useState<string | null>(null);

  const handleImageUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setImage(URL.createObjectURL(file));
    setError(null);
    setResults(null);
    setAnnotatedImage(null);

    await analyzeImage(file);
  };

  const analyzeImage = async (file: File) => {
    setLoading(true);
    
    try {
      const formData = new FormData();
      formData.append('image', file);

      const response = await fetch('/api/analyze-dental', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) throw new Error('Analysis failed');

      const data = await response.json();
      setResults(data.results);
      setAnnotatedImage(data.annotated_image_url);
    } catch (err: any) {
      setError(err.message || 'Failed to analyze image');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-12">
          <div className="inline-flex items-center gap-3 bg-blue-600 text-white px-6 py-3 rounded-full mb-4">
            <Activity className="w-6 h-6" />
            <h1 className="text-2xl font-bold">Adaptive Dental Analysis</h1>
          </div>
          <p className="text-gray-600 max-w-2xl mx-auto">
            AI-powered tool for measuring tooth width differences
          </p>
        </div>

        <div className="bg-white rounded-2xl shadow-xl p-8 mb-8">
          <label className="flex flex-col items-center justify-center w-full h-64 border-2 border-dashed border-gray-300 rounded-xl cursor-pointer hover:border-blue-500 hover:bg-blue-50 transition-all">
            <div className="flex flex-col items-center justify-center pt-5 pb-6">
              <Upload className="w-16 h-16 text-gray-400 mb-4" />
              <p className="mb-2 text-xl font-semibold text-gray-700">
                Upload Panoramic Radiograph
              </p>
              <p className="text-sm text-gray-500">PNG, JPG (MAX. 10MB)</p>
            </div>
            <input
              type="file"
              className="hidden"
              accept="image/*"
              onChange={handleImageUpload}
            />
          </label>
        </div>

        {loading && (
          <div className="bg-white rounded-2xl shadow-xl p-12 text-center">
            <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600 text-lg">Analyzing radiograph...</p>
          </div>
        )}

        {error && (
          <div className="bg-red-50 border-l-4 border-red-500 rounded-lg p-6 mb-8">
            <div className="flex items-center gap-3">
              <AlertTriangle className="w-6 h-6 text-red-600" />
              <div>
                <h3 className="font-semibold text-red-900">Analysis Failed</h3>
                <p className="text-red-700">{error}</p>
              </div>
            </div>
          </div>
        )}

        {results && annotatedImage && (
          <div className="space-y-8">
            <div className="bg-white rounded-2xl shadow-xl overflow-hidden">
              <div className="bg-gradient-to-r from-blue-600 to-indigo-600 p-6 text-white">
                <h2 className="text-2xl font-bold">Analysis Results</h2>
              </div>
              <div className="p-6">
                <img src={annotatedImage} alt="Annotated" className="w-full rounded-lg" />
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
EOF

# API utility
cat > frontend/src/api/dental.ts << 'EOF'
export async function analyzeDental(file: File) {
  const formData = new FormData();
  formData.append('image', file);

  const response = await fetch('/api/analyze-dental', {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    throw new Error('Analysis failed');
  }

  return response.json();
}
EOF

# ============================================
# SUPABASE EDGE FUNCTION
# ============================================

echo -e "${BLUE}Creating Supabase edge function...${NC}"

cat > supabase/functions/analyze-dental/index.ts << 'EOF'
import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    const formData = await req.formData()
    const imageFile = formData.get('image') as File

    if (!imageFile) {
      throw new Error('No image file provided')
    }

    const supabaseUrl = Deno.env.get('SUPABASE_URL')!
    const supabaseKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
    const supabase = createClient(supabaseUrl, supabaseKey)

    const fileName = `${crypto.randomUUID()}.jpg`
    const { data: uploadData, error: uploadError } = await supabase.storage
      .from('dental-images')
      .upload(fileName, imageFile)

    if (uploadError) throw uploadError

    const { data: { publicUrl } } = supabase.storage
      .from('dental-images')
      .getPublicUrl(fileName)

    const pythonBackendUrl = Deno.env.get('PYTHON_BACKEND_URL')!
    
    const analysisResponse = await fetch(pythonBackendUrl + '/analyze', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        image_url: publicUrl,
        image_path: fileName
      })
    })

    if (!analysisResponse.ok) {
      throw new Error('Analysis failed')
    }

    const analysisResults = await analysisResponse.json()

    if (analysisResults.annotated_image_base64) {
      const annotatedFileName = `annotated_${fileName}`
      const byteCharacters = atob(analysisResults.annotated_image_base64)
      const byteNumbers = new Array(byteCharacters.length)
      
      for (let i = 0; i < byteCharacters.length; i++) {
        byteNumbers[i] = byteCharacters.charCodeAt(i)
      }
      
      const byteArray = new Uint8Array(byteNumbers)
      const blob = new Blob([byteArray], { type: 'image/jpeg' })
      
      const { data: annotatedUpload, error: annotatedError } = await supabase.storage
        .from('dental-images')
        .upload(annotatedFileName, blob)

      if (annotatedError) throw annotatedError

      const { data: { publicUrl: annotatedUrl } } = supabase.storage
        .from('dental-images')
        .getPublicUrl(annotatedFileName)

      analysisResults.annotated_image_url = annotatedUrl
    }

    return new Response(
      JSON.stringify(analysisResults),
      { 
        headers: { 
          ...corsHeaders,
          'Content-Type': 'application/json' 
        } 
      }
    )

  } catch (error: any) {
    return new Response(
      JSON.stringify({ error: error.message }),
      { 
        status: 500,
        headers: { 
          ...corsHeaders,
          'Content-Type': 'application/json' 
        } 
      }
    )
  }
})
EOF

# ============================================
# CONFIGURATION FILES
# ============================================

echo -e "${BLUE}Creating configuration files...${NC}"

# YOLO data config
cat > dataset/data.yaml << 'EOF'
path: ./dataset
train: images/train
val: images/val
test: images/test

nc: 8
names:
  0: primary_second_molar_upper_right
  1: primary_second_molar_upper_left
  2: primary_second_molar_lower_left
  3: primary_second_molar_lower_right
  4: second_premolar_upper_right
  5: second_premolar_upper_left
  6: second_premolar_lower_left
  7: second_premolar_lower_right
EOF

# Training script
cat > scripts/train_model.py << 'EOF'
from ultralytics import YOLO

def train():
    model = YOLO('yolov8n.pt')
    
    results = model.train(
        data='dataset/data.yaml',
        epochs=100,
        imgsz=640,
        batch=16,
        device='0',
        patience=20,
        save=True,
        project='runs/train',
        name='dental_detection',
        hsv_h=0.015,
        hsv_s=0.7,
        hsv_v=0.4,
        degrees=10,
        translate=0.1,
        scale=0.5,
        flipud=0.0,
        fliplr=0.5,
        mosaic=1.0,
    )
    
    print("Training complete!")
    print(f"Best model saved to: {results.save_dir}")

if __name__ == '__main__':
    train()
EOF

# Environment template
cat > .env.example << 'EOF'
# Supabase
SUPABASE_URL=your-supabase-url
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
SUPABASE_ANON_KEY=your-anon-key

# Python Backend
PYTHON_BACKEND_URL=http://localhost:8000

# Model
MODEL_PATH=models/best.pt
EOF

# Package.json
cat > frontend/package.json << 'EOF'
{
  "name": "dental-width-predictor",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "lucide-react": "^0.263.1",
    "@supabase/supabase-js": "^2.38.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.43",
    "@types/react-dom": "^18.2.17",
    "@vitejs/plugin-react": "^4.2.1",
    "typescript": "^5.2.2",
    "vite": "^5.0.8",
    "tailwindcss": "^3.3.0",
    "autoprefixer": "^10.4.16",
    "postcss": "^8.4.32"
  }
}
EOF

# Tailwind config
cat > frontend/tailwind.config.js << 'EOF'
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
EOF

# README
cat > README.md << 'EOF'
# Dental Width Detection System

AI-powered tool for measuring tooth width differences between primary second molars and second premolars in dental panoramic radiographs.

## Features

- 🦷 Automatic tooth detection using YOLOv8
- 📏 Precise width measurements with magnification correction
- 🎨 Visual annotations matching clinical standards
- 📊 Clinical insights and recommendations
- ⚡ Real-time processing

## Setup

### 1. Backend (Python)

```bash
cd backend
pip install -r requirements.txt
python app.py
```

### 2. Frontend (React)

```bash
cd frontend
npm install
npm run dev
```

### 3. Train Model

```bash
# Prepare your dataset in dataset/ folder
python scripts/train_model.py
```

### 4. Deploy

- Backend: Deploy to Render/Railway using Dockerfile
- Frontend: Deploy to Vercel
- Supabase: Deploy edge function

## Configuration

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

## Usage

1. Upload a panoramic radiograph
2. System automatically detects teeth
3. Measures widths and calculates differences
4. Displays annotated results

## Expected Results

- Primary Second Molar Width: 9-10mm
- Second Premolar Width: 7-8mm
- Width Difference: 2.0-2.8mm (normal range)

## License

MIT
EOF

# Deployment scripts
cat > scripts/deploy_backend.sh << 'EOF'
#!/bin/bash

echo "Deploying Python Backend..."

# Build Docker image
docker build -t dental-backend ./backend

# Tag for registry
docker tag dental-backend your-registry/dental-backend:latest

# Push to registry
docker push your-registry/dental-backend:latest

echo "Backend deployed!"
EOF

chmod +x scripts/deploy_backend.sh

cat > scripts/deploy_frontend.sh << 'EOF'
#!/bin/bash

echo "Deploying Frontend to Vercel..."

cd frontend
npm install
npm run build
vercel --prod

echo "Frontend deployed!"
EOF

chmod +x scripts/deploy_frontend.sh

# ============================================
# DOCUMENTATION
# ============================================

cat > docs/TRAINING_GUIDE.md << 'EOF'
# Model Training Guide

## Dataset Preparation

1. **Collect Images**: Gather panoramic radiographs
2. **Annotate**: Use LabelImg or Roboflow
3. **Organize**: Place in dataset/ following structure

## Training

```bash
python scripts/train_model.py
```

## Evaluation

Monitor training with:
- mAP (should be > 0.95)
- Precision/Recall (should be > 0.95)
- Loss curves

## Tips

- Use at least 500 images per class
- Balance dataset across all tooth types
- Apply data augmentation
- Train for 100+ epochs
EOF

cat > docs/API_REFERENCE.md << 'EOF'
# API Reference

## Analyze Endpoint

**POST** `/analyze`

### Request

```json
{
  "image_url": "https://...",
  "image_path": "filename.jpg"
}
```

### Response

```json
{
  "results": [
    {
      "primary_molar": {
        "class": "primary_second_molar_upper_right",
        "width_mm": 10.24,
        "confidence": 0.95
      },
      "premolar": {
        "class": "second_premolar_upper_right",
        "width_mm": 8.14,
        "confidence": 0.93
      },
      "difference_mm": 2.10,
      "within_normal_range": true
    }
  ],
  "total_pairs_detected": 1,
  "annotated_image_base64": "..."
}
```
EOF

# ============================================
# FINAL STEPS
# ============================================

echo -e "${GREEN}✅ Setup complete!${NC}"
echo ""
echo "📁 Directory structure created:"
tree -L 2 2>/dev/null || find . -maxdepth 2 -type d

echo ""
echo "📋 Next Steps:"
echo "1. cd backend && pip install -r requirements.txt"
echo "2. cd frontend && npm install"
echo "3. Prepare your dataset in dataset/ folder"
echo "4. python scripts/train_model.py"
echo "5. Configure .env file"
echo "6. python backend/app.py (start backend)"
echo "7. cd frontend && npm run dev (start frontend)"
echo ""
echo "📚 Documentation created in docs/"
echo "🚀 Deploy scripts available in scripts/"
echo ""
echo -e "${GREEN}Happy coding! 🦷${NC}"
EOF

chmod +x setup_dental_system.sh

echo -e "${GREEN}✅ Script created successfully!${NC}"
echo ""
echo "To setup your project, run:"
echo ""
echo "  chmod +x setup_dental_system.sh"
echo "  ./setup_dental_system.sh"
echo ""
echo "This will create all files and folders for your dental detection system!"
