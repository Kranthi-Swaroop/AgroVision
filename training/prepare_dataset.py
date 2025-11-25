import os
import shutil
import urllib.request
import zipfile
from pathlib import Path
from tqdm import tqdm


DATASET_DIR = Path("datasets")
PLANTVILLAGE_DIR = DATASET_DIR / "plantvillage"
INDIAN_CROPS_DIR = DATASET_DIR / "indian_crops"
FINAL_DATASET_DIR = DATASET_DIR / "agrosentinel_dataset"

INDIAN_CROP_CLASSES = [
    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot",
    "Corn_(maize)___Common_rust_",
    "Corn_(maize)___Northern_Leaf_Blight",
    "Corn_(maize)___healthy",
    "Potato___Early_blight",
    "Potato___Late_blight", 
    "Potato___healthy",
    "Rice___Brown_Spot",
    "Rice___Leaf_Blast",
    "Rice___Neck_Blast",
    "Rice___healthy",
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
    "Wheat___Brown_Rust",
    "Wheat___Yellow_Rust",
    "Wheat___Septoria",
    "Wheat___healthy",
    "Cotton___Bacterial_Blight",
    "Cotton___Curl_Virus",
    "Cotton___Fusarium_Wilt",
    "Cotton___healthy",
    "Grape___Black_rot",
    "Grape___Esca_(Black_Measles)",
    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)",
    "Grape___healthy",
]

SEVERITY_MAPPING = {
    "Early_blight": ["early", "moderate", "severe"],
    "Late_blight": ["early", "moderate", "severe"],
    "Leaf_Blast": ["early", "moderate", "severe"],
    "Brown_Spot": ["early", "moderate", "severe"],
    "Bacterial_spot": ["early", "moderate", "severe"],
}


class DownloadProgressBar(tqdm):
    def update_to(self, b=1, bsize=1, tsize=None):
        if tsize is not None:
            self.total = tsize
        self.update(b * bsize - self.n)


def download_plantvillage():
    print("Setting up PlantVillage dataset...")
    print("\nPlantVillage dataset needs to be downloaded from Kaggle.")
    print("Please follow these steps:\n")
    print("1. Go to: https://www.kaggle.com/datasets/emmarex/plantdisease")
    print("2. Click 'Download' (requires free Kaggle account)")
    print("3. Extract the ZIP file")
    print(f"4. Move the 'PlantVillage' folder to: {PLANTVILLAGE_DIR.absolute()}")
    print("\nAlternatively, run this command if you have kaggle CLI:")
    print("  kaggle datasets download -d emmarex/plantdisease")
    print(f"  unzip plantdisease.zip -d {DATASET_DIR.absolute()}")
    
    DATASET_DIR.mkdir(parents=True, exist_ok=True)
    PLANTVILLAGE_DIR.mkdir(parents=True, exist_ok=True)
    
    if not any(PLANTVILLAGE_DIR.iterdir()):
        print(f"\nWaiting for dataset at: {PLANTVILLAGE_DIR.absolute()}")
        print("Press Enter once you've placed the dataset, or type 'skip' to continue with demo data...")
        user_input = input().strip().lower()
        if user_input == 'skip':
            print("Skipping PlantVillage, creating demo structure...")
            create_demo_plantvillage()
    else:
        print(f"PlantVillage dataset found at {PLANTVILLAGE_DIR}")


def create_demo_plantvillage():
    demo_classes = [
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
    ]
    
    for cls in demo_classes:
        cls_dir = PLANTVILLAGE_DIR / cls
        cls_dir.mkdir(parents=True, exist_ok=True)


def download_rice_disease_dataset():
    print("\nSetting up Rice Disease dataset...")
    
    rice_dir = INDIAN_CROPS_DIR / "rice"
    rice_dir.mkdir(parents=True, exist_ok=True)
    
    print("Rice disease images should be added to:")
    for cls in ["Rice___Brown_Spot", "Rice___Leaf_Blast", "Rice___Neck_Blast", "Rice___healthy"]:
        cls_path = rice_dir / cls
        cls_path.mkdir(parents=True, exist_ok=True)
        print(f"  {cls_path}")
    
    print("\nYou can download rice disease images from:")
    print("  https://www.kaggle.com/datasets/minhhuy2810/rice-diseases-image-dataset")
    print("  https://www.kaggle.com/datasets/vbookshelf/rice-leaf-diseases")


def download_wheat_disease_dataset():
    print("Downloading Wheat Disease dataset...")
    
    wheat_dir = INDIAN_CROPS_DIR / "wheat"
    wheat_dir.mkdir(parents=True, exist_ok=True)
    
    print("Creating wheat disease classes (add your own images)...")
    for cls in ["Wheat___Brown_Rust", "Wheat___Yellow_Rust", "Wheat___Septoria", "Wheat___healthy"]:
        (wheat_dir / cls).mkdir(parents=True, exist_ok=True)


def download_cotton_disease_dataset():
    print("Downloading Cotton Disease dataset...")
    
    cotton_dir = INDIAN_CROPS_DIR / "cotton"
    cotton_dir.mkdir(parents=True, exist_ok=True)
    
    print("Creating cotton disease classes (add your own images)...")
    for cls in ["Cotton___Bacterial_Blight", "Cotton___Curl_Virus", "Cotton___Fusarium_Wilt", "Cotton___healthy"]:
        (cotton_dir / cls).mkdir(parents=True, exist_ok=True)


def filter_indian_crops():
    print("Filtering Indian-relevant crops from PlantVillage...")
    
    FINAL_DATASET_DIR.mkdir(parents=True, exist_ok=True)
    train_dir = FINAL_DATASET_DIR / "train"
    val_dir = FINAL_DATASET_DIR / "val"
    train_dir.mkdir(exist_ok=True)
    val_dir.mkdir(exist_ok=True)
    
    plantvillage_classes = [
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
    ]
    
    for cls_name in plantvillage_classes:
        src_dir = PLANTVILLAGE_DIR / cls_name
        if not src_dir.exists():
            for subdir in PLANTVILLAGE_DIR.iterdir():
                if subdir.is_dir():
                    potential = subdir / cls_name
                    if potential.exists():
                        src_dir = potential
                        break
        
        if src_dir.exists():
            clean_name = cls_name.replace(" ", "_").replace("(", "").replace(")", "")
            
            images = list(src_dir.glob("*.[jJ][pP][gG]")) + list(src_dir.glob("*.[pP][nN][gG]"))
            
            if len(images) == 0:
                continue
                
            split_idx = int(len(images) * 0.85)
            train_images = images[:split_idx]
            val_images = images[split_idx:]
            
            train_cls_dir = train_dir / clean_name
            val_cls_dir = val_dir / clean_name
            train_cls_dir.mkdir(exist_ok=True)
            val_cls_dir.mkdir(exist_ok=True)
            
            for img in train_images:
                shutil.copy2(img, train_cls_dir / img.name)
            for img in val_images:
                shutil.copy2(img, val_cls_dir / img.name)
            
            print(f"  {clean_name}: {len(train_images)} train, {len(val_images)} val")


def add_indian_crops():
    print("Adding Indian crop datasets...")
    
    train_dir = FINAL_DATASET_DIR / "train"
    val_dir = FINAL_DATASET_DIR / "val"
    
    for crop_dir in INDIAN_CROPS_DIR.iterdir():
        if crop_dir.is_dir():
            for cls_dir in crop_dir.iterdir():
                if cls_dir.is_dir():
                    images = list(cls_dir.glob("*.[jJ][pP][gG]")) + list(cls_dir.glob("*.[pP][nN][gG]"))
                    
                    if len(images) == 0:
                        continue
                    
                    split_idx = int(len(images) * 0.85)
                    train_images = images[:split_idx]
                    val_images = images[split_idx:]
                    
                    clean_name = cls_dir.name.replace(" ", "_")
                    train_cls_dir = train_dir / clean_name
                    val_cls_dir = val_dir / clean_name
                    train_cls_dir.mkdir(exist_ok=True)
                    val_cls_dir.mkdir(exist_ok=True)
                    
                    for img in train_images:
                        shutil.copy2(img, train_cls_dir / img.name)
                    for img in val_images:
                        shutil.copy2(img, val_cls_dir / img.name)
                    
                    print(f"  {clean_name}: {len(train_images)} train, {len(val_images)} val")


def create_dataset_yaml():
    train_dir = FINAL_DATASET_DIR / "train"
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
    
    print(f"\nDataset YAML created: {yaml_path}")
    print(f"Total classes: {len(classes)}")
    
    class_list_path = FINAL_DATASET_DIR / "classes.txt"
    with open(class_list_path, "w") as f:
        for i, cls in enumerate(classes):
            f.write(f"{i}: {cls}\n")
    
    return classes


def print_dataset_stats():
    print("\n" + "="*50)
    print("DATASET STATISTICS")
    print("="*50)
    
    train_dir = FINAL_DATASET_DIR / "train"
    val_dir = FINAL_DATASET_DIR / "val"
    
    total_train = 0
    total_val = 0
    
    for cls_dir in sorted(train_dir.iterdir()):
        if cls_dir.is_dir():
            train_count = len(list(cls_dir.glob("*")))
            val_count = len(list((val_dir / cls_dir.name).glob("*"))) if (val_dir / cls_dir.name).exists() else 0
            total_train += train_count
            total_val += val_count
            print(f"{cls_dir.name}: {train_count} train, {val_count} val")
    
    print("="*50)
    print(f"TOTAL: {total_train} training, {total_val} validation images")
    print("="*50)


def main():
    print("="*50)
    print("AgroSentinel Dataset Preparation")
    print("="*50 + "\n")
    
    download_plantvillage()
    
    download_rice_disease_dataset()
    download_wheat_disease_dataset()
    download_cotton_disease_dataset()
    
    filter_indian_crops()
    
    add_indian_crops()
    
    classes = create_dataset_yaml()
    
    print_dataset_stats()
    
    print("\nDataset preparation complete!")
    print(f"Dataset location: {FINAL_DATASET_DIR.absolute()}")
    print(f"\nNext step: Run train_model.py")


if __name__ == "__main__":
    main()
