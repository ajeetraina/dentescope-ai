import cv2
import numpy as np
from pathlib import Path

class SmartDentalAnnotator:
    def __init__(self, images_dir, output_dir):
        self.images_dir = Path(images_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Tooth classes
        self.classes = {
            '55': 0, '65': 1, '75': 2, '85': 3,  # Primary Second Molars
            '15': 4, '25': 5, '35': 6, '45': 7   # Second Premolars
        }
        
        # Current state
        self.current_image = None
        self.current_image_name = None
        self.current_boxes = []
        self.current_class = 0
        
    def preprocess_xray(self, img):
        """Enhance X-ray for better tooth detection"""
        # Convert to grayscale
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img.copy()
        
        # Apply CLAHE for better contrast
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        enhanced = clahe.apply(gray)
        
        # Denoise
        denoised = cv2.fastNlMeansDenoising(enhanced, None, 10, 7, 21)
        
        return denoised
    
    def suggest_teeth_regions(self, img):
        """Use image processing to suggest tooth regions"""
        processed = self.preprocess_xray(img)
        
        # Thresholding to find teeth (they appear brighter)
        _, thresh = cv2.threshold(processed, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Morphological operations
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 15))
        closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        
        # Find contours
        contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filter contours by size and shape
        suggestions = []
        h, w = img.shape[:2]
        
        for contour in contours:
            x, y, cw, ch = cv2.boundingRect(contour)
            area = cv2.contourArea(contour)
            
            # Filter based on reasonable tooth dimensions
            if (area > 1000 and area < 50000 and  # Reasonable size
                cw > 20 and ch > 20 and              # Not too small
                cw < w * 0.3 and ch < h * 0.3):      # Not too large
                suggestions.append([x, y, cw, ch])
        
        return suggestions
    
    def annotate_interactive(self):
        """Interactive annotation tool"""
        image_files = list(self.images_dir.glob('*.jpg')) + list(self.images_dir.glob('*.tif'))
        
        print(f"\n🦷 Dental X-Ray Annotator")
        print(f"Found {len(image_files)} images")
        print("\nControls:")
        print("  - Click and drag to draw bounding box")
        print("  - Keys 0-7: Select tooth class")
        print("  - 's': Save and next image")
        print("  - 'a': Auto-suggest boxes")
        print("  - 'd': Delete last box")
        print("  - 'q': Quit")
        
        for img_file in image_files:
            self.annotate_image(img_file)
    
    def annotate_image(self, img_path):
        """Annotate single image"""
        self.current_image = cv2.imread(str(img_path))
        self.current_image_name = img_path.stem
        self.current_boxes = []
        
        if self.current_image is None:
            print(f"⚠️  Could not load {img_path}")
            return
        
        # Check if already annotated
        label_file = self.output_dir / f"{self.current_image_name}.txt"
        if label_file.exists():
            print(f"⏭️  Skipping {self.current_image_name} (already annotated)")
            return
        
        h, w = self.current_image.shape[:2]
        display = self.current_image.copy()
        
        # Auto-suggest boxes
        suggestions = self.suggest_teeth_regions(self.current_image)
        print(f"\n📊 {self.current_image_name}")
        print(f"   Found {len(suggestions)} suggested tooth regions")
        
        # Draw suggestions
        for (x, y, bw, bh) in suggestions:
            cv2.rectangle(display, (x, y), (x + bw, y + bh), (0, 255, 255), 2)
        
        cv2.namedWindow('Annotate', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Annotate', 1200, 800)
        
        drawing = False
        start_point = None
        
        def mouse_callback(event, x, y, flags, param):
            nonlocal drawing, start_point, display
            
            if event == cv2.EVENT_LBUTTONDOWN:
                drawing = True
                start_point = (x, y)
            
            elif event == cv2.EVENT_MOUSEMOVE and drawing:
                temp = display.copy()
                cv2.rectangle(temp, start_point, (x, y), (0, 255, 0), 2)
                cv2.imshow('Annotate', temp)
            
            elif event == cv2.EVENT_LBUTTONUP:
                drawing = False
                x1, y1 = start_point
                x2, y2 = x, y
                
                # Ensure x1 < x2 and y1 < y2
                x1, x2 = min(x1, x2), max(x1, x2)
                y1, y2 = min(y1, y2), max(y1, y2)
                
                # Convert to YOLO format (normalized center x, center y, width, height)
                box_w = (x2 - x1) / w
                box_h = (y2 - y1) / h
                center_x = ((x1 + x2) / 2) / w
                center_y = ((y1 + y2) / 2) / h
                
                self.current_boxes.append({
                    'class': self.current_class,
                    'bbox': [center_x, center_y, box_w, box_h]
                })
                
                # Redraw all boxes
                display = self.current_image.copy()
                for box in self.current_boxes:
                    self.draw_box(display, box, w, h)
                
                cv2.imshow('Annotate', display)
        
        cv2.setMouseCallback('Annotate', mouse_callback)
        cv2.imshow('Annotate', display)
        
        while True:
            key = cv2.waitKey(1) & 0xFF
            
            # Select class
            if ord('0') <= key <= ord('7'):
                self.current_class = key - ord('0')
                class_name = list(self.classes.keys())[self.current_class]
                print(f"   Selected class: {self.current_class} ({class_name})")
            
            # Auto-suggest
            elif key == ord('a'):
                for (x, y, bw, bh) in suggestions[:8]:  # Limit to 8 teeth
                    box_w = bw / w
                    box_h = bh / h
                    center_x = (x + bw / 2) / w
                    center_y = (y + bh / 2) / h
                    
                    self.current_boxes.append({
                        'class': len(self.current_boxes) % 8,
                        'bbox': [center_x, center_y, box_w, box_h]
                    })
                
                display = self.current_image.copy()
                for box in self.current_boxes:
                    self.draw_box(display, box, w, h)
                cv2.imshow('Annotate', display)
                print(f"   Added {len(suggestions[:8])} auto-suggested boxes")
            
            # Delete last box
            elif key == ord('d') and len(self.current_boxes) > 0:
                self.current_boxes.pop()
                display = self.current_image.copy()
                for box in self.current_boxes:
                    self.draw_box(display, box, w, h)
                cv2.imshow('Annotate', display)
                print(f"   Deleted last box ({len(self.current_boxes)} remaining)")
            
            # Save and next
            elif key == ord('s'):
                self.save_annotation()
                break
            
            # Quit
            elif key == ord('q'):
                cv2.destroyAllWindows()
                return
        
        cv2.destroyAllWindows()
    
    def draw_box(self, img, box, w, h):
        """Draw a box on the image"""
        cx, cy, bw, bh = box['bbox']
        x1 = int((cx - bw / 2) * w)
        y1 = int((cy - bh / 2) * h)
        x2 = int((cx + bw / 2) * w)
        y2 = int((cy + bh / 2) * h)
        
        color = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0),
                 (255, 0, 255), (0, 255, 255), (128, 128, 128), (255, 128, 0)][box['class']]
        
        cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
        class_name = list(self.classes.keys())[box['class']]
        cv2.putText(img, class_name, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    
    def save_annotation(self):
        """Save annotation in YOLO format"""
        if len(self.current_boxes) == 0:
            print(f"   ⚠️  No boxes to save")
            return
        
        label_file = self.output_dir / f"{self.current_image_name}.txt"
        
        with open(label_file, 'w') as f:
            for box in self.current_boxes:
                class_id = box['class']
                bbox = box['bbox']
                f.write(f"{class_id} {bbox[0]:.6f} {bbox[1]:.6f} {bbox[2]:.6f} {bbox[3]:.6f}\n")
        
        print(f"   ✅ Saved {len(self.current_boxes)} annotations")

if __name__ == "__main__":
    annotator = SmartDentalAnnotator(
        images_dir="data/samples",
        output_dir="dataset/labels"
    )
    annotator.annotate_interactive()
