from ultralytics import YOLO
from pathlib import Path
import torch

def train_yolo_model():
    """Train YOLOv8 model for dental tooth detection"""
    
    print("🚀 Starting YOLOv8 Training for Dental Tooth Detection")
    print("=" * 60)
    
    # Check if dataset is prepared
    dataset_yaml = Path("dataset/dataset.yaml")
    if not dataset_yaml.exists():
        print("❌ Dataset not prepared!")
        print("   Please run: python scripts/prepare_dataset.py")
        return
    
    # Check GPU availability
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"💻 Using device: {device}")
    
    # Load pretrained YOLOv8 nano model for transfer learning
    print("\n📥 Loading YOLOv8n model...")
    model = YOLO('yolov8n.pt')
    
    # Training parameters
    training_params = {
        'data': str(dataset_yaml),
        'epochs': 100,
        'imgsz': 640,
        'batch': 16,
        'patience': 20,
        'save': True,
        'device': device,
        'workers': 4,
        'project': 'runs/detect',
        'name': 'dental_tooth_detector',
        'exist_ok': True,
        
        # Augmentation
        'hsv_h': 0.015,
        'hsv_s': 0.7,
        'hsv_v': 0.4,
        'degrees': 10.0,
        'translate': 0.1,
        'scale': 0.5,
        'shear': 2.0,
        'perspective': 0.0,
        'flipud': 0.0,
        'fliplr': 0.5,
        'mosaic': 1.0,
        'mixup': 0.0,
        
        # Optimizer
        'optimizer': 'AdamW',
        'lr0': 0.001,
        'lrf': 0.01,
        'momentum': 0.937,
        'weight_decay': 0.0005,
        
        # Loss weights
        'box': 7.5,
        'cls': 0.5,
        'dfl': 1.5,
    }
    
    print("\n📊 Training Configuration:")
    print(f"   Epochs: {training_params['epochs']}")
    print(f"   Image Size: {training_params['imgsz']}")
    print(f"   Batch Size: {training_params['batch']}")
    print(f"   Device: {training_params['device']}")
    
    # Train the model
    print("\n🎓 Starting training...")
    results = model.train(**training_params)
    
    # Validate the model
    print("\n✅ Training complete! Running validation...")
    metrics = model.val()
    
    print("\n📈 Validation Metrics:")
    print(f"   mAP50: {metrics.box.map50:.4f}")
    print(f"   mAP50-95: {metrics.box.map:.4f}")
    
    # Export the model
    best_model_path = Path('runs/detect/dental_tooth_detector/weights/best.pt')
    if best_model_path.exists():
        print(f"\n💾 Best model saved to: {best_model_path}")
        
        # Copy to model directory
        model_dir = Path('model')
        model_dir.mkdir(exist_ok=True)
        import shutil
        shutil.copy2(best_model_path, model_dir / 'dental_detector.pt')
        print(f"   Model copied to: model/dental_detector.pt")
    
    print("\n🎉 Training completed successfully!")
    print("\nNext steps:")
    print("   1. Review training results in: runs/detect/dental_tooth_detector")
    print("   2. Test the model: python scripts/test_model.py")
    print("   3. Update backend to use the trained model")

if __name__ == "__main__":
    train_yolo_model()
