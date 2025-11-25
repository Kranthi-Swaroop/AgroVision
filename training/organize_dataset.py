"""
AgroSentinel - Dataset Organization Script
Organizes PlantVillage dataset into train/val/test splits
"""

import os
import shutil
import random
from pathlib import Path
from collections import defaultdict

# Configuration
RANDOM_SEED = 42
TRAIN_RATIO = 0.8
VAL_RATIO = 0.15
TEST_RATIO = 0.05

random.seed(RANDOM_SEED)

# Class name mapping for clean labels
CLASS_MAPPING = {
    'Tomato_Bacterial_spot': 'tomato_bacterial_spot',
    'Tomato_Early_blight': 'tomato_early_blight',
    'Tomato_Late_blight': 'tomato_late_blight',
    'Tomato_Leaf_Mold': 'tomato_leaf_mold',
    'Tomato_Septoria_leaf_spot': 'tomato_septoria_leaf_spot',
    'Tomato_Spider_mites_Two_spotted_spider_mite': 'tomato_spider_mites',
    'Tomato__Target_Spot': 'tomato_target_spot',
    'Tomato__Tomato_mosaic_virus': 'tomato_mosaic_virus',
    'Tomato__Tomato_YellowLeaf__Curl_Virus': 'tomato_yellow_leaf_curl_virus',
    'Tomato_healthy': 'tomato_healthy',
    'Potato___Early_blight': 'potato_early_blight',
    'Potato___Late_blight': 'potato_late_blight',
    'Potato___healthy': 'potato_healthy',
    'Pepper__bell___Bacterial_spot': 'pepper_bacterial_spot',
    'Pepper__bell___healthy': 'pepper_healthy',
}

# Disease info for India focus
DISEASE_INFO = {
    'tomato_bacterial_spot': {'crop': 'Tomato', 'disease': 'Bacterial Spot', 'severity': 'medium'},
    'tomato_early_blight': {'crop': 'Tomato', 'disease': 'Early Blight', 'severity': 'high'},
    'tomato_late_blight': {'crop': 'Tomato', 'disease': 'Late Blight', 'severity': 'critical'},
    'tomato_leaf_mold': {'crop': 'Tomato', 'disease': 'Leaf Mold', 'severity': 'medium'},
    'tomato_septoria_leaf_spot': {'crop': 'Tomato', 'disease': 'Septoria Leaf Spot', 'severity': 'medium'},
    'tomato_spider_mites': {'crop': 'Tomato', 'disease': 'Spider Mites', 'severity': 'medium'},
    'tomato_target_spot': {'crop': 'Tomato', 'disease': 'Target Spot', 'severity': 'medium'},
    'tomato_mosaic_virus': {'crop': 'Tomato', 'disease': 'Mosaic Virus', 'severity': 'high'},
    'tomato_yellow_leaf_curl_virus': {'crop': 'Tomato', 'disease': 'Yellow Leaf Curl Virus', 'severity': 'critical'},
    'tomato_healthy': {'crop': 'Tomato', 'disease': 'Healthy', 'severity': 'none'},
    'potato_early_blight': {'crop': 'Potato', 'disease': 'Early Blight', 'severity': 'high'},
    'potato_late_blight': {'crop': 'Potato', 'disease': 'Late Blight', 'severity': 'critical'},
    'potato_healthy': {'crop': 'Potato', 'disease': 'Healthy', 'severity': 'none'},
    'pepper_bacterial_spot': {'crop': 'Pepper', 'disease': 'Bacterial Spot', 'severity': 'medium'},
    'pepper_healthy': {'crop': 'Pepper', 'disease': 'Healthy', 'severity': 'none'},
}


def count_images(folder):
    """Count image files in a folder"""
    extensions = {'.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG'}
    return sum(1 for f in folder.iterdir() if f.is_file() and f.suffix in extensions)


def get_images(folder):
    """Get all image files in a folder"""
    extensions = {'.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG'}
    return [f for f in folder.iterdir() if f.is_file() and f.suffix in extensions]


def main():
    print("=" * 60)
    print("AgroSentinel Dataset Organization")
    print("=" * 60)
    
    # Setup paths
    script_dir = Path(__file__).parent
    source_root = script_dir / 'datasets' / 'plantvillage_raw' / 'PlantVillage'
    dest_root = script_dir / 'datasets' / 'agrosentinel'
    
    if not source_root.exists():
        print(f"\n❌ Source not found: {source_root}")
        return
    
    print(f"\nSource: {source_root}")
    print(f"Destination: {dest_root}")
    
    # Remove existing if present
    if dest_root.exists():
        print(f"\n⚠ Removing existing destination...")
        shutil.rmtree(dest_root)
    
    # Create destination directories
    for split in ['train', 'val', 'test']:
        (dest_root / split).mkdir(parents=True, exist_ok=True)
    
    # Find matching folders
    print("\n" + "=" * 60)
    print("Scanning source folders...")
    print("=" * 60)
    
    available_folders = list(source_root.iterdir())
    print(f"Found {len(available_folders)} folders in source")
    
    # Map source folders to our classes
    folder_mapping = {}
    for folder in available_folders:
        if not folder.is_dir():
            continue
        folder_name = folder.name
        
        # Try exact match
        if folder_name in CLASS_MAPPING:
            folder_mapping[folder_name] = CLASS_MAPPING[folder_name]
            continue
            
        # Try fuzzy match
        for orig_name, clean_name in CLASS_MAPPING.items():
            # Handle variations in naming
            normalized_folder = folder_name.lower().replace(' ', '_').replace('-', '_')
            normalized_orig = orig_name.lower().replace(' ', '_').replace('-', '_')
            
            if normalized_folder == normalized_orig:
                folder_mapping[folder_name] = clean_name
                break
    
    print(f"\nMatched {len(folder_mapping)} classes:")
    for orig, clean in sorted(folder_mapping.items()):
        count = count_images(source_root / orig)
        print(f"  {orig} -> {clean} ({count} images)")
    
    # Organize dataset
    print("\n" + "=" * 60)
    print("Organizing dataset...")
    print("=" * 60)
    
    stats = defaultdict(lambda: {'train': 0, 'val': 0, 'test': 0, 'total': 0})
    
    for orig_name, clean_name in folder_mapping.items():
        source_folder = source_root / orig_name
        images = get_images(source_folder)
        
        if not images:
            print(f"⚠ No images in {orig_name}")
            continue
        
        # Shuffle and split
        random.shuffle(images)
        n_total = len(images)
        n_train = int(n_total * TRAIN_RATIO)
        n_val = int(n_total * VAL_RATIO)
        
        train_images = images[:n_train]
        val_images = images[n_train:n_train + n_val]
        test_images = images[n_train + n_val:]
        
        # Copy images
        for split_name, split_images in [('train', train_images), ('val', val_images), ('test', test_images)]:
            dest_folder = dest_root / split_name / clean_name
            dest_folder.mkdir(parents=True, exist_ok=True)
            
            for img in split_images:
                shutil.copy2(img, dest_folder / img.name)
            
            stats[clean_name][split_name] = len(split_images)
        
        stats[clean_name]['total'] = n_total
        print(f"✓ {clean_name}: {n_total} images -> train:{len(train_images)} val:{len(val_images)} test:{len(test_images)}")
    
    # Create class mapping file
    print("\n" + "=" * 60)
    print("Creating class mapping...")
    print("=" * 60)
    
    classes = sorted([v for v in folder_mapping.values()])
    
    mapping_file = script_dir / 'class_mapping.py'
    with open(mapping_file, 'w') as f:
        f.write('"""Auto-generated class mapping for AgroSentinel model"""\n\n')
        f.write(f'CLASSES = {classes}\n\n')
        f.write(f'NUM_CLASSES = {len(classes)}\n\n')
        f.write('CLASS_TO_IDX = {\n')
        for idx, cls in enumerate(classes):
            f.write(f'    "{cls}": {idx},\n')
        f.write('}\n\n')
        f.write('IDX_TO_CLASS = {\n')
        for idx, cls in enumerate(classes):
            f.write(f'    {idx}: "{cls}",\n')
        f.write('}\n\n')
        f.write('DISEASE_INFO = {\n')
        for cls in classes:
            if cls in DISEASE_INFO:
                info = DISEASE_INFO[cls]
                f.write(f'    "{cls}": {{"crop": "{info["crop"]}", "disease": "{info["disease"]}", "severity": "{info["severity"]}"}},\n')
        f.write('}\n')
    
    print(f"✓ Class mapping saved to: {mapping_file}")
    
    # Print summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    total_train = sum(s['train'] for s in stats.values())
    total_val = sum(s['val'] for s in stats.values())
    total_test = sum(s['test'] for s in stats.values())
    total = sum(s['total'] for s in stats.values())
    
    print(f"\nTotal Classes: {len(stats)}")
    print(f"Total Images: {total}")
    print(f"  - Train: {total_train} ({100*total_train/total:.1f}%)")
    print(f"  - Val: {total_val} ({100*total_val/total:.1f}%)")
    print(f"  - Test: {total_test} ({100*total_test/total:.1f}%)")
    
    print("\n" + "=" * 60)
    print("✓ Dataset organization complete!")
    print("=" * 60)
    print(f"\nDataset ready at: {dest_root}")
    print(f"\nNext step: python train_model.py")


if __name__ == '__main__':
    main()
