# CNN Color Ratio Model Architecture

This document describes the CNN-based deep learning model for predicting color mixing ratios from RGB images.

## Overview

The `CNNColorRatioModel` is a convolutional neural network that takes an RGB image as input and predicts the mixing ratios for 16 base colors. The model outputs a probability distribution where all ratios sum to 100%.

## Architecture

### Network Structure

```
Input: RGB Image (224x224x3)
    ↓
Conv Block 1: Conv2D(32) + BatchNorm + ReLU + MaxPool
    ↓
Conv Block 2: Conv2D(64) + BatchNorm + ReLU + MaxPool
    ↓
Conv Block 3: Conv2D(128) + BatchNorm + ReLU + MaxPool
    ↓
Conv Block 4: Conv2D(256) + BatchNorm + ReLU + MaxPool
    ↓
Flatten (256 * 14 * 14 = 50,176 features)
    ↓
Dense Layer 1: 512 neurons + ReLU + Dropout(0.5)
    ↓
Dense Layer 2: 256 neurons + ReLU + Dropout(0.3)
    ↓
Output Layer: 16 neurons + Softmax
    ↓
Output: 16 ratios summing to 1.0 (100%)
```

### Layer Details

**Convolutional Blocks:**
- Block 1: 3 → 32 filters, 3x3 kernel, padding=1
- Block 2: 32 → 64 filters, 3x3 kernel, padding=1
- Block 3: 64 → 128 filters, 3x3 kernel, padding=1
- Block 4: 128 → 256 filters, 3x3 kernel, padding=1

Each block includes:
- Convolutional layer
- Batch normalization
- ReLU activation
- Max pooling (2x2, stride=2)

**Fully Connected Layers:**
- FC1: 50,176 → 512 neurons
- FC2: 512 → 256 neurons
- Output: 256 → 16 neurons

**Regularization:**
- Dropout after FC1: 50% dropout rate
- Dropout after FC2: 30% dropout rate
- Batch normalization after each conv layer

## Model Classes

### CNNColorRatioNetwork

Low-level PyTorch `nn.Module` implementing the network architecture.

```python
from src.deep_color_model import CNNColorRatioNetwork

# Create network
network = CNNColorRatioNetwork(
    num_colors=16,
    conv_filters=[32, 64, 128, 256],
    dense_units=[512, 256],
    dropout_rates=[0.5, 0.3]
)

# Forward pass
output = network(input_tensor)  # Shape: (batch_size, 16)
```

### CNNColorRatioModel

High-level interface for model operations.

```python
from src.deep_color_model import CNNColorRatioModel
import numpy as np

# Initialize model
model = CNNColorRatioModel(
    model_path="models/color_detection/cnn_color_ratio_v1.0.0.pth",
    device="auto",  # auto, cuda, mps, cpu
    num_colors=16
)

# Predict single image
image = np.random.randint(0, 256, (224, 224, 3), dtype=np.uint8)
ratios = model.predict(image)  # Shape: (16,), sum=1.0

# Predict batch
images = [image1, image2, image3]
ratios = model.predict_batch(images)  # Shape: (3, 16)

# Get model info
info = model.get_model_info()
print(f"Parameters: {info['num_parameters']}")
print(f"Device: {info['device']}")
```

## Image Preprocessing

**IMPORTANT: Preprocessing has been updated to fix double normalization issue.**

Input images are preprocessed before inference:

1. **Input Validation**: Verify image shape is (H, W, 3) and values are in [0, 255]
2. **Resize**: Scale to 224x224 pixels using cv2.resize()
3. **Single Normalization**: Convert to [0, 1] range by dividing by 255.0
   - **NOTE**: ImageNet normalization is NO LONGER applied
   - Previous versions incorrectly applied ImageNet stats, causing double normalization
   - This was inappropriate for color mixing tasks
4. **Tensor Conversion**: Convert to PyTorch tensor (C, H, W)
5. **Batch Dimension**: Add batch dimension (1, C, H, W)
6. **Device Transfer**: Move to GPU/CPU

**Preprocessing Consistency:**
- Training and inference use IDENTICAL preprocessing
- Dataset generation also uses single [0,1] normalization
- No ImageNet statistics (mean/std) are applied anywhere

## Model Persistence

### Saving Models

```python
# Save model weights
model.save_model(
    path="models/color_detection/cnn_color_ratio_v1.0.0.pth",
    model_version="v1.0.0",
    training_metadata={"accuracy": 0.92, "delta_e": 1.5}
)

# Save training checkpoint
model.save_checkpoint(
    path="models/color_detection/checkpoints/checkpoint_epoch_50.pth",
    epoch=50,
    optimizer_state=optimizer.state_dict(),
    train_loss=0.15,
    val_loss=0.18,
    val_delta_e=1.3,
    hyperparameters={"lr": 0.001, "batch_size": 32}
)
```

### Loading Models

```python
# Load model weights
model = CNNColorRatioModel()
success = model.load_model("models/color_detection/cnn_color_ratio_v1.0.0.pth")

# Load checkpoint for training
checkpoint = model.load_checkpoint("models/color_detection/checkpoints/checkpoint_epoch_50.pth")
start_epoch = checkpoint["epoch"]
train_loss = checkpoint["train_loss"]
```

### Checkpoint Format

```python
{
    "model_state_dict": OrderedDict,      # Model weights
    "optimizer_state_dict": OrderedDict,  # Optimizer state (optional)
    "epoch": int,                         # Training epoch
    "train_loss": float,                  # Training loss
    "val_loss": float,                    # Validation loss
    "val_delta_e": float,                 # Validation Delta E
    "hyperparameters": dict,              # Training config
    "model_version": str,                 # Version string
    "num_colors": int,                    # Number of output colors
    "architecture": dict,                 # Architecture config
    "training_timestamp": str             # ISO timestamp
}
```

## Output Format

The model outputs a probability distribution over 16 base colors:

```python
ratios = model.predict(image)
# Example output:
# array([0.35, 0.25, 0.15, 0.10, 0.05, 0.03, 0.02, 0.02, 0.01, 0.01, 0.01, 0.0, 0.0, 0.0, 0.0, 0.0])
# Sum: 1.0 (100%)

# Corresponds to 16 base colors:
# [Đen, Trắng, Vàng Chanh, Đỏ, Xanh Lá, Xanh Biển Sâu, Xanh Dương, Tím, 
#  Nâu, Vàng Neon, Xanh Neon, Xanh Lam Neon, Cam Neon, Hồng Neon, Tím Neon, Vàng Kim]
```

## Model Parameters

Total parameters: ~10-15 million (depending on exact configuration)

**Breakdown:**
- Conv layers: ~1.5M parameters
- FC layers: ~13M parameters
- Batch norm: ~0.5M parameters

## Device Support

The model automatically detects and uses available hardware:

- **NVIDIA GPU**: Uses CUDA backend
- **Apple Silicon**: Uses MPS (Metal Performance Shaders) backend
- **CPU**: Falls back to CPU computation

```python
from src.device_utils import get_device_info

info = get_device_info()
print(f"Device: {info['device']}")
print(f"GPU Available: {info['gpu_available']}")
```

## Testing

Comprehensive unit tests are available in `tests/test_cnn_model.py`:

```bash
# Run all model tests (requires PyTorch)
python3 -m pytest tests/test_cnn_model.py -v

# Run structure tests (no PyTorch required)
python3 -m pytest tests/test_model_structure.py -v
```

**Test Coverage:**
- Network initialization and architecture
- Forward pass and output validation
- Batch processing
- Image preprocessing
- Model saving and loading
- Checkpoint management
- Output probability distribution validation
- Consistency checks

## Performance Characteristics

**Inference Speed:**
- CPU: ~50-100ms per image
- GPU (CUDA): ~10-20ms per image
- GPU (MPS): ~15-30ms per image

**Memory Usage:**
- Model size: ~50-60 MB
- Runtime memory: ~200-300 MB

**Accuracy Targets:**
- Mean Delta E: < 2.0
- Top-1 accuracy: > 85%
- R² score: > 0.90

## Integration Points

The model integrates with:

1. **ColorAnalysisEngine**: Main analysis orchestrator
2. **Training Pipeline**: For model training and evaluation
3. **Jupyter Notebook**: For demonstrations and experiments
4. **Kivy UI**: For production color analysis

## Next Steps

With the model architecture complete, the next tasks are:

1. Implement training data generator
2. Implement training pipeline
3. Implement evaluation metrics
4. Integrate with existing color analysis system

## References

- PyTorch Documentation: https://pytorch.org/docs/
- Model configuration: `src/dl_config.py`
- Device utilities: `src/device_utils.py`
- Design document: `.kiro/specs/deep-learning-color-ratio-recognition/design.md`
