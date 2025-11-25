#!/usr/bin/env python3
"""
Standalone training script for CNN Color Ratio Model.
Supports command-line interface and configuration files.
"""

import argparse
import sys
import yaml
import json
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from color_data_generator import ColorDataGenerator, create_train_val_test_datasets
from deep_color_model import CNNColorRatioModel
from color_evaluator import ColorPredictionEvaluator
from dl_config import BASE_COLORS

try:
    import torch
    from torch.utils.data import DataLoader
    from color_data_generator import ColorRatioDataset
except ImportError:
    print("Error: PyTorch not installed. Install with: pip install torch torchvision")
    sys.exit(1)


def load_config(config_path: str) -> dict:
    """Load configuration from YAML or JSON file."""
    config_path = Path(config_path)
    
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    with open(config_path, 'r') as f:
        if config_path.suffix in ['.yaml', '.yml']:
            config = yaml.safe_load(f)
        elif config_path.suffix == '.json':
            config = json.load(f)
        else:
            raise ValueError(f"Unsupported config format: {config_path.suffix}")
    
    return config


def create_default_config() -> dict:
    """Create default training configuration."""
    return {
        'data': {
            'num_train': 10000,
            'num_val': 2000,
            'num_test': 1000,
            'output_dir': 'data',
            'apply_augmentation': True
        },
        'model': {
            'device': 'auto',
            'num_colors': 16
        },
        'training': {
            'epochs': 50,
            'batch_size': 32,
            'learning_rate': 0.001,
            'early_stopping_patience': 10,
            'scheduler_patience': 3,
            'scheduler_factor': 0.5
        },
        'checkpoints': {
            'dir': 'models/checkpoints',
            'interval': 5
        },
        'logging': {
            'dir': 'logs',
            'experiment_name': None  # Auto-generated if None
        },
        'output': {
            'model_dir': 'models/color_detection',
            'model_name': 'cnn_color_ratio',
            'model_version': 'v1.0.0'
        }
    }


def generate_data(config: dict):
    """Generate training, validation, and test datasets."""
    print("\n" + "="*60)
    print("STEP 1: Generating Training Data")
    print("="*60)
    
    data_config = config['data']
    
    train_path, val_path, test_path = create_train_val_test_datasets(
        num_train=data_config['num_train'],
        num_val=data_config['num_val'],
        num_test=data_config['num_test'],
        output_dir=data_config['output_dir'],
        apply_augmentation=data_config['apply_augmentation']
    )
    
    print(f"\n✓ Training data: {train_path}")
    print(f"✓ Validation data: {val_path}")
    print(f"✓ Test data: {test_path}")
    
    return train_path, val_path, test_path


def train_model(config: dict, train_path: str, val_path: str):
    """Train the CNN model."""
    print("\n" + "="*60)
    print("STEP 2: Training CNN Model")
    print("="*60)
    
    # Initialize model
    model_config = config['model']
    model = CNNColorRatioModel(
        device=model_config['device'],
        num_colors=model_config['num_colors']
    )
    
    print(f"\nModel initialized on device: {model.device}")
    print(f"Number of parameters: {model.get_model_info()['num_parameters']:,}")
    
    # Load datasets
    train_dataset = ColorRatioDataset(train_path)
    val_dataset = ColorRatioDataset(val_path)
    
    # Create data loaders
    training_config = config['training']
    train_loader = DataLoader(
        train_dataset,
        batch_size=training_config['batch_size'],
        shuffle=True
    )
    val_loader = DataLoader(
        val_dataset,
        batch_size=training_config['batch_size'],
        shuffle=False
    )
    
    print(f"\nDataset sizes:")
    print(f"  Training: {len(train_dataset)} samples")
    print(f"  Validation: {len(val_dataset)} samples")
    
    # Generate experiment name if not provided
    logging_config = config['logging']
    if logging_config['experiment_name'] is None:
        logging_config['experiment_name'] = f"training_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Train model
    print(f"\nStarting training for {training_config['epochs']} epochs...")
    print(f"Experiment: {logging_config['experiment_name']}")
    
    history = model.train(
        train_loader=train_loader,
        val_loader=val_loader,
        epochs=training_config['epochs'],
        learning_rate=training_config['learning_rate'],
        checkpoint_dir=config['checkpoints']['dir'],
        checkpoint_interval=config['checkpoints']['interval'],
        early_stopping_patience=training_config['early_stopping_patience'],
        scheduler_patience=training_config['scheduler_patience'],
        scheduler_factor=training_config['scheduler_factor'],
        log_dir=logging_config['dir'],
        experiment_name=logging_config['experiment_name']
    )
    
    print("\n✓ Training complete!")
    
    return model, history


def evaluate_model_performance(config: dict, model, test_path: str):
    """Evaluate the trained model."""
    print("\n" + "="*60)
    print("STEP 3: Model Evaluation")
    print("="*60)
    
    # Load test dataset
    test_dataset = ColorRatioDataset(test_path)
    test_loader = DataLoader(
        test_dataset,
        batch_size=config['training']['batch_size'],
        shuffle=False
    )
    
    print(f"\nTest set size: {len(test_dataset)} samples")
    
    # Create evaluator
    evaluator = ColorPredictionEvaluator(model, BASE_COLORS)
    
    # Evaluate
    print("\nEvaluating model...")
    metrics = evaluator.evaluate_dataset(test_loader, calculate_per_color_metrics=True)
    
    # Print results
    print(f"\n{'='*60}")
    print("EVALUATION RESULTS")
    print(f"{'='*60}")
    print(f"Mean Delta E: {metrics['mean_delta_e']:.2f}")
    print(f"Median Delta E: {metrics['median_delta_e']:.2f}")
    print(f"\nQuality Distribution:")
    print(f"  Excellent (ΔE < 1): {metrics['delta_e_below_1']*100:.1f}%")
    print(f"  Good (ΔE < 2): {metrics['delta_e_below_2']*100:.1f}%")
    print(f"  Acceptable (ΔE < 4): {metrics['delta_e_below_4']*100:.1f}%")
    print(f"\nRegression Metrics:")
    print(f"  MSE: {metrics['mse']:.6f}")
    print(f"  MAE: {metrics['mae']:.6f}")
    print(f"  Mean R² Score: {metrics['mean_r2_score']:.4f}")
    
    # Calculate classification metrics
    classification_metrics = evaluator.calculate_classification_metrics(
        metrics['all_predictions'],
        metrics['all_targets']
    )
    
    print(f"\nClassification Accuracy:")
    print(f"  Top-1: {classification_metrics['top1_accuracy']*100:.2f}%")
    print(f"  Top-3: {classification_metrics['top3_accuracy']*100:.2f}%")
    
    return metrics, classification_metrics


def save_model(config: dict, model):
    """Save the trained model."""
    print("\n" + "="*60)
    print("STEP 4: Saving Model")
    print("="*60)
    
    output_config = config['output']
    
    # Create output directory
    output_dir = Path(output_config['model_dir'])
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate model filename
    model_name = output_config['model_name']
    model_version = output_config['model_version']
    model_filename = f"{model_name}_{model_version}.pth"
    model_path = output_dir / model_filename
    
    # Save model
    model.save_model(
        str(model_path),
        model_version=model_version,
        training_metadata={
            'training_date': datetime.now().isoformat(),
            'config': config
        }
    )
    
    print(f"\n✓ Model saved to: {model_path}")
    
    return str(model_path)


def main():
    """Main training function."""
    parser = argparse.ArgumentParser(
        description='Train CNN Color Ratio Model',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Train with default configuration
  python train_cnn_model.py
  
  # Train with custom config file
  python train_cnn_model.py --config config.yaml
  
  # Generate data only
  python train_cnn_model.py --data-only
  
  # Skip data generation (use existing data)
  python train_cnn_model.py --skip-data-gen --train-data data/training/train_dataset.h5
        """
    )
    
    parser.add_argument(
        '--config',
        type=str,
        help='Path to configuration file (YAML or JSON)'
    )
    parser.add_argument(
        '--data-only',
        action='store_true',
        help='Only generate data, do not train'
    )
    parser.add_argument(
        '--skip-data-gen',
        action='store_true',
        help='Skip data generation, use existing datasets'
    )
    parser.add_argument(
        '--train-data',
        type=str,
        help='Path to training dataset (required if --skip-data-gen)'
    )
    parser.add_argument(
        '--val-data',
        type=str,
        help='Path to validation dataset (required if --skip-data-gen)'
    )
    parser.add_argument(
        '--test-data',
        type=str,
        help='Path to test dataset (required if --skip-data-gen)'
    )
    parser.add_argument(
        '--epochs',
        type=int,
        help='Number of training epochs (overrides config)'
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        help='Batch size (overrides config)'
    )
    parser.add_argument(
        '--lr',
        type=float,
        help='Learning rate (overrides config)'
    )
    parser.add_argument(
        '--device',
        type=str,
        choices=['auto', 'cpu', 'cuda', 'mps'],
        help='Device to use for training (overrides config)'
    )
    
    args = parser.parse_args()
    
    # Load or create configuration
    if args.config:
        print(f"Loading configuration from: {args.config}")
        config = load_config(args.config)
    else:
        print("Using default configuration")
        config = create_default_config()
    
    # Apply command-line overrides
    if args.epochs:
        config['training']['epochs'] = args.epochs
    if args.batch_size:
        config['training']['batch_size'] = args.batch_size
    if args.lr:
        config['training']['learning_rate'] = args.lr
    if args.device:
        config['model']['device'] = args.device
    
    print("\nConfiguration:")
    print(json.dumps(config, indent=2))
    
    # Generate or load data
    if args.skip_data_gen:
        if not all([args.train_data, args.val_data, args.test_data]):
            print("Error: --train-data, --val-data, and --test-data required with --skip-data-gen")
            sys.exit(1)
        
        train_path = args.train_data
        val_path = args.val_data
        test_path = args.test_data
        
        print(f"\nUsing existing datasets:")
        print(f"  Training: {train_path}")
        print(f"  Validation: {val_path}")
        print(f"  Test: {test_path}")
    else:
        train_path, val_path, test_path = generate_data(config)
    
    if args.data_only:
        print("\n✓ Data generation complete. Exiting (--data-only specified).")
        return
    
    # Train model
    model, history = train_model(config, train_path, val_path)
    
    # Evaluate model
    metrics, classification_metrics = evaluate_model_performance(
        config, model, test_path
    )
    
    # Save model
    model_path = save_model(config, model)
    
    print("\n" + "="*60)
    print("Training Complete!")
    print("="*60)
    print(f"\nModel saved to: {model_path}")
    print(f"Logs saved to: {config['logging']['dir']}")
    print(f"Checkpoints saved to: {config['checkpoints']['dir']}")
    print(f"\nFinal Metrics:")
    print(f"  Mean Delta E: {metrics['mean_delta_e']:.2f}")
    print(f"  Top-1 Accuracy: {classification_metrics['top1_accuracy']*100:.2f}%")
    print(f"  Mean R² Score: {metrics['mean_r2_score']:.4f}")
    
    # Check if requirements are met
    print(f"\nRequirements Check:")
    delta_e_ok = metrics['delta_e_below_2'] >= 0.80
    accuracy_ok = classification_metrics['top1_accuracy'] >= 0.85
    r2_ok = metrics['mean_r2_score'] >= 0.90
    
    print(f"  ΔE < 2.0 for 80% samples: {'✓' if delta_e_ok else '✗'} ({metrics['delta_e_below_2']*100:.1f}%)")
    print(f"  Top-1 accuracy > 85%: {'✓' if accuracy_ok else '✗'} ({classification_metrics['top1_accuracy']*100:.1f}%)")
    print(f"  Mean R² > 0.90: {'✓' if r2_ok else '✗'} ({metrics['mean_r2_score']:.4f})")
    
    if all([delta_e_ok, accuracy_ok, r2_ok]):
        print("\n🎉 All requirements met! Model is ready for production.")
    else:
        print("\n⚠ Some requirements not met. Consider:")
        print("  - Training for more epochs")
        print("  - Generating more training data")
        print("  - Adjusting hyperparameters")
        print("  - Adding more augmentation")


if __name__ == '__main__':
    main()
