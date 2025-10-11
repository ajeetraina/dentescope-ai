from ultralytics import YOLO
from pathlib import Path
import cv2
import numpy as np

def test_model():
    """Test the trained YOLOv8 model"""
    
    print("🧪 Testing Dental Tooth Detector")
    print("=" * 60)
    
    # Check if model exists
    model_path = Path('model/dental_detector.pt')
    if not model_path.exists():
        print("❌ Trained model not found!")
        print(f"   Expected: {model_path}")
        print("   Please train the model first: python scripts/train_yolo.py")
        return
    
    # Load model
    print(f"📥 Loading model from: {model_path}")
    model = YOLO(str(model_path))
    
    # Get test images
    test_dir = Path('data/samples')
    test_images = list(test_dir.glob('*.jpg'))[:5]  # Test on first 5 images
    
    if len(test_images) == 0:
        print("❌ No test images found!")
        return
    
    print(f"🖼️  Testing on {len(test_images)} images...")
    
    # Class names
    class_names = ['55', '65', '75', '85', '15', '25', '35', '45']
    
    # Create output directory
    output_dir = Path('test_results')
    output_dir.mkdir(exist_ok=True)
    
    for img_path in test_images:
        print(f"\n📊 Processing: {img_path.name}")
        
        # Run inference
        results = model(str(img_path), conf=0.25)
        
        # Get the result
        result = results[0]
        
        # Count detections
        boxes = result.boxes
        num_detections = len(boxes)
        print(f"   Detected {num_detections} teeth")
        
        # Display detections
        if num_detections > 0:
            for i, box in enumerate(boxes):
                cls = int(box.cls[0])
                conf = float(box.conf[0])
                tooth_name = class_names[cls]
                print(f"   - Tooth {tooth_name}: {conf:.2%} confidence")
        
        # Save annotated image
        annotated = result.plot()
        output_path = output_dir / f"result_{img_path.name}"
        cv2.imwrite(str(output_path), annotated)
        print(f"   ✅ Saved to: {output_path}")
    
    print(f"\n🎉 Testing complete!")
    print(f"📁 Results saved to: {output_dir}/")

if __name__ == "__main__":
    test_model()
