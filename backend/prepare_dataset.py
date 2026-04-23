"""
Prepare PlantVillage dataset for training
Filters only Tomato and Potato diseases we need
"""
import os
import shutil
from pathlib import Path
import random

# Classes we need (matching exact folder names in Dataset)
REQUIRED_CLASSES = [
    'Potato___Early_blight',      # Triple underscore
    'Potato___Late_blight',        # Triple underscore
    'Potato___healthy',            # Triple underscore
    'Tomato_Early_blight',         # Single underscore
    'Tomato_Late_blight',          # Single underscore
    'Tomato_healthy'               # Single underscore
]

def prepare_dataset(source_dir, target_dir):
    """
    Filter and organize dataset
    
    Args:
        source_dir: Downloaded PlantVillage folder
        target_dir: Target dataset folder
    """
    
    print("=" * 50)
    print("Dataset Preparation for Biological Sprinkler")
    print("=" * 50)
    
    # Create train/val directories
    train_dir = os.path.join(target_dir, 'train')
    val_dir = os.path.join(target_dir, 'val')
    
    os.makedirs(train_dir, exist_ok=True)
    os.makedirs(val_dir, exist_ok=True)
    
    total_train = 0
    total_val = 0
    
    # Process each required class
    for class_name in REQUIRED_CLASSES:
        source_class_dir = os.path.join(source_dir, class_name)
        
        if not os.path.exists(source_class_dir):
            print(f"⚠ Warning: {class_name} not found in {source_dir}")
            print(f"  Looking for: {source_class_dir}")
            continue
        
        # Get all images
        images = [f for f in os.listdir(source_class_dir) 
                 if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        
        if len(images) == 0:
            print(f"⚠ Warning: No images found in {class_name}")
            continue
        
        # Shuffle for random split
        random.shuffle(images)
        
        total = len(images)
        split_idx = int(total * 0.8)  # 80% train, 20% val
        
        # Create class directories
        train_class_dir = os.path.join(train_dir, class_name)
        val_class_dir = os.path.join(val_dir, class_name)
        os.makedirs(train_class_dir, exist_ok=True)
        os.makedirs(val_class_dir, exist_ok=True)
        
        # Copy to train
        print(f"\nProcessing {class_name}...")
        for i, img in enumerate(images[:split_idx]):
            src = os.path.join(source_class_dir, img)
            dst = os.path.join(train_class_dir, img)
            shutil.copy2(src, dst)
            if (i + 1) % 100 == 0:
                print(f"  Copied {i + 1} training images...")
        
        # Copy to val
        for img in images[split_idx:]:
            src = os.path.join(source_class_dir, img)
            dst = os.path.join(val_class_dir, img)
            shutil.copy2(src, dst)
        
        total_train += split_idx
        total_val += (total - split_idx)
        
        print(f"✓ {class_name}: {split_idx} train, {total-split_idx} val")
    
    print("\n" + "=" * 50)
    print("Dataset Preparation Complete!")
    print("=" * 50)
    print(f"Total training images: {total_train}")
    print(f"Total validation images: {total_val}")
    print(f"\nTrain directory: {train_dir}")
    print(f"Val directory: {val_dir}")
    print("\nNext step: Run 'python model_training.py' to train the model")
    print("=" * 50)

if __name__ == '__main__':
    import sys
    
    # Default paths - Updated to match actual dataset location
    source = r"d:\biological sprinkler\Dataset"  # Source has all class folders
    target = r"d:\biological sprinkler\dataset"  # Target will have train/val
    
    # Check if custom paths provided
    if len(sys.argv) >= 2:
        source = sys.argv[1]
    if len(sys.argv) >= 3:
        target = sys.argv[2]
    
    print(f"Source directory: {source}")
    print(f"Target directory: {target}")
    
    if not os.path.exists(source):
        print(f"\n✗ Error: Source directory not found: {source}")
        print("\nUsage:")
        print("  python prepare_dataset.py [source_dir] [target_dir]")
        print("\nExample:")
        print('  python prepare_dataset.py "d:\\Dataset" "d:\\biological sprinkler\\dataset"')
        sys.exit(1)
    
    prepare_dataset(source, target)
