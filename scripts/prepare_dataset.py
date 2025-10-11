import shutil
from pathlib import Path
from sklearn.model_selection import train_test_split
import yaml

def prepare_yolo_dataset():
    """Organize dataset for YOLO training"""
    
    print("🔧 Preparing YOLO dataset...")
    
    # Create directory structure
    dataset_root = Path("dataset")
    for split in ['train', 'val']:
        (dataset_root / split / 'images').mkdir(parents=True, exist_ok=True)
        (dataset_root / split / 'labels').mkdir(parents=True, exist_ok=True)
    
    # Get all annotated images
    images_dir = Path("data/samples")
    labels_dir = Path("dataset/labels")
    
    image_files = []
    for ext in ['*.jpg', '*.jpeg', '*.png', '*.tif']:
        image_files.extend(list(images_dir.glob(ext)))
    
    # Filter images that have labels
    annotated_images = []
    for img_file in image_files:
        label_file = labels_dir / f"{img_file.stem}.txt"
        if label_file.exists():
            annotated_images.append(img_file)
    
    print(f"📊 Found {len(annotated_images)} annotated images")
    
    if len(annotated_images) == 0:
        print("❌ No annotated images found! Please run annotation first.")
        return False
    
    # Split into train/val (80/20)
    train_images, val_images = train_test_split(
        annotated_images, 
        test_size=0.2, 
        random_state=42
    )
    
    print(f"📂 Train set: {len(train_images)} images")
    print(f"📂 Val set: {len(val_images)} images")
    
    # Copy files to respective directories
    for split_name, image_list in [('train', train_images), ('val', val_images)]:
        for img_file in image_list:
            # Copy image
            dst_img = dataset_root / split_name / 'images' / img_file.name
            shutil.copy2(img_file, dst_img)
            
            # Copy label
            label_file = labels_dir / f"{img_file.stem}.txt"
            dst_label = dataset_root / split_name / 'labels' / f"{img_file.stem}.txt"
            shutil.copy2(label_file, dst_label)
    
    # Create dataset.yaml for YOLO
    dataset_yaml = {
        'path': str(dataset_root.absolute()),
        'train': 'train/images',
        'val': 'val/images',
        'nc': 8,
        'names': ['55', '65', '75', '85', '15', '25', '35', '45']
    }
    
    yaml_path = dataset_root / 'dataset.yaml'
    with open(yaml_path, 'w') as f:
        yaml.dump(dataset_yaml, f, default_flow_style=False)
    
    print(f"✅ Dataset prepared successfully!")
    print(f"📄 Config saved to: {yaml_path}")
    
    return True

if __name__ == "__main__":
    success = prepare_yolo_dataset()
    if success:
        print("\n✨ Ready for training!")
        print("   Run: python scripts/train_yolo.py")
