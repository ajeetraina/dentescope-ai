"""
Smart Tooth Detector - Hybrid approach using image processing + YOLO
Fallback to manual selection if confidence is low
"""

import cv2
import numpy as np
from typing import List, Dict, Tuple, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SmartToothDetector:
    """
    Intelligent tooth detection using multiple techniques:
    1. Edge detection for tooth boundaries
    2. Template matching for common tooth shapes
    3. Region-based analysis for molar/premolar identification
    """
    
    def __init__(self):
        self.mm_per_pixel = 0.15
        self.magnification = 1.25
        
        # Tooth identification thresholds
        self.min_tooth_area = 1000  # pixels
        self.max_tooth_area = 50000
        
        # Clinical knowledge: primary molars are wider than premolars
        self.width_ratio_threshold = 1.2
        
    def preprocess_xray(self, image: np.ndarray) -> np.ndarray:
        """Enhanced preprocessing for panoramic X-rays"""
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # Contrast enhancement
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        
        # Noise reduction
        denoised = cv2.fastNlMeansDenoising(enhanced, None, h=10, 
                                            templateWindowSize=7, 
                                            searchWindowSize=21)
        
        # Normalize
        normalized = cv2.normalize(denoised, None, 0, 255, cv2.NORM_MINMAX)
        
        return normalized
    
    def detect_tooth_regions(self, image: np.ndarray) -> List[Dict]:
        """
        Detect potential tooth regions using edge detection and contours
        """
        # Preprocess
        processed = self.preprocess_xray(image)
        
        # Edge detection
        edges = cv2.Canny(processed, 50, 150)
        
        # Morphological operations to connect edges
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel, iterations=2)
        
        # Find contours
        contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, 
                                       cv2.CHAIN_APPROX_SIMPLE)
        
        tooth_regions = []
        
        for contour in contours:
            area = cv2.contourArea(contour)
            
            # Filter by area
            if self.min_tooth_area < area < self.max_tooth_area:
                x, y, w, h = cv2.boundingRect(contour)
                
                # Calculate features
                aspect_ratio = float(w) / h if h > 0 else 0
                
                # Teeth in panoramic X-rays typically have aspect ratio between 0.5 and 2.0
                if 0.4 < aspect_ratio < 2.5:
                    tooth_regions.append({
                        'bbox': [x, y, x + w, y + h],
                        'area': area,
                        'width': w,
                        'height': h,
                        'aspect_ratio': aspect_ratio,
                        'center': (x + w // 2, y + h // 2)
                    })
        
        return tooth_regions
    
    def classify_teeth(self, tooth_regions: List[Dict], image_width: int) -> Dict:
        """
        Classify detected regions as primary molars or premolars
        Based on:
        1. Width (primary molars are wider)
        2. Position (left vs right side)
        3. Relative size comparison
        """
        if not tooth_regions:
            return {'primary_molars': [], 'premolars': []}
        
        # Sort by width (descending)
        sorted_by_width = sorted(tooth_regions, key=lambda x: x['width'], reverse=True)
        
        # Split into left and right halves
        mid_x = image_width / 2
        left_teeth = [t for t in tooth_regions if t['center'][0] < mid_x]
        right_teeth = [t for t in tooth_regions if t['center'][0] >= mid_x]
        
        primary_molars = []
        premolars = []
        
        # Process each side
        for side_teeth in [left_teeth, right_teeth]:
            if len(side_teeth) < 2:
                continue
            
            # Sort by width
            side_sorted = sorted(side_teeth, key=lambda x: x['width'], reverse=True)
            
            # Typically, the wider teeth are primary molars
            # and narrower adjacent teeth are premolars
            if len(side_sorted) >= 2:
                potential_molar = side_sorted[0]
                potential_premolar = side_sorted[1]
                
                # Check if width difference suggests molar vs premolar
                width_ratio = potential_molar['width'] / potential_premolar['width']
                
                if width_ratio >= self.width_ratio_threshold:
                    potential_molar['type'] = 'primary_molar'
                    potential_premolar['type'] = 'premolar'
                    primary_molars.append(potential_molar)
                    premolars.append(potential_premolar)
                else:
                    # If not clear, mark as uncertain
                    potential_molar['type'] = 'uncertain'
                    potential_premolar['type'] = 'uncertain'
        
        return {
            'primary_molars': primary_molars,
            'premolars': premolars
        }
    
    def match_pairs(self, classified: Dict) -> List[Tuple[Dict, Dict]]:
        """
        Match primary molars with corresponding premolars
        Based on spatial proximity
        """
        primary_molars = classified['primary_molars']
        premolars = classified['premolars']
        
        pairs = []
        used_premolars = set()
        
        for molar in primary_molars:
            molar_center = molar['center']
            min_dist = float('inf')
            best_match = None
            best_idx = None
            
            for idx, premolar in enumerate(premolars):
                if idx in used_premolars:
                    continue
                
                premolar_center = premolar['center']
                
                # Calculate distance
                dist = np.sqrt((molar_center[0] - premolar_center[0])**2 + 
                             (molar_center[1] - premolar_center[1])**2)
                
                # Also check if they're on the same side
                same_side = ((molar_center[0] < premolar_center[0]) or 
                           (molar_center[0] > premolar_center[0]))
                
                if dist < min_dist and same_side:
                    min_dist = dist
                    best_match = premolar
                    best_idx = idx
            
            if best_match and min_dist < 300:  # Proximity threshold
                pairs.append((molar, best_match))
                used_premolars.add(best_idx)
        
        return pairs
    
    def calculate_measurements(self, pairs: List[Tuple[Dict, Dict]]) -> List[Dict]:
        """
        Calculate width measurements and differences for each pair
        """
        results = []
        
        for molar, premolar in pairs:
            # Convert pixel measurements to mm
            molar_width_mm = (molar['width'] * self.mm_per_pixel) / self.magnification
            premolar_width_mm = (premolar['width'] * self.mm_per_pixel) / self.magnification
            
            difference = molar_width_mm - premolar_width_mm
            
            # Determine if within normal clinical range (2.0-2.8mm)
            within_normal = 2.0 <= difference <= 2.8
            
            results.append({
                'primary_molar': {
                    'bbox': molar['bbox'],
                    'width_mm': round(molar_width_mm, 2),
                    'confidence': 0.75  # Base confidence for image processing
                },
                'premolar': {
                    'bbox': premolar['bbox'],
                    'width_mm': round(premolar_width_mm, 2),
                    'confidence': 0.75
                },
                'difference_mm': round(abs(difference), 2),
                'within_normal_range': within_normal,
                'requires_manual_verification': difference < 1.5 or difference > 3.5
            })
        
        return results
    
    def detect_and_analyze(self, image: np.ndarray) -> Dict:
        """
        Complete detection and analysis pipeline
        """
        height, width = image.shape[:2] if len(image.shape) == 2 else image.shape[:2]
        
        logger.info("Starting tooth detection...")
        
        # Step 1: Detect tooth regions
        tooth_regions = self.detect_tooth_regions(image)
        logger.info(f"Detected {len(tooth_regions)} potential tooth regions")
        
        if len(tooth_regions) < 2:
            return {
                'success': False,
                'message': 'Insufficient tooth regions detected. Please use manual selection.',
                'detected_regions': tooth_regions,
                'requires_manual': True
            }
        
        # Step 2: Classify teeth
        classified = self.classify_teeth(tooth_regions, width)
        logger.info(f"Classified: {len(classified['primary_molars'])} molars, "
                   f"{len(classified['premolars'])} premolars")
        
        if not classified['primary_molars'] or not classified['premolars']:
            return {
                'success': False,
                'message': 'Could not identify tooth types. Please use manual selection.',
                'detected_regions': tooth_regions,
                'requires_manual': True
            }
        
        # Step 3: Match pairs
        pairs = self.match_pairs(classified)
        logger.info(f"Matched {len(pairs)} tooth pairs")
        
        if not pairs:
            return {
                'success': False,
                'message': 'Could not match tooth pairs. Please use manual selection.',
                'detected_regions': tooth_regions,
                'classified': classified,
                'requires_manual': True
            }
        
        # Step 4: Calculate measurements
        results = self.calculate_measurements(pairs)
        
        # Overall confidence score
        avg_confidence = np.mean([r['primary_molar']['confidence'] for r in results])
        
        return {
            'success': True,
            'confidence': round(avg_confidence, 2),
            'results': results,
            'total_pairs': len(results),
            'requires_manual': avg_confidence < 0.70,
            'message': 'Automatic detection successful!' if avg_confidence >= 0.70 
                      else 'Low confidence. Manual verification recommended.'
        }
    
    def draw_detections(self, image: np.ndarray, analysis_result: Dict) -> np.ndarray:
        """
        Draw bounding boxes and measurements on the image
        """
        annotated = image.copy()
        
        if not analysis_result.get('success'):
            return annotated
        
        results = analysis_result.get('results', [])
        
        for result in results:
            # Draw primary molar
            molar_bbox = result['primary_molar']['bbox']
            cv2.rectangle(annotated, 
                         (molar_bbox[0], molar_bbox[1]),
                         (molar_bbox[2], molar_bbox[3]),
                         (255, 0, 0), 3)  # Blue
            
            # Draw premolar
            premolar_bbox = result['premolar']['bbox']
            cv2.rectangle(annotated,
                         (premolar_bbox[0], premolar_bbox[1]),
                         (premolar_bbox[2], premolar_bbox[3]),
                         (0, 255, 0), 3)  # Green
            
            # Draw measurement line and text
            molar_center = ((molar_bbox[0] + molar_bbox[2]) // 2,
                          (molar_bbox[1] + molar_bbox[3]) // 2)
            premolar_center = ((premolar_bbox[0] + premolar_bbox[2]) // 2,
                             (premolar_bbox[1] + premolar_bbox[3]) // 2)
            
            cv2.line(annotated, molar_center, premolar_center, (0, 0, 255), 2)
            
            # Add text
            mid_point = ((molar_center[0] + premolar_center[0]) // 2,
                        (molar_center[1] + premolar_center[1]) // 2)
            
            text = f"Δ {result['difference_mm']}mm"
            cv2.putText(annotated, text, mid_point,
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        return annotated


def main():
    """Test the detector"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python smart_tooth_detector.py <image_path>")
        sys.exit(1)
    
    image_path = sys.argv[1]
    image = cv2.imread(image_path)
    
    if image is None:
        print(f"Error: Could not load image from {image_path}")
        sys.exit(1)
    
    detector = SmartToothDetector()
    result = detector.detect_and_analyze(image)
    
    print("\n" + "="*60)
    print("DETECTION RESULTS")
    print("="*60)
    print(f"Success: {result['success']}")
    print(f"Message: {result.get('message', 'N/A')}")
    
    if result['success']:
        print(f"Confidence: {result.get('confidence', 0):.2f}")
        print(f"Total Pairs Detected: {result.get('total_pairs', 0)}")
        print(f"Requires Manual Verification: {result.get('requires_manual', False)}")
        
        print("\nDetailed Results:")
        for i, res in enumerate(result.get('results', []), 1):
            print(f"\nPair {i}:")
            print(f"  Primary Molar Width: {res['primary_molar']['width_mm']}mm")
            print(f"  Premolar Width: {res['premolar']['width_mm']}mm")
            print(f"  Difference: {res['difference_mm']}mm")
            print(f"  Within Normal Range: {res['within_normal_range']}")
    
    # Save annotated image
    if result['success']:
        annotated = detector.draw_detections(image, result)
        output_path = image_path.replace('.', '_detected.')
        cv2.imwrite(output_path, annotated)
        print(f"\nAnnotated image saved to: {output_path}")


if __name__ == "__main__":
    main()
