"""
Auto-Annotation Helper for Dental X-rays
Uses image processing to suggest tooth locations
"""
import cv2
import numpy as np
from pathlib import Path
import json
from typing import List, Tuple, Dict

class DentalAutoAnnotator:
    def __init__(self):
        self.class_names = {
            0: 'primary_second_molar_55',
            1: 'primary_second_molar_65',
            2: 'primary_second_molar_75',
            3: 'primary_second_molar_85',
            4: 'second_premolar_15',
            5: 'second_premolar_25',
            6: 'second_premolar_35',
            7: 'second_premolar_45'
        }
    
    def preprocess_xray(self, image_path: str) -> np.ndarray:
        """Enhance X-ray image for better feature detection"""
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        
        if img is None:
            raise ValueError(f"Could not load image: {image_path}")
        
        # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(img)
        
        # Denoise
        denoised = cv2.fastNlMeansDenoising(enhanced, None, h=10)
        
        # Normalize
        normalized = cv2.normalize(denoised, None, 0, 255, cv2.NORM_MINMAX)
        
        return normalized
    
    def detect_tooth_regions(self, image: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Detect potential tooth regions using image processing
        Returns list of bounding boxes (x, y, w, h)
        """
        # Apply adaptive thresholding
        thresh = cv2.adaptiveThreshold(
            image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY_INV, 11, 2
        )
        
        # Morphological operations to clean up
        kernel = np.ones((3, 3), np.uint8)
        morph = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=2)
        morph = cv2.morphologyEx(morph, cv2.MORPH_OPEN, kernel, iterations=1)
        
        # Find contours
        contours, _ = cv2.findContours(morph, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filter contours by size and shape
        height, width = image.shape
        min_area = (width * height) * 0.005  # At least 0.5% of image
        max_area = (width * height) * 0.08   # At most 8% of image
        
        tooth_regions = []
        
        for contour in contours:
            area = cv2.contourArea(contour)
            
            if min_area < area < max_area:
                x, y, w, h = cv2.boundingRect(contour)
                
                # Check aspect ratio (teeth are roughly square-ish to slightly rectangular)
                aspect_ratio = w / float(h) if h > 0 else 0
                
                if 0.3 < aspect_ratio < 2.5:
                    tooth_regions.append((x, y, w, h))
        
        return tooth_regions
    
    def classify_tooth_position(self, bbox: Tuple[int, int, int, int], 
                                img_width: int, img_height: int) -> int:
        """
        Roughly classify tooth position based on location in image
        Returns class_id (0-7)
        """
        x, y, w, h = bbox
        center_x = x + w / 2
        center_y = y + h / 2
        
        # Normalize coordinates
        norm_x = center_x / img_width
        norm_y = center_y / img_height
        
        # Simple heuristic: left vs right, top vs bottom, size
        is_left = norm_x < 0.5
        is_top = norm_y < 0.5
        
        # Estimate if it's a molar (larger) or premolar (smaller)
        relative_size = (w * h) / (img_width * img_height)
        is_molar = relative_size > 0.02  # Molars are typically larger
        
        # Map to class IDs (this is a rough approximation)
        if is_top and is_left:
            return 0 if is_molar else 4  # 55 or 15
        elif is_top and not is_left:
            return 1 if is_molar else 5  # 65 or 25
        elif not is_top and is_left:
            return 2 if is_molar else 6  # 75 or 35
        else:
            return 3 if is_molar else 7  # 85 or 45
    
    def bbox_to_yolo(self, bbox: Tuple[int, int, int, int], 
                     img_width: int, img_height: int) -> Tuple[float, float, float, float]:
        """
        Convert bounding box from (x, y, w, h) to YOLO format
        (center_x, center_y, width, height) all normalized 0-1
        """
        x, y, w, h = bbox
        
        center_x = (x + w / 2) / img_width
        center_y = (y + h / 2) / img_height
        norm_w = w / img_width
        norm_h = h / img_height
        
        return (center_x, center_y, norm_w, norm_h)
    
    def annotate_image(self, image_path: str, output_label_path: str = None) -> List[Dict]:
        """
        Generate annotations for an image
        Returns list of detections with class_id and bbox
        """
        # Load and preprocess
        image = self.preprocess_xray(image_path)
        height, width = image.shape
        
        # Detect tooth regions
        tooth_regions = self.detect_tooth_regions(image)
        
        annotations = []
        
        for bbox in tooth_regions:
            # Classify tooth type
            class_id = self.classify_tooth_position(bbox, width, height)
            
            # Convert to YOLO format
            yolo_bbox = self.bbox_to_yolo(bbox, width, height)
            
            annotations.append({
                'class_id': class_id,
                'class_name': self.class_names[class_id],
                'bbox': yolo_bbox,
                'confidence': 0.5  # Auto-annotation confidence
            })
        
        # Save to label file if path provided
        if output_label_path:
            Path(output_label_path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_label_path, 'w') as f:
                for ann in annotations:
                    cx, cy, w, h = ann['bbox']
                    f.write(f"{ann['class_id']} {cx:.6f} {cy:.6f} {w:.6f} {h:.6f}\n")
        
        return annotations
    
    def visualize_annotations(self, image_path: str, annotations: List[Dict], 
                             output_path: str = None):
        """Visualize the auto-annotations"""
        image = cv2.imread(image_path)
        height, width = image.shape[:2]
        
        colors = [
            (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0),
            (255, 0, 255), (0, 255, 255), (128, 128, 128), (128, 0, 128)
        ]
        
        for ann in annotations:
            cx, cy, w, h = ann['bbox']
            class_id = ann['class_id']
            
            # Convert from YOLO to pixel coordinates
            x1 = int((cx - w/2) * width)
            y1 = int((cy - h/2) * height)
            x2 = int((cx + w/2) * width)
            y2 = int((cy + h/2) * height)
            
            color = colors[class_id % len(colors)]
            
            cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
            
            label = f"{ann['class_name']}"
            cv2.putText(image, label, (x1, y1-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        if output_path:
            cv2.imwrite(output_path, image)
        
        return image

def main():
    """Auto-annotate all images in dataset"""
    print("🦷 Dental Auto-Annotation Helper")
    print("=" * 60)
    
    annotator = DentalAutoAnnotator()
    
    # Define paths
    dataset_path = Path('backend/dataset')
    images_dir = dataset_path / 'images' / 'train'
    labels_dir = dataset_path / 'labels' / 'train'
    viz_dir = Path('auto_annotations_viz')
    
    labels_dir.mkdir(parents=True, exist_ok=True)
    viz_dir.mkdir(exist_ok=True)
    
    # Process all images
    image_files = list(images_dir.glob('*.jpg')) + list(images_dir.glob('*.png'))
    
    print(f"\n📸 Found {len(image_files)} images to annotate")
    print("\n⚠️  NOTE: These are AUTO-GENERATED suggestions!")
    print("   Please review and refine them using tools like Roboflow or CVAT\n")
    
    for i, img_file in enumerate(image_files, 1):
        print(f"[{i}/{len(image_files)}] Processing {img_file.name}...", end=' ')
        
        try:
            # Generate label file
            label_file = labels_dir / f"{img_file.stem}.txt"
            
            annotations = annotator.annotate_image(str(img_file), str(label_file))
            
            # Save visualization
            viz_file = viz_dir / img_file.name
            annotator.visualize_annotations(str(img_file), annotations, str(viz_file))
            
            print(f"✅ Found {len(annotations)} teeth")
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Auto-annotation complete!")
    print(f"📁 Labels saved to: {labels_dir}")
    print(f"📁 Visualizations saved to: {viz_dir}")
    print("\n📝 Next steps:")
    print("   1. Review visualizations in auto_annotations_viz/")
    print("   2. Refine labels using Roboflow or CVAT")
    print("   3. Run training: python scripts/enhanced_train_model.py")
    print("=" * 60)

if __name__ == '__main__':
    main()
