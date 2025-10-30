#!/usr/bin/env python3
"""
🦷 Dentescope-AI Training Script for NVIDIA Jetson Thor
Optimized for edge AI dental detection training

Author: Ajeet Singh Raina
Hardware: NVIDIA Jetson AGX Thor (128GB, 2070 TFLOPS)
"""

import os
import sys
import time
import torch
from ultralytics import YOLO
from pathlib import Path
import json
from datetime import datetime

class ThorDentalTrainer:
    def __init__(self, model_size='m', project_name='dental_thor'):
        """
        Initialize trainer for Jetson Thor
        
        Args:
            model_size: 'n', 's', 'm', 'l', 'x' (nano to extra-large)
            project_name: Name for this training run
        """
        self.model_size = model_size
        self.project_name = project_name
        self.device = 0 if torch.cuda.is_available() else 'cpu'
        
        # Thor-optimized settings
        self.thor_config = {
            'n': {'batch': 64, 'epochs': 100, 'imgsz': 640},   # Fast training
            's': {'batch': 48, 'epochs': 120, 'imgsz': 640},   # Balanced
            'm': {'batch': 32, 'epochs': 150, 'imgsz': 1024},  # Recommended
            'l': {'batch': 24, 'epochs': 180, 'imgsz': 1024},  # High accuracy
            'x': {'batch': 16, 'epochs': 200, 'imgsz': 1280},  # Maximum
        }
        
    def check_system(self):
        """Verify Thor system requirements"""
        print("🔍 Checking System...")
        
        # Check CUDA
        if not torch.cuda.is_available():
            print("❌ CUDA not available! Training will be slow.")
            return False
            
        # Check GPU
        gpu_name = torch.cuda.get_device_name(0)
        gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        
        print(f"✅ GPU: {gpu_name}")
        print(f"✅ GPU Memory: {gpu_memory:.1f} GB")
        print(f"✅ PyTorch: {torch.__version__}")
        print(f"✅ CUDA: {torch.version.cuda}")
        
        return True
        
    def check_dataset(self):
        """Verify dataset exists and is properly formatted"""
        print("\n📊 Checking Dataset...")
        
        dataset_path = Path('dataset')
        data_yaml = dataset_path / 'data.yaml'
        
        if not data_yaml.exists():
            print("❌ dataset/data.yaml not found!")
            print("💡 Run: python3 scripts/prepare_dataset.py")
            return False
            
        # Count images
        train_imgs = list((dataset_path / 'train' / 'images').glob('*.jpg'))
        val_imgs = list((dataset_path / 'val' / 'images').glob('*.jpg'))
        
        print(f"✅ Training images: {len(train_imgs)}")
        print(f"✅ Validation images: {len(val_imgs)}")
        
        if len(train_imgs) < 10:
            print("⚠️  Warning: Very few training images. Consider adding more.")
            
        return True
        
    def train(self, resume=False):
        """Start training with Thor-optimized settings"""
        
        # System checks
        if not self.check_system():
            return None
            
        if not self.check_dataset():
            return None
            
        print(f"\n🚀 Starting Training (Model: YOLOv8{self.model_size})")
        print("="*60)
        
        # Get Thor-optimized config
        config = self.thor_config[self.model_size]
        
        # Initialize model
        model_path = f'yolov8{self.model_size}.pt'
        print(f"📥 Loading {model_path}...")
        model = YOLO(model_path)
        
        # Training arguments
        train_args = {
            'data': 'dataset/data.yaml',
            'epochs': config['epochs'],
            'imgsz': config['imgsz'],
            'batch': config['batch'],
            'device': self.device,
            
            # Thor optimizations
            'cache': True,           # Use 128GB RAM!
            'amp': True,             # Mixed precision
            'workers': 8,            # Multi-threading
            
            # Training settings
            'patience': 20,          # Early stopping
            'save': True,
            'save_period': 10,       # Save every 10 epochs
            'plots': True,
            'verbose': True,
            
            # Augmentation
            'hsv_h': 0.015,
            'hsv_s': 0.7,
            'hsv_v': 0.4,
            'degrees': 10.0,
            'translate': 0.1,
            'scale': 0.5,
            'shear': 2.0,
            'perspective': 0.0,
            'flipud': 0.5,
            'fliplr': 0.5,
            'mosaic': 1.0,
            'mixup': 0.1,
            
            # Output
            'project': 'runs/detect',
            'name': f'{self.project_name}_{self.model_size}_{datetime.now().strftime("%Y%m%d_%H%M")}',
            'exist_ok': True,
        }
        
        if resume:
            train_args['resume'] = True
            
        # Print configuration
        print("\n⚙️  Training Configuration:")
        for key, value in train_args.items():
            if key not in ['data', 'project']:
                print(f"  {key}: {value}")
        print()
        
        # Start training
        start_time = time.time()
        
        try:
            results = model.train(**train_args)
            
            # Training complete
            duration = time.time() - start_time
            hours = int(duration // 3600)
            minutes = int((duration % 3600) // 60)
            
            print("\n" + "="*60)
            print("✅ TRAINING COMPLETE!")
            print(f"⏱️  Duration: {hours}h {minutes}m")
            print(f"📁 Results: {results.save_dir}")
            print("="*60)
            
            # Save training summary
            self.save_summary(results, duration)
            
            return results
            
        except KeyboardInterrupt:
            print("\n⚠️  Training interrupted by user")
            return None
        except Exception as e:
            print(f"\n❌ Training failed: {e}")
            return None
            
    def save_summary(self, results, duration):
        """Save training summary"""
        summary = {
            'model_size': self.model_size,
            'project_name': self.project_name,
            'duration_seconds': duration,
            'device': str(self.device),
            'config': self.thor_config[self.model_size],
            'timestamp': datetime.now().isoformat(),
            'results_dir': str(results.save_dir),
        }
        
        summary_file = Path(results.save_dir) / 'training_summary.json'
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
            
        print(f"\n💾 Summary saved: {summary_file}")
        
    def validate(self, model_path=None):
        """Validate trained model"""
        print("\n🔍 Validating Model...")
        
        if model_path is None:
            # Find latest trained model
            model_path = self.find_latest_model()
            
        if not Path(model_path).exists():
            print(f"❌ Model not found: {model_path}")
            return None
            
        model = YOLO(model_path)
        metrics = model.val()
        
        print("\n📊 Validation Results:")
        print(f"  mAP50: {metrics.box.map50:.3f}")
        print(f"  mAP50-95: {metrics.box.map:.3f}")
        print(f"  Precision: {metrics.box.mp:.3f}")
        print(f"  Recall: {metrics.box.mr:.3f}")
        
        # Performance assessment
        if metrics.box.map50 > 0.70:
            print("  🌟 Excellent performance!")
        elif metrics.box.map50 > 0.50:
            print("  ✅ Good performance")
        else:
            print("  ⚠️  Performance could be improved")
            
        return metrics
        
    def export_tensorrt(self, model_path=None):
        """Export model to TensorRT for maximum inference speed"""
        print("\n🚀 Exporting to TensorRT...")
        
        if model_path is None:
            model_path = self.find_latest_model()
            
        if not Path(model_path).exists():
            print(f"❌ Model not found: {model_path}")
            return None
            
        model = YOLO(model_path)
        
        # Export to TensorRT
        engine_path = model.export(
            format='engine',
            device=self.device,
            half=True,  # FP16 for speed
            workspace=4,  # 4GB workspace
            verbose=True
        )
        
        print(f"✅ TensorRT engine: {engine_path}")
        print("💡 Use this for production inference (3-5x faster!)")
        
        return engine_path
        
    def find_latest_model(self):
        """Find the most recent trained model"""
        runs_dir = Path('runs/detect')
        
        if not runs_dir.exists():
            return None
            
        # Find all weight files
        weight_files = list(runs_dir.glob('**/weights/best.pt'))
        
        if not weight_files:
            return None
            
        # Return most recent
        latest = max(weight_files, key=lambda p: p.stat().st_mtime)
        return str(latest)


def main():
    """Main training script"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Train Dentescope-AI on Jetson Thor',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Train medium model (recommended)
  python3 train_thor.py
  
  # Train nano model (fastest)
  python3 train_thor.py --model n
  
  # Train large model (best accuracy)
  python3 train_thor.py --model l
  
  # Resume training
  python3 train_thor.py --resume
  
  # Validate model
  python3 train_thor.py --validate
  
  # Export to TensorRT
  python3 train_thor.py --export
        """
    )
    
    parser.add_argument(
        '--model', 
        type=str, 
        default='m',
        choices=['n', 's', 'm', 'l', 'x'],
        help='Model size (n=nano, s=small, m=medium, l=large, x=xlarge)'
    )
    
    parser.add_argument(
        '--project', 
        type=str, 
        default='dental_thor',
        help='Project name for this training run'
    )
    
    parser.add_argument(
        '--resume',
        action='store_true',
        help='Resume training from last checkpoint'
    )
    
    parser.add_argument(
        '--validate',
        action='store_true',
        help='Validate the trained model'
    )
    
    parser.add_argument(
        '--export',
        action='store_true',
        help='Export model to TensorRT'
    )
    
    parser.add_argument(
        '--model-path',
        type=str,
        help='Path to model for validation/export'
    )
    
    args = parser.parse_args()
    
    # Create trainer
    trainer = ThorDentalTrainer(
        model_size=args.model,
        project_name=args.project
    )
    
    print("🦷 Dentescope-AI Training on Jetson Thor")
    print("="*60)
    print(f"Model: YOLOv8{args.model}")
    print(f"Project: {args.project}")
    print("="*60)
    
    # Execute requested action
    if args.validate:
        trainer.validate(args.model_path)
        
    elif args.export:
        trainer.export_tensorrt(args.model_path)
        
    else:
        # Train model
        results = trainer.train(resume=args.resume)
        
        if results:
            print("\n🎯 Next Steps:")
            print("1. Validate model:")
            print(f"   python3 train_thor.py --validate")
            print("\n2. Export to TensorRT:")
            print(f"   python3 train_thor.py --export")
            print("\n3. Test inference:")
            print(f"   python3 scripts/test_model.py")
            print("\n4. Deploy to backend:")
            print(f"   cp {results.save_dir}/weights/best.pt backend/models/")


if __name__ == '__main__':
    main()
