import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torchvision import transforms, datasets, models
from sklearn.metrics import classification_report, confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path
import json
import numpy as np


MODEL_DIR = Path("models")
DATASET_DIR = Path("datasets/agrosentinel_dataset")


def load_model(checkpoint_path, num_classes, model_name="efficientnet_b2"):
    if model_name == "efficientnet_b2":
        model = models.efficientnet_b2(weights=None)
        model.classifier[1] = nn.Linear(model.classifier[1].in_features, num_classes)
    elif model_name == "efficientnet_b0":
        model = models.efficientnet_b0(weights=None)
        model.classifier[1] = nn.Linear(model.classifier[1].in_features, num_classes)
    elif model_name == "resnet50":
        model = models.resnet50(weights=None)
        model.fc = nn.Linear(model.fc.in_features, num_classes)
    
    checkpoint = torch.load(checkpoint_path, map_location='cpu')
    model.load_state_dict(checkpoint['model_state_dict'])
    model.eval()
    
    return model


def main():
    print("="*60)
    print("Model Evaluation")
    print("="*60)
    
    with open(MODEL_DIR / "training_config.json") as f:
        config = json.load(f)
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    model = load_model(
        MODEL_DIR / "agrosentinel_best.pth",
        config['num_classes'],
        config['model_name']
    ).to(device)
    
    val_transform = transforms.Compose([
        transforms.Resize((config['img_size'], config['img_size'])),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])
    
    val_dataset = datasets.ImageFolder(DATASET_DIR / "val", transform=val_transform)
    val_loader = DataLoader(val_dataset, batch_size=32, shuffle=False, num_workers=4)
    
    class_names = config['class_names']
    
    all_preds = []
    all_labels = []
    all_probs = []
    
    with torch.no_grad():
        for images, labels in val_loader:
            images = images.to(device)
            outputs = model(images)
            probs = torch.softmax(outputs, dim=1)
            _, predicted = outputs.max(1)
            
            all_preds.extend(predicted.cpu().numpy())
            all_labels.extend(labels.numpy())
            all_probs.extend(probs.cpu().numpy())
    
    all_preds = np.array(all_preds)
    all_labels = np.array(all_labels)
    all_probs = np.array(all_probs)
    
    print("\n" + "="*60)
    print("CLASSIFICATION REPORT")
    print("="*60)
    
    short_names = [n.split("___")[-1][:20] for n in class_names]
    print(classification_report(all_labels, all_preds, target_names=short_names, digits=3))
    
    accuracy = (all_preds == all_labels).sum() / len(all_labels) * 100
    print(f"\nOverall Accuracy: {accuracy:.2f}%")
    
    cm = confusion_matrix(all_labels, all_preds)
    
    plt.figure(figsize=(20, 16))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=short_names, yticklabels=short_names)
    plt.xlabel('Predicted')
    plt.ylabel('True')
    plt.title('Confusion Matrix')
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    plt.tight_layout()
    plt.savefig(MODEL_DIR / "confusion_matrix.png", dpi=150)
    plt.close()
    print(f"\nConfusion matrix saved: {MODEL_DIR / 'confusion_matrix.png'}")
    
    top1_correct = (all_preds == all_labels).sum()
    top5_correct = 0
    for i, label in enumerate(all_labels):
        top5_preds = np.argsort(all_probs[i])[-5:]
        if label in top5_preds:
            top5_correct += 1
    
    print(f"\nTop-1 Accuracy: {top1_correct / len(all_labels) * 100:.2f}%")
    print(f"Top-5 Accuracy: {top5_correct / len(all_labels) * 100:.2f}%")
    
    per_class_acc = {}
    for i, name in enumerate(class_names):
        mask = all_labels == i
        if mask.sum() > 0:
            acc = (all_preds[mask] == i).sum() / mask.sum() * 100
            per_class_acc[name] = acc
    
    sorted_acc = sorted(per_class_acc.items(), key=lambda x: x[1])
    
    print("\n" + "="*60)
    print("WORST PERFORMING CLASSES (Need more data/augmentation)")
    print("="*60)
    for name, acc in sorted_acc[:5]:
        print(f"  {name}: {acc:.1f}%")
    
    print("\n" + "="*60)
    print("BEST PERFORMING CLASSES")
    print("="*60)
    for name, acc in sorted_acc[-5:]:
        print(f"  {name}: {acc:.1f}%")
    
    eval_results = {
        'accuracy': accuracy,
        'top5_accuracy': top5_correct / len(all_labels) * 100,
        'per_class_accuracy': per_class_acc,
        'num_samples': len(all_labels)
    }
    
    with open(MODEL_DIR / "evaluation_results.json", "w") as f:
        json.dump(eval_results, f, indent=2)
    
    print(f"\nEvaluation results saved: {MODEL_DIR / 'evaluation_results.json'}")


if __name__ == "__main__":
    main()
