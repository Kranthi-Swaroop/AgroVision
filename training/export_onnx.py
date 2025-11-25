import torch
import torch.nn as nn
from torchvision import models
from pathlib import Path
import json
import onnx
import onnxruntime as ort
import numpy as np


MODEL_DIR = Path("models")
BACKEND_MODEL_DIR = Path("../backend/models")


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
    elif model_name == "convnext_tiny":
        model = models.convnext_tiny(weights=None)
        model.classifier[2] = nn.Linear(model.classifier[2].in_features, num_classes)
    
    checkpoint = torch.load(checkpoint_path, map_location='cpu')
    model.load_state_dict(checkpoint['model_state_dict'])
    model.eval()
    
    return model, checkpoint


def export_to_onnx(model, img_size, onnx_path):
    dummy_input = torch.randn(1, 3, img_size, img_size)
    
    torch.onnx.export(
        model,
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
    
    onnx_model = onnx.load(onnx_path)
    onnx.checker.check_model(onnx_model)
    
    print(f"ONNX model exported: {onnx_path}")
    print(f"Model size: {onnx_path.stat().st_size / 1e6:.2f} MB")


def verify_onnx(onnx_path, pytorch_model, img_size):
    ort_session = ort.InferenceSession(str(onnx_path), providers=['CPUExecutionProvider'])
    
    test_input = np.random.randn(1, 3, img_size, img_size).astype(np.float32)
    
    with torch.no_grad():
        pytorch_output = pytorch_model(torch.from_numpy(test_input)).numpy()
    
    ort_inputs = {ort_session.get_inputs()[0].name: test_input}
    ort_output = ort_session.run(None, ort_inputs)[0]
    
    diff = np.abs(pytorch_output - ort_output).max()
    print(f"Max difference between PyTorch and ONNX: {diff:.6f}")
    
    if diff < 1e-4:
        print("ONNX model verification: PASSED")
        return True
    else:
        print("ONNX model verification: WARNING - outputs differ")
        return False


def main():
    print("="*60)
    print("Exporting Model to ONNX")
    print("="*60)
    
    checkpoint_path = MODEL_DIR / "agrosentinel_best.pth"
    
    if not checkpoint_path.exists():
        print(f"Error: Checkpoint not found at {checkpoint_path}")
        print("Please run train_model.py first")
        return
    
    with open(MODEL_DIR / "training_config.json") as f:
        config = json.load(f)
    
    print(f"\nLoading model: {config['model_name']}")
    print(f"Number of classes: {config['num_classes']}")
    print(f"Best accuracy: {config['best_val_acc']:.2f}%")
    
    model, checkpoint = load_model(
        checkpoint_path,
        config['num_classes'],
        config['model_name']
    )
    
    onnx_path = MODEL_DIR / "agrosentinel_model.onnx"
    export_to_onnx(model, config['img_size'], onnx_path)
    
    print("\nVerifying ONNX model...")
    verify_onnx(onnx_path, model, config['img_size'])
    
    BACKEND_MODEL_DIR.mkdir(parents=True, exist_ok=True)
    backend_onnx_path = BACKEND_MODEL_DIR / "crop_disease_model.onnx"
    
    import shutil
    shutil.copy2(onnx_path, backend_onnx_path)
    print(f"\nModel copied to backend: {backend_onnx_path}")
    
    backend_classes_path = BACKEND_MODEL_DIR / "class_names.json"
    with open(backend_classes_path, "w") as f:
        json.dump(config['class_names'], f, indent=2)
    print(f"Class names saved: {backend_classes_path}")
    
    print("\n" + "="*60)
    print("EXPORT COMPLETE")
    print("="*60)
    print(f"ONNX Model: {backend_onnx_path}")
    print(f"Classes: {config['num_classes']}")
    print("\nUpdate backend/app/config.py to use the new model:")
    print(f'  model_path: str = "models/crop_disease_model.onnx"')
    print("\nSet DEMO_MODE = False in backend/app/services/inference.py")


if __name__ == "__main__":
    main()
