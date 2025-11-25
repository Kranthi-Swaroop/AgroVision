"""
AgroSentinel Model Training v2 - Improved Version
Fixes: 
- Cross-crop confusion (tomato vs potato)
- Confidence calibration issues
- Better generalization
"""
import os
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from torch.utils.data import DataLoader, WeightedRandomSampler
from torchvision import transforms, datasets, models
from pathlib import Path
import json
import numpy as np
from tqdm import tqdm
import matplotlib.pyplot as plt
from collections import Counter


DATASET_DIR = Path("datasets/agrosentinel")
MODEL_DIR = Path("models")
MODEL_DIR.mkdir(exist_ok=True)

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {DEVICE}")
if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")


class Config:
    img_size = 260  # Larger input for better detail
    batch_size = 24  # Slightly smaller for larger images
    epochs = 50
    lr = 0.0005  # Lower LR for stability
    weight_decay = 1e-4
    num_workers = 0
    patience = 12
    model_name = "efficientnet_b3"  # Larger model
    label_smoothing = 0.1  # Reduce overconfidence
    mixup_alpha = 0.2  # Mixup augmentation
    focal_gamma = 2.0  # Focal loss for hard examples


class LabelSmoothingCrossEntropy(nn.Module):
    """Cross Entropy with Label Smoothing - reduces overconfidence"""
    def __init__(self, smoothing=0.1):
        super().__init__()
        self.smoothing = smoothing
        
    def forward(self, pred, target):
        n_classes = pred.size(-1)
        log_preds = F.log_softmax(pred, dim=-1)
        
        # Smooth labels
        with torch.no_grad():
            smooth_labels = torch.zeros_like(log_preds)
            smooth_labels.fill_(self.smoothing / (n_classes - 1))
            smooth_labels.scatter_(1, target.unsqueeze(1), 1 - self.smoothing)
        
        loss = (-smooth_labels * log_preds).sum(dim=-1).mean()
        return loss


class FocalLoss(nn.Module):
    """Focal Loss - focuses on hard examples"""
    def __init__(self, gamma=2.0, smoothing=0.1):
        super().__init__()
        self.gamma = gamma
        self.smoothing = smoothing
        
    def forward(self, pred, target):
        ce_loss = F.cross_entropy(pred, target, reduction='none', label_smoothing=self.smoothing)
        pt = torch.exp(-ce_loss)
        focal_loss = ((1 - pt) ** self.gamma * ce_loss).mean()
        return focal_loss


def mixup_data(x, y, alpha=0.2):
    """Mixup augmentation - blends images to improve generalization"""
    if alpha > 0:
        lam = np.random.beta(alpha, alpha)
    else:
        lam = 1
    
    batch_size = x.size(0)
    index = torch.randperm(batch_size).to(x.device)
    
    mixed_x = lam * x + (1 - lam) * x[index]
    y_a, y_b = y, y[index]
    return mixed_x, y_a, y_b, lam


def mixup_criterion(criterion, pred, y_a, y_b, lam):
    """Loss for mixup"""
    return lam * criterion(pred, y_a) + (1 - lam) * criterion(pred, y_b)


def get_transforms():
    """Enhanced augmentations for better generalization"""
    train_transform = transforms.Compose([
        transforms.RandomResizedCrop(Config.img_size, scale=(0.7, 1.0)),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomVerticalFlip(p=0.3),
        transforms.RandomRotation(45),
        transforms.ColorJitter(brightness=0.4, contrast=0.4, saturation=0.4, hue=0.15),
        transforms.RandomAffine(degrees=0, translate=(0.15, 0.15), scale=(0.85, 1.15)),
        transforms.RandomPerspective(distortion_scale=0.2, p=0.3),
        transforms.GaussianBlur(kernel_size=5, sigma=(0.1, 2.5)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        transforms.RandomErasing(p=0.25, scale=(0.02, 0.2)),
    ])
    
    val_transform = transforms.Compose([
        transforms.Resize(Config.img_size + 20),
        transforms.CenterCrop(Config.img_size),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])
    
    return train_transform, val_transform


def create_model(num_classes):
    """Create model with dropout for better calibration"""
    if Config.model_name == "efficientnet_b3":
        model = models.efficientnet_b3(weights=models.EfficientNet_B3_Weights.IMAGENET1K_V1)
        # Add dropout before final classifier
        in_features = model.classifier[1].in_features
        model.classifier = nn.Sequential(
            nn.Dropout(p=0.4, inplace=True),
            nn.Linear(in_features, 512),
            nn.ReLU(inplace=True),
            nn.Dropout(p=0.3),
            nn.Linear(512, num_classes)
        )
    elif Config.model_name == "efficientnet_b2":
        model = models.efficientnet_b2(weights=models.EfficientNet_B2_Weights.IMAGENET1K_V1)
        in_features = model.classifier[1].in_features
        model.classifier = nn.Sequential(
            nn.Dropout(p=0.4, inplace=True),
            nn.Linear(in_features, 512),
            nn.ReLU(inplace=True),
            nn.Dropout(p=0.3),
            nn.Linear(512, num_classes)
        )
    
    return model.to(DEVICE)


def get_class_weights(dataset):
    """Calculate class weights for imbalanced data"""
    targets = [dataset.targets[i] for i in range(len(dataset))]
    class_counts = Counter(targets)
    total = len(targets)
    weights = {cls: total / count for cls, count in class_counts.items()}
    
    # Normalize
    max_weight = max(weights.values())
    weights = {cls: w / max_weight for cls, w in weights.items()}
    
    return torch.tensor([weights[i] for i in range(len(class_counts))], dtype=torch.float).to(DEVICE)


class EarlyStopping:
    def __init__(self, patience=10, min_delta=0.001):
        self.patience = patience
        self.min_delta = min_delta
        self.counter = 0
        self.best_loss = None
        self.early_stop = False
        
    def __call__(self, val_loss):
        if self.best_loss is None:
            self.best_loss = val_loss
        elif val_loss > self.best_loss - self.min_delta:
            self.counter += 1
            if self.counter >= self.patience:
                self.early_stop = True
        else:
            self.best_loss = val_loss
            self.counter = 0
        return self.early_stop


def train_epoch(model, loader, criterion, optimizer, scaler, use_mixup=True):
    model.train()
    running_loss = 0.0
    correct = 0
    total = 0
    
    pbar = tqdm(loader, desc="Training")
    for images, labels in pbar:
        images, labels = images.to(DEVICE), labels.to(DEVICE)
        
        optimizer.zero_grad()
        
        # Apply mixup with probability
        if use_mixup and np.random.random() < 0.5:
            images, labels_a, labels_b, lam = mixup_data(images, labels, Config.mixup_alpha)
            
            with torch.cuda.amp.autocast():
                outputs = model(images)
                loss = mixup_criterion(criterion, outputs, labels_a, labels_b, lam)
            
            # For accuracy, use original labels
            _, predicted = outputs.max(1)
            correct += (lam * predicted.eq(labels_a).sum().item() + 
                       (1 - lam) * predicted.eq(labels_b).sum().item())
        else:
            with torch.cuda.amp.autocast():
                outputs = model(images)
                loss = criterion(outputs, labels)
            
            _, predicted = outputs.max(1)
            correct += predicted.eq(labels).sum().item()
        
        scaler.scale(loss).backward()
        scaler.step(optimizer)
        scaler.update()
        
        running_loss += loss.item()
        total += labels.size(0)
        
        pbar.set_postfix({
            'loss': f'{running_loss/len(pbar):.4f}',
            'acc': f'{100.*correct/total:.2f}%'
        })
    
    return running_loss / len(loader), 100. * correct / total


def validate(model, loader, criterion):
    model.eval()
    running_loss = 0.0
    correct = 0
    total = 0
    
    all_preds = []
    all_labels = []
    all_probs = []
    
    with torch.no_grad():
        for images, labels in tqdm(loader, desc="Validating"):
            images, labels = images.to(DEVICE), labels.to(DEVICE)
            
            with torch.cuda.amp.autocast():
                outputs = model(images)
                loss = criterion(outputs, labels)
            
            probs = F.softmax(outputs, dim=1)
            
            running_loss += loss.item()
            _, predicted = outputs.max(1)
            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()
            
            all_preds.extend(predicted.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
            all_probs.extend(probs.cpu().numpy())
    
    return running_loss / len(loader), 100. * correct / total, all_preds, all_labels, all_probs


def analyze_confusion(preds, labels, class_names):
    """Analyze which classes are confused"""
    from collections import defaultdict
    
    confusion = defaultdict(lambda: defaultdict(int))
    
    for pred, label in zip(preds, labels):
        if pred != label:
            pred_name = class_names[pred]
            true_name = class_names[label]
            confusion[true_name][pred_name] += 1
    
    print("\n🔍 Confusion Analysis (Top misclassifications):")
    for true_class, pred_dict in sorted(confusion.items()):
        total_errors = sum(pred_dict.values())
        if total_errors > 0:
            top_confused = sorted(pred_dict.items(), key=lambda x: -x[1])[:3]
            print(f"  {true_class}:")
            for pred_class, count in top_confused:
                print(f"    → {pred_class}: {count} times")


def calibrate_temperature(model, val_loader, init_temp=1.5):
    """Learn optimal temperature for calibration"""
    model.eval()
    
    all_logits = []
    all_labels = []
    
    with torch.no_grad():
        for images, labels in val_loader:
            images = images.to(DEVICE)
            outputs = model(images)
            all_logits.append(outputs.cpu())
            all_labels.append(labels)
    
    logits = torch.cat(all_logits)
    labels = torch.cat(all_labels)
    
    # Optimize temperature
    temperature = nn.Parameter(torch.tensor(init_temp))
    optimizer = optim.LBFGS([temperature], lr=0.01, max_iter=50)
    
    def eval_temp():
        optimizer.zero_grad()
        loss = F.cross_entropy(logits / temperature, labels)
        loss.backward()
        return loss
    
    optimizer.step(eval_temp)
    
    optimal_temp = temperature.item()
    print(f"\n🌡️  Optimal Temperature: {optimal_temp:.3f}")
    return optimal_temp


def main():
    print("="*60)
    print("AgroSentinel Model Training v2 - Improved")
    print("="*60)
    print("\nImprovements:")
    print("  ✓ Label Smoothing - reduces overconfidence")
    print("  ✓ Focal Loss - focuses on hard examples")
    print("  ✓ Mixup - improves generalization")
    print("  ✓ Larger model (EfficientNet-B3)")
    print("  ✓ Better augmentations")
    print("  ✓ Temperature calibration")
    print("="*60)
    
    train_transform, val_transform = get_transforms()
    
    train_dataset = datasets.ImageFolder(DATASET_DIR / "train", transform=train_transform)
    val_dataset = datasets.ImageFolder(DATASET_DIR / "val", transform=val_transform)
    
    num_classes = len(train_dataset.classes)
    class_names = train_dataset.classes
    
    print(f"\n📊 Dataset:")
    print(f"  Training: {len(train_dataset)} images")
    print(f"  Validation: {len(val_dataset)} images")
    print(f"  Classes: {num_classes}")
    
    # Class distribution
    print(f"\n📈 Class distribution:")
    class_counts = Counter(train_dataset.targets)
    for idx, name in enumerate(class_names):
        print(f"  {name}: {class_counts[idx]} samples")
    
    # Save class names
    with open(MODEL_DIR / "class_names.json", "w") as f:
        json.dump(class_names, f, indent=2)
    
    # Create data loaders
    train_loader = DataLoader(
        train_dataset,
        batch_size=Config.batch_size,
        shuffle=True,
        num_workers=Config.num_workers,
        pin_memory=True,
        drop_last=True
    )
    
    val_loader = DataLoader(
        val_dataset,
        batch_size=Config.batch_size,
        shuffle=False,
        num_workers=Config.num_workers,
        pin_memory=True
    )
    
    # Create model
    print(f"\n🏗️  Creating {Config.model_name} model...")
    model = create_model(num_classes)
    
    # Count parameters
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"  Total parameters: {total_params:,}")
    print(f"  Trainable: {trainable_params:,}")
    
    # Loss with Focal Loss + Label Smoothing
    criterion = FocalLoss(gamma=Config.focal_gamma, smoothing=Config.label_smoothing)
    
    # Optimizer
    optimizer = optim.AdamW(
        model.parameters(),
        lr=Config.lr,
        weight_decay=Config.weight_decay
    )
    
    # Cosine annealing scheduler
    scheduler = optim.lr_scheduler.CosineAnnealingWarmRestarts(
        optimizer, T_0=10, T_mult=2, eta_min=1e-6
    )
    
    scaler = torch.cuda.amp.GradScaler()
    early_stopping = EarlyStopping(patience=Config.patience)
    
    # Training history
    history = {'train_loss': [], 'val_loss': [], 'train_acc': [], 'val_acc': []}
    best_val_acc = 0.0
    
    print(f"\n🚀 Starting training for {Config.epochs} epochs...")
    print(f"  Learning rate: {Config.lr}")
    print(f"  Label smoothing: {Config.label_smoothing}")
    print(f"  Focal loss gamma: {Config.focal_gamma}")
    print(f"  Mixup alpha: {Config.mixup_alpha}")
    print("-" * 60)
    
    for epoch in range(Config.epochs):
        print(f"\nEpoch {epoch+1}/{Config.epochs}")
        
        # Train
        train_loss, train_acc = train_epoch(
            model, train_loader, criterion, optimizer, scaler, 
            use_mixup=(epoch > 2)  # Start mixup after warmup
        )
        
        # Validate
        val_loss, val_acc, preds, labels, probs = validate(model, val_loader, criterion)
        
        # Update scheduler
        scheduler.step()
        
        # Log
        history['train_loss'].append(train_loss)
        history['val_loss'].append(val_loss)
        history['train_acc'].append(train_acc)
        history['val_acc'].append(val_acc)
        
        current_lr = optimizer.param_groups[0]['lr']
        print(f"  Train Loss: {train_loss:.4f} | Train Acc: {train_acc:.2f}%")
        print(f"  Val Loss: {val_loss:.4f} | Val Acc: {val_acc:.2f}%")
        print(f"  LR: {current_lr:.6f}")
        
        # Save best model
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            torch.save({
                'epoch': epoch + 1,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'val_acc': val_acc,
                'class_names': class_names
            }, MODEL_DIR / "agrosentinel_best_v2.pth")
            print(f"  ✓ New best model saved! ({val_acc:.2f}%)")
            
            # Analyze confusion for best model
            if val_acc > 95:
                analyze_confusion(preds, labels, class_names)
        
        # Early stopping
        if early_stopping(val_loss):
            print(f"\n⚠️  Early stopping at epoch {epoch+1}")
            break
    
    print("\n" + "="*60)
    print("Training Complete!")
    print(f"Best Validation Accuracy: {best_val_acc:.2f}%")
    print("="*60)
    
    # Load best model for temperature calibration
    checkpoint = torch.load(MODEL_DIR / "agrosentinel_best_v2.pth")
    model.load_state_dict(checkpoint['model_state_dict'])
    
    # Calibrate temperature
    optimal_temp = calibrate_temperature(model, val_loader)
    
    # Save training config
    config = {
        'model': Config.model_name,
        'img_size': Config.img_size,
        'best_val_acc': best_val_acc,
        'num_classes': num_classes,
        'class_names': class_names,
        'label_smoothing': Config.label_smoothing,
        'focal_gamma': Config.focal_gamma,
        'optimal_temperature': optimal_temp,
        'epochs_trained': len(history['train_loss'])
    }
    
    with open(MODEL_DIR / "training_config_v2.json", "w") as f:
        json.dump(config, f, indent=2)
    
    # Plot training history
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    axes[0].plot(history['train_loss'], label='Train Loss', color='blue')
    axes[0].plot(history['val_loss'], label='Val Loss', color='red')
    axes[0].set_xlabel('Epoch')
    axes[0].set_ylabel('Loss')
    axes[0].set_title('Training & Validation Loss')
    axes[0].legend()
    axes[0].grid(True)
    
    axes[1].plot(history['train_acc'], label='Train Acc', color='blue')
    axes[1].plot(history['val_acc'], label='Val Acc', color='red')
    axes[1].set_xlabel('Epoch')
    axes[1].set_ylabel('Accuracy (%)')
    axes[1].set_title('Training & Validation Accuracy')
    axes[1].legend()
    axes[1].grid(True)
    
    plt.tight_layout()
    plt.savefig(MODEL_DIR / "training_history_v2.png", dpi=150)
    print(f"\n📊 Training plot saved: {MODEL_DIR / 'training_history_v2.png'}")


if __name__ == "__main__":
    main()
