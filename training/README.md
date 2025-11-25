# AgroSentinel Model Training

## Quick Start

### 1. Install Dependencies
```bash
cd training
pip install -r requirements.txt
```

### 2. Prepare Dataset
```bash
python prepare_dataset.py
```
This downloads and prepares the PlantVillage dataset filtered for Indian crops.

### 3. Train Model
```bash
python train_model.py
```
Training takes ~4-6 hours on RTX 3050.

### 4. Export to ONNX
```bash
python export_onnx.py
```
This creates the ONNX model and copies it to the backend.

### 5. Evaluate Model
```bash
python evaluate_model.py
```
Generates accuracy metrics and confusion matrix.

## Model Architecture

- **Base Model**: EfficientNet-B2 (pretrained on ImageNet)
- **Input Size**: 224x224 RGB
- **Output**: 21+ classes (Indian crop diseases)

## Training Features

- **Mixed Precision Training** (FP16) for faster training
- **Data Augmentation**: Random crops, flips, rotations, color jitter
- **Class Weighting**: Handles imbalanced datasets
- **Label Smoothing**: Reduces overconfidence
- **Cosine Annealing LR**: Better convergence
- **Early Stopping**: Prevents overfitting

## Expected Results

- Training Accuracy: ~95-98%
- Validation Accuracy: ~90-95%
- Top-5 Accuracy: ~99%

## Classes Included

### Indian Crops:
- Rice (Brown Spot, Leaf Blast, Neck Blast)
- Wheat (Brown Rust, Yellow Rust, Septoria)
- Cotton (Bacterial Blight, Curl Virus, Fusarium Wilt)
- Corn/Maize (Gray Leaf Spot, Common Rust, Northern Leaf Blight)
- Tomato (10 diseases)
- Potato (Early Blight, Late Blight)
- Grape (Black Rot, Esca, Leaf Blight)

## GPU Memory Usage

- RTX 3050 6GB: batch_size=32 (optimal)
- RTX 3060 12GB: batch_size=64
- RTX 3080+: batch_size=128

## Troubleshooting

### Out of Memory
Reduce batch_size in train_model.py:
```python
class Config:
    batch_size = 16  # Reduce from 32
```

### Slow Training
- Ensure CUDA is available: `torch.cuda.is_available()`
- Reduce num_workers if CPU bottlenecked
- Use SSD for dataset storage
