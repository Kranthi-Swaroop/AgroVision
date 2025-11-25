"""
Export improved model to ONNX with temperature scaling
"""
import torch
import torch.nn as nn
from torchvision import models
from pathlib import Path
import json


MODEL_DIR = Path("models")


class CalibratedModel(nn.Module):
    """Wrapper that applies temperature scaling"""
    def __init__(self, base_model, temperature=1.0):
        super().__init__()
        self.base_model = base_model
        self.temperature = temperature
    
    def forward(self, x):
        logits = self.base_model(x)
        # Apply temperature scaling for calibration
        return logits / self.temperature


def create_model(num_classes):
    """Recreate model architecture"""
    model = models.efficientnet_b3(weights=None)
    in_features = 1536  # EfficientNet-B3 features
    model.classifier = nn.Sequential(
        nn.Dropout(p=0.4, inplace=True),
        nn.Linear(in_features, 512),
        nn.ReLU(inplace=True),
        nn.Dropout(p=0.3),
        nn.Linear(512, num_classes)
    )
    return model


def main():
    # Load config
    config_path = MODEL_DIR / "training_config_v2.json"
    if not config_path.exists():
        print("❌ Training config not found. Train the model first.")
        return
    
    with open(config_path) as f:
        config = json.load(f)
    
    num_classes = config['num_classes']
    img_size = config['img_size']
    temperature = config.get('optimal_temperature', 1.0)
    
    print(f"Loading model for {num_classes} classes...")
    print(f"Input size: {img_size}x{img_size}")
    print(f"Temperature: {temperature:.3f}")
    
    # Load checkpoint
    checkpoint_path = MODEL_DIR / "agrosentinel_best_v2.pth"
    checkpoint = torch.load(checkpoint_path, map_location='cpu')
    
    # Create model
    model = create_model(num_classes)
    model.load_state_dict(checkpoint['model_state_dict'])
    model.eval()
    
    # Wrap with temperature scaling
    calibrated_model = CalibratedModel(model, temperature)
    calibrated_model.eval()
    
    # Export to ONNX
    dummy_input = torch.randn(1, 3, img_size, img_size)
    onnx_path = MODEL_DIR / "agrosentinel_model_v2.onnx"
    
    print(f"\nExporting to ONNX...")
    torch.onnx.export(
        calibrated_model,
        dummy_input,
        onnx_path,
        export_params=True,
        opset_version=14,
        do_constant_folding=True,
        input_names=['input'],
        output_names=['output'],
        dynamic_axes={
            'input': {0: 'batch_size'},
            'output': {0: 'batch_size'}
        }
    )
    
    # Verify
    import onnx
    onnx_model = onnx.load(onnx_path)
    onnx.checker.check_model(onnx_model)
    
    file_size = onnx_path.stat().st_size / (1024 * 1024)
    print(f"\n✓ Model exported: {onnx_path}")
    print(f"  Size: {file_size:.2f} MB")
    print(f"  Validation accuracy: {config['best_val_acc']:.2f}%")
    print(f"  Temperature calibration: {temperature:.3f}")
    
    # Save updated config for inference
    inference_config = {
        'img_size': img_size,
        'num_classes': num_classes,
        'temperature': temperature,
        'class_names': config['class_names']
    }
    
    with open(MODEL_DIR / "inference_config.json", "w") as f:
        json.dump(inference_config, f, indent=2)
    
    print(f"  Config saved: {MODEL_DIR / 'inference_config.json'}")


if __name__ == "__main__":
    main()
