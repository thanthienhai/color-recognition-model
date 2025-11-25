"""
CNN Color Ratio Model - Training and Inference Demo
This script demonstrates the complete workflow for training and using the CNN model.
Can be converted to Jupyter notebook cells.
"""

# %% [markdown]
# # Deep Learning Color Ratio Model
# 
# This notebook demonstrates:
# 1. Training data generation
# 2. CNN model training with progress visualization
# 3. Model evaluation with comprehensive metrics
# 4. Inference examples comparing CNN vs CIEDE2000
# 5. Integration with the color analysis engine

# %% Setup and Imports
import sys
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

# Add src to path
sys.path.insert(0, str(Path.cwd().parent / "src"))

from color_data_generator import ColorDataGenerator, create_train_val_test_datasets
from deep_color_model import CNNColorRatioModel
from color_evaluator import ColorPredictionEvaluator, evaluate_model
from advanced_color_analysis import ColorAnalysisEngineV2
from dl_config import BASE_COLORS

print("✓ All imports successful")

# %% [markdown]
# ## 1. Data Generation
# 
# Generate synthetic training data by mathematically mixing base colors with known ratios.
# Apply realistic augmentations to simulate real-world conditions.

# %% Generate Training Data
print("=" * 60)
print("STEP 1: Generating Training Data")
print("=" * 60)

# Initialize data generator
generator = ColorDataGenerator()

print(f"\nBase colors: {len(generator.color_names)}")
print(f"Image size: {generator.image_size}")
print(f"Color range: {generator.min_colors}-{generator.max_colors} colors per sample")

# Generate a few sample images to visualize
print("\nGenerating sample images...")
fig, axes = plt.subplots(2, 5, figsize=(15, 6))
fig.suptitle('Sample Generated Training Images', fontsize=16)

for idx, ax in enumerate(axes.flat):
    image, ratios = generator.generate_sample()
    
    # Apply augmentation to half of them
    if idx >= 5:
        image = generator.apply_augmentations(image)
    
    ax.imshow(image)
    ax.axis('off')
    
    # Show top 3 colors
    top_colors = np.argsort(ratios)[-3:][::-1]
    title = ", ".join([f"{generator.color_names[i]}: {ratios[i]*100:.1f}%" 
                       for i in top_colors])
    ax.set_title(title, fontsize=8)

plt.tight_layout()
plt.savefig('sample_training_images.png', dpi=150, bbox_inches='tight')
print("✓ Sample images saved to 'sample_training_images.png'")

# %% Generate Full Datasets
print("\n" + "=" * 60)
print("Generating full datasets...")
print("=" * 60)

# Generate train/val/test datasets
# Adjust numbers based on your needs (smaller for quick testing)
train_path, val_path, test_path = create_train_val_test_datasets(
    num_train=1000,   # Use 10000+ for production
    num_val=200,      # Use 2000+ for production
    num_test=100,     # Use 1000+ for production
    output_dir="../data",
    apply_augmentation=True
)

print(f"\n✓ Training data: {train_path}")
print(f"✓ Validation data: {val_path}")
print(f"✓ Test data: {test_path}")

# %% [markdown]
# ## 2. Model Training
# 
# Train the CNN model with validation and checkpointing.
# Monitor training progress with loss curves and Delta E metrics.

# %% Initialize Model
print("\n" + "=" * 60)
print("STEP 2: Training CNN Model")
print("=" * 60)

# Initialize model
model = CNNColorRatioModel(device="auto")

print(f"\nModel initialized on device: {model.device}")
print(f"Number of parameters: {model.get_model_info()['num_parameters']:,}")

# %% Prepare Data Loaders
import torch
from torch.utils.data import DataLoader
from color_data_generator import ColorRatioDataset

# Load datasets
train_dataset = ColorRatioDataset(train_path)
val_dataset = ColorRatioDataset(val_path)
test_dataset = ColorRatioDataset(test_path)

# Create data loaders
train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=32, shuffle=False)
test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False)

print(f"\nDataset sizes:")
print(f"  Training: {len(train_dataset)} samples")
print(f"  Validation: {len(val_dataset)} samples")
print(f"  Test: {len(test_dataset)} samples")

# %% Train Model
print("\n" + "=" * 60)
print("Training model...")
print("=" * 60)

# Train with checkpointing and logging
history = model.train(
    train_loader=train_loader,
    val_loader=val_loader,
    epochs=10,  # Use 50+ for production
    learning_rate=0.001,
    checkpoint_dir="../models/checkpoints",
    checkpoint_interval=5,
    early_stopping_patience=10,
    log_dir="../logs",
    experiment_name="cnn_color_ratio_demo"
)

print("\n✓ Training complete!")

# %% Plot Training History
print("\nPlotting training history...")

fig, axes = plt.subplots(1, 3, figsize=(15, 4))

# Loss curves
axes[0].plot(history['train_loss'], label='Train Loss', marker='o')
axes[0].plot(history['val_loss'], label='Val Loss', marker='s')
axes[0].set_xlabel('Epoch')
axes[0].set_ylabel('Loss (MSE)')
axes[0].set_title('Training and Validation Loss')
axes[0].legend()
axes[0].grid(True, alpha=0.3)

# Delta E
axes[1].plot(history['val_delta_e'], label='Val Delta E', marker='o', color='green')
axes[1].axhline(y=2.0, color='r', linestyle='--', label='Target (ΔE < 2)')
axes[1].set_xlabel('Epoch')
axes[1].set_ylabel('Delta E')
axes[1].set_title('Validation Delta E')
axes[1].legend()
axes[1].grid(True, alpha=0.3)

# Learning rate
axes[2].plot(history['learning_rates'], marker='o', color='orange')
axes[2].set_xlabel('Epoch')
axes[2].set_ylabel('Learning Rate')
axes[2].set_title('Learning Rate Schedule')
axes[2].set_yscale('log')
axes[2].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('training_history.png', dpi=150, bbox_inches='tight')
print("✓ Training history saved to 'training_history.png'")

# %% [markdown]
# ## 3. Model Evaluation
# 
# Evaluate the trained model with comprehensive metrics:
# - Delta E distribution
# - Classification accuracy
# - Per-color R² scores
# - Confusion matrix

# %% Evaluate Model
print("\n" + "=" * 60)
print("STEP 3: Model Evaluation")
print("=" * 60)

# Create evaluator
evaluator = ColorPredictionEvaluator(model, BASE_COLORS)

# Evaluate on test set
print("\nEvaluating on test set...")
metrics = evaluator.evaluate_dataset(test_loader, calculate_per_color_metrics=True)

print(f"\n{'='*60}")
print("EVALUATION RESULTS")
print(f"{'='*60}")
print(f"Mean Delta E: {metrics['mean_delta_e']:.2f}")
print(f"Median Delta E: {metrics['median_delta_e']:.2f}")
print(f"Std Delta E: {metrics['std_delta_e']:.2f}")
print(f"\nQuality Distribution:")
print(f"  Excellent (ΔE < 1): {metrics['delta_e_below_1']*100:.1f}%")
print(f"  Good (ΔE < 2): {metrics['delta_e_below_2']*100:.1f}%")
print(f"  Acceptable (ΔE < 4): {metrics['delta_e_below_4']*100:.1f}%")
print(f"\nRegression Metrics:")
print(f"  MSE: {metrics['mse']:.6f}")
print(f"  MAE: {metrics['mae']:.6f}")
print(f"  Mean R² Score: {metrics['mean_r2_score']:.4f}")

# %% Calculate Classification Metrics
print("\nCalculating classification metrics...")

classification_metrics = evaluator.calculate_classification_metrics(
    metrics['all_predictions'],
    metrics['all_targets']
)

print(f"\nClassification Accuracy:")
print(f"  Top-1: {classification_metrics['top1_accuracy']*100:.2f}%")
print(f"  Top-3: {classification_metrics['top3_accuracy']*100:.2f}%")
print(f"  Mean R²: {classification_metrics['mean_r2_score']:.4f}")

# %% Visualize Results
print("\nGenerating visualizations...")

# Delta E distribution
evaluator.plot_delta_e_distribution(
    metrics['delta_e_values'],
    save_path='delta_e_distribution.png'
)
print("✓ Delta E distribution saved")

# Prediction errors
evaluator.plot_prediction_errors(
    metrics['all_predictions'],
    metrics['all_targets'],
    save_path='prediction_errors.png'
)
print("✓ Prediction errors saved")

# Confusion matrix
evaluator.plot_confusion_matrix(
    classification_metrics['confusion_matrix'],
    save_path='confusion_matrix.png'
)
print("✓ Confusion matrix saved")

# %% Export Results
print("\nExporting results...")

evaluator.export_results_to_csv(
    {**metrics, **classification_metrics},
    save_path='../results/evaluation_results.csv'
)
print("✓ Results exported to CSV")

evaluator.generate_summary_report(
    {**metrics, **classification_metrics},
    save_path='../results/evaluation_report.txt'
)
print("✓ Summary report generated")

# %% [markdown]
# ## 4. CNN Inference Examples
# 
# Compare CNN predictions with CIEDE2000 for various test colors.

# %% Initialize Color Analysis Engine with CNN
print("\n" + "=" * 60)
print("STEP 4: CNN Inference Examples")
print("=" * 60)

# Save the trained model
model_path = "../models/color_detection/cnn_color_ratio_demo.pth"
model.save_model(model_path, model_version="v1.0.0")
print(f"\n✓ Model saved to {model_path}")

# Initialize engine with CNN model
engine = ColorAnalysisEngineV2(cnn_model_path=model_path)
print(f"✓ Engine initialized with CNN model")
print(f"  CNN available: {engine.cnn_available}")

# %% Test Colors
test_colors = [
    {"name": "Pure Red", "rgb": (255, 0, 0), "lab": (53.0, 80.0, 67.0)},
    {"name": "Pure Blue", "rgb": (0, 0, 255), "lab": (32.0, 79.0, -108.0)},
    {"name": "Pure Green", "rgb": (0, 255, 0), "lab": (46.0, -52.0, 50.0)},
    {"name": "Yellow", "rgb": (255, 255, 0), "lab": (95.0, -15.0, 90.0)},
    {"name": "Purple", "rgb": (128, 0, 128), "lab": (30.0, 59.0, -36.0)},
    {"name": "Orange", "rgb": (255, 128, 0), "lab": (67.0, 55.0, 70.0)},
]

print("\n" + "=" * 60)
print("Comparing CNN vs CIEDE2000 Predictions")
print("=" * 60)

for test_color in test_colors:
    print(f"\n{test_color['name']} - RGB{test_color['rgb']}")
    print("-" * 60)
    
    # Create test image
    test_image = np.full((224, 224, 3), test_color['rgb'], dtype=np.uint8)
    
    # CNN prediction
    pred_cnn = engine.analyze_color(
        test_color['rgb'],
        test_color['lab'],
        method="cnn",
        image=test_image
    )
    
    # CIEDE2000 prediction
    pred_ciede = engine.analyze_color(
        test_color['rgb'],
        test_color['lab'],
        method="ciede2000"
    )
    
    # Display results
    print(f"\nCNN Prediction:")
    print(f"  Method: {pred_cnn.prediction_method}")
    print(f"  Dominant: {pred_cnn.dominant_color} ({pred_cnn.confidence*100:.1f}%)")
    print(f"  Quality: {pred_cnn.quality_score}")
    print(f"  Inference time: {pred_cnn.inference_time_ms:.2f}ms")
    print(f"  Top 3 colors:")
    for i, (color, pct) in enumerate(list(pred_cnn.primary_colors.items())[:3]):
        print(f"    {i+1}. {color}: {pct:.1f}%")
    
    print(f"\nCIEDE2000 Prediction:")
    print(f"  Dominant: {pred_ciede.dominant_color} ({pred_ciede.confidence*100:.1f}%)")
    print(f"  Quality: {pred_ciede.quality_score}")
    print(f"  Top 3 colors:")
    for i, (color, pct) in enumerate(list(pred_ciede.primary_colors.items())[:3]):
        print(f"    {i+1}. {color}: {pct:.1f}%")
    
    # Generate mixing formulas
    formula_cnn = engine.get_mixing_formula(pred_cnn, simplify=True, max_colors=5)
    formula_ciede = engine.get_mixing_formula(pred_ciede, simplify=True, max_colors=5)
    
    print(f"\nMixing Formulas:")
    print(f"  CNN: {formula_cnn}")
    print(f"  CIEDE2000: {formula_ciede}")

# %% Visualize Comparison
print("\n" + "=" * 60)
print("Creating comparison visualization...")
print("=" * 60)

fig, axes = plt.subplots(len(test_colors), 3, figsize=(12, len(test_colors)*2))
fig.suptitle('CNN vs CIEDE2000 Comparison', fontsize=16)

for idx, test_color in enumerate(test_colors):
    # Create test image
    test_image = np.full((100, 100, 3), test_color['rgb'], dtype=np.uint8)
    
    # Get predictions
    pred_cnn = engine.analyze_color(
        test_color['rgb'], test_color['lab'],
        method="cnn", image=test_image
    )
    pred_ciede = engine.analyze_color(
        test_color['rgb'], test_color['lab'],
        method="ciede2000"
    )
    
    # Original color
    axes[idx, 0].imshow(test_image)
    axes[idx, 0].set_title(f"{test_color['name']}\nOriginal")
    axes[idx, 0].axis('off')
    
    # CNN top colors
    cnn_colors = list(pred_cnn.primary_colors.items())[:3]
    cnn_text = "\n".join([f"{c}: {p:.1f}%" for c, p in cnn_colors])
    axes[idx, 1].text(0.5, 0.5, f"CNN\n{pred_cnn.quality_score}\n\n{cnn_text}",
                      ha='center', va='center', fontsize=10)
    axes[idx, 1].axis('off')
    
    # CIEDE2000 top colors
    ciede_colors = list(pred_ciede.primary_colors.items())[:3]
    ciede_text = "\n".join([f"{c}: {p:.1f}%" for c, p in ciede_colors])
    axes[idx, 2].text(0.5, 0.5, f"CIEDE2000\n{pred_ciede.quality_score}\n\n{ciede_text}",
                      ha='center', va='center', fontsize=10)
    axes[idx, 2].axis('off')

plt.tight_layout()
plt.savefig('cnn_vs_ciede2000_comparison.png', dpi=150, bbox_inches='tight')
print("✓ Comparison visualization saved to 'cnn_vs_ciede2000_comparison.png'")

# %% [markdown]
# ## 5. Production Usage
# 
# Example of using the CNN model in production with automatic fallback.

# %% Production Example
print("\n" + "=" * 60)
print("STEP 5: Production Usage Example")
print("=" * 60)

# Initialize engine with auto method (tries CNN first, falls back to CIEDE2000)
engine_auto = ColorAnalysisEngineV2(cnn_model_path=model_path)

# Example: Analyze a custom color
custom_rgb = (180, 100, 120)
custom_lab = (50.0, 35.0, 10.0)
custom_image = np.full((224, 224, 3), custom_rgb, dtype=np.uint8)

print(f"\nAnalyzing custom color: RGB{custom_rgb}")

# Auto method (tries CNN first)
prediction = engine_auto.analyze_color(
    custom_rgb,
    custom_lab,
    method="auto",
    image=custom_image
)

print(f"\nPrediction Results:")
print(f"  Method used: {prediction.prediction_method}")
print(f"  Dominant color: {prediction.dominant_color}")
print(f"  Confidence: {prediction.confidence*100:.1f}%")
print(f"  Quality: {prediction.quality_score}")

# Generate and save mixing formula
formula = engine_auto.get_mixing_formula(prediction, simplify=True, max_colors=5)
print(f"\nMixing Formula: {formula}")

# Validate formula
validation = engine_auto.validate_mixing_formula(formula)
print(f"\nFormula Validation:")
print(f"  Valid: {validation['valid']}")
print(f"  Total parts: {validation['total_parts']}")
print(f"  Num colors: {validation['num_colors']}")

# Save formula
saved_path = engine_auto.save_formula_to_file(
    formula,
    prediction,
    output_dir="../mixing_formulas"
)
print(f"\n✓ Formula saved to: {saved_path}")

# Generate UART message
uart_msg = engine_auto.format_uart_message(formula)
print(f"✓ UART message: {uart_msg}")

print("\n" + "=" * 60)
print("Demo Complete!")
print("=" * 60)
print("\nNext steps:")
print("1. Train with larger datasets (10k+ samples)")
print("2. Fine-tune hyperparameters")
print("3. Test with real camera images")
print("4. Integrate into production UI")
