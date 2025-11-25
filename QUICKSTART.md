# Quick Start Guide - CNN Color Ratio Model

This guide will help you generate datasets and train the CNN model in just a few steps.

## Prerequisites

Make sure you have the required packages installed:

```bash
pip install torch torchvision numpy opencv-python h5py matplotlib
```

## Step 1: Generate Datasets

The datasets are generated synthetically by mathematically mixing base colors with known ratios and applying realistic augmentations.

### Option A: Quick Test (Small Dataset)

For quick testing and validation (takes ~1 minute):

```bash
python scripts/generate_datasets.py --small
```

This generates:
- 100 training samples
- 20 validation samples  
- 10 test samples

### Option B: Development (Medium Dataset)

For development and experimentation (takes ~5 minutes):

```bash
python scripts/generate_datasets.py --medium
```

This generates:
- 1,000 training samples
- 200 validation samples
- 100 test samples

### Option C: Production (Large Dataset)

For production-quality model (takes ~30 minutes):

```bash
python scripts/generate_datasets.py --large
```

This generates:
- 10,000 training samples
- 2,000 validation samples
- 1,000 test samples

### Option D: Custom Size

```bash
python scripts/generate_datasets.py --train 5000 --val 1000 --test 500
```

### What Gets Generated?

The script creates HDF5 files in the `data/` directory:
```
data/
├── training/
│   └── train_dataset.h5
├── validation/
│   └── val_dataset.h5
└── test/
    └── test_dataset.h5
```

Each dataset contains:
- **Images**: 224x224 RGB images of mixed colors
- **Ratios**: Ground truth mixing ratios for 16 base colors
- **Metadata**: Generation parameters and timestamps

## Step 2: Train the Model

Once datasets are generated, train the model:

### Quick Training (for testing)

```bash
python scripts/train_cnn_model.py --epochs 5 --batch-size 16
```

### Full Training (for production)

```bash
python scripts/train_cnn_model.py --epochs 50 --batch-size 32
```

### Training with Custom Config

Create a config file `my_config.yaml`:

```yaml
data:
  num_train: 5000
  num_val: 1000
  num_test: 500
  output_dir: data
  apply_augmentation: true

training:
  epochs: 30
  batch_size: 32
  learning_rate: 0.001
```

Then train:

```bash
python scripts/train_cnn_model.py --config my_config.yaml
```

## Step 3: Validate the Model

After training, validate the model meets requirements:

```bash
python scripts/final_validation.py \
  --model models/color_detection/cnn_color_ratio_v1.0.0.pth \
  --test-data data/test/test_dataset.h5
```

This checks:
- ✓ Delta E < 2.0 for 80%+ samples
- ✓ Top-1 accuracy > 85%
- ✓ Mean R² score > 0.90
- ✓ Integration with ColorAnalysisEngine
- ✓ Backward compatibility
- ✓ Deployment readiness

## Step 4: Benchmark Performance

Test inference speed and throughput:

```bash
python scripts/benchmark_performance.py \
  --model models/color_detection/cnn_color_ratio_v1.0.0.pth \
  --samples 100
```

This measures:
- Inference time (CPU/GPU)
- Batch processing throughput
- Memory usage
- CNN vs CIEDE2000 comparison

## Complete Workflow Example

Here's a complete workflow from scratch:

```bash
# 1. Generate medium-sized datasets
python scripts/generate_datasets.py --medium

# 2. Train the model (10 epochs for quick test)
python scripts/train_cnn_model.py --epochs 10

# 3. Validate the model
python scripts/final_validation.py

# 4. Benchmark performance
python scripts/benchmark_performance.py
```

## Using the Trained Model

### In Python Code

```python
from advanced_color_analysis import ColorAnalysisEngineV2
import numpy as np

# Initialize engine with CNN model
engine = ColorAnalysisEngineV2(
    cnn_model_path='models/color_detection/cnn_color_ratio_v1.0.0.pth'
)

# Analyze a color
rgb = (255, 100, 100)
lab = (60.0, 50.0, 30.0)
image = np.full((224, 224, 3), rgb, dtype=np.uint8)

# Use CNN method
prediction = engine.analyze_color(rgb, lab, method='cnn', image=image)

print(f"Dominant color: {prediction.dominant_color}")
print(f"Confidence: {prediction.confidence*100:.1f}%")
print(f"Quality: {prediction.quality_score}")
print(f"Inference time: {prediction.inference_time_ms:.1f}ms")

# Generate mixing formula
formula = engine.get_mixing_formula(prediction, simplify=True, max_colors=5)
print(f"Mixing formula: {formula}")
```

### In Jupyter Notebook

See `notebooks/cnn_training_demo.py` for a complete interactive demo.

## Troubleshooting

### "No module named 'torch'"

Install PyTorch:
```bash
pip install torch torchvision
```

### "No module named 'h5py'"

Install h5py:
```bash
pip install h5py
```

### "CUDA out of memory"

Reduce batch size:
```bash
python scripts/train_cnn_model.py --batch-size 16
```

Or use CPU:
```bash
python scripts/train_cnn_model.py --device cpu
```

### Datasets taking too long to generate

Start with small datasets:
```bash
python scripts/generate_datasets.py --small
```

### Training is slow

- Use GPU if available (automatic)
- Reduce number of epochs for testing
- Use smaller datasets for development

## Next Steps

1. **Integrate with UI**: See `docs/KIVY_CNN_INTEGRATION.md`
2. **Fine-tune model**: Adjust hyperparameters in config file
3. **Add more data**: Generate larger datasets for better accuracy
4. **Deploy**: Follow deployment checklist in validation report

## File Structure

After running the quick start, you'll have:

```
.
├── data/
│   ├── training/train_dataset.h5
│   ├── validation/val_dataset.h5
│   └── test/test_dataset.h5
├── models/
│   ├── checkpoints/
│   │   ├── best_model.pth
│   │   └── checkpoint_epoch_*.pth
│   └── color_detection/
│       └── cnn_color_ratio_v1.0.0.pth
├── logs/
│   └── training_*/
│       ├── tensorboard/
│       └── training_history.json
└── results/
    ├── validation_report.json
    └── benchmark_results.json
```

## Support

For more detailed information:
- Training: See `scripts/train_cnn_model.py --help`
- Architecture: See `docs/CNN_MODEL_ARCHITECTURE.md`
- Integration: See `docs/KIVY_CNN_INTEGRATION.md`
- Setup: See `docs/DEEP_LEARNING_SETUP.md`
