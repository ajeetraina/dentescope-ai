#!/usr/bin/env python3
"""
🦷 Toothy Width Mate - AI-Assisted Annotation Tool
=================================================
Interactive tool for annotating dental panoramic X-rays with tooth detection bounding boxes.

Features:
- AI-assisted pre-annotation using existing models
- Interactive bounding box drawing and editing
- Keyboard shortcuts for efficient workflow
- Progress tracking and validation
- Auto-save and session recovery
- Export to YOLO format

Author: Collabnix Team
"""

import cv2
import numpy as np
import os
import json
import glob
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import argparse
from datetime import datetime

# Tooth classes matching your dataset/classes.txt
TOOTH_CLASSES = [
    "primary_second_molar_55",    # 0
    "primary_second_molar_65",    # 1
    "primary_second_molar_75",    # 2
    "primary_second_molar_85",    # 3
    "second_premolar_15",          # 4
    "second_premolar_25",          # 5
    "second_premolar_35",          # 6
    "second_premolar_45"           # 7
]

# Color palette for visualization (BGR format)
COLORS = [
    (255, 0, 0),      # Blue - primary_second_molar_55
    (0, 255, 0),      # Green - primary_second_molar_65
    (0, 0, 255),      # Red - primary_second_molar_75
    (255, 255, 0),    # Cyan - primary_second_molar_85
    (255, 0, 255),    # Magenta - second_premolar_15
    (0, 255, 255),    # Yellow - second_premolar_25
    (128, 128, 0),    # Teal - second_premolar_35
    (128, 0, 128)     # Purple - second_premolar_45
]


class BoundingBox:
    """Represents a single bounding box annotation"""
    def __init__(self, x1: int, y1: int, x2: int, y2: int, class_id: int, confidence: float = 1.0):
        self.x1 = min(x1, x2)
        self.y1 = min(y1, y2)
        self.x2 = max(x1, x2)
        self.y2 = max(y1, y2)
        self.class_id = class_id
        self.confidence = confidence
        
    def to_yolo(self, img_width: int, img_height: int) -> str:
        """Convert to YOLO format: class_id x_center y_center width height (normalized)"""
        x_center = ((self.x1 + self.x2) / 2) / img_width
        y_center = ((self.y1 + self.y2) / 2) / img_height
        width = (self.x2 - self.x1) / img_width
        height = (self.y2 - self.y1) / img_height
        return f"{self.class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}"
    
    @staticmethod
    def from_yolo(line: str, img_width: int, img_height: int) -> 'BoundingBox':
        """Create BoundingBox from YOLO format line"""
        parts = line.strip().split()
        class_id = int(parts[0])
        x_center = float(parts[1]) * img_width
        y_center = float(parts[2]) * img_height
        width = float(parts[3]) * img_width
        height = float(parts[4]) * img_height
        
        x1 = int(x_center - width / 2)
        y1 = int(y_center - height / 2)
        x2 = int(x_center + width / 2)
        y2 = int(y_center + height / 2)
        
        return BoundingBox(x1, y1, x2, y2, class_id)
    
    def contains_point(self, x: int, y: int) -> bool:
        """Check if point is inside the bounding box"""
        return self.x1 <= x <= self.x2 and self.y1 <= y <= self.y2
    
    def get_area(self) -> int:
        """Calculate bounding box area"""
        return (self.x2 - self.x1) * (self.y2 - self.y1)


class ToothAnnotationTool:
    """Interactive annotation tool for dental X-rays"""
    
    def __init__(self, images_dir: str, labels_dir: str, output_dir: str, 
                 ai_assist: bool = False, model_path: Optional[str] = None):
        self.images_dir = Path(images_dir)
        self.labels_dir = Path(labels_dir)
        self.output_dir = Path(output_dir)
        self.ai_assist = ai_assist
        self.model_path = model_path
        
        # Create output directories
        self.output_dir.mkdir(parents=True, exist_ok=True)
        (self.output_dir / 'images').mkdir(exist_ok=True)
        (self.output_dir / 'labels').mkdir(exist_ok=True)
        
        # Get list of images
        self.image_files = sorted(self.images_dir.glob('*.jpg')) + \
                          sorted(self.images_dir.glob('*.jpeg')) + \
                          sorted(self.images_dir.glob('*.png')) + \
                          sorted(self.images_dir.glob('*.tif'))
        
        if not self.image_files:
            raise ValueError(f"No images found in {images_dir}")
        
        print(f"📸 Found {len(self.image_files)} images to annotate")
        
        # Current state
        self.current_idx = 0
        self.current_image = None
        self.display_image = None
        self.img_height = 0
        self.img_width = 0
        
        # Annotation state
        self.boxes: List[BoundingBox] = []
        self.current_class = 0
        self.drawing = False
        self.start_point = None
        self.selected_box_idx = None
        
        # Window settings
        self.window_name = "🦷 Tooth Annotation Tool"
        self.scale = 1.0
        
        # Progress tracking
        self.progress_file = self.output_dir / 'annotation_progress.json'
        self.progress = self.load_progress()
        
        # AI model (optional)
        self.model = None
        if self.ai_assist and self.model_path:
            self.load_ai_model()
    
    def load_ai_model(self):
        """Load YOLO model for AI-assisted annotation"""
        try:
            from ultralytics import YOLO
            print(f"🤖 Loading AI model from {self.model_path}...")
            self.model = YOLO(self.model_path)
            print("✅ AI model loaded successfully")
        except Exception as e:
            print(f"⚠️  Failed to load AI model: {e}")
            self.ai_assist = False
    
    def load_progress(self) -> Dict:
        """Load annotation progress from file"""
        if self.progress_file.exists():
            with open(self.progress_file, 'r') as f:
                return json.load(f)
        return {'annotated': [], 'last_index': 0}
    
    def save_progress(self):
        """Save annotation progress to file"""
        with open(self.progress_file, 'w') as f:
            json.dump(self.progress, f, indent=2)
    
    def load_image(self, idx: int):
        """Load image and existing annotations"""
        self.current_idx = idx
        img_path = self.image_files[idx]
        
        print(f"\n📷 Loading image {idx + 1}/{len(self.image_files)}: {img_path.name}")
        
        # Load image
        self.current_image = cv2.imread(str(img_path))
        if self.current_image is None:
            print(f"❌ Failed to load image: {img_path}")
            return False
        
        self.img_height, self.img_width = self.current_image.shape[:2]
        
        # Try to load existing annotations
        label_path = self.labels_dir / f"{img_path.stem}.txt"
        self.boxes = []
        
        if label_path.exists():
            print(f"📝 Loading existing annotations from {label_path.name}")
            with open(label_path, 'r') as f:
                for line in f:
                    if line.strip():
                        box = BoundingBox.from_yolo(line, self.img_width, self.img_height)
                        self.boxes.append(box)
            print(f"✅ Loaded {len(self.boxes)} existing annotations")
        elif self.ai_assist and self.model:
            # AI-assisted pre-annotation
            self.ai_preannotate()
        
        self.update_display()
        return True
    
    def ai_preannotate(self):
        """Use AI model to suggest bounding boxes"""
        print("🤖 Running AI pre-annotation...")
        try:
            results = self.model(self.current_image, conf=0.3)
            
            # Note: Generic COCO model won't detect teeth properly
            # This is just to demonstrate the workflow
            # In production, you'd use a trained dental model
            
            for result in results:
                if result.boxes is not None:
                    for box in result.boxes:
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        # Map to tooth class (you'd need proper mapping here)
                        self.boxes.append(BoundingBox(x1, y1, x2, y2, 0, float(box.conf[0])))
            
            print(f"🎯 AI suggested {len(self.boxes)} boxes (review and correct them!)")
        except Exception as e:
            print(f"⚠️  AI pre-annotation failed: {e}")
    
    def update_display(self):
        """Update the display with current annotations"""
        self.display_image = self.current_image.copy()
        
        # Draw all bounding boxes
        for i, box in enumerate(self.boxes):
            color = COLORS[box.class_id % len(COLORS)]
            
            # Highlight selected box
            thickness = 3 if i == self.selected_box_idx else 2
            
            cv2.rectangle(self.display_image, 
                         (box.x1, box.y1), 
                         (box.x2, box.y2), 
                         color, thickness)
            
            # Add label
            label = f"{TOOTH_CLASSES[box.class_id]}"
            if box.confidence < 1.0:
                label += f" {box.confidence:.2f}"
            
            label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            cv2.rectangle(self.display_image,
                         (box.x1, box.y1 - label_size[1] - 8),
                         (box.x1 + label_size[0] + 4, box.y1),
                         color, -1)
            cv2.putText(self.display_image, label,
                       (box.x1 + 2, box.y1 - 4),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Draw current class info
        self.draw_info_panel()
        
        # If drawing, show rectangle
        if self.drawing and self.start_point is not None:
            cv2.rectangle(self.display_image,
                         self.start_point,
                         self.end_point,
                         COLORS[self.current_class], 2)
        
        cv2.imshow(self.window_name, self.display_image)
    
    def draw_info_panel(self):
        """Draw information panel on the image"""
        panel_height = 120
        panel = np.zeros((panel_height, self.img_width, 3), dtype=np.uint8)
        
        # Current class
        class_text = f"Current Class [{self.current_class}]: {TOOTH_CLASSES[self.current_class]}"
        cv2.putText(panel, class_text, (10, 25), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Progress
        progress_text = f"Image: {self.current_idx + 1}/{len(self.image_files)} | Boxes: {len(self.boxes)}"
        cv2.putText(panel, progress_text, (10, 50),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        # Controls
        controls = "SPACE: Next | B: Back | S: Save | D: Delete | 0-7: Change Class | Q: Quit"
        cv2.putText(panel, controls, (10, 80),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        
        # Combine with image
        self.display_image = np.vstack([self.display_image, panel])
    
    def mouse_callback(self, event, x, y, flags, param):
        """Handle mouse events for drawing bounding boxes"""
        if event == cv2.EVENT_LBUTTONDOWN:
            # Start drawing
            self.drawing = True
            self.start_point = (x, y)
            self.end_point = (x, y)
            
        elif event == cv2.EVENT_MOUSEMOVE:
            if self.drawing:
                self.end_point = (x, y)
                self.update_display()
            
        elif event == cv2.EVENT_LBUTTONUP:
            if self.drawing:
                self.drawing = False
                self.end_point = (x, y)
                
                # Create bounding box if it has valid size
                if abs(self.end_point[0] - self.start_point[0]) > 10 and \
                   abs(self.end_point[1] - self.start_point[1]) > 10:
                    box = BoundingBox(
                        self.start_point[0], self.start_point[1],
                        self.end_point[0], self.end_point[1],
                        self.current_class
                    )
                    self.boxes.append(box)
                    print(f"✅ Added box for {TOOTH_CLASSES[self.current_class]}")
                
                self.update_display()
        
        elif event == cv2.EVENT_RBUTTONDOWN:
            # Select box for deletion
            for i, box in enumerate(self.boxes):
                if box.contains_point(x, y):
                    self.selected_box_idx = i
                    self.update_display()
                    break
    
    def save_annotations(self):
        """Save annotations to YOLO format"""
        img_name = self.image_files[self.current_idx].name
        label_name = self.image_files[self.current_idx].stem + '.txt'
        
        # Save to output directory
        label_path = self.output_dir / 'labels' / label_name
        
        with open(label_path, 'w') as f:
            for box in self.boxes:
                f.write(box.to_yolo(self.img_width, self.img_height) + '\n')
        
        # Copy image to output
        import shutil
        shutil.copy(self.image_files[self.current_idx],
                   self.output_dir / 'images' / img_name)
        
        # Update progress
        if img_name not in self.progress['annotated']:
            self.progress['annotated'].append(img_name)
        self.progress['last_index'] = self.current_idx
        self.save_progress()
        
        print(f"💾 Saved {len(self.boxes)} annotations to {label_name}")
    
    def run(self):
        """Main annotation loop"""
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        cv2.setMouseCallback(self.window_name, self.mouse_callback)
        
        # Start from last position
        start_idx = self.progress.get('last_index', 0)
        if not self.load_image(start_idx):
            return
        
        print("\n" + "="*60)
        print("🦷 TOOTH ANNOTATION TOOL")
        print("="*60)
        print("\nControls:")
        print("  🖱️  Left Click + Drag: Draw bounding box")
        print("  🖱️  Right Click: Select box for deletion")
        print("  0-7: Change tooth class")
        print("  D: Delete selected box")
        print("  S: Save annotations")
        print("  SPACE: Next image")
        print("  B: Previous image")
        print("  Q: Quit")
        print("="*60 + "\n")
        
        while True:
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):
                print("\n👋 Quitting annotation tool")
                break
            
            elif key == ord('s'):
                self.save_annotations()
            
            elif key == ord(' '):  # Space
                self.save_annotations()
                if self.current_idx < len(self.image_files) - 1:
                    self.load_image(self.current_idx + 1)
                else:
                    print("\n🎉 All images annotated!")
                    break
            
            elif key == ord('b'):
                if self.current_idx > 0:
                    self.load_image(self.current_idx - 1)
            
            elif key == ord('d'):
                if self.selected_box_idx is not None:
                    removed = self.boxes.pop(self.selected_box_idx)
                    print(f"🗑️  Deleted box for {TOOTH_CLASSES[removed.class_id]}")
                    self.selected_box_idx = None
                    self.update_display()
            
            elif ord('0') <= key <= ord('7'):
                self.current_class = key - ord('0')
                print(f"🔄 Changed class to: {TOOTH_CLASSES[self.current_class]}")
                self.update_display()
        
        cv2.destroyAllWindows()
        print("\n📊 Annotation Statistics:")
        print(f"  Total images: {len(self.image_files)}")
        print(f"  Annotated: {len(self.progress['annotated'])}")
        print(f"  Remaining: {len(self.image_files) - len(self.progress['annotated'])}")


def create_dataset_yaml(output_dir: Path):
    """Create dataset.yaml file for YOLO training"""
    yaml_content = f"""# Tooth Detection Dataset
path: {output_dir.absolute()}
train: images
val: images

# Classes
names:
  0: primary_second_molar_55
  1: primary_second_molar_65
  2: primary_second_molar_75
  3: primary_second_molar_85
  4: second_premolar_15
  5: second_premolar_25
  6: second_premolar_35
  7: second_premolar_45
"""
    
    yaml_path = output_dir / 'dataset.yaml'
    with open(yaml_path, 'w') as f:
        f.write(yaml_content)
    print(f"📄 Created dataset.yaml at {yaml_path}")


def main():
    parser = argparse.ArgumentParser(
        description='🦷 Interactive Tooth Annotation Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic annotation
  python tooth_annotation_tool.py --images data/samples --output annotated_data
  
  # With AI-assisted pre-annotation
  python tooth_annotation_tool.py --images data/samples --output annotated_data \\
    --ai-assist --model backend/yolov8n.pt
        """
    )
    
    parser.add_argument('--images', type=str, required=True,
                       help='Directory containing images to annotate')
    parser.add_argument('--labels', type=str, default=None,
                       help='Directory with existing labels (optional)')
    parser.add_argument('--output', type=str, required=True,
                       help='Output directory for annotated data')
    parser.add_argument('--ai-assist', action='store_true',
                       help='Enable AI-assisted pre-annotation')
    parser.add_argument('--model', type=str, default='yolov8n.pt',
                       help='Path to YOLO model for AI assistance')
    
    args = parser.parse_args()
    
    # Use labels from output if not specified
    labels_dir = args.labels if args.labels else args.images
    
    print("\n" + "="*60)
    print("🦷 TOOTHY WIDTH MATE - ANNOTATION TOOL")
    print("="*60)
    print(f"📂 Images: {args.images}")
    print(f"📝 Labels: {labels_dir}")
    print(f"💾 Output: {args.output}")
    print(f"🤖 AI Assist: {args.ai_assist}")
    if args.ai_assist:
        print(f"📦 Model: {args.model}")
    print("="*60 + "\n")
    
    try:
        tool = ToothAnnotationTool(
            images_dir=args.images,
            labels_dir=labels_dir,
            output_dir=args.output,
            ai_assist=args.ai_assist,
            model_path=args.model if args.ai_assist else None
        )
        
        tool.run()
        
        # Create dataset.yaml for YOLO training
        create_dataset_yaml(Path(args.output))
        
        print("\n✅ Annotation complete!")
        print(f"📦 Annotated dataset ready at: {args.output}")
        print("\n🚀 Next steps:")
        print("  1. Review annotations for quality")
        print("  2. Split dataset into train/val/test")
        print("  3. Train YOLOv8 model:")
        print(f"     yolo train data={args.output}/dataset.yaml model=yolov8n.pt epochs=100")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
