"""
Color prediction evaluator for CNN model.
Calculates comprehensive metrics including Delta E, accuracy, and R² scores.
"""

import logging
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import numpy as np

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    torch = None

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    cv2 = None

from dl_config import BASE_COLORS

logger = logging.getLogger(__name__)


class ColorPredictionEvaluator:
    """
    Evaluator for color ratio prediction model.
    Calculates Delta E, classification metrics, and R² scores.
    """
    
    def __init__(self, model, base_colors: Optional[Dict] = None):
        """
        Initialize evaluator.
        
        Args:
            model: CNNColorRatioModel instance
            base_colors: Dictionary of base colors with Lab values
        """
        self.model = model
        self.base_colors = base_colors or BASE_COLORS
        self.color_names = list(self.base_colors.keys())
        self.num_colors = len(self.color_names)
        
        logger.info(f"ColorPredictionEvaluator initialized with {self.num_colors} colors")
    
    def calculate_delta_e(
        self,
        predicted_ratios: np.ndarray,
        target_ratios: np.ndarray
    ) -> float:
        """
        Calculate Delta E between predicted and target color ratios.
        
        Reconstructs Lab colors from ratios and calculates CIEDE2000.
        
        Args:
            predicted_ratios: Predicted ratios (16,)
            target_ratios: Target ratios (16,)
            
        Returns:
            Delta E value
        """
        # Reconstruct Lab colors from ratios
        pred_lab = self._reconstruct_lab_from_ratios(predicted_ratios)
        target_lab = self._reconstruct_lab_from_ratios(target_ratios)
        
        # Calculate Delta E using CIEDE2000 formula
        delta_e = self._calculate_ciede2000(pred_lab, target_lab)
        
        return delta_e
    
    def _reconstruct_lab_from_ratios(self, ratios: np.ndarray) -> Tuple[float, float, float]:
        """
        Reconstruct Lab color from mixing ratios.
        
        Args:
            ratios: Color ratios (16,)
            
        Returns:
            Lab color tuple (L, a, b)
        """
        L, a, b = 0.0, 0.0, 0.0
        
        for i, ratio in enumerate(ratios):
            if ratio > 0:
                color_name = self.color_names[i]
                color_lab = self.base_colors[color_name]
                L += color_lab[0] * ratio
                a += color_lab[1] * ratio
                b += color_lab[2] * ratio
        
        return (L, a, b)
    
    def _calculate_ciede2000(
        self,
        lab1: Tuple[float, float, float],
        lab2: Tuple[float, float, float]
    ) -> float:
        """
        Calculate CIEDE2000 Delta E between two Lab colors.
        
        This is a simplified implementation. For production,
        consider using colorspacious or colour-science library.
        
        Args:
            lab1: First Lab color (L, a, b)
            lab2: Second Lab color (L, a, b)
            
        Returns:
            Delta E value
        """
        # Simple Euclidean distance in Lab space as approximation
        # For accurate CIEDE2000, use a proper library
        L1, a1, b1 = lab1
        L2, a2, b2 = lab2
        
        delta_L = L1 - L2
        delta_a = a1 - a2
        delta_b = b1 - b2
        
        # Euclidean distance
        delta_e = np.sqrt(delta_L**2 + delta_a**2 + delta_b**2)
        
        return delta_e
    
    def evaluate_dataset(
        self,
        test_loader,
        calculate_per_color_metrics: bool = True
    ) -> Dict:
        """
        Evaluate model on test dataset with comprehensive metrics.
        
        Args:
            test_loader: DataLoader for test data
            calculate_per_color_metrics: Whether to calculate per-color R² scores
            
        Returns:
            Dictionary with evaluation metrics
        """
        self.model.network.eval()
        
        all_predictions = []
        all_targets = []
        delta_e_values = []
        
        with torch.no_grad():
            for images, ratios in test_loader:
                # Move to device
                images = self.model.device_manager.move_to_device(images)
                ratios = self.model.device_manager.move_to_device(ratios)
                
                # Predict
                outputs = self.model.network(images)
                
                # Convert to numpy
                pred_ratios = outputs.cpu().numpy()
                true_ratios = ratios.cpu().numpy()
                
                all_predictions.append(pred_ratios)
                all_targets.append(true_ratios)
                
                # Calculate Delta E for each sample
                for pred, true in zip(pred_ratios, true_ratios):
                    delta_e = self.calculate_delta_e(pred, true)
                    delta_e_values.append(delta_e)
        
        # Concatenate all predictions and targets
        all_predictions = np.vstack(all_predictions)
        all_targets = np.vstack(all_targets)
        
        # Calculate metrics
        metrics = {
            'mean_delta_e': np.mean(delta_e_values),
            'median_delta_e': np.median(delta_e_values),
            'std_delta_e': np.std(delta_e_values),
            'min_delta_e': np.min(delta_e_values),
            'max_delta_e': np.max(delta_e_values),
            'delta_e_below_1': np.sum(np.array(delta_e_values) < 1.0) / len(delta_e_values),
            'delta_e_below_2': np.sum(np.array(delta_e_values) < 2.0) / len(delta_e_values),
            'delta_e_below_4': np.sum(np.array(delta_e_values) < 4.0) / len(delta_e_values),
            'num_samples': len(delta_e_values)
        }
        
        # Calculate MSE
        mse = np.mean((all_predictions - all_targets) ** 2)
        metrics['mse'] = mse
        
        # Calculate MAE
        mae = np.mean(np.abs(all_predictions - all_targets))
        metrics['mae'] = mae
        
        # Calculate per-color R² scores
        if calculate_per_color_metrics:
            r2_scores = {}
            for i, color_name in enumerate(self.color_names):
                r2 = self._calculate_r2_score(
                    all_predictions[:, i],
                    all_targets[:, i]
                )
                r2_scores[color_name] = r2
            
            metrics['r2_scores'] = r2_scores
            metrics['mean_r2_score'] = np.mean(list(r2_scores.values()))
        
        # Store raw data for further analysis
        metrics['all_predictions'] = all_predictions
        metrics['all_targets'] = all_targets
        metrics['delta_e_values'] = delta_e_values
        
        logger.info(f"Evaluation complete: Mean Delta E = {metrics['mean_delta_e']:.2f}")
        logger.info(f"Samples with Delta E < 2.0: {metrics['delta_e_below_2']*100:.1f}%")
        
        return metrics
    
    def _calculate_r2_score(self, y_pred: np.ndarray, y_true: np.ndarray) -> float:
        """
        Calculate R² (coefficient of determination) score.
        
        Args:
            y_pred: Predicted values
            y_true: True values
            
        Returns:
            R² score
        """
        # Calculate mean of true values
        y_mean = np.mean(y_true)
        
        # Total sum of squares
        ss_tot = np.sum((y_true - y_mean) ** 2)
        
        # Residual sum of squares
        ss_res = np.sum((y_true - y_pred) ** 2)
        
        # R² score
        if ss_tot == 0:
            return 1.0 if ss_res == 0 else 0.0
        
        r2 = 1 - (ss_res / ss_tot)
        
        return r2
    
    def calculate_dominant_color_accuracy(
        self,
        predictions: np.ndarray,
        targets: np.ndarray,
        top_k: int = 1
    ) -> float:
        """
        Calculate top-k accuracy for dominant color prediction.
        
        Args:
            predictions: Predicted ratios (N, 16)
            targets: Target ratios (N, 16)
            top_k: Number of top predictions to consider
            
        Returns:
            Top-k accuracy
        """
        correct = 0
        total = len(predictions)
        
        for pred, target in zip(predictions, targets):
            # Get top-k predicted colors
            top_k_pred = np.argsort(pred)[-top_k:]
            
            # Get dominant target color
            dominant_target = np.argmax(target)
            
            # Check if dominant target is in top-k predictions
            if dominant_target in top_k_pred:
                correct += 1
        
        accuracy = correct / total
        return accuracy
    
    def get_quality_classification(self, delta_e: float) -> str:
        """
        Classify prediction quality based on Delta E.
        
        Args:
            delta_e: Delta E value
            
        Returns:
            Quality classification string
        """
        if delta_e < 1.0:
            return "Excellent"
        elif delta_e < 2.0:
            return "Good"
        elif delta_e < 4.0:
            return "Acceptable"
        else:
            return "Poor"
    
    def generate_confusion_matrix(
        self,
        predictions: np.ndarray,
        targets: np.ndarray
    ) -> np.ndarray:
        """
        Generate confusion matrix for dominant color classification.
        
        Args:
            predictions: Predicted ratios (N, 16)
            targets: Target ratios (N, 16)
            
        Returns:
            Confusion matrix (16, 16)
        """
        confusion_matrix = np.zeros((self.num_colors, self.num_colors), dtype=np.int32)
        
        for pred, target in zip(predictions, targets):
            # Get dominant colors
            pred_dominant = np.argmax(pred)
            target_dominant = np.argmax(target)
            
            # Update confusion matrix
            confusion_matrix[target_dominant, pred_dominant] += 1
        
        return confusion_matrix
    
    def calculate_classification_metrics(
        self,
        predictions: np.ndarray,
        targets: np.ndarray
    ) -> Dict:
        """
        Calculate comprehensive classification metrics.
        
        Args:
            predictions: Predicted ratios (N, 16)
            targets: Target ratios (N, 16)
            
        Returns:
            Dictionary with classification metrics
        """
        # Calculate top-1 and top-3 accuracy
        top1_accuracy = self.calculate_dominant_color_accuracy(predictions, targets, top_k=1)
        top3_accuracy = self.calculate_dominant_color_accuracy(predictions, targets, top_k=3)
        
        # Generate confusion matrix
        confusion_matrix = self.generate_confusion_matrix(predictions, targets)
        
        # Calculate per-class metrics
        per_class_metrics = {}
        for i, color_name in enumerate(self.color_names):
            # True positives, false positives, false negatives
            tp = confusion_matrix[i, i]
            fp = np.sum(confusion_matrix[:, i]) - tp
            fn = np.sum(confusion_matrix[i, :]) - tp
            tn = np.sum(confusion_matrix) - tp - fp - fn
            
            # Precision, recall, F1
            precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
            f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
            
            per_class_metrics[color_name] = {
                'precision': precision,
                'recall': recall,
                'f1_score': f1,
                'support': int(np.sum(confusion_matrix[i, :]))
            }
        
        # Calculate R² scores for each base color
        r2_scores = {}
        for i, color_name in enumerate(self.color_names):
            r2 = self._calculate_r2_score(predictions[:, i], targets[:, i])
            r2_scores[color_name] = r2
        
        metrics = {
            'top1_accuracy': top1_accuracy,
            'top3_accuracy': top3_accuracy,
            'confusion_matrix': confusion_matrix,
            'per_class_metrics': per_class_metrics,
            'r2_scores': r2_scores,
            'mean_r2_score': np.mean(list(r2_scores.values()))
        }
        
        logger.info(f"Top-1 Accuracy: {top1_accuracy*100:.2f}%")
        logger.info(f"Top-3 Accuracy: {top3_accuracy*100:.2f}%")
        logger.info(f"Mean R² Score: {metrics['mean_r2_score']:.4f}")
        
        return metrics


    def plot_prediction_errors(
        self,
        predictions: np.ndarray,
        targets: np.ndarray,
        save_path: Optional[str] = None
    ):
        """
        Plot prediction errors with scatter plots.
        
        Args:
            predictions: Predicted ratios (N, 16)
            targets: Target ratios (N, 16)
            save_path: Path to save plot (optional)
        """
        try:
            import matplotlib.pyplot as plt
        except ImportError:
            logger.warning("matplotlib not available, skipping plot")
            return
        
        # Create figure with subplots
        fig, axes = plt.subplots(4, 4, figsize=(16, 16))
        fig.suptitle('Prediction vs Target for Each Color', fontsize=16)
        
        for i, (ax, color_name) in enumerate(zip(axes.flat, self.color_names)):
            # Scatter plot
            ax.scatter(targets[:, i], predictions[:, i], alpha=0.5, s=10)
            
            # Perfect prediction line
            max_val = max(targets[:, i].max(), predictions[:, i].max())
            ax.plot([0, max_val], [0, max_val], 'r--', linewidth=1)
            
            # Labels
            ax.set_xlabel('Target Ratio')
            ax.set_ylabel('Predicted Ratio')
            ax.set_title(color_name)
            ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            logger.info(f"Prediction error plot saved to {save_path}")
        else:
            plt.show()
        
        plt.close()
    
    def plot_delta_e_distribution(
        self,
        delta_e_values: List[float],
        save_path: Optional[str] = None
    ):
        """
        Plot histogram of Delta E distribution.
        
        Args:
            delta_e_values: List of Delta E values
            save_path: Path to save plot (optional)
        """
        try:
            import matplotlib.pyplot as plt
        except ImportError:
            logger.warning("matplotlib not available, skipping plot")
            return
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Histogram
        ax.hist(delta_e_values, bins=50, edgecolor='black', alpha=0.7)
        
        # Add vertical lines for quality thresholds
        ax.axvline(x=1.0, color='g', linestyle='--', linewidth=2, label='Excellent (ΔE < 1)')
        ax.axvline(x=2.0, color='y', linestyle='--', linewidth=2, label='Good (ΔE < 2)')
        ax.axvline(x=4.0, color='r', linestyle='--', linewidth=2, label='Acceptable (ΔE < 4)')
        
        # Labels
        ax.set_xlabel('Delta E', fontsize=12)
        ax.set_ylabel('Frequency', fontsize=12)
        ax.set_title('Distribution of Delta E Values', fontsize=14)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Add statistics text
        mean_de = np.mean(delta_e_values)
        median_de = np.median(delta_e_values)
        stats_text = f'Mean: {mean_de:.2f}\nMedian: {median_de:.2f}'
        ax.text(0.95, 0.95, stats_text, transform=ax.transAxes,
                verticalalignment='top', horizontalalignment='right',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            logger.info(f"Delta E distribution plot saved to {save_path}")
        else:
            plt.show()
        
        plt.close()
    
    def plot_confusion_matrix(
        self,
        confusion_matrix: np.ndarray,
        save_path: Optional[str] = None
    ):
        """
        Plot confusion matrix as heatmap.
        
        Args:
            confusion_matrix: Confusion matrix (16, 16)
            save_path: Path to save plot (optional)
        """
        try:
            import matplotlib.pyplot as plt
        except ImportError:
            logger.warning("matplotlib not available, skipping plot")
            return
        
        fig, ax = plt.subplots(figsize=(12, 10))
        
        # Create heatmap
        im = ax.imshow(confusion_matrix, cmap='Blues', aspect='auto')
        
        # Add colorbar
        plt.colorbar(im, ax=ax)
        
        # Set ticks
        ax.set_xticks(np.arange(self.num_colors))
        ax.set_yticks(np.arange(self.num_colors))
        ax.set_xticklabels(self.color_names, rotation=45, ha='right')
        ax.set_yticklabels(self.color_names)
        
        # Labels
        ax.set_xlabel('Predicted Color', fontsize=12)
        ax.set_ylabel('True Color', fontsize=12)
        ax.set_title('Confusion Matrix for Dominant Color', fontsize=14)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            logger.info(f"Confusion matrix plot saved to {save_path}")
        else:
            plt.show()
        
        plt.close()
    
    def visualize_color_comparison(
        self,
        predicted_ratios: np.ndarray,
        target_ratios: np.ndarray,
        save_path: Optional[str] = None
    ):
        """
        Create visual comparison of predicted vs target colors.
        
        Args:
            predicted_ratios: Predicted ratios
            target_ratios: Target ratios
            save_path: Path to save visualization (optional)
        """
        if not CV2_AVAILABLE:
            logger.warning("OpenCV not available, skipping color comparison")
            return
        
        # Reconstruct colors
        pred_lab = self._reconstruct_lab_from_ratios(predicted_ratios)
        target_lab = self._reconstruct_lab_from_ratios(target_ratios)
        
        # Convert Lab to RGB for visualization
        pred_rgb = self._lab_to_rgb(pred_lab)
        target_rgb = self._lab_to_rgb(target_lab)
        
        # Create comparison image
        height, width = 100, 200
        comparison = np.zeros((height, width * 2, 3), dtype=np.uint8)
        
        # Fill with colors
        comparison[:, :width] = target_rgb
        comparison[:, width:] = pred_rgb
        
        if save_path:
            cv2.imwrite(save_path, cv2.cvtColor(comparison, cv2.COLOR_RGB2BGR))
            logger.info(f"Color comparison saved to {save_path}")
        
        return comparison
    
    def _lab_to_rgb(self, lab: Tuple[float, float, float]) -> Tuple[int, int, int]:
        """
        Convert Lab color to RGB.
        
        Args:
            lab: Lab color (L, a, b)
            
        Returns:
            RGB color (r, g, b)
        """
        if not CV2_AVAILABLE:
            return (128, 128, 128)
        
        # Create Lab image
        lab_img = np.array([[[lab[0], lab[1], lab[2]]]], dtype=np.float32)
        
        # Convert to RGB
        rgb_img = cv2.cvtColor(lab_img, cv2.COLOR_LAB2RGB)
        
        # Extract and scale RGB values
        r, g, b = rgb_img[0, 0]
        return (int(r * 255), int(g * 255), int(b * 255))


    def export_results_to_csv(
        self,
        metrics: Dict,
        save_path: str
    ):
        """
        Export evaluation results to CSV file.
        
        Args:
            metrics: Dictionary with evaluation metrics
            save_path: Path to save CSV file
        """
        try:
            import pandas as pd
        except ImportError:
            logger.warning("pandas not available, using basic CSV export")
            self._export_results_basic_csv(metrics, save_path)
            return
        
        # Create summary dataframe
        summary_data = {
            'Metric': [
                'Mean Delta E',
                'Median Delta E',
                'Std Delta E',
                'Min Delta E',
                'Max Delta E',
                'Delta E < 1.0 (%)',
                'Delta E < 2.0 (%)',
                'Delta E < 4.0 (%)',
                'MSE',
                'MAE',
                'Mean R² Score',
                'Top-1 Accuracy',
                'Top-3 Accuracy',
                'Num Samples'
            ],
            'Value': [
                metrics.get('mean_delta_e', 0),
                metrics.get('median_delta_e', 0),
                metrics.get('std_delta_e', 0),
                metrics.get('min_delta_e', 0),
                metrics.get('max_delta_e', 0),
                metrics.get('delta_e_below_1', 0) * 100,
                metrics.get('delta_e_below_2', 0) * 100,
                metrics.get('delta_e_below_4', 0) * 100,
                metrics.get('mse', 0),
                metrics.get('mae', 0),
                metrics.get('mean_r2_score', 0),
                metrics.get('top1_accuracy', 0) * 100 if 'top1_accuracy' in metrics else 0,
                metrics.get('top3_accuracy', 0) * 100 if 'top3_accuracy' in metrics else 0,
                metrics.get('num_samples', 0)
            ]
        }
        
        df_summary = pd.DataFrame(summary_data)
        
        # Save summary
        summary_path = Path(save_path).parent / f"{Path(save_path).stem}_summary.csv"
        df_summary.to_csv(summary_path, index=False)
        logger.info(f"Summary results saved to {summary_path}")
        
        # Export per-color R² scores if available
        if 'r2_scores' in metrics:
            r2_data = {
                'Color': list(metrics['r2_scores'].keys()),
                'R² Score': list(metrics['r2_scores'].values())
            }
            df_r2 = pd.DataFrame(r2_data)
            
            r2_path = Path(save_path).parent / f"{Path(save_path).stem}_r2_scores.csv"
            df_r2.to_csv(r2_path, index=False)
            logger.info(f"R² scores saved to {r2_path}")
        
        # Export per-class metrics if available
        if 'per_class_metrics' in metrics:
            per_class_data = []
            for color_name, class_metrics in metrics['per_class_metrics'].items():
                per_class_data.append({
                    'Color': color_name,
                    'Precision': class_metrics['precision'],
                    'Recall': class_metrics['recall'],
                    'F1 Score': class_metrics['f1_score'],
                    'Support': class_metrics['support']
                })
            
            df_per_class = pd.DataFrame(per_class_data)
            
            per_class_path = Path(save_path).parent / f"{Path(save_path).stem}_per_class.csv"
            df_per_class.to_csv(per_class_path, index=False)
            logger.info(f"Per-class metrics saved to {per_class_path}")
    
    def _export_results_basic_csv(self, metrics: Dict, save_path: str):
        """
        Basic CSV export without pandas.
        
        Args:
            metrics: Dictionary with evaluation metrics
            save_path: Path to save CSV file
        """
        import csv
        
        with open(save_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Metric', 'Value'])
            
            writer.writerow(['Mean Delta E', metrics.get('mean_delta_e', 0)])
            writer.writerow(['Median Delta E', metrics.get('median_delta_e', 0)])
            writer.writerow(['Std Delta E', metrics.get('std_delta_e', 0)])
            writer.writerow(['MSE', metrics.get('mse', 0)])
            writer.writerow(['MAE', metrics.get('mae', 0)])
            writer.writerow(['Mean R² Score', metrics.get('mean_r2_score', 0)])
            writer.writerow(['Num Samples', metrics.get('num_samples', 0)])
        
        logger.info(f"Results saved to {save_path}")
    
    def save_confusion_matrix_image(
        self,
        confusion_matrix: np.ndarray,
        save_path: str
    ):
        """
        Save confusion matrix as image file.
        
        Args:
            confusion_matrix: Confusion matrix (16, 16)
            save_path: Path to save image
        """
        self.plot_confusion_matrix(confusion_matrix, save_path)
    
    def generate_summary_report(
        self,
        metrics: Dict,
        save_path: str
    ):
        """
        Generate comprehensive summary report.
        
        Args:
            metrics: Dictionary with evaluation metrics
            save_path: Path to save report (text file)
        """
        report_lines = []
        report_lines.append("=" * 60)
        report_lines.append("COLOR PREDICTION MODEL EVALUATION REPORT")
        report_lines.append("=" * 60)
        report_lines.append("")
        
        # Overall metrics
        report_lines.append("OVERALL METRICS")
        report_lines.append("-" * 60)
        report_lines.append(f"Number of Samples: {metrics.get('num_samples', 0)}")
        report_lines.append(f"Mean Delta E: {metrics.get('mean_delta_e', 0):.2f}")
        report_lines.append(f"Median Delta E: {metrics.get('median_delta_e', 0):.2f}")
        report_lines.append(f"Std Delta E: {metrics.get('std_delta_e', 0):.2f}")
        report_lines.append(f"Min Delta E: {metrics.get('min_delta_e', 0):.2f}")
        report_lines.append(f"Max Delta E: {metrics.get('max_delta_e', 0):.2f}")
        report_lines.append("")
        
        # Quality distribution
        report_lines.append("QUALITY DISTRIBUTION")
        report_lines.append("-" * 60)
        report_lines.append(f"Excellent (ΔE < 1.0): {metrics.get('delta_e_below_1', 0)*100:.1f}%")
        report_lines.append(f"Good (ΔE < 2.0): {metrics.get('delta_e_below_2', 0)*100:.1f}%")
        report_lines.append(f"Acceptable (ΔE < 4.0): {metrics.get('delta_e_below_4', 0)*100:.1f}%")
        report_lines.append("")
        
        # Regression metrics
        report_lines.append("REGRESSION METRICS")
        report_lines.append("-" * 60)
        report_lines.append(f"MSE: {metrics.get('mse', 0):.6f}")
        report_lines.append(f"MAE: {metrics.get('mae', 0):.6f}")
        report_lines.append(f"Mean R² Score: {metrics.get('mean_r2_score', 0):.4f}")
        report_lines.append("")
        
        # Classification metrics
        if 'top1_accuracy' in metrics:
            report_lines.append("CLASSIFICATION METRICS")
            report_lines.append("-" * 60)
            report_lines.append(f"Top-1 Accuracy: {metrics.get('top1_accuracy', 0)*100:.2f}%")
            report_lines.append(f"Top-3 Accuracy: {metrics.get('top3_accuracy', 0)*100:.2f}%")
            report_lines.append("")
        
        # Per-color R² scores
        if 'r2_scores' in metrics:
            report_lines.append("PER-COLOR R² SCORES")
            report_lines.append("-" * 60)
            for color_name, r2_score in metrics['r2_scores'].items():
                report_lines.append(f"{color_name:20s}: {r2_score:.4f}")
            report_lines.append("")
        
        report_lines.append("=" * 60)
        
        # Write to file
        with open(save_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report_lines))
        
        logger.info(f"Summary report saved to {save_path}")


def evaluate_model(
    model,
    test_loader,
    base_colors: Optional[Dict] = None
) -> Dict:
    """
    Convenience function to evaluate a model.
    
    Args:
        model: CNNColorRatioModel instance
        test_loader: DataLoader for test data
        base_colors: Dictionary of base colors
        
    Returns:
        Dictionary with evaluation metrics
    """
    evaluator = ColorPredictionEvaluator(model, base_colors)
    metrics = evaluator.evaluate_dataset(test_loader)
    
    return metrics
