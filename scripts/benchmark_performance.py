#!/usr/bin/env python3
"""
Performance benchmarking script for CNN Color Ratio Model.
Measures inference time, memory usage, and throughput.
"""

import sys
import time
import argparse
from pathlib import Path
import numpy as np

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from deep_color_model import CNNColorRatioModel
from advanced_color_analysis import ColorAnalysisEngineV2

try:
    import torch
    import psutil
except ImportError:
    print("Error: Required packages not installed")
    print("Install with: pip install torch psutil")
    sys.exit(1)


def benchmark_inference_speed(model, num_samples=100, batch_sizes=[1, 8, 16, 32]):
    """Benchmark inference speed for different batch sizes."""
    print("\n" + "="*60)
    print("Inference Speed Benchmark")
    print("="*60)
    
    results = {}
    
    for batch_size in batch_sizes:
        # Generate random test images
        images = np.random.randint(0, 256, (num_samples, 224, 224, 3), dtype=np.uint8)
        
        # Warmup
        for i in range(5):
            _ = model.predict(images[0])
        
        # Benchmark
        times = []
        for i in range(0, num_samples, batch_size):
            batch = images[i:min(i+batch_size, num_samples)]
            
            start = time.time()
            if len(batch) == 1:
                _ = model.predict(batch[0])
            else:
                _ = model.predict_batch(list(batch))
            end = time.time()
            
            times.append((end - start) * 1000)  # Convert to ms
        
        avg_time = np.mean(times)
        std_time = np.std(times)
        throughput = (batch_size / avg_time) * 1000  # images/second
        
        results[batch_size] = {
            'avg_time_ms': avg_time,
            'std_time_ms': std_time,
            'throughput': throughput
        }
        
        print(f"\nBatch Size: {batch_size}")
        print(f"  Avg Time: {avg_time:.2f} ± {std_time:.2f} ms")
        print(f"  Throughput: {throughput:.1f} images/sec")
    
    return results


def benchmark_memory_usage(model):
    """Benchmark memory usage."""
    print("\n" + "="*60)
    print("Memory Usage Benchmark")
    print("="*60)
    
    process = psutil.Process()
    
    # Baseline memory
    baseline_memory = process.memory_info().rss / 1024 / 1024  # MB
    
    # Generate test image
    image = np.random.randint(0, 256, (224, 224, 3), dtype=np.uint8)
    
    # Measure memory during inference
    _ = model.predict(image)
    inference_memory = process.memory_info().rss / 1024 / 1024  # MB
    
    # Model parameters memory
    if torch.cuda.is_available():
        torch.cuda.synchronize()
        gpu_memory = torch.cuda.memory_allocated() / 1024 / 1024  # MB
    else:
        gpu_memory = 0
    
    print(f"\nBaseline Memory: {baseline_memory:.2f} MB")
    print(f"Inference Memory: {inference_memory:.2f} MB")
    print(f"Memory Increase: {inference_memory - baseline_memory:.2f} MB")
    if gpu_memory > 0:
        print(f"GPU Memory: {gpu_memory:.2f} MB")
    
    return {
        'baseline_mb': baseline_memory,
        'inference_mb': inference_memory,
        'increase_mb': inference_memory - baseline_memory,
        'gpu_mb': gpu_memory
    }


def benchmark_batch_processing(model, batch_sizes=[1, 8, 16, 32, 64]):
    """Benchmark batch processing throughput."""
    print("\n" + "="*60)
    print("Batch Processing Throughput")
    print("="*60)
    
    results = {}
    
    for batch_size in batch_sizes:
        # Generate batch
        images = [np.random.randint(0, 256, (224, 224, 3), dtype=np.uint8) 
                  for _ in range(batch_size)]
        
        # Warmup
        _ = model.predict_batch(images[:min(5, batch_size)])
        
        # Benchmark
        start = time.time()
        _ = model.predict_batch(images)
        end = time.time()
        
        total_time = (end - start) * 1000  # ms
        time_per_image = total_time / batch_size
        throughput = (batch_size / total_time) * 1000  # images/sec
        
        results[batch_size] = {
            'total_time_ms': total_time,
            'time_per_image_ms': time_per_image,
            'throughput': throughput
        }
        
        print(f"\nBatch Size: {batch_size}")
        print(f"  Total Time: {total_time:.2f} ms")
        print(f"  Time/Image: {time_per_image:.2f} ms")
        print(f"  Throughput: {throughput:.1f} images/sec")
    
    return results


def benchmark_engine_comparison(model_path):
    """Compare CNN vs CIEDE2000 performance."""
    print("\n" + "="*60)
    print("Engine Comparison: CNN vs CIEDE2000")
    print("="*60)
    
    # Initialize engine
    engine = ColorAnalysisEngineV2(cnn_model_path=model_path)
    
    # Test colors
    test_colors = [
        ((255, 0, 0), (53.0, 80.0, 67.0)),
        ((0, 255, 0), (46.0, -52.0, 50.0)),
        ((0, 0, 255), (32.0, 79.0, -108.0)),
        ((255, 255, 0), (95.0, -15.0, 90.0)),
        ((128, 128, 128), (53.0, 0.0, 0.0))
    ]
    
    num_iterations = 50
    
    # Benchmark CNN
    cnn_times = []
    for _ in range(num_iterations):
        for rgb, lab in test_colors:
            image = np.full((224, 224, 3), rgb, dtype=np.uint8)
            start = time.time()
            _ = engine.analyze_color(rgb, lab, method="cnn", image=image)
            cnn_times.append((time.time() - start) * 1000)
    
    # Benchmark CIEDE2000
    ciede_times = []
    for _ in range(num_iterations):
        for rgb, lab in test_colors:
            start = time.time()
            _ = engine.analyze_color(rgb, lab, method="ciede2000")
            ciede_times.append((time.time() - start) * 1000)
    
    print(f"\nCNN Method:")
    print(f"  Avg Time: {np.mean(cnn_times):.2f} ± {np.std(cnn_times):.2f} ms")
    print(f"  Min Time: {np.min(cnn_times):.2f} ms")
    print(f"  Max Time: {np.max(cnn_times):.2f} ms")
    
    print(f"\nCIEDE2000 Method:")
    print(f"  Avg Time: {np.mean(ciede_times):.2f} ± {np.std(ciede_times):.2f} ms")
    print(f"  Min Time: {np.min(ciede_times):.2f} ms")
    print(f"  Max Time: {np.max(ciede_times):.2f} ms")
    
    print(f"\nSpeedup: {np.mean(ciede_times) / np.mean(cnn_times):.2f}x")
    
    return {
        'cnn': {
            'avg_ms': np.mean(cnn_times),
            'std_ms': np.std(cnn_times),
            'min_ms': np.min(cnn_times),
            'max_ms': np.max(cnn_times)
        },
        'ciede2000': {
            'avg_ms': np.mean(ciede_times),
            'std_ms': np.std(ciede_times),
            'min_ms': np.min(ciede_times),
            'max_ms': np.max(ciede_times)
        }
    }


def check_requirements(results):
    """Check if performance meets requirements."""
    print("\n" + "="*60)
    print("Requirements Check")
    print("="*60)
    
    # Requirement: Inference time < 100ms per image (CPU), < 20ms (GPU)
    device = "GPU" if torch.cuda.is_available() else "CPU"
    threshold = 20 if device == "GPU" else 100
    
    single_image_time = results['inference_speed'][1]['avg_time_ms']
    inference_ok = single_image_time < threshold
    
    print(f"\n1. Inference Time ({device}):")
    print(f"   Requirement: < {threshold}ms")
    print(f"   Actual: {single_image_time:.2f}ms")
    print(f"   Status: {'✓ PASS' if inference_ok else '✗ FAIL'}")
    
    # Requirement: Batch processing > 50 images/second
    batch_throughput = results['batch_processing'][32]['throughput']
    throughput_ok = batch_throughput > 50
    
    print(f"\n2. Batch Processing Throughput:")
    print(f"   Requirement: > 50 images/sec")
    print(f"   Actual: {batch_throughput:.1f} images/sec")
    print(f"   Status: {'✓ PASS' if throughput_ok else '✗ FAIL'}")
    
    # Requirement: Memory usage < 500MB
    memory_usage = results['memory']['inference_mb']
    memory_ok = memory_usage < 500
    
    print(f"\n3. Memory Usage:")
    print(f"   Requirement: < 500MB")
    print(f"   Actual: {memory_usage:.2f}MB")
    print(f"   Status: {'✓ PASS' if memory_ok else '✗ FAIL'}")
    
    all_pass = all([inference_ok, throughput_ok, memory_ok])
    
    print(f"\n{'='*60}")
    if all_pass:
        print("✓ All performance requirements met!")
    else:
        print("✗ Some requirements not met. Consider optimization.")
    print(f"{'='*60}")
    
    return all_pass


def main():
    parser = argparse.ArgumentParser(description='Benchmark CNN model performance')
    parser.add_argument(
        '--model',
        type=str,
        default='models/color_detection/cnn_color_ratio_v1.0.0.pth',
        help='Path to model file'
    )
    parser.add_argument(
        '--samples',
        type=int,
        default=100,
        help='Number of samples for benchmarking'
    )
    
    args = parser.parse_args()
    
    print("="*60)
    print("CNN Color Ratio Model - Performance Benchmark")
    print("="*60)
    
    # Load model
    print(f"\nLoading model from: {args.model}")
    model = CNNColorRatioModel(model_path=args.model)
    
    print(f"Device: {model.device}")
    print(f"Model info: {model.get_model_info()}")
    
    # Run benchmarks
    results = {}
    
    results['inference_speed'] = benchmark_inference_speed(model, args.samples)
    results['memory'] = benchmark_memory_usage(model)
    results['batch_processing'] = benchmark_batch_processing(model)
    results['engine_comparison'] = benchmark_engine_comparison(args.model)
    
    # Check requirements
    check_requirements(results)
    
    # Save results
    import json
    output_file = 'benchmark_results.json'
    with open(output_file, 'w') as f:
        # Convert numpy types to native Python types
        def convert(obj):
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            return obj
        
        json.dump(results, f, indent=2, default=convert)
    
    print(f"\n✓ Results saved to: {output_file}")


if __name__ == '__main__':
    main()
