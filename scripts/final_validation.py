#!/usr/bin/env python3
"""
Final validation script for CNN Color Ratio Model.
Validates all requirements are met before deployment.
"""

import sys
import argparse
from pathlib import Path
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from deep_color_model import CNNColorRatioModel
from advanced_color_analysis import ColorAnalysisEngineV2
from color_evaluator import ColorPredictionEvaluator
from dl_config import BASE_COLORS

try:
    import torch
    from torch.utils.data import DataLoader
    from color_data_generator import ColorRatioDataset
    import numpy as np
except ImportError:
    print("Error: Required packages not installed")
    sys.exit(1)


def validate_model_accuracy(model, test_path):
    """Validate model accuracy requirements."""
    print("\n" + "="*60)
    print("1. Model Accuracy Validation")
    print("="*60)
    
    # Load test dataset
    test_dataset = ColorRatioDataset(test_path)
    test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False)
    
    # Evaluate
    evaluator = ColorPredictionEvaluator(model, BASE_COLORS)
    metrics = evaluator.evaluate_dataset(test_loader, calculate_per_color_metrics=True)
    classification_metrics = evaluator.calculate_classification_metrics(
        metrics['all_predictions'],
        metrics['all_targets']
    )
    
    # Check requirements
    results = {}
    
    # Requirement 1: Delta E < 2.0 for 80% of samples
    delta_e_80 = metrics['delta_e_below_2']
    results['delta_e_80_percent'] = {
        'requirement': 0.80,
        'actual': delta_e_80,
        'pass': delta_e_80 >= 0.80
    }
    
    print(f"\n✓ Delta E < 2.0 for 80% samples:")
    print(f"  Requirement: ≥ 80%")
    print(f"  Actual: {delta_e_80*100:.1f}%")
    print(f"  Status: {'✓ PASS' if results['delta_e_80_percent']['pass'] else '✗ FAIL'}")
    
    # Requirement 2: Top-1 accuracy > 85%
    top1_acc = classification_metrics['top1_accuracy']
    results['top1_accuracy'] = {
        'requirement': 0.85,
        'actual': top1_acc,
        'pass': top1_acc >= 0.85
    }
    
    print(f"\n✓ Top-1 Accuracy:")
    print(f"  Requirement: ≥ 85%")
    print(f"  Actual: {top1_acc*100:.1f}%")
    print(f"  Status: {'✓ PASS' if results['top1_accuracy']['pass'] else '✗ FAIL'}")
    
    # Requirement 3: R² scores > 0.90
    mean_r2 = metrics['mean_r2_score']
    results['mean_r2_score'] = {
        'requirement': 0.90,
        'actual': mean_r2,
        'pass': mean_r2 >= 0.90
    }
    
    print(f"\n✓ Mean R² Score:")
    print(f"  Requirement: ≥ 0.90")
    print(f"  Actual: {mean_r2:.4f}")
    print(f"  Status: {'✓ PASS' if results['mean_r2_score']['pass'] else '✗ FAIL'}")
    
    return results


def validate_integration(model_path):
    """Validate integration with ColorAnalysisEngine."""
    print("\n" + "="*60)
    print("2. Integration Validation")
    print("="*60)
    
    results = {}
    
    # Test 1: Engine initialization
    try:
        engine = ColorAnalysisEngineV2(cnn_model_path=model_path)
        results['engine_init'] = {'pass': True, 'error': None}
        print("\n✓ Engine initialization: PASS")
    except Exception as e:
        results['engine_init'] = {'pass': False, 'error': str(e)}
        print(f"\n✗ Engine initialization: FAIL - {e}")
        return results
    
    # Test 2: CNN availability
    results['cnn_available'] = {
        'pass': engine.cnn_available,
        'error': None if engine.cnn_available else "CNN not available"
    }
    print(f"✓ CNN availability: {'PASS' if engine.cnn_available else 'FAIL'}")
    
    # Test 3: Method selection
    test_rgb = (255, 0, 0)
    test_lab = (53.0, 80.0, 67.0)
    test_image = np.full((224, 224, 3), test_rgb, dtype=np.uint8)
    
    try:
        # Test auto method
        pred_auto = engine.analyze_color(test_rgb, test_lab, method="auto", image=test_image)
        results['method_auto'] = {'pass': True, 'error': None}
        print("✓ Auto method: PASS")
        
        # Test CNN method
        pred_cnn = engine.analyze_color(test_rgb, test_lab, method="cnn", image=test_image)
        results['method_cnn'] = {'pass': True, 'error': None}
        print("✓ CNN method: PASS")
        
        # Test CIEDE2000 method
        pred_ciede = engine.analyze_color(test_rgb, test_lab, method="ciede2000")
        results['method_ciede2000'] = {'pass': True, 'error': None}
        print("✓ CIEDE2000 method: PASS")
        
    except Exception as e:
        results['method_selection'] = {'pass': False, 'error': str(e)}
        print(f"✗ Method selection: FAIL - {e}")
    
    # Test 4: Fallback mechanism
    try:
        # Test with invalid image (should fallback)
        pred_fallback = engine.analyze_color(test_rgb, test_lab, method="auto", image=None)
        fallback_ok = pred_fallback.prediction_method == "ciede2000"
        results['fallback'] = {'pass': fallback_ok, 'error': None}
        print(f"✓ Fallback mechanism: {'PASS' if fallback_ok else 'FAIL'}")
    except Exception as e:
        results['fallback'] = {'pass': False, 'error': str(e)}
        print(f"✗ Fallback mechanism: FAIL - {e}")
    
    # Test 5: Formula generation
    try:
        formula = engine.get_mixing_formula(pred_cnn, simplify=True, max_colors=8)
        validation = engine.validate_mixing_formula(formula)
        formula_ok = validation['valid']
        results['formula_generation'] = {'pass': formula_ok, 'error': None}
        print(f"✓ Formula generation: {'PASS' if formula_ok else 'FAIL'}")
    except Exception as e:
        results['formula_generation'] = {'pass': False, 'error': str(e)}
        print(f"✗ Formula generation: FAIL - {e}")
    
    return results


def validate_backward_compatibility():
    """Validate backward compatibility with existing workflows."""
    print("\n" + "="*60)
    print("3. Backward Compatibility Validation")
    print("="*60)
    
    results = {}
    
    # Test 1: CIEDE2000-only engine
    try:
        engine = ColorAnalysisEngineV2()  # No CNN model
        test_rgb = (128, 128, 128)
        test_lab = (53.0, 0.0, 0.0)
        pred = engine.analyze_color(test_rgb, test_lab, method="ciede2000")
        
        ciede_ok = pred.prediction_method == "ciede2000"
        results['ciede2000_only'] = {'pass': ciede_ok, 'error': None}
        print(f"✓ CIEDE2000-only mode: {'PASS' if ciede_ok else 'FAIL'}")
    except Exception as e:
        results['ciede2000_only'] = {'pass': False, 'error': str(e)}
        print(f"✗ CIEDE2000-only mode: FAIL - {e}")
    
    # Test 2: ColorPrediction structure
    try:
        # Check all required fields exist
        required_fields = [
            'primary_colors', 'dominant_color', 'confidence',
            'rgb_values', 'lab_values', 'delta_e_values',
            'prediction_method', 'model_version', 'inference_time_ms', 'quality_score'
        ]
        
        all_fields_exist = all(hasattr(pred, field) for field in required_fields)
        results['prediction_structure'] = {'pass': all_fields_exist, 'error': None}
        print(f"✓ ColorPrediction structure: {'PASS' if all_fields_exist else 'FAIL'}")
    except Exception as e:
        results['prediction_structure'] = {'pass': False, 'error': str(e)}
        print(f"✗ ColorPrediction structure: FAIL - {e}")
    
    return results


def validate_deployment_readiness(model_path):
    """Validate deployment readiness."""
    print("\n" + "="*60)
    print("4. Deployment Readiness Validation")
    print("="*60)
    
    results = {}
    
    # Check 1: Model file exists
    model_file = Path(model_path)
    results['model_exists'] = {
        'pass': model_file.exists(),
        'error': None if model_file.exists() else "Model file not found"
    }
    print(f"✓ Model file exists: {'PASS' if results['model_exists']['pass'] else 'FAIL'}")
    
    # Check 2: Model loads successfully
    try:
        model = CNNColorRatioModel(model_path=model_path)
        results['model_loads'] = {'pass': True, 'error': None}
        print("✓ Model loads: PASS")
    except Exception as e:
        results['model_loads'] = {'pass': False, 'error': str(e)}
        print(f"✗ Model loads: FAIL - {e}")
        return results
    
    # Check 3: Model has version info
    model_info = model.get_model_info()
    has_version = model_info.get('model_version') is not None
    results['model_version'] = {
        'pass': has_version,
        'error': None if has_version else "No version info"
    }
    print(f"✓ Model version info: {'PASS' if has_version else 'FAIL'}")
    
    # Check 4: Device compatibility
    device_ok = str(model.device) in ['cpu', 'cuda', 'mps']
    results['device_compatibility'] = {
        'pass': device_ok,
        'error': None if device_ok else f"Unknown device: {model.device}"
    }
    print(f"✓ Device compatibility: {'PASS' if device_ok else 'FAIL'} ({model.device})")
    
    # Check 5: Inference works
    try:
        test_image = np.random.randint(0, 256, (224, 224, 3), dtype=np.uint8)
        ratios = model.predict(test_image)
        inference_ok = ratios.shape == (16,) and np.isclose(ratios.sum(), 1.0)
        results['inference_works'] = {'pass': inference_ok, 'error': None}
        print(f"✓ Inference works: {'PASS' if inference_ok else 'FAIL'}")
    except Exception as e:
        results['inference_works'] = {'pass': False, 'error': str(e)}
        print(f"✗ Inference works: FAIL - {e}")
    
    return results


def generate_validation_report(all_results, output_file='validation_report.json'):
    """Generate comprehensive validation report."""
    print("\n" + "="*60)
    print("Validation Summary")
    print("="*60)
    
    # Count passes and fails
    total_checks = 0
    passed_checks = 0
    
    for category, results in all_results.items():
        for check, result in results.items():
            total_checks += 1
            if result.get('pass', False):
                passed_checks += 1
    
    pass_rate = (passed_checks / total_checks) * 100 if total_checks > 0 else 0
    
    print(f"\nTotal Checks: {total_checks}")
    print(f"Passed: {passed_checks}")
    print(f"Failed: {total_checks - passed_checks}")
    print(f"Pass Rate: {pass_rate:.1f}%")
    
    # Save report
    report = {
        'timestamp': str(Path(__file__).parent),
        'summary': {
            'total_checks': total_checks,
            'passed': passed_checks,
            'failed': total_checks - passed_checks,
            'pass_rate': pass_rate
        },
        'results': all_results
    }
    
    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n✓ Validation report saved to: {output_file}")
    
    # Final verdict
    print("\n" + "="*60)
    if pass_rate == 100:
        print("✓ ALL VALIDATIONS PASSED - READY FOR DEPLOYMENT")
    elif pass_rate >= 90:
        print("⚠ MOSTLY PASSED - REVIEW FAILURES BEFORE DEPLOYMENT")
    else:
        print("✗ VALIDATION FAILED - NOT READY FOR DEPLOYMENT")
    print("="*60)
    
    return pass_rate == 100


def main():
    parser = argparse.ArgumentParser(description='Final validation for CNN model')
    parser.add_argument(
        '--model',
        type=str,
        default='models/color_detection/cnn_color_ratio_v1.0.0.pth',
        help='Path to model file'
    )
    parser.add_argument(
        '--test-data',
        type=str,
        default='data/test/test_dataset.h5',
        help='Path to test dataset'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='validation_report.json',
        help='Output file for validation report'
    )
    
    args = parser.parse_args()
    
    print("="*60)
    print("CNN Color Ratio Model - Final Validation")
    print("="*60)
    
    all_results = {}
    
    # Run validations
    try:
        # Load model
        print(f"\nLoading model from: {args.model}")
        model = CNNColorRatioModel(model_path=args.model)
        
        # 1. Accuracy validation
        if Path(args.test_data).exists():
            all_results['accuracy'] = validate_model_accuracy(model, args.test_data)
        else:
            print(f"\n⚠ Test data not found: {args.test_data}")
            print("  Skipping accuracy validation")
        
        # 2. Integration validation
        all_results['integration'] = validate_integration(args.model)
        
        # 3. Backward compatibility
        all_results['backward_compatibility'] = validate_backward_compatibility()
        
        # 4. Deployment readiness
        all_results['deployment'] = validate_deployment_readiness(args.model)
        
        # Generate report
        ready = generate_validation_report(all_results, args.output)
        
        sys.exit(0 if ready else 1)
    
    except Exception as e:
        print(f"\n✗ Validation failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
