#!/usr/bin/env python3
"""
Validate datasets to ensure correct preprocessing and data integrity.
Checks image ranges, ratio sums, and logs statistics.
"""

import sys
import argparse
from pathlib import Path
import json

import numpy as np
import h5py

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from dl_config import TRAINING_DATA_DIR, VALIDATION_DATA_DIR, TEST_DATA_DIR


def validate_dataset(dataset_path: Path, verbose: bool = True) -> dict:
    """
    Validate a single dataset file.
    
    Args:
        dataset_path: Path to HDF5 dataset file
        verbose: Print validation details
        
    Returns:
        Dictionary with validation results and statistics
    """
    if not dataset_path.exists():
        return {
            'valid': False,
            'error': f'Dataset file not found: {dataset_path}'
        }
    
    try:
        with h5py.File(dataset_path, 'r') as f:
            images = f['images'][:]
            ratios = f['ratios'][:]
            
            # Load metadata
            metadata = {}
            if 'metadata' in f.attrs:
                metadata = json.loads(f.attrs['metadata'])
            
            if verbose:
                print(f"\nValidating: {dataset_path.name}")
                print("=" * 60)
            
            # Validation checks
            results = {
                'valid': True,
                'path': str(dataset_path),
                'num_samples': len(images),
                'checks': {}
            }
            
            # Check 1: Image shape
            expected_shape = (len(images), 224, 224, 3)
            if images.shape == expected_shape:
                results['checks']['image_shape'] = 'PASS'
                if verbose:
                    print(f"✓ Image shape: {images.shape}")
            else:
                results['checks']['image_shape'] = 'FAIL'
                results['valid'] = False
                if verbose:
                    print(f"✗ Image shape: {images.shape} (expected {expected_shape})")
            
            # Check 2: Image data type
            if images.dtype == np.uint8:
                results['checks']['image_dtype'] = 'PASS'
                if verbose:
                    print(f"✓ Image dtype: {images.dtype}")
            else:
                results['checks']['image_dtype'] = 'FAIL'
                results['valid'] = False
                if verbose:
                    print(f"✗ Image dtype: {images.dtype} (expected uint8)")
            
            # Check 3: Image value range [0, 255]
            img_min = images.min()
            img_max = images.max()
            if img_min >= 0 and img_max <= 255:
                results['checks']['image_range'] = 'PASS'
                if verbose:
                    print(f"✓ Image range: [{img_min}, {img_max}]")
            else:
                results['checks']['image_range'] = 'FAIL'
                results['valid'] = False
                if verbose:
                    print(f"✗ Image range: [{img_min}, {img_max}] (expected [0, 255])")
            
            # Check 4: Ratios shape
            expected_ratios_shape = (len(images), 16)
            if ratios.shape == expected_ratios_shape:
                results['checks']['ratios_shape'] = 'PASS'
                if verbose:
                    print(f"✓ Ratios shape: {ratios.shape}")
            else:
                results['checks']['ratios_shape'] = 'FAIL'
                results['valid'] = False
                if verbose:
                    print(f"✗ Ratios shape: {ratios.shape} (expected {expected_ratios_shape})")
            
            # Check 5: Ratios data type
            if ratios.dtype == np.float32:
                results['checks']['ratios_dtype'] = 'PASS'
                if verbose:
                    print(f"✓ Ratios dtype: {ratios.dtype}")
            else:
                results['checks']['ratios_dtype'] = 'FAIL'
                results['valid'] = False
                if verbose:
                    print(f"✗ Ratios dtype: {ratios.dtype} (expected float32)")
            
            # Check 6: Ratios sum to 1.0
            ratios_sums = ratios.sum(axis=1)
            tolerance = 1e-6
            all_sum_to_one = np.all(np.abs(ratios_sums - 1.0) < tolerance)
            
            if all_sum_to_one:
                results['checks']['ratios_sum'] = 'PASS'
                if verbose:
                    print(f"✓ All ratios sum to 1.0 (tolerance: {tolerance})")
            else:
                results['checks']['ratios_sum'] = 'FAIL'
                results['valid'] = False
                bad_indices = np.where(np.abs(ratios_sums - 1.0) >= tolerance)[0]
                if verbose:
                    print(f"✗ {len(bad_indices)} samples have ratios not summing to 1.0")
                    print(f"  Example bad sums: {ratios_sums[bad_indices[:5]]}")
            
            # Check 7: Ratios range [0, 1]
            ratios_min = ratios.min()
            ratios_max = ratios.max()
            if ratios_min >= 0 and ratios_max <= 1.0:
                results['checks']['ratios_range'] = 'PASS'
                if verbose:
                    print(f"✓ Ratios range: [{ratios_min:.6f}, {ratios_max:.6f}]")
            else:
                results['checks']['ratios_range'] = 'FAIL'
                results['valid'] = False
                if verbose:
                    print(f"✗ Ratios range: [{ratios_min}, {ratios_max}] (expected [0, 1])")
            
            # Check 8: Preprocessing metadata
            if 'preprocessing_version' in metadata:
                results['checks']['preprocessing_metadata'] = 'PASS'
                if verbose:
                    print(f"✓ Preprocessing version: {metadata['preprocessing_version']}")
                    print(f"  Method: {metadata.get('preprocessing_method', 'N/A')}")
                    print(f"  ImageNet normalization: {metadata.get('imagenet_normalization', 'N/A')}")
            else:
                results['checks']['preprocessing_metadata'] = 'WARNING'
                if verbose:
                    print(f"⚠ No preprocessing metadata found (old dataset format)")
            
            # Calculate statistics
            if verbose:
                print("\nDataset Statistics:")
                print("-" * 60)
                
                # Image statistics (normalized to [0,1] for analysis)
                images_normalized = images.astype(np.float32) / 255.0
                print(f"Images (normalized to [0,1]):")
                print(f"  Mean: {images_normalized.mean():.4f}")
                print(f"  Std:  {images_normalized.std():.4f}")
                print(f"  Min:  {images_normalized.min():.4f}")
                print(f"  Max:  {images_normalized.max():.4f}")
                
                # Per-channel statistics
                for c, channel in enumerate(['R', 'G', 'B']):
                    channel_data = images_normalized[:, :, :, c]
                    print(f"  {channel} channel - Mean: {channel_data.mean():.4f}, Std: {channel_data.std():.4f}")
                
                # Ratios statistics
                print(f"\nRatios:")
                print(f"  Mean: {ratios.mean():.4f}")
                print(f"  Std:  {ratios.std():.4f}")
                print(f"  Min:  {ratios.min():.6f}")
                print(f"  Max:  {ratios.max():.6f}")
                
                # Non-zero ratios statistics
                non_zero_ratios = ratios[ratios > 0]
                print(f"  Non-zero ratios mean: {non_zero_ratios.mean():.4f}")
                print(f"  Non-zero ratios count: {len(non_zero_ratios)}")
                
                # Colors per sample statistics
                colors_per_sample = (ratios > 0.01).sum(axis=1)  # Count colors > 1%
                print(f"\nColors per sample (>1% ratio):")
                print(f"  Mean: {colors_per_sample.mean():.2f}")
                print(f"  Min:  {colors_per_sample.min()}")
                print(f"  Max:  {colors_per_sample.max()}")
            
            # Store statistics in results
            images_normalized = images.astype(np.float32) / 255.0
            results['statistics'] = {
                'images': {
                    'mean': float(images_normalized.mean()),
                    'std': float(images_normalized.std()),
                    'min': float(images_normalized.min()),
                    'max': float(images_normalized.max())
                },
                'ratios': {
                    'mean': float(ratios.mean()),
                    'std': float(ratios.std()),
                    'min': float(ratios.min()),
                    'max': float(ratios.max())
                }
            }
            
            results['metadata'] = metadata
            
            return results
    
    except Exception as e:
        return {
            'valid': False,
            'error': str(e)
        }


def main():
    parser = argparse.ArgumentParser(
        description='Validate datasets for correct preprocessing',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--dataset',
        type=str,
        help='Path to specific dataset file to validate'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Validate all datasets (train, val, test)'
    )
    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Suppress detailed output'
    )
    
    args = parser.parse_args()
    verbose = not args.quiet
    
    try:
        if args.dataset:
            # Validate specific dataset
            dataset_path = Path(args.dataset)
            results = validate_dataset(dataset_path, verbose=verbose)
            
            if results['valid']:
                print("\n" + "=" * 60)
                print("✓ VALIDATION PASSED")
                print("=" * 60)
                sys.exit(0)
            else:
                print("\n" + "=" * 60)
                print("✗ VALIDATION FAILED")
                if 'error' in results:
                    print(f"Error: {results['error']}")
                print("=" * 60)
                sys.exit(1)
        
        elif args.all:
            # Validate all datasets
            datasets = [
                ("Training", TRAINING_DATA_DIR / "train_dataset.h5"),
                ("Validation", VALIDATION_DATA_DIR / "val_dataset.h5"),
                ("Test", TEST_DATA_DIR / "test_dataset.h5")
            ]
            
            all_valid = True
            all_results = []
            
            for name, path in datasets:
                if verbose:
                    print(f"\n{'=' * 60}")
                    print(f"Validating {name} Dataset")
                    print(f"{'=' * 60}")
                
                results = validate_dataset(path, verbose=verbose)
                all_results.append((name, results))
                
                if not results['valid']:
                    all_valid = False
            
            # Summary
            print("\n" + "=" * 60)
            print("VALIDATION SUMMARY")
            print("=" * 60)
            
            for name, results in all_results:
                status = "✓ PASS" if results['valid'] else "✗ FAIL"
                print(f"{name:15} {status}")
                if not results['valid'] and 'error' in results:
                    print(f"  Error: {results['error']}")
            
            print("=" * 60)
            
            if all_valid:
                print("✓ ALL DATASETS VALID")
                sys.exit(0)
            else:
                print("✗ SOME DATASETS FAILED VALIDATION")
                sys.exit(1)
        
        else:
            # Default: validate all
            parser.print_help()
            print("\nUse --all to validate all datasets")
            sys.exit(1)
    
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
