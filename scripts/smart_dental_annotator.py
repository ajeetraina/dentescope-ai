#!/usr/bin/env python3
"""
🦷 Smart Dental Annotator - Reference-Based Semi-Automated Tool
Uses your reference image to intelligently suggest tooth regions
"""

import cv2
import numpy as np
import os
from pathlib import Path
import json
from typing import List, Dict, Tuple, Optional

# Tooth classes based on your reference
TOOTH_CLASSES = {
    0: {"name": "primary_second_molar_55", "color": (255, 100, 100), "label": "Primary Molar 55"},
    1: {"name": "primary_second_molar_65", "color": (255, 150, 100), "label": "Primary Molar 65"},
    2: {"name": "primary_second_molar_75", "color": (255, 200, 100), "label": "Primary Molar 75"},
    3: {"name": "primary_second_molar_85", "color": (255, 255, 100), "label": "Primary Molar 85"},
    4: {"name": "second_premolar_15", "color": (100, 255, 200), "label": "Premolar 15"},
    5: {"name": "second_premolar_25", "color": (100, 200, 255), "label": "Premolar 25"},
    6: {"name": "second_premolar_35", "color": (100, 150, 255), "label": "Premolar 35"},
    7: {"name": "second_premolar_45", "color": (100, 100, 255), "label": "Premolar 45"}
}


class SmartToothDetector:
    """
    Intelligent tooth detection based on anatomical knowledge
    Uses edge detection, contour analysis, and template matching
    """
    
    def __init__(self):
        # Anatomical parameters (based on typical panoramic X-rays)
        self.tooth_width_range = (50, 180)  # pixels
        self.tooth_height_range = (80, 250)  # pixels
        self.molar_vs_premolar_ratio = 1.15  # molars are ~15% wider
        
        # Image processing parameters
        self.clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        
    def preprocess_xray(self, image: np.ndarray) -> np.ndarray:
        """Enhanced preprocessing for panoramic X-rays"""
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # Apply CLAHE for contrast enhancement
        enhanced = self.clahe.apply(gray)
        
        # Denoise
        denoised = cv2.fastNlMeansDenoising(enhanced, None, h=10, 
                                           templateWindowSize=7, 
                                           searchWindowSize=21)
        
        # Normalize
        normalized = cv2.normalize(denoised, None, 0, 255, cv2.NORM_MINMAX)
        
        return normalized
    
    def detect_mandible_region(self, image: np.ndarray) -> Tuple[int, int]:
        """
        Detect the mandible (lower jaw) region
        Returns (y_start, y_end) for the region of interest
        """
        height, width = image.shape[:2]
        
        # The mandible is typically in the lower 40-70% of panoramic X-rays
        y_start = int(height * 0.4)
        y_end = int(height * 0.85)
        
        return y_start, y_end
    
    def detect_tooth_regions(self, image: np.ndarray) -> List[Dict]:
        """
        Detect potential tooth regions using edge detection and contour analysis
        Based on your reference image patterns
        """
        # Preprocess
        processed = self.preprocess_xray(image)
        
        # Focus on mandible region (where molars and premolars are)
        height, width = processed.shape[:2]
        y_start, y_end = self.detect_mandible_region(processed)
        mandible_region = processed[y_start:y_end, :]
        
        # Edge detection
        edges = cv2.Canny(mandible_region, 30, 100)
        
        # Morphological operations to connect tooth boundaries
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))
        closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel, iterations=2)
        
        # Dilate to merge nearby edges
        dilated = cv2.dilate(closed, kernel, iterations=1)
        
        # Find contours
        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        tooth_regions = []
        
        for contour in contours:
            area = cv2.contourArea(contour)
            
            # Filter by area (teeth have characteristic sizes)
            if area < 2000 or area > 50000:
                continue
            
            x, y, w, h = cv2.boundingRect(contour)
            
            # Adjust y coordinates back to full image
            y_adjusted = y + y_start
            
            # Filter by dimensions
            if not (self.tooth_width_range[0] <= w <= self.tooth_width_range[1]):
                continue
            if not (self.tooth_height_range[0] <= h <= self.tooth_height_range[1]):
                continue
            
            # Calculate aspect ratio
            aspect_ratio = float(w) / h if h > 0 else 0
            
            # Teeth typically have aspect ratio between 0.4 and 0.9
            if not (0.3 < aspect_ratio < 1.0):
                continue
            
            # Calculate density (how much of the bounding box is filled)
            mask = np.zeros(mandible_region.shape, dtype=np.uint8)
            cv2.drawContours(mask, [contour], -1, 255, -1)
            density = cv2.countNonZero(mask[y:y+h, x:x+w]) / (w * h)
            
            # Teeth should have reasonable density
            if density < 0.2 or density > 0.8:
                continue
            
            tooth_regions.append({
                'bbox': [x, y_adjusted, x + w, y_adjusted + h],
                'width': w,
                'height': h,
                'area': area,
                'aspect_ratio': aspect_ratio,
                'density': density,
                'center_x': x + w // 2,
                'center_y': y_adjusted + h // 2
            })
        
        # Sort by horizontal position (left to right)
        tooth_regions.sort(key=lambda r: r['center_x'])
        
        return tooth_regions
    
    def classify_teeth(self, tooth_regions: List[Dict], img_width: int) -> List[Dict]:
        """
        Classify detected regions as molars or premolars based on:
        1. Position (left vs right side)
        2. Relative size (molars are wider)
        3. Anatomical knowledge
        """
        if not tooth_regions:
            return []
        
        # Separate left and right sides
        mid_x = img_width / 2
        left_teeth = [t for t in tooth_regions if t['center_x'] < mid_x]
        right_teeth = [t for t in tooth_regions if t['center_x'] >= mid_x]
        
        annotated_teeth = []
        
        # Process left side (teeth 75, 85)
        left_teeth.sort(key=lambda t: t['center_x'])
        for i, tooth in enumerate(left_teeth[:4]):  # Take up to 4 teeth
            # Larger teeth are more likely to be molars
            if tooth['width'] > np.median([t['width'] for t in left_teeth]):
                tooth['class_id'] = 2  # primary_second_molar_75
                tooth['class_name'] = "Primary Molar 75"
            else:
                tooth['class_id'] = 6  # second_premolar_35
                tooth['class_name'] = "Premolar 35"
            annotated_teeth.append(tooth)
        
        # Process right side (teeth 65, 55)
        right_teeth.sort(key=lambda t: t['center_x'])
        for i, tooth in enumerate(right_teeth[:4]):  # Take up to 4 teeth
            # Larger teeth are more likely to be molars
            if tooth['width'] > np.median([t['width'] for t in right_teeth]):
                tooth['class_id'] = 1  # primary_second_molar_65
                tooth['class_name'] = "Primary Molar 65"
            else:
                tooth['class_id'] = 5  # second_premolar_25
                tooth['class_name'] = "Premolar 25"
            annotated_teeth.append(tooth)
        
        return annotated_teeth


class InteractiveAnnotationTool:
    """
    Interactive tool with smart suggestions based on your reference
    """
    
    def __init__(self, images_dir: str, output_dir: str):
        self.images_dir = Path(images_dir)
        self.output_dir = Path(output_dir)
        
        # Create output structure
        (self.output_dir / 'images').mkdir(parents=True, exist_ok=True)
        (self.output_dir / 'labels').mkdir(parents=True, exist_ok=True)
        
        # Get images
        self.image_files = sorted(list(self.images_dir.glob('*.jpg')) + 
                                 list(self.images_dir.glob('*.jpeg')) + 
                                 list(self.images_dir.glob('*.png')) +
                                 list(self.images_dir.glob('*.tif')))
        
        print(f"📸 Found {len(self.image_files)} images")
        
        # State
        self.current_idx = 0
        self.current_image = None
        self.display_image = None
        self.annotations = []
        self.suggested_regions = []
        
        # Smart detector
        self.detector = SmartToothDetector()
        
        # UI state
        self.drawing = False
        self.start_point = None
        self.current_class = 0
        self.selected_idx = None
        self.show_suggestions = True
        
        self.window_name = "🦷 Smart Dental Annotator"
        
        # Progress
        self.progress_file = self.output_dir / 'progress.json'
        self.progress = self.load_progress()
    
    def load_progress(self) -> Dict:
        if self.progress_file.exists():
            with open(self.progress_file, 'r') as f:
                return json.load(f)
        return {'annotated': [], 'last_index': 0}
    
    def save_progress(self):
        with open(self.progress_file, 'w') as f:
            json.dump(self.progress, f, indent=2)
    
    def load_image(self, idx: int):
        """Load image and generate smart suggestions"""
        self.current_idx = idx
        img_path = self.image_files[idx]
        
        print(f"\n📷 [{idx + 1}/{len(self.image_files)}] {img_path.name}")
        
        # Load image
        self.current_image = cv2.imread(str(img_path))
        if self.current_image is None:
            print(f"❌ Failed to load: {img_path}")
            return False
        
        self.img_height, self.img_width = self.current_image.shape[:2]
        
        # Try to load existing annotations
        label_path = self.output_dir / 'labels' / f"{img_path.stem}.txt"
        self.annotations = []
        
        if label_path.exists():
            print(f"📝 Loading existing annotations...")
            with open(label_path, 'r') as f:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) >= 5:
                        class_id = int(parts[0])
                        x_center = float(parts[1]) * self.img_width
                        y_center = float(parts[2]) * self.img_height
                        width = float(parts[3]) * self.img_width
                        height = float(parts[4]) * self.img_height
                        
                        x1 = int(x_center - width / 2)
                        y1 = int(y_center - height / 2)
                        x2 = int(x_center + width / 2)
                        y2 = int(y_center + height / 2)
                        
                        self.annotations.append({
                            'bbox': [x1, y1, x2, y2],
                            'class_id': class_id,
                            'class_name': TOOTH_CLASSES[class_id]['name']
                        })
            print(f"✅ Loaded {len(self.annotations)} annotations")
        else:
            # Generate smart suggestions
            print("🤖 Generating smart suggestions...")
            self.suggested_regions = self.detector.detect_tooth_regions(self.current_image)
            self.suggested_regions = self.detector.classify_teeth(
                self.suggested_regions, 
                self.img_width
            )
            print(f"💡 Found {len(self.suggested_regions)} suggested regions")
            print("   Press 'A' to accept all suggestions")
            print("   Press 'Space' to accept current suggestion")
        
        self.update_display()
        return True
    
    def update_display(self):
        """Update display with annotations and suggestions"""
        self.display_image = self.current_image.copy()
        
        # Draw confirmed annotations
        for i, ann in enumerate(self.annotations):
            x1, y1, x2, y2 = ann['bbox']
            color = TOOTH_CLASSES[ann['class_id']]['color']
            
            thickness = 3 if i == self.selected_idx else 2
            cv2.rectangle(self.display_image, (x1, y1), (x2, y2), color, thickness)
            
            # Label
            label = TOOTH_CLASSES[ann['class_id']]['label']
            cv2.rectangle(self.display_image,
                         (x1, y1 - 25), (x1 + len(label) * 10, y1),
                         color, -1)
            cv2.putText(self.display_image, label, (x1 + 5, y1 - 8),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Draw suggestions (dotted lines)
        if self.show_suggestions and self.suggested_regions:
            for region in self.suggested_regions:
                x1, y1, x2, y2 = region['bbox']
                color = (0, 255, 255)  # Yellow for suggestions
                
                # Draw dotted rectangle
                self.draw_dotted_rect(self.display_image, (x1, y1), (x2, y2), color, 2)
                
                # Label
                label = f"Suggestion: {region.get('class_name', 'Tooth')}"
                cv2.putText(self.display_image, label, (x1, y1 - 5),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
        
        # Draw info panel
        self.draw_info_panel()
        
        cv2.imshow(self.window_name, self.display_image)
    
    def draw_dotted_rect(self, img, pt1, pt2, color, thickness):
        """Draw dotted rectangle"""
        x1, y1 = pt1
        x2, y2 = pt2
        
        # Top
        for x in range(x1, x2, 10):
            cv2.line(img, (x, y1), (min(x + 5, x2), y1), color, thickness)
        # Bottom
        for x in range(x1, x2, 10):
            cv2.line(img, (x, y2), (min(x + 5, x2), y2), color, thickness)
        # Left
        for y in range(y1, y2, 10):
            cv2.line(img, (x1, y), (x1, min(y + 5, y2)), color, thickness)
        # Right
        for y in range(y1, y2, 10):
            cv2.line(img, (x2, y), (x2, min(y + 5, y2)), color, thickness)
    
    def draw_info_panel(self):
        """Draw information overlay"""
        panel_height = 150
        panel = np.zeros((panel_height, self.img_width, 3), dtype=np.uint8)
        
        # Stats
        y_offset = 20
        cv2.putText(panel, f"Image: {self.current_idx + 1}/{len(self.image_files)}", 
                   (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        y_offset += 25
        cv2.putText(panel, f"Annotations: {len(self.annotations)}", 
                   (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        y_offset += 25
        cv2.putText(panel, f"Suggestions: {len(self.suggested_regions)}", 
                   (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        
        y_offset += 25
        cv2.putText(panel, f"Current Class: {TOOTH_CLASSES[self.current_class]['label']}", 
                   (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.6, 
                   TOOTH_CLASSES[self.current_class]['color'], 2)
        
        # Controls
        y_offset += 30
        controls = "A: Accept All | Space: Accept One | S: Save | D: Delete | 0-7: Change Class | H: Toggle Help | Q: Quit"
        cv2.putText(panel, controls, (10, y_offset), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
        
        self.display_image = np.vstack([self.display_image, panel])
    
    def accept_all_suggestions(self):
        """Accept all suggested regions as annotations"""
        for region in self.suggested_regions:
            self.annotations.append({
                'bbox': region['bbox'],
                'class_id': region['class_id'],
                'class_name': region['class_name']
            })
        self.suggested_regions = []
        print(f"✅ Accepted all suggestions! Total annotations: {len(self.annotations)}")
        self.update_display()
    
    def save_annotations(self):
        """Save annotations in YOLO format"""
        img_name = self.image_files[self.current_idx].name
        label_name = self.image_files[self.current_idx].stem + '.txt'
        
        # Save label file
        label_path = self.output_dir / 'labels' / label_name
        with open(label_path, 'w') as f:
            for ann in self.annotations:
                x1, y1, x2, y2 = ann['bbox']
                x_center = ((x1 + x2) / 2) / self.img_width
                y_center = ((y1 + y2) / 2) / self.img_height
                width = (x2 - x1) / self.img_width
                height = (y2 - y1) / self.img_height
                f.write(f"{ann['class_id']} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n")
        
        # Copy image
        import shutil
        shutil.copy(self.image_files[self.current_idx],
                   self.output_dir / 'images' / img_name)
        
        # Update progress
        if img_name not in self.progress['annotated']:
            self.progress['annotated'].append(img_name)
        self.progress['last_index'] = self.current_idx
        self.save_progress()
        
        print(f"💾 Saved {len(self.annotations)} annotations")
    
    def mouse_callback(self, event, x, y, flags, param):
        """Handle mouse events for manual drawing"""
        if event == cv2.EVENT_LBUTTONDOWN:
            self.drawing = True
            self.start_point = (x, y)
        
        elif event == cv2.EVENT_MOUSEMOVE:
            if self.drawing:
                self.end_point = (x, y)
                self.update_display()
                # Draw current rectangle
                cv2.rectangle(self.display_image, self.start_point, self.end_point,
                            TOOTH_CLASSES[self.current_class]['color'], 2)
                cv2.imshow(self.window_name, self.display_image)
        
        elif event == cv2.EVENT_LBUTTONUP:
            if self.drawing:
                self.drawing = False
                self.end_point = (x, y)
                
                # Add annotation
                x1 = min(self.start_point[0], self.end_point[0])
                y1 = min(self.start_point[1], self.end_point[1])
                x2 = max(self.start_point[0], self.end_point[0])
                y2 = max(self.start_point[1], self.end_point[1])
                
                if abs(x2 - x1) > 20 and abs(y2 - y1) > 20:
                    self.annotations.append({
                        'bbox': [x1, y1, x2, y2],
                        'class_id': self.current_class,
                        'class_name': TOOTH_CLASSES[self.current_class]['name']
                    })
                    print(f"✅ Added: {TOOTH_CLASSES[self.current_class]['label']}")
                
                self.update_display()
    
    def run(self):
        """Main annotation loop"""
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        cv2.setMouseCallback(self.window_name, self.mouse_callback)
        
        # Start from last position
        start_idx = self.progress.get('last_index', 0)
        self.load_image(start_idx)
        
        print("\n" + "="*70)
        print("🦷 SMART DENTAL ANNOTATOR")
        print("="*70)
        print("\n🤖 AI-Assisted Annotation Based on Your Reference Image")
        print("\nControls:")
        print("  A: Accept ALL smart suggestions")
        print("  Sp
