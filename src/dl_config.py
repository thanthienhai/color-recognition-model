"""
Configuration settings for deep learning color ratio recognition.
"""

import os
from pathlib import Path
from typing import Dict, List, Tuple

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# Directory paths
DATA_DIR = PROJECT_ROOT / "data"
TRAINING_DATA_DIR = DATA_DIR / "training"
VALIDATION_DATA_DIR = DATA_DIR / "validation"
TEST_DATA_DIR = DATA_DIR / "test"

MODELS_DIR = PROJECT_ROOT / "models"
COLOR_DETECTION_MODELS_DIR = MODELS_DIR / "color_detection"
CHECKPOINTS_DIR = COLOR_DETECTION_MODELS_DIR / "checkpoints"

LOGS_DIR = PROJECT_ROOT / "logs"

# Ensure directories exist
for directory in [
    DATA_DIR, TRAINING_DATA_DIR, VALIDATION_DATA_DIR, TEST_DATA_DIR,
    MODELS_DIR, COLOR_DETECTION_MODELS_DIR, CHECKPOINTS_DIR, LOGS_DIR
]:
    directory.mkdir(parents=True, exist_ok=True)

# Model configuration
MODEL_CONFIG = {
    "input_size": (224, 224, 3),
    "num_base_colors": 16,
    "conv_filters": [32, 64, 128, 256],
    "dense_units": [512, 256],
    "dropout_rates": [0.5, 0.3],
    "activation": "relu",
    "output_activation": "softmax"
}

# Training configuration
TRAINING_CONFIG = {
    "batch_size": 32,
    "epochs": 100,
    "learning_rate": 0.001,
    "weight_decay": 1e-5,
    "early_stopping_patience": 10,
    "checkpoint_interval": 5,
    "validation_split": 0.2
}

# Data generation configuration
DATA_GEN_CONFIG = {
    "image_size": (224, 224),
    "min_colors": 2,
    "max_colors": 5,
    "augmentation": {
        "brightness_range": (0.7, 1.3),
        "contrast_range": (0.8, 1.2),
        "noise_sigma_range": (5, 15),
        "texture_opacity": 0.2,
        "color_temp_shift": 500
    }
}

# Base colors (16 colors) with Lab values
BASE_COLORS: Dict[str, Tuple[float, float, float]] = {
    "Đen": (0.0, 0.0, 0.0),
    "Trắng": (100.0, 0.0, 0.0),
    "Vàng Chanh": (97.14, -21.55, 94.48),
    "Đỏ": (53.23, 80.11, 67.22),
    "Xanh Lá": (87.74, -86.18, 83.18),
    "Xanh Biển Sâu": (29.57, 68.30, -112.03),
    "Xanh Dương": (32.30, 79.19, -107.86),
    "Tím": (29.78, 58.94, -36.50),
    "Nâu": (37.99, 13.56, 42.53),
    "Vàng Neon": (97.14, -15.79, 93.39),
    "Xanh Neon": (87.74, -79.29, 80.99),
    "Xanh Lam Neon": (91.11, -48.09, -14.13),
    "Cam Neon": (74.93, 23.93, 78.95),
    "Hồng Neon": (70.48, 51.87, -17.10),
    "Tím Neon": (47.51, 65.55, -55.68),
    "Vàng Kim": (83.89, 3.19, 80.45)
}

# ImageNet normalization (DEPRECATED - no longer used)
# These constants are kept for backward compatibility but are NOT applied
# in preprocessing. The model now uses simple [0,1] normalization only.
# Using ImageNet stats caused double normalization issues and was not
# appropriate for color mixing tasks.
IMAGENET_MEAN = [0.485, 0.456, 0.406]  # DEPRECATED
IMAGENET_STD = [0.229, 0.224, 0.225]   # DEPRECATED

# Evaluation thresholds
EVALUATION_CONFIG = {
    "excellent_delta_e": 1.0,
    "good_delta_e": 2.0,
    "acceptable_delta_e": 4.0,
    "min_ratio_threshold": 0.03,  # 3%
    "max_colors_in_formula": 8,
    "target_accuracy": 0.85,
    "target_r2_score": 0.90
}

# Device configuration
DEVICE_CONFIG = {
    "default_device": "auto",  # auto, cuda, mps, cpu
    "enable_gpu": True,
    "gpu_memory_fraction": 0.8
}

# Logging configuration
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "log_file": LOGS_DIR / "deep_learning.log",
    "max_bytes": 10 * 1024 * 1024,  # 10 MB
    "backup_count": 5
}

# Model file paths
DEFAULT_MODEL_PATH = COLOR_DETECTION_MODELS_DIR / "cnn_color_ratio_latest.pth"
MODEL_VERSION = "v1.0.0"


def get_model_path(version: str = None) -> Path:
    """
    Get the path to a model file.
    
    Args:
        version: Model version (e.g., "v1.0.0"), or None for latest
        
    Returns:
        Path to model file
    """
    if version is None:
        return DEFAULT_MODEL_PATH
    return COLOR_DETECTION_MODELS_DIR / f"cnn_color_ratio_{version}.pth"


def get_checkpoint_path(epoch: int) -> Path:
    """
    Get the path to a checkpoint file.
    
    Args:
        epoch: Training epoch number
        
    Returns:
        Path to checkpoint file
    """
    return CHECKPOINTS_DIR / f"checkpoint_epoch_{epoch}.pth"


def get_dataset_path(split: str) -> Path:
    """
    Get the path to a dataset file.
    
    Args:
        split: Dataset split ("train", "val", or "test")
        
    Returns:
        Path to dataset file
    """
    if split == "train":
        return TRAINING_DATA_DIR / "train_dataset.h5"
    elif split == "val":
        return VALIDATION_DATA_DIR / "val_dataset.h5"
    elif split == "test":
        return TEST_DATA_DIR / "test_dataset.h5"
    else:
        raise ValueError(f"Invalid split: {split}")
