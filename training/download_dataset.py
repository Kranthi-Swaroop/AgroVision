import os
import shutil
import zipfile
import urllib.request
from pathlib import Path
from tqdm import tqdm
import ssl


ssl._create_default_https_context = ssl._create_unverified_context

DATASET_DIR = Path("datasets")
FINAL_DATASET_DIR = DATASET_DIR / "agrosentinel_dataset"


KAGGLE_DATASETS = {
    "plantvillage": {
        "url": "https://data.mendeley.com/public-files/datasets/tywbtsjrjv/files/d5652a28-c1d8-4b76-97f3-72fb80f94efc/file_downloaded",
        "name": "PlantVillage Dataset"
    }
}

CLASSES_TO_KEEP = [
    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot",
    "Corn_(maize)___Common_rust_",
    "Corn_(maize)___Northern_Leaf_Blight",
    "Corn_(maize)___healthy",
    "Grape___Black_rot",
    "Grape___Esca_(Black_Measles)",
    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)",
    "Grape___healthy",
    "Potato___Early_blight",
    "Potato___Late_blight",
    "Potato___healthy",
    "Tomato___Bacterial_spot",
    "Tomato___Early_blight",
    "Tomato___Late_blight",
    "Tomato___Leaf_Mold",
    "Tomato___Septoria_leaf_spot",
    "Tomato___Spider_mites Two-spotted_spider_mite",
    "Tomato___Target_Spot",
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus",
    "Tomato___Tomato_mosaic_virus",
    "Tomato___healthy",
    "Apple___Apple_scab",
    "Apple___Black_rot",
    "Apple___Cedar_apple_rust",
    "Apple___healthy",
    "Pepper,_bell___Bacterial_spot",
    "Pepper,_bell___healthy",
]


class DownloadProgress(tqdm):
    def update_to(self, b=1, bsize=1, tsize=None):
        if tsize is not None:
            self.total = tsize
        self.update(b * bsize - self.n)


def download_file(url, dest_path, desc="Downloading"):
    dest_path = Path(dest_path)
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    
    with DownloadProgress(unit='B', unit_scale=True, miniters=1, desc=desc) as t:
        urllib.request.urlretrieve(url, dest_path, reporthook=t.update_to)
    
    return dest_path


def setup_plantvillage():
    print("="*60)
    print("PlantVillage Dataset Setup")
    print("="*60)
    
    zip_path = DATASET_DIR / "plantvillage.zip"
    extract_dir = DATASET_DIR / "plantvillage_raw"
    
    if not zip_path.exists():
        print("\nOption 1: Download from Mendeley (2.3 GB)")
        print("Option 2: Download from Kaggle (requires account)")
        print("\nAttempting Mendeley download...")
        
        url = "https://data.mendeley.com/public-files/datasets/tywbtsjrjv/files/d5652a28-c1d8-4b76-97f3-72fb80f94efc/file_downloaded"
        
        try:
            download_file(url, zip_path, "PlantVillage")
        except Exception as e:
            print(f"\nAutomatic download failed: {e}")
            print("\nPlease download manually:")
            print("1. Go to: https://www.kaggle.com/datasets/emmarex/plantdisease")
            print("2. Download and extract to:", DATASET_DIR / "plantvillage_raw")
            print("3. Run this script again")
            return False
    
    if not extract_dir.exists() and zip_path.exists():
        print("\nExtracting dataset...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        print("Extraction complete!")
    
    return True


def organize_dataset():
    print("\n" + "="*60)
    print("Organizing Dataset")
    print("="*60)
    
    raw_dir = DATASET_DIR / "plantvillage_raw"
    
    plant_dir = None
    for item in raw_dir.rglob("*"):
        if item.is_dir() and "Plant" in item.name:
            plant_dir = item
            break
    
    if not plant_dir:
        for item in raw_dir.iterdir():
            if item.is_dir():
                plant_dir = item
                break
    
    if not plant_dir:
        print("Could not find dataset directory structure")
        return False
    
    train_dir = FINAL_DATASET_DIR / "train"
    val_dir = FINAL_DATASET_DIR / "val"
    train_dir.mkdir(parents=True, exist_ok=True)
    val_dir.mkdir(parents=True, exist_ok=True)
    
    total_train = 0
    total_val = 0
    
    for class_dir in sorted(plant_dir.iterdir()):
        if not class_dir.is_dir():
            continue
        
        class_name = class_dir.name.replace(" ", "_")
        
        images = list(class_dir.glob("*.[jJ][pP][gG]")) + \
                 list(class_dir.glob("*.[jJ][pP][eE][gG]")) + \
                 list(class_dir.glob("*.[pP][nN][gG]"))
        
        if len(images) == 0:
            continue
        
        split_idx = int(len(images) * 0.85)
        train_images = images[:split_idx]
        val_images = images[split_idx:]
        
        train_class_dir = train_dir / class_name
        val_class_dir = val_dir / class_name
        train_class_dir.mkdir(exist_ok=True)
        val_class_dir.mkdir(exist_ok=True)
        
        for img in train_images:
            shutil.copy2(img, train_class_dir / img.name)
        for img in val_images:
            shutil.copy2(img, val_class_dir / img.name)
        
        total_train += len(train_images)
        total_val += len(val_images)
        print(f"  {class_name}: {len(train_images)} train, {len(val_images)} val")
    
    print(f"\nTotal: {total_train} training, {total_val} validation images")
    return True


def create_dataset_yaml():
    train_dir = FINAL_DATASET_DIR / "train"
    
    if not train_dir.exists():
        print("No training directory found!")
        return []
    
    classes = sorted([d.name for d in train_dir.iterdir() if d.is_dir()])
    
    yaml_content = f"""path: {FINAL_DATASET_DIR.absolute()}
train: train
val: val

nc: {len(classes)}
names: {classes}
"""
    
    yaml_path = FINAL_DATASET_DIR / "dataset.yaml"
    with open(yaml_path, "w") as f:
        f.write(yaml_content)
    
    class_list_path = FINAL_DATASET_DIR / "classes.txt"
    with open(class_list_path, "w") as f:
        for i, cls in enumerate(classes):
            f.write(f"{i}: {cls}\n")
    
    print(f"\nDataset YAML created: {yaml_path}")
    print(f"Total classes: {len(classes)}")
    
    return classes


def main():
    print("="*60)
    print("AgroSentinel Dataset Preparation v2")
    print("="*60)
    
    DATASET_DIR.mkdir(parents=True, exist_ok=True)
    
    if setup_plantvillage():
        if organize_dataset():
            classes = create_dataset_yaml()
            
            print("\n" + "="*60)
            print("SETUP COMPLETE!")
            print("="*60)
            print(f"Dataset location: {FINAL_DATASET_DIR.absolute()}")
            print(f"Classes: {len(classes)}")
            print("\nNext step: Run train_model.py")
        else:
            print("\nDataset organization failed. Check the directory structure.")
    else:
        print("\nDataset download failed. Please download manually.")


if __name__ == "__main__":
    main()
