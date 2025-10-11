#!/usr/bin/env python3
"""
Validation script to check if everything is set up correctly
"""

import sys
from pathlib import Path

def check_section(title, checks):
    """Run checks for a section"""
    print(f"\n{'='*60}")
    print(f"🔍 {title}")
    print('='*60)
    
    all_passed = True
    for check_name, check_func in checks:
        try:
            result = check_func()
            if result:
                print(f"✅ {check_name}")
            else:
                print(f"❌ {check_name}")
                all_passed = False
        except Exception as e:
            print(f"❌ {check_name}: {str(e)}")
            all_passed = False
    
    return all_passed

def check_python_version():
    """Check Python version"""
    return sys.version_info >= (3, 8)

def check_data_samples():
    """Check if sample images exist"""
    samples_dir = Path("data/samples")
    if not samples_dir.exists():
        return False
    images = list(samples_dir.glob("*.jpg")) + list(samples_dir.glob("*.tif"))
    return len(images) > 0

def check_scripts_exist():
    """Check if training scripts exist"""
    required_scripts = [
        "scripts/smart_annotator.py",
        "scripts/prepare_dataset.py",
        "scripts/train_yolo.py",
        "scripts/test_model.py"
    ]
    return all(Path(script).exists() for script in required_scripts)

def check_dependencies():
    """Check if key dependencies are installed"""
    try:
        import cv2
        import numpy
        import sklearn
        import yaml
        return True
    except ImportError as e:
        print(f"      Missing: {str(e)}")
        return False

def check_ultralytics():
    """Check if ultralytics is installed"""
    try:
        from ultralytics import YOLO
        return True
    except ImportError:
        return False

def check_annotations():
    """Check if any annotations exist"""
    labels_dir = Path("dataset/labels")
    if not labels_dir.exists():
        return None  # Not an error, just not done yet
    labels = list(labels_dir.glob("*.txt"))
    return len(labels) if len(labels) > 0 else None

def check_dataset_prepared():
    """Check if dataset is prepared"""
    dataset_yaml = Path("dataset/dataset.yaml")
    return dataset_yaml.exists()

def check_model_trained():
    """Check if model is trained"""
    model_path = Path("model/dental_detector.pt")
    return model_path.exists()

def main():
    """Run all validation checks"""
    print("🦷 Toothy Width Mate - Setup Validation")
    print("="*60)
    
    # Environment checks
    env_checks = [
        ("Python >= 3.8", check_python_version),
        ("Sample images exist (data/samples/)", check_data_samples),
        ("Training scripts exist", check_scripts_exist),
    ]
    env_passed = check_section("Environment Setup", env_checks)
    
    # Dependencies checks
    dep_checks = [
        ("Core dependencies (opencv, numpy, sklearn)", check_dependencies),
        ("Ultralytics YOLO", check_ultralytics),
    ]
    dep_passed = check_section("Python Dependencies", dep_checks)
    
    # Progress checks
    progress_checks = []
    
    # Check annotations
    annotation_count = check_annotations()
    if annotation_count is None:
        progress_checks.append(("Annotations created", lambda: False))
    elif annotation_count > 0:
        progress_checks.append((f"Annotations created ({annotation_count} images)", lambda: True))
    
    progress_checks.extend([
        ("Dataset prepared (train/val split)", check_dataset_prepared),
        ("Model trained", check_model_trained),
    ])
    
    progress_passed = check_section("Training Progress", progress_checks)
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 Summary")
    print('='*60)
    
    if env_passed and dep_passed:
        print("✅ Environment is ready!")
        
        if not annotation_count:
            print("\n📝 Next Step: Annotate your images")
            print("   Run: python scripts/smart_annotator.py")
        elif not check_dataset_prepared():
            print("\n📝 Next Step: Prepare dataset")
            print("   Run: python scripts/prepare_dataset.py")
        elif not check_model_trained():
            print("\n📝 Next Step: Train model")
            print("   Run: python scripts/train_yolo.py")
        else:
            print("\n🎉 Everything is complete!")
            print("   Test your model: python scripts/test_model.py")
            print("   Run the app: docker-compose up")
    else:
        print("❌ Setup incomplete. Please fix the issues above.")
        if not dep_passed:
            print("\n💡 Install dependencies:")
            print("   pip install -r scripts/requirements.txt")
    
    print(f"\n{'='*60}")
    print("📖 Need help? Check IMPLEMENTATION_GUIDE.md")
    print('='*60)

if __name__ == "__main__":
    main()
