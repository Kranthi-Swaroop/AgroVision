import numpy as np
import os
import random
import json
from PIL import Image, ImageOps, ImageEnhance
import io
from pathlib import Path

# Load class names and inference config from JSON files
MODEL_DIR = Path(__file__).parent.parent.parent / "models"
CLASS_NAMES_FILE = MODEL_DIR / "class_names.json"
INFERENCE_CONFIG_FILE = MODEL_DIR / "inference_config.json"

# Load inference config (for image size, temperature, etc.)
INFERENCE_CONFIG = {}
if INFERENCE_CONFIG_FILE.exists():
    with open(INFERENCE_CONFIG_FILE) as f:
        INFERENCE_CONFIG = json.load(f)

if CLASS_NAMES_FILE.exists():
    with open(CLASS_NAMES_FILE) as f:
        DISEASE_CLASSES = json.load(f)
else:
    # Fallback class names matching our trained model
    DISEASE_CLASSES = [
        "pepper_bacterial_spot",
        "pepper_healthy",
        "potato_early_blight",
        "potato_healthy",
        "potato_late_blight",
        "tomato_bacterial_spot",
        "tomato_early_blight",
        "tomato_healthy",
        "tomato_late_blight",
        "tomato_leaf_mold",
        "tomato_mosaic_virus",
        "tomato_septoria_leaf_spot",
        "tomato_spider_mites",
        "tomato_target_spot",
        "tomato_yellow_leaf_curl_virus"
    ]

# Confidence threshold - below this, mark as "uncertain"
CONFIDENCE_THRESHOLD = 0.50

# Set to False to use the real model
DEMO_MODE = False


class DemoInference:
    """Demo inference for testing without a model"""
    def predict(self, image_bytes: bytes) -> tuple[str, float, list, bool]:
        random.seed(len(image_bytes) % 1000)
        disease_idx = random.randint(0, len(DISEASE_CLASSES) - 1)
        disease = DISEASE_CLASSES[disease_idx]
        confidence = random.uniform(0.75, 0.98)
        return disease, confidence, [], True


class EfficientNetInference:
    """EfficientNet-based classification inference with TTA"""
    def __init__(self, model_path: str):
        import onnxruntime as ort
        
        # Try GPU first, fallback to CPU
        providers = ['CUDAExecutionProvider', 'CPUExecutionProvider']
        try:
            self.session = ort.InferenceSession(model_path, providers=providers)
        except:
            self.session = ort.InferenceSession(
                model_path,
                providers=['CPUExecutionProvider']
            )
        
        self.input_name = self.session.get_inputs()[0].name
        # Get image size from config or default to 260 for EfficientNet-B3
        self.img_size = INFERENCE_CONFIG.get('img_size', 260)
        
        # ImageNet normalization values
        self.mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
        self.std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
        
        print(f"✓ Model loaded: {model_path}")
        print(f"  Input: {self.input_name}, Size: {self.img_size}x{self.img_size}")
        print(f"  Classes: {len(DISEASE_CLASSES)}")
        print(f"  TTA: Enabled (5 augmentations)")
        print(f"  Confidence threshold: {CONFIDENCE_THRESHOLD}")
    
    def smart_preprocess(self, image: Image.Image) -> Image.Image:
        """
        Smart preprocessing for real-world images:
        - Handle various aspect ratios with center crop
        - Remove borders/watermarks by focusing on center
        """
        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Get dimensions
        w, h = image.size
        
        # For very different aspect ratios, do a center crop first
        # This helps remove borders, watermarks, text
        aspect = w / h
        if aspect > 1.5:  # Very wide image
            # Crop to center square
            new_w = int(h * 1.2)
            left = (w - new_w) // 2
            image = image.crop((left, 0, left + new_w, h))
        elif aspect < 0.67:  # Very tall image
            # Crop to center square
            new_h = int(w * 1.2)
            top = (h - new_h) // 2
            image = image.crop((0, top, w, top + new_h))
        
        # Resize with high quality
        image = image.resize((self.img_size, self.img_size), Image.LANCZOS)
        
        return image
    
    def preprocess_to_tensor(self, image: Image.Image) -> np.ndarray:
        """Convert PIL image to normalized tensor"""
        img_array = np.array(image, dtype=np.float32) / 255.0
        img_array = (img_array - self.mean) / self.std
        img_array = np.transpose(img_array, (2, 0, 1))
        img_array = np.expand_dims(img_array, axis=0)
        return img_array
    
    def get_tta_images(self, image: Image.Image) -> list:
        """
        Generate Test-Time Augmentation variants:
        1. Original
        2. Horizontal flip
        3. Slight rotation
        4. Brightness adjusted
        5. Center crop zoom
        """
        augmented = []
        
        # 1. Original
        augmented.append(image)
        
        # 2. Horizontal flip
        augmented.append(ImageOps.mirror(image))
        
        # 3. Slight rotation (-10 degrees)
        rotated = image.rotate(-10, resample=Image.BILINEAR, fillcolor=(128, 128, 128))
        augmented.append(rotated)
        
        # 4. Brightness adjustment (slightly brighter)
        enhancer = ImageEnhance.Brightness(image)
        augmented.append(enhancer.enhance(1.1))
        
        # 5. Center crop zoom (crop 90% from center, then resize back)
        w, h = image.size
        crop_size = int(min(w, h) * 0.9)
        left = (w - crop_size) // 2
        top = (h - crop_size) // 2
        cropped = image.crop((left, top, left + crop_size, top + crop_size))
        cropped = cropped.resize((self.img_size, self.img_size), Image.LANCZOS)
        augmented.append(cropped)
        
        return augmented
    
    def run_inference(self, tensor: np.ndarray) -> np.ndarray:
        """Run single inference and return logits"""
        outputs = self.session.run(None, {self.input_name: tensor})
        return outputs[0][0]
    
    def predict(self, image_bytes: bytes) -> tuple[str, float, list, bool]:
        """
        Run inference with Test-Time Augmentation (TTA)
        Returns: (disease, confidence, top5, is_confident)
        """
        # Load and preprocess image
        image = Image.open(io.BytesIO(image_bytes))
        image = self.smart_preprocess(image)
        
        # Get TTA variants
        tta_images = self.get_tta_images(image)
        
        # Run inference on all variants
        all_logits = []
        for aug_image in tta_images:
            tensor = self.preprocess_to_tensor(aug_image)
            logits = self.run_inference(tensor)
            all_logits.append(logits)
        
        # Average the logits (before softmax for better calibration)
        avg_logits = np.mean(all_logits, axis=0)
        
        # Softmax
        exp_logits = np.exp(avg_logits - np.max(avg_logits))
        probabilities = exp_logits / np.sum(exp_logits)
        
        # Get prediction
        class_idx = int(np.argmax(probabilities))
        confidence = float(probabilities[class_idx])
        disease = DISEASE_CLASSES[class_idx] if class_idx < len(DISEASE_CLASSES) else "unknown"
        
        # Check if confident enough
        is_confident = confidence >= CONFIDENCE_THRESHOLD
        
        # Top-5 predictions
        top5_indices = np.argsort(probabilities)[-5:][::-1]
        top5 = [
            {"class": DISEASE_CLASSES[i], "confidence": float(probabilities[i])}
            for i in top5_indices if i < len(DISEASE_CLASSES)
        ]
        
        return disease, confidence, top5, is_confident


_inference_instance = None


def get_inference(model_path: str):
    """Get or create inference instance"""
    global _inference_instance
    
    if _inference_instance is None:
        if DEMO_MODE:
            print("⚠ Running in DEMO MODE - using mock predictions")
            _inference_instance = DemoInference()
        elif not os.path.exists(model_path):
            print(f"⚠ Model not found at {model_path} - using DEMO MODE")
            _inference_instance = DemoInference()
        else:
            print(f"Loading model from {model_path}...")
            _inference_instance = EfficientNetInference(model_path)
    
    return _inference_instance
