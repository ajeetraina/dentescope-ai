#!/usr/bin/env python3
import os
import shutil
from pathlib import Path
import random

def organize_dataset():
    print("Organizing Dental Dataset")
    print("=" * 50)
    
    # Correct path to your data
    source_dir = Path('../data/samples')
    
    # Get all JPG files
    all_images = list(source_dir.glob('*.jpg'))
    
    total_images = len(all_images)
    print(f"\nFound {total_images} images in ../data/samples/")
    
    if total_images == 0:
        print("Error: No images found!")
        return
    
    # Create dataset structure in backend
    dataset_dir = Path('dataset')
    for split in ['train', 'val', 'test']:
        (dataset_dir / 'images' / split).mkdir(parents=True, exist_ok=True)
        (dataset_dir / 'labels' / split).mkdir(parents=True, exist_ok=True)
    
    # Shuffle and split (80/10/10)
    random.seed(42)
    random.shuffle(all_images)
    
    train_idx = int(0.8 * total_images)
    val_idx = int(0.9 * total_images)
    
    train_images = all_images[:train_idx]
    val_images = all_images[train_idx:val_idx]
    test_images = all_images[val_idx:]
    
    # Copy images
    print("\nCopying images...")
    for img in train_images:
        shutil.copy(img, dataset_dir / 'images' / 'train' / img.name)
    print(f"  Train: {len(train_images)} images")
    
    for img in val_images:
        shutil.copy(img, dataset_dir / 'images' / 'val' / img.name)
    print(f"  Val: {len(val_images)} images")
    
    for img in test_images:
        shutil.copy(img, dataset_dir / 'images' / 'test' / img.name)
    print(f"  Test: {len(test_images)} images")
    
    print("\nDataset organized successfully!")
    
    # Recommendations
    if total_images < 100:
        print(f"\nWarning: Only {total_images} images. Recommend 100+ for good accuracy")
    else:
        print(f"\nGreat! {total_images} images is sufficient for training")
    
    print("\nNext step: Label the images")
    print("  labelimg dataset/images/train dataset/classes.txt dataset/labels/train")

if __name__ == '__main__':
    organize_dataset()
