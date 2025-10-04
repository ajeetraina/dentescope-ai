from dental_width_analyzer import DentalWidthAnalyzer
import cv2
import numpy as np
import os

# Create sample test image (simulating dental X-ray)
print("Creating test image...")
img = np.ones((800, 1200, 3), dtype=np.uint8) * 80
cv2.rectangle(img, (300, 300), (400, 450), (200, 200, 200), -1)
cv2.rectangle(img, (500, 320), (580, 450), (200, 200, 200), -1)

os.makedirs('test_images', exist_ok=True)
cv2.imwrite('test_images/sample.jpg', img)
print("✓ Test image created")

# Initialize analyzer
print("\nInitializing analyzer...")
analyzer = DentalWidthAnalyzer(model_path='../models/yolov8n.pt')

# Test preprocessing
print("Testing preprocessing...")
processed = analyzer.preprocess_image('test_images/sample.jpg')
print(f"✓ Preprocessed: {processed.shape}")

# Test detection
print("\nTesting detection...")
detections = analyzer.detect_teeth(processed)
print(f"✓ Detected {len(detections)} objects")

print("\n✅ Basic pipeline working!")
