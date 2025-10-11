"""
Enhanced Training Script for Dental Tooth Detection
Uses YOLOv8 transfer learning with aggressive augmentation
"""
from ultralytics import YOLO
import torch
import yaml
from pathlib import Path
import shutil
import os

class EnhancedDentalTrainer:
    def __init__(self, data_yaml='dataset/data.yaml'):
        self.data_yaml = data_yaml
        self.project_dir = 'runs/train'
        self.model_name = 'dental_detection_v2'
        
        # Check for GPU
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print(f"🔥 Using device: {self.device}")
        
    def validate_dataset(self):
        """Validate that dataset exists and has proper structure"""
        print("📋 Validating dataset...")
        
        with open(self.data_yaml, 'r') as f:
            data = yaml.safe_load(f)
        
        dataset_path = Path(data['path'])
        train_images = dataset_path / 'images' / 'train'
        val_images = dataset_path / 'images' / 'val'
        
        train_count = len(list(train_images.glob('*.jpg'))) + len(list(train_images.glob('*.png')))
        val_count = len(list(val_images.glob('*.jpg'))) + len(list(val_images.glob('*.png')))
        
        print(f"✅ Found {train_count} training images")
        print(f"✅ Found {val_count} validation images")
        
        if train_count == 0:
            print("⚠️  WARNING: No training images found!")
            print(f"   Expected images in: {train_images}")
            return False
            
        return True
    
    def create_dummy_labels_if_missing(self):
        """
        Creates dummy label files for training to work
        These should be replaced with real annotations later
        """
        print("🏷️  Checking for label files...")
        
        with open(self.data_yaml, 'r') as f:
            data = yaml.safe_load(f)
        
        dataset_path = Path(data['path'])
        
        for split in ['train', 'val', 'test']:
            images_dir = dataset_path / 'images' / split
            labels_dir = dataset_path / 'labels' / split
            
            if not images_dir.exists():
                continue
                
            labels_dir.mkdir(parents=True, exist_ok=True)
            
            # Check each image for corresponding label
            image_files = list(images_dir.glob('*.jpg')) + list(images_dir.glob('*.png'))
            
            for img_file in image_files:
                label_file = labels_dir / f"{img_file.stem}.txt"
                
                if not label_file.exists():
                    # Create a dummy label - this should be replaced with real annotations
                    # Format: class_id center_x center_y width height (normalized 0-1)
                    print(f"⚠️  Creating dummy label for: {img_file.name}")
                    
                    # Create 4 dummy boxes (2 molars, 2 premolars) in typical locations
                    # These are placeholder positions - REPLACE WITH REAL ANNOTATIONS
                    dummy_labels = [
                        "0 0.25 0.5 0.08 0.12",  # Upper left molar
                        "1 0.75 0.5 0.08 0.12",  # Upper right molar  
                        "4 0.30 0.5 0.06 0.10",  # Upper left premolar
                        "5 0.70 0.5 0.06 0.10",  # Upper right premolar
                    ]
                    
                    with open(label_file, 'w') as f:
                        f.write('\n'.join(dummy_labels))
        
        print("✅ Label file check complete")
        print("⚠️  IMPORTANT: Replace dummy labels with real annotations for better accuracy!")
    
    def train(self, epochs=100, imgsz=640, batch=8, patience=30):
        """
        Train the YOLOv8 model with enhanced augmentation
        """
        if not self.validate_dataset():
            print("❌ Dataset validation failed!")
            return None
        
        # Create dummy labels if missing (for initial testing)
        self.create_dummy_labels_if_missing()
        
        print("🚀 Starting training with transfer learning...")
        print(f"   Epochs: {epochs}")
        print(f"   Image size: {imgsz}")
        print(f"   Batch size: {batch}")
        print(f"   Patience: {patience}")
        
        # Load pre-trained YOLOv8 nano model
        model = YOLO('yolov8n.pt')  # Nano for speed, use yolov8s.pt or yolov8m.pt for better accuracy
        
        try:
            # Train with aggressive augmentation
            results = model.train(
                data=self.data_yaml,
                epochs=epochs,
                imgsz=imgsz,
                batch=batch,
                device=self.device,
                patience=patience,
                save=True,
                project=self.project_dir,
                name=self.model_name,
                exist_ok=True,
                
                # Augmentation parameters for dental X-rays
                hsv_h=0.015,          # Slight hue variation
                hsv_s=0.7,            # Saturation variation  
                hsv_v=0.4,            # Value/brightness variation
                degrees=10,           # Rotation up to 10 degrees
                translate=0.1,        # Translation
                scale=0.5,            # Scaling
                shear=2.0,            # Shearing
                perspective=0.0001,   # Perspective transformation
                flipud=0.0,           # No vertical flip (X-rays have orientation)
                fliplr=0.5,           # Horizontal flip 50% (left/right symmetry)
                mosaic=1.0,           # Mosaic augmentation
                mixup=0.1,            # Mixup augmentation
                copy_paste=0.1,       # Copy-paste augmentation
                
                # Optimizer settings
                optimizer='AdamW',
                lr0=0.001,            # Initial learning rate
                lrf=0.01,             # Final learning rate
                momentum=0.937,
                weight_decay=0.0005,
                warmup_epochs=3,
                warmup_momentum=0.8,
                warmup_bias_lr=0.1,
                
                # Performance settings
                amp=True,             # Automatic mixed precision
                close_mosaic=10,      # Disable mosaic in last N epochs
                
                # Validation
                val=True,
                plots=True,
                save_period=10,       # Save checkpoint every 10 epochs
            )
            
            print("\n✅ Training completed successfully!")
            
            # Get best model path
            best_model_path = Path(self.project_dir) / self.model_name / 'weights' / 'best.pt'
            
            if best_model_path.exists():
                print(f"📦 Best model saved to: {best_model_path}")
                
                # Copy to main models directory
                models_dir = Path('models')
                models_dir.mkdir(exist_ok=True)
                
                destination = models_dir / 'best.pt'
                shutil.copy(best_model_path, destination)
                print(f"📦 Model copied to: {destination}")
                
                # Also copy to backend directory for easy access
                backend_models = Path('backend/models')
                backend_models.mkdir(exist_ok=True)
                shutil.copy(best_model_path, backend_models / 'best.pt')
                print(f"📦 Model copied to: {backend_models / 'best.pt'}")
                
                return str(destination)
            else:
                print("⚠️  Warning: Best model file not found")
                return None
                
        except Exception as e:
            print(f"❌ Training failed with error: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def evaluate(self, model_path='models/best.pt'):
        """Evaluate the trained model"""
        print(f"\n📊 Evaluating model: {model_path}")
        
        if not Path(model_path).exists():
            print(f"❌ Model not found: {model_path}")
            return
        
        model = YOLO(model_path)
        
        # Run validation
        results = model.val(
            data=self.data_yaml,
            imgsz=640,
            batch=8,
            conf=0.25,
            iou=0.45,
            device=self.device,
        )
        
        print("\n📈 Evaluation Results:")
        print(f"   mAP50: {results.box.map50:.3f}")
        print(f"   mAP50-95: {results.box.map:.3f}")
        print(f"   Precision: {results.box.mp:.3f}")
        print(f"   Recall: {results.box.mr:.3f}")

def main():
    """Main training function"""
    print("=" * 60)
    print("🦷 DENTAL TOOTH DETECTION - Enhanced Training")
    print("=" * 60)
    
    trainer = EnhancedDentalTrainer()
    
    # Train model
    model_path = trainer.train(
        epochs=100,      # Increase if you have more data
        imgsz=640,       # Image size
        batch=8,         # Reduce if running out of memory
        patience=30      # Early stopping patience
    )
    
    if model_path:
        print("\n" + "=" * 60)
        print("✅ TRAINING COMPLETE!")
        print("=" * 60)
        print(f"\n📦 Model saved to: {model_path}")
        print("\n📝 Next steps:")
        print("   1. Review training plots in runs/train/dental_detection_v2/")
        print("   2. Test the model with: python scripts/test_detection.py")
        print("   3. Start the backend: cd backend && python app.py")
        print("   4. Annotate more data for better accuracy!")
        print("\n⚠️  IMPORTANT: Current model uses dummy labels!")
        print("   For production use, annotate your data properly.")
        
        # Evaluate the model
        trainer.evaluate(model_path)
    else:
        print("\n❌ Training failed. Please check the logs above.")

if __name__ == '__main__':
    main()
