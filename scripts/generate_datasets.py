#!/usr/bin/env python3
"""
Generate training, validation, and test datasets for CNN Color Ratio Model.
This script creates synthetic color images with known mixing ratios.
"""

import sys
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from color_data_generator import create_train_val_test_datasets

def main():
    parser = argparse.ArgumentParser(
        description='Generate datasets for CNN training',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate small datasets for testing (fast)
  python generate_datasets.py --small
  
  # Generate medium datasets for development
  python generate_datasets.py --medium
  
  # Generate large datasets for production
  python generate_datasets.py --large
  
  # Generate custom size datasets
  python generate_datasets.py --train 10000 --val 2000 --test 1000
        """
    )
    
    parser.add_argument(
        '--small',
        action='store_true',
        help='Generate small datasets (100/20/10 samples) - for quick testing'
    )
    parser.add_argument(
        '--medium',
        action='store_true',
        help='Generate medium datasets (1000/200/100 samples) - for development'
    )
    parser.add_argument(
        '--large',
        action='store_true',
        help='Generate large datasets (10000/2000/1000 samples) - for production'
    )
    parser.add_argument(
        '--train',
        type=int,
        help='Number of training samples (custom)'
    )
    parser.add_argument(
        '--val',
        type=int,
        help='Number of validation samples (custom)'
    )
    parser.add_argument(
        '--test',
        type=int,
        help='Number of test samples (custom)'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='data',
        help='Output directory for datasets (default: data)'
    )
    parser.add_argument(
        '--no-augmentation',
        action='store_true',
        help='Disable augmentation for training data'
    )
    
    args = parser.parse_args()
    
    # Determine dataset sizes
    if args.small:
        num_train, num_val, num_test = 100, 20, 10
        print("Generating SMALL datasets (for quick testing)")
    elif args.medium:
        num_train, num_val, num_test = 1000, 200, 100
        print("Generating MEDIUM datasets (for development)")
    elif args.large:
        num_train, num_val, num_test = 10000, 2000, 1000
        print("Generating LARGE datasets (for production)")
    elif args.train and args.val and args.test:
        num_train, num_val, num_test = args.train, args.val, args.test
        print(f"Generating CUSTOM datasets ({num_train}/{num_val}/{num_test})")
    else:
        # Default to medium
        num_train, num_val, num_test = 1000, 200, 100
        print("Generating MEDIUM datasets (default)")
    
    print(f"\nDataset configuration:")
    print(f"  Training samples: {num_train}")
    print(f"  Validation samples: {num_val}")
    print(f"  Test samples: {num_test}")
    print(f"  Output directory: {args.output_dir}")
    print(f"  Augmentation: {'Disabled' if args.no_augmentation else 'Enabled'}")
    
    # Generate datasets
    print("\n" + "="*60)
    print("Starting dataset generation...")
    print("="*60)
    
    try:
        train_path, val_path, test_path = create_train_val_test_datasets(
            num_train=num_train,
            num_val=num_val,
            num_test=num_test,
            output_dir=args.output_dir,
            apply_augmentation=not args.no_augmentation
        )
        
        print("\n" + "="*60)
        print("✓ Dataset generation complete!")
        print("="*60)
        print(f"\nGenerated files:")
        print(f"  Training: {train_path}")
        print(f"  Validation: {val_path}")
        print(f"  Test: {test_path}")
        
        # Show file sizes
        from pathlib import Path
        train_size = Path(train_path).stat().st_size / (1024 * 1024)  # MB
        val_size = Path(val_path).stat().st_size / (1024 * 1024)
        test_size = Path(test_path).stat().st_size / (1024 * 1024)
        total_size = train_size + val_size + test_size
        
        print(f"\nFile sizes:")
        print(f"  Training: {train_size:.1f} MB")
        print(f"  Validation: {val_size:.1f} MB")
        print(f"  Test: {test_size:.1f} MB")
        print(f"  Total: {total_size:.1f} MB")
        
        print(f"\n✓ Ready to train! Use these datasets with:")
        print(f"  python scripts/train_cnn_model.py --skip-data-gen \\")
        print(f"    --train-data {train_path} \\")
        print(f"    --val-data {val_path} \\")
        print(f"    --test-data {test_path}")
        
    except Exception as e:
        print(f"\n✗ Error generating datasets: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
