#!/usr/bin/env python3
"""
Test Pre-trained Dental Model on Your Images
"""

from roboflow import Roboflow
import cv2
from pathlib import Path
import json

# Configuration
API_KEY = "40NFqXXXXXxmjww"  # Get from Roboflow dashboard
WORKSPACE = "https://universe.roboflow.com/codebase-szuhc"    # From model URL
PROJECT = "panoramic-xray-mk1hj"        # From model URL
VERSION = 1                     # Model version

# Your images
IMAGES_DIR = "backend/dataset/images/train"
OUTPUT_DIR = "pretrained_predictions"

def test_model():
    """Test model on your dental X-rays"""

    # Initialize
    rf = Roboflow(api_key=API_KEY)
    project = rf.workspace(WORKSPACE).project(PROJECT)
    model = project.version(VERSION).model

    # Create output directory
    Path(OUTPUT_DIR).mkdir(exist_ok=True)

    # Get images
    images_dir = Path(IMAGES_DIR)
    image_files = list(images_dir.glob("*.jpg")) + list(images_dir.glob("*.png"))

    print(f"\n📸 Testing on {len(image_files)} images\n")

    results_summary = []

    for i, img_path in enumerate(image_files, 1):
        print(f"[{i}/{len(image_files)}] {img_path.name}...", end=" ")

        try:
            # Predict
            result = model.predict(str(img_path), confidence=40, overlap=30)

            # Save visualization
            output_path = Path(OUTPUT_DIR) / img_path.name
            result.save(str(output_path))

            # Get predictions
            predictions = result.json()
            num_teeth = len(predictions['predictions'])

            print(f"✅ {num_teeth} teeth detected")

            # Calculate widths
            teeth_data = []
            for pred in predictions['predictions']:
                teeth_data.append({
                    'class': pred['class'],
                    'width_pixels': pred['width'],
                    'height_pixels': pred['height'],
                    'confidence': pred['confidence']
                })

            results_summary.append({
                'image': img_path.name,
                'num_teeth': num_teeth,
                'teeth': teeth_data
            })

        except Exception as e:
            print(f"❌ Error: {e}")

    # Save summary
    with open(Path(OUTPUT_DIR) / 'results_summary.json', 'w') as f:
        json.dump(results_summary, f, indent=2)

    print(f"\n✅ Results saved to {OUTPUT_DIR}/")
    print(f"📊 Check results_summary.json for width measurements")

if __name__ == '__main__':
    test_model()
