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
