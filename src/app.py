"""
Main application for color recognition and mixing system
Provides command-line interface and pipeline orchestration
"""

import argparse
import os
import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import numpy as np
import matplotlib.pyplot as plt

# Add src to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils import (
    ColorSpaceConverter, 
    ImageProcessor, 
    ColorDifferenceCalculator,
    Visualizer
)
from preprocessing import CameraCalibrator, ImagePreprocessor
from color_recognition import (
    SVMColorClassifier, 
    DeepColorClassifier,
    create_color_detection_pipeline
)
from mixing_formula import (
    KubelkaMunkModel, 
    MixingOptimizer,
    create_standard_pigments,
    create_mixing_calculator,
    visualize_optimization_results
)
from optimization import (
    MultiObjectiveOptimizer,
    AdaptiveOptimizer,
    create_optimization_pipeline
)


class ColorRecognitionPipeline:
    """Complete color recognition and mixing pipeline"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.calibrator = None
        self.preprocessor = None
        self.color_detector = None
        self.mixing_calculator = None
        self.optimizer = None
        
        self._initialize_components()
    
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load configuration from file or use defaults"""
        default_config = {
            "calibration": {
                "method": "neural_network",
                "model_path": "models/camera_calibration.joblib"
            },
            "preprocessing": {
                "apply_calibration": True,
                "correct_lighting": True,
                "lighting_method": "gray_world",
                "remove_shadows": False,
                "target_size": [224, 224]
            },
            "color_detection": {
                "model_type": "svm",
                "feature_type": "combined",
                "model_path": "models/color_detector.joblib"
            },
            "mixing": {
                "optimization_method": "adaptive",
                "max_iterations": 1000,
                "cost_weight": 0.1,
                "complexity_weight": 0.05
            },
            "output": {
                "save_visualizations": True,
                "save_results": True,
                "results_format": "json"
            }
        }
        
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                user_config = json.load(f)
            # Merge configurations
            for key, value in user_config.items():
                if key in default_config and isinstance(value, dict):
                    default_config[key].update(value)
                else:
                    default_config[key] = value
        
        return default_config
    
    def _initialize_components(self):
        """Initialize all pipeline components"""
        # Camera calibrator
        calibration_config = self.config["calibration"]
        self.calibrator = CameraCalibrator(method=calibration_config["method"])
        
        # Try to load existing calibration
        calib_path = calibration_config["model_path"]
        if os.path.exists(calib_path):
            self.calibrator.load_calibration(calib_path)
            print(f"Loaded camera calibration from {calib_path}")
        
        # Preprocessor
        self.preprocessor = ImagePreprocessor(self.calibrator)
        
        # Color detector
        detection_config = self.config["color_detection"]
        if detection_config["model_type"] == "svm":
            self.color_detector = SVMColorClassifier(
                feature_type=detection_config["feature_type"]
            )
        elif detection_config["model_type"] == "cnn":
            self.color_detector = DeepColorClassifier(num_classes=10)
        
        # Try to load existing model
        model_path = detection_config["model_path"]
        if os.path.exists(model_path):
            if hasattr(self.color_detector, 'load_model'):
                self.color_detector.load_model(model_path)
                print(f"Loaded color detection model from {model_path}")
        
        # Mixing calculator
        pigments = create_standard_pigments()
        self.km_model, self.mixing_calculator = create_mixing_calculator(pigments)
        
        # Optimizer
        mixing_config = self.config["mixing"]
        optimization_method = mixing_config["optimization_method"]
        self.optimizer = create_optimization_pipeline(self.km_model, optimization_method)
        
        print("Pipeline initialized successfully")
    
    def calibrate_camera(self, calibration_image_path: str, 
                        save_path: Optional[str] = None) -> bool:
        """Calibrate camera using color checker image"""
        print(f"Calibrating camera using {calibration_image_path}")
        
        # Load calibration image
        calib_image = ImageProcessor.load_image(calibration_image_path)
        
        # Perform calibration
        success = self.calibrator.calibrate(calib_image)
        
        if success:
            # Save calibration
            if save_path is None:
                save_path = self.config["calibration"]["model_path"]
            
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            self.calibrator.save_calibration(save_path)
            print(f"Camera calibration saved to {save_path}")
        
        return success
    
    def train_color_detector(self, training_data_path: str,
                           save_path: Optional[str] = None) -> Dict:
        """Train color detection model"""
        print(f"Training color detector using {training_data_path}")
        
        # Load training data (implement based on your data format)
        # This is a placeholder - implement actual data loading
        images, labels = self._load_training_data(training_data_path)
        
        # Preprocess training images
        preprocessed_images = []
        for image in images:
            preprocessed = self.preprocessor.preprocess_image(
                image, **self.config["preprocessing"]
            )
            preprocessed_images.append(preprocessed)
        
        # Train model
        results = self.color_detector.train(preprocessed_images, labels)
        
        # Save model
        if save_path is None:
            save_path = self.config["color_detection"]["model_path"]
        
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        self.color_detector.save_model(save_path)
        print(f"Color detection model saved to {save_path}")
        
        return results
    
    def _load_training_data(self, data_path: str) -> Tuple[List[np.ndarray], List[str]]:
        """Load training data (placeholder implementation)"""
        # Implement based on your data format
        # This could load from CSV, directory structure, etc.
        images = []
        labels = []
        
        # Example: Load from directory structure
        if os.path.isdir(data_path):
            for class_dir in os.listdir(data_path):
                class_path = os.path.join(data_path, class_dir)
                if os.path.isdir(class_path):
                    for image_file in os.listdir(class_path):
                        if image_file.lower().endswith(('.jpg', '.jpeg', '.png')):
                            image_path = os.path.join(class_path, image_file)
                            image = ImageProcessor.load_image(image_path)
                            images.append(image)
                            labels.append(class_dir)
        
        return images, labels
    
    def process_single_image(self, image_path: str, 
                           output_dir: Optional[str] = None) -> Dict:
        """Process single image through complete pipeline"""
        print(f"Processing image: {image_path}")
        
        # Load image
        image = ImageProcessor.load_image(image_path)
        
        # Preprocess
        start_time = time.time()
        preprocessed = self.preprocessor.preprocess_image(
            image, **self.config["preprocessing"]
        )
        preprocess_time = time.time() - start_time
        
        # Detect color
        start_time = time.time()
        if self.color_detector.is_trained:
            color_label, confidence = self.color_detector.predict(preprocessed)
        else:
            # Use average color if no trained model
            avg_color = np.mean(preprocessed, axis=(0, 1))
            color_label = "unknown"
            confidence = 0.0
        detection_time = time.time() - start_time
        
        # Convert to Lab for mixing calculation
        avg_rgb = np.mean(preprocessed, axis=(0, 1))
        target_lab = ColorSpaceConverter.rgb_to_lab(avg_rgb)
        
        # Calculate mixing formula
        start_time = time.time()
        mixing_config = self.config["mixing"]
        
        if hasattr(self.optimizer, 'optimize_formula'):
            mixing_result = self.optimizer.optimize_formula(
                target_lab,
                max_iterations=mixing_config["max_iterations"],
                cost_weight=mixing_config["cost_weight"],
                complexity_weight=mixing_config["complexity_weight"]
            )
        else:
            # Fallback to basic optimizer
            mixing_result = self.mixing_calculator.optimize_formula(target_lab)
        
        mixing_time = time.time() - start_time
        
        # Compile results
        results = {
            'input_image': image_path,
            'color_detection': {
                'label': color_label,
                'confidence': confidence,
                'rgb_color': avg_rgb.tolist(),
                'lab_color': target_lab.tolist()
            },
            'mixing_formula': {
                'concentrations': mixing_result['concentrations'],
                'predicted_lab': mixing_result['predicted_lab'].tolist(),
                'delta_e': mixing_result['delta_e'],
                'total_cost': mixing_result['total_cost'],
                'success': mixing_result['success']
            },
            'performance': {
                'preprocessing_time': preprocess_time,
                'detection_time': detection_time,
                'mixing_time': mixing_time,
                'total_time': preprocess_time + detection_time + mixing_time
            }
        }
        
        # Save results and visualizations
        if output_dir:
            self._save_results(results, image, preprocessed, output_dir)
        
        return results
    
    def _save_results(self, results: Dict, original_image: np.ndarray,
                     processed_image: np.ndarray, output_dir: str) -> None:
        """Save results and visualizations"""
        os.makedirs(output_dir, exist_ok=True)
        
        # Save JSON results
        if self.config["output"]["save_results"]:
            results_file = os.path.join(output_dir, "results.json")
            with open(results_file, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"Results saved to {results_file}")
        
        # Save visualizations
        if self.config["output"]["save_visualizations"]:
            # Original vs processed comparison
            fig, axes = plt.subplots(1, 2, figsize=(12, 6))
            
            axes[0].imshow(original_image)
            axes[0].set_title('Original Image')
            axes[0].axis('off')
            
            axes[1].imshow(processed_image)
            axes[1].set_title('Processed Image')
            axes[1].axis('off')
            
            comparison_file = os.path.join(output_dir, "preprocessing_comparison.png")
            plt.savefig(comparison_file, dpi=150, bbox_inches='tight')
            plt.close()
            
            # Color swatch and mixing visualization
            if 'mixing_formula' in results:
                mixing_result = results['mixing_formula']
                target_lab = np.array(results['color_detection']['lab_color'])
                predicted_lab = np.array(mixing_result['predicted_lab'])
                
                # Create color swatches
                target_rgb = ColorSpaceConverter.lab_to_rgb(target_lab)
                predicted_rgb = ColorSpaceConverter.lab_to_rgb(predicted_lab)
                
                fig, axes = plt.subplots(2, 2, figsize=(12, 10))
                
                # Color comparison
                axes[0, 0].imshow([[target_rgb, predicted_rgb]])
                axes[0, 0].set_title(f'Target vs Predicted (ΔE: {mixing_result["delta_e"]:.2f})')
                axes[0, 0].set_xticks([0, 1])
                axes[0, 0].set_xticklabels(['Target', 'Predicted'])
                axes[0, 0].set_yticks([])
                
                # Concentration pie chart
                concentrations = mixing_result['concentrations']
                nonzero_conc = {k: v for k, v in concentrations.items() if v > 0.001}
                
                if nonzero_conc:
                    axes[0, 1].pie(nonzero_conc.values(), labels=nonzero_conc.keys(), 
                                  autopct='%1.1f%%')
                    axes[0, 1].set_title('Pigment Concentrations')
                
                # Performance metrics
                perf = results['performance']
                metrics = ['Preprocessing', 'Detection', 'Mixing', 'Total']
                times = [perf['preprocessing_time'], perf['detection_time'], 
                        perf['mixing_time'], perf['total_time']]
                
                axes[1, 0].bar(metrics, times)
                axes[1, 0].set_title('Processing Times (seconds)')
                axes[1, 0].set_ylabel('Time (s)')
                plt.setp(axes[1, 0].xaxis.get_majorticklabels(), rotation=45)
                
                # Summary table
                axes[1, 1].axis('off')
                summary_text = f"""
                Detection Result: {results['color_detection']['label']}
                Confidence: {results['color_detection']['confidence']:.2f}
                
                Formula Quality:
                ΔE: {mixing_result['delta_e']:.2f}
                Cost: {mixing_result['total_cost']:.2f}
                Pigments Used: {len(nonzero_conc)}
                
                Total Time: {perf['total_time']:.2f}s
                """
                axes[1, 1].text(0.1, 0.5, summary_text, fontsize=12, 
                               verticalalignment='center')
                axes[1, 1].set_title('Summary')
                
                mixing_file = os.path.join(output_dir, "mixing_results.png")
                plt.savefig(mixing_file, dpi=150, bbox_inches='tight')
                plt.close()
                
                print(f"Visualizations saved to {output_dir}")
    
    def batch_process(self, input_dir: str, output_dir: str) -> List[Dict]:
        """Process multiple images in batch"""
        print(f"Batch processing images from {input_dir}")
        
        image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
        image_files = [f for f in os.listdir(input_dir) 
                      if any(f.lower().endswith(ext) for ext in image_extensions)]
        
        results = []
        
        for i, filename in enumerate(image_files):
            print(f"Processing {i+1}/{len(image_files)}: {filename}")
            
            try:
                image_path = os.path.join(input_dir, filename)
                image_output_dir = os.path.join(output_dir, os.path.splitext(filename)[0])
                
                result = self.process_single_image(image_path, image_output_dir)
                result['filename'] = filename
                results.append(result)
                
            except Exception as e:
                print(f"Error processing {filename}: {e}")
                results.append({
                    'filename': filename,
                    'error': str(e)
                })
        
        # Save batch summary
        summary_file = os.path.join(output_dir, "batch_summary.json")
        with open(summary_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"Batch processing completed. Summary saved to {summary_file}")
        return results


def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(description="Color Recognition and Mixing System")
    
    parser.add_argument('--config', type=str, 
                       help='Configuration file path')
    parser.add_argument('--mode', choices=['calibrate', 'train', 'process', 'batch'],
                       required=True, help='Operation mode')
    
    # Calibration arguments
    parser.add_argument('--calibration-image', type=str,
                       help='Path to color checker calibration image')
    
    # Training arguments
    parser.add_argument('--training-data', type=str,
                       help='Path to training data directory')
    
    # Processing arguments
    parser.add_argument('--input', type=str,
                       help='Input image or directory path')
    parser.add_argument('--output', type=str,
                       help='Output directory path')
    
    args = parser.parse_args()
    
    # Initialize pipeline
    pipeline = ColorRecognitionPipeline(args.config)
    
    try:
        if args.mode == 'calibrate':
            if not args.calibration_image:
                print("Error: --calibration-image required for calibrate mode")
                return 1
            
            success = pipeline.calibrate_camera(args.calibration_image)
            return 0 if success else 1
        
        elif args.mode == 'train':
            if not args.training_data:
                print("Error: --training-data required for train mode")
                return 1
            
            results = pipeline.train_color_detector(args.training_data)
            print(f"Training completed. Accuracy: {results.get('test_accuracy', 'N/A')}")
            return 0
        
        elif args.mode == 'process':
            if not args.input or not args.output:
                print("Error: --input and --output required for process mode")
                return 1
            
            result = pipeline.process_single_image(args.input, args.output)
            print(f"Processing completed. ΔE: {result['mixing_formula']['delta_e']:.2f}")
            return 0
        
        elif args.mode == 'batch':
            if not args.input or not args.output:
                print("Error: --input and --output required for batch mode")
                return 1
            
            results = pipeline.batch_process(args.input, args.output)
            successful = sum(1 for r in results if 'error' not in r)
            print(f"Batch processing completed. {successful}/{len(results)} images processed successfully")
            return 0
    
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())