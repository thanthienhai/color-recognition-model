# Models Directory

This directory contains trained deep learning models for color ratio recognition.

## Directory Organization

```
models/
├── color_detection/           # CNN color ratio models
│   ├── cnn_color_ratio_v1.0.0.pth
│   ├── cnn_color_ratio_latest.pth
│   └── checkpoints/          # Training checkpoints
│       ├── checkpoint_epoch_10.pth
│       └── checkpoint_epoch_20.pth
└── README.md                 # This file
```

## Model Format

Models are saved as PyTorch checkpoint files (.pth) with the following structure:

```python
{
    "model_state_dict": OrderedDict,      # Model weights
    "optimizer_state_dict": OrderedDict,  # Optimizer state (for training)
    "epoch": int,                         # Training epoch
    "train_loss": float,                  # Training loss
    "val_loss": float,                    # Validation loss
    "val_delta_e": float,                 # Validation Delta E metric
    "hyperparameters": {
        "learning_rate": float,
        "batch_size": int,
        "architecture": str
    },
    "training_timestamp": str
}
```

## Model Versioning

Models follow semantic versioning: `v{major}.{minor}.{patch}`

- **Major**: Breaking changes to architecture
- **Minor**: New features or improvements
- **Patch**: Bug fixes or minor updates

## Loading Models

```python
from src.deep_color_model import CNNColorRatioModel

model = CNNColorRatioModel(model_path="models/color_detection/cnn_color_ratio_v1.0.0.pth")
model.load_model()
```

## Model Architecture

The CNN model predicts mixing ratios for 16 base colors:

- Input: RGB image (224x224x3)
- Output: 16 ratios (percentages summing to 100%)

See `design.md` for detailed architecture specifications.
