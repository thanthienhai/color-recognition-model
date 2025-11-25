# Deep Learning Setup Documentation

This document describes the deep learning infrastructure setup for the CNN-based color ratio recognition system.

## Directory Structure

The following directories have been created:

```
color-recognition-model/
├── data/                          # Training and test data
│   ├── training/                  # Training datasets
│   ├── validation/                # Validation datasets
│   ├── test/                      # Test datasets
│   └── README.md                  # Data documentation
├── models/                        # Trained models
│   ├── color_detection/           # CNN color ratio models
│   │   ├── checkpoints/           # Training checkpoints
│   │   └── cnn_color_ratio_*.pth  # Model files
│   └── README.md                  # Model documentation
├── logs/                          # Training and inference logs
└── src/                           # Source code
    ├── device_utils.py            # GPU/CPU detection utilities
    └── dl_config.py               # Configuration settings
```

## Dependencies Added

The following PyTorch and deep learning dependencies have been added to `requirements.txt`:

- **torch==2.0.1**: PyTorch deep learning framework
- **torchvision==0.15.2**: Computer vision utilities for PyTorch
- **tensorboard==2.13.0**: Training visualization and monitoring
- **h5py==3.9.0**: HDF5 file format for datasets
- **scikit-learn==1.3.0**: Machine learning utilities

## Core Components

### 1. Device Manager (`src/device_utils.py`)

Handles automatic GPU/CPU detection and device management:

```python
from src.device_utils import get_device_info, DeviceManager

# Get device information
info = get_device_info()
print(info)  # {'device': 'cuda', 'gpu_available': True, ...}

# Create device manager
manager = DeviceManager(device="auto")  # auto, cuda, mps, cpu
device = manager.device

# Move model to device
model = model.to(device)
```

**Features:**
- Automatic detection of CUDA (NVIDIA GPU)
- Automatic detection of MPS (Apple Silicon GPU)
- Graceful fallback to CPU
- Device information logging
- Memory management utilities

### 2. Configuration (`src/dl_config.py`)

Centralized configuration for all deep learning components:

```python
from src.dl_config import (
    BASE_COLORS,           # 16 base colors with Lab values
    MODEL_CONFIG,          # CNN architecture settings
    TRAINING_CONFIG,       # Training hyperparameters
    DATA_GEN_CONFIG,       # Data generation settings
    get_model_path,        # Get model file paths
    get_checkpoint_path,   # Get checkpoint paths
    get_dataset_path       # Get dataset paths
)
```

**Key Configurations:**

- **Model Architecture:**
  - Input size: 224x224x3
  - Conv filters: [32, 64, 128, 256]
  - Dense units: [512, 256]
  - Output: 16 color ratios

- **Training Settings:**
  - Batch size: 32
  - Learning rate: 0.001
  - Early stopping patience: 10 epochs
  - Checkpoint interval: 5 epochs

- **Data Generation:**
  - Image size: 224x224
  - Colors per sample: 2-5
  - Augmentation: brightness, contrast, noise, texture

## Base Colors

The system supports 16 base colors with predefined Lab color space values:

1. Đen (Black)
2. Trắng (White)
3. Vàng Chanh (Lemon Yellow)
4. Đỏ (Red)
5. Xanh Lá (Green)
6. Xanh Biển Sâu (Deep Blue)
7. Xanh Dương (Blue)
8. Tím (Purple)
9. Nâu (Brown)
10. Vàng Neon (Neon Yellow)
11. Xanh Neon (Neon Green)
12. Xanh Lam Neon (Neon Cyan)
13. Cam Neon (Neon Orange)
14. Hồng Neon (Neon Pink)
15. Tím Neon (Neon Purple)
16. Vàng Kim (Gold)

## Testing

Comprehensive tests have been created in `tests/test_dl_setup.py`:

```bash
# Run setup tests
python3 -m pytest tests/test_dl_setup.py -v
```

**Test Coverage:**
- Directory structure validation
- Device manager functionality
- Configuration integrity
- Base colors validation
- Path generation utilities

## Next Steps

With the infrastructure in place, the next tasks are:

1. **Task 2**: Implement CNN color ratio model architecture
2. **Task 3**: Implement training data generator
3. **Task 4**: Implement training pipeline
4. **Task 5**: Implement evaluation and metrics

## Installation

To install the deep learning dependencies:

```bash
# Install all dependencies
pip install -r requirements.txt

# Verify PyTorch installation
python3 -c "import torch; print(f'PyTorch {torch.__version__}')"

# Check GPU availability
python3 -c "from src.device_utils import get_device_info; import json; print(json.dumps(get_device_info(), indent=2))"
```

## GPU Support

The system automatically detects and uses GPU when available:

- **NVIDIA GPUs**: Uses CUDA backend
- **Apple Silicon**: Uses MPS (Metal Performance Shaders) backend
- **No GPU**: Falls back to CPU

## Troubleshooting

### PyTorch Not Found

If PyTorch is not installed:
```bash
pip install torch torchvision
```

### GPU Not Detected

Check GPU availability:
```python
from src.device_utils import is_gpu_available
print(f"GPU available: {is_gpu_available()}")
```

### Directory Permissions

If directory creation fails, ensure write permissions:
```bash
chmod -R u+w data/ models/ logs/
```

## References

- PyTorch Documentation: https://pytorch.org/docs/
- TensorBoard Guide: https://www.tensorflow.org/tensorboard
- HDF5 Format: https://www.h5py.org/
