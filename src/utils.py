"""
Utilities module for color recognition and mixing system
Provides common functions for image processing, color space conversion, and evaluation metrics
"""

import cv2
import numpy as np
import matplotlib.pyplot as plt
from colorspacious import cspace_convert
from typing import Tuple, List, Union, Optional
import pandas as pd


class ColorSpaceConverter:
    """Handle color space conversions between different color models"""
    
    @staticmethod
    def rgb_to_lab(rgb: np.ndarray) -> np.ndarray:
        """
        Convert RGB to CIE Lab color space
        
        Args:
            rgb: RGB array with values in [0, 255] or [0, 1]
            
        Returns:
            Lab array with L in [0, 100], a,b in [-127, 127]
        """
        if rgb.max() > 1:
            rgb = rgb / 255.0
        
        return cspace_convert(rgb, "sRGB1", "CIELab")
    
    @staticmethod
    def lab_to_rgb(lab: np.ndarray) -> np.ndarray:
        """
        Convert CIE Lab to RGB color space
        
        Args:
            lab: Lab array with L in [0, 100], a,b in [-127, 127]
            
        Returns:
            RGB array with values in [0, 255]
        """
        rgb = cspace_convert(lab, "CIELab", "sRGB1")
        return np.clip(rgb * 255, 0, 255).astype(np.uint8)
    
    @staticmethod
    def rgb_to_hsv(rgb: np.ndarray) -> np.ndarray:
        """Convert RGB to HSV color space"""
        if len(rgb.shape) == 3:
            return cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
        else:
            # Single color
            rgb_img = rgb.reshape(1, 1, 3).astype(np.uint8)
            hsv = cv2.cvtColor(rgb_img, cv2.COLOR_RGB2HSV)
            return hsv.reshape(3)


class ColorDifferenceCalculator:
    """Calculate color differences using various metrics"""
    
    @staticmethod
    def delta_e_cie76(lab1: np.ndarray, lab2: np.ndarray) -> float:
        """
        Calculate ΔE using CIE76 formula
        
        Args:
            lab1, lab2: Lab color arrays [L, a, b]
            
        Returns:
            ΔE value (lower is better, <2.0 is excellent)
        """
        return np.sqrt(np.sum((lab1 - lab2) ** 2))
    
    @staticmethod
    def delta_e_ciede2000(lab1: np.ndarray, lab2: np.ndarray) -> float:
        """
        Calculate ΔE using CIEDE2000 formula (most accurate)
        
        Args:
            lab1, lab2: Lab color arrays [L, a, b]
            
        Returns:
            ΔE value using CIEDE2000 formula
        """
        L1, a1, b1 = lab1
        L2, a2, b2 = lab2
        
        # Implementation of CIEDE2000 formula
        # This is a simplified version - for production, use colorspacious library
        delta_L = L2 - L1
        delta_a = a2 - a1
        delta_b = b2 - b1
        
        C1 = np.sqrt(a1**2 + b1**2)
        C2 = np.sqrt(a2**2 + b2**2)
        delta_C = C2 - C1
        
        delta_H = np.sqrt(delta_a**2 + delta_b**2 - delta_C**2)
        
        # Simplified calculation (use colorspacious for full implementation)
        return np.sqrt(delta_L**2 + delta_C**2 + delta_H**2)


class ImageProcessor:
    """Image processing utilities for color analysis"""
    
    @staticmethod
    def load_image(image_path: str) -> np.ndarray:
        """Load image from file path"""
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Could not load image from {image_path}")
        return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    @staticmethod
    def save_image(image: np.ndarray, output_path: str) -> None:
        """Save image to file"""
        if len(image.shape) == 3:
            image_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        else:
            image_bgr = image
        cv2.imwrite(output_path, image_bgr)
    
    @staticmethod
    def extract_color_patch(image: np.ndarray, bbox: Tuple[int, int, int, int]) -> np.ndarray:
        """
        Extract color patch from image
        
        Args:
            image: Input image
            bbox: Bounding box (x, y, width, height)
            
        Returns:
            Average color of the patch in RGB
        """
        x, y, w, h = bbox
        patch = image[y:y+h, x:x+w]
        return np.mean(patch, axis=(0, 1))
    
    @staticmethod
    def create_color_swatch(color: Union[np.ndarray, List], size: Tuple[int, int] = (100, 100)) -> np.ndarray:
        """Create a color swatch image"""
        color = np.array(color, dtype=np.uint8)
        swatch = np.full((*size, 3), color, dtype=np.uint8)
        return swatch


class Visualizer:
    """Visualization utilities for color analysis"""
    
    @staticmethod
    def plot_color_comparison(original_colors: List[np.ndarray], 
                            predicted_colors: List[np.ndarray],
                            labels: Optional[List[str]] = None) -> None:
        """Plot comparison between original and predicted colors"""
        n_colors = len(original_colors)
        fig, axes = plt.subplots(2, n_colors, figsize=(3*n_colors, 6))
        
        if n_colors == 1:
            axes = axes.reshape(2, 1)
        
        for i in range(n_colors):
            # Original color
            orig_swatch = ImageProcessor.create_color_swatch(original_colors[i])
            axes[0, i].imshow(orig_swatch)
            axes[0, i].set_title(f'Original {labels[i] if labels else i}')
            axes[0, i].axis('off')
            
            # Predicted color
            pred_swatch = ImageProcessor.create_color_swatch(predicted_colors[i])
            axes[1, i].imshow(pred_swatch)
            axes[1, i].set_title(f'Predicted {labels[i] if labels else i}')
            axes[1, i].axis('off')
            
            # Calculate and display ΔE
            lab_orig = ColorSpaceConverter.rgb_to_lab(original_colors[i])
            lab_pred = ColorSpaceConverter.rgb_to_lab(predicted_colors[i])
            delta_e = ColorDifferenceCalculator.delta_e_cie76(lab_orig, lab_pred)
            axes[1, i].text(0.5, -0.1, f'ΔE: {delta_e:.2f}', 
                          transform=axes[1, i].transAxes, ha='center')
        
        plt.tight_layout()
        plt.show()
    
    @staticmethod
    def plot_color_histogram(image: np.ndarray, color_space: str = 'RGB') -> None:
        """Plot histogram for different color channels"""
        if color_space == 'RGB':
            colors = ['red', 'green', 'blue']
            labels = ['R', 'G', 'B']
        elif color_space == 'HSV':
            image = ColorSpaceConverter.rgb_to_hsv(image)
            colors = ['red', 'green', 'blue']
            labels = ['H', 'S', 'V']
        elif color_space == 'Lab':
            image = ColorSpaceConverter.rgb_to_lab(image)
            colors = ['black', 'red', 'blue']
            labels = ['L', 'a', 'b']
        
        plt.figure(figsize=(12, 4))
        for i in range(3):
            plt.subplot(1, 3, i+1)
            plt.hist(image[:, :, i].flatten(), bins=50, color=colors[i], alpha=0.7)
            plt.title(f'{labels[i]} Channel')
            plt.xlabel('Value')
            plt.ylabel('Frequency')
        
        plt.tight_layout()
        plt.show()


class DataProcessor:
    """Data processing utilities for model training and evaluation"""
    
    @staticmethod
    def create_color_dataset(image_paths: List[str], 
                           color_labels: List[str],
                           bbox_annotations: Optional[List[List]] = None) -> pd.DataFrame:
        """
        Create dataset from image paths and labels
        
        Args:
            image_paths: List of image file paths
            color_labels: List of color labels
            bbox_annotations: Optional bounding box annotations
            
        Returns:
            DataFrame with color features and labels
        """
        data = []
        
        for i, (img_path, label) in enumerate(zip(image_paths, color_labels)):
            image = ImageProcessor.load_image(img_path)
            
            if bbox_annotations and i < len(bbox_annotations):
                # Extract color from specific region
                color_rgb = ImageProcessor.extract_color_patch(image, bbox_annotations[i])
            else:
                # Use entire image average
                color_rgb = np.mean(image, axis=(0, 1))
            
            # Convert to different color spaces
            color_lab = ColorSpaceConverter.rgb_to_lab(color_rgb)
            color_hsv = ColorSpaceConverter.rgb_to_hsv(color_rgb)
            
            # Create feature vector
            features = {
                'image_path': img_path,
                'label': label,
                'R': color_rgb[0],
                'G': color_rgb[1], 
                'B': color_rgb[2],
                'L': color_lab[0],
                'a': color_lab[1],
                'b': color_lab[2],
                'H': color_hsv[0],
                'S': color_hsv[1],
                'V': color_hsv[2]
            }
            
            data.append(features)
        
        return pd.DataFrame(data)
    
    @staticmethod
    def normalize_features(features: np.ndarray, method: str = 'minmax') -> np.ndarray:
        """Normalize feature vectors"""
        if method == 'minmax':
            return (features - features.min(axis=0)) / (features.max(axis=0) - features.min(axis=0))
        elif method == 'zscore':
            return (features - features.mean(axis=0)) / features.std(axis=0)
        else:
            raise ValueError(f"Unknown normalization method: {method}")


def calculate_mixing_cost(pigment_ratios: np.ndarray, 
                         pigment_costs: np.ndarray) -> float:
    """
    Calculate total cost of pigment mixture
    
    Args:
        pigment_ratios: Array of pigment ratios [0, 1]
        pigment_costs: Array of cost per unit for each pigment
        
    Returns:
        Total cost of mixture
    """
    return np.sum(pigment_ratios * pigment_costs)


def validate_color_accuracy(predicted_colors: np.ndarray,
                          target_colors: np.ndarray,
                          threshold: float = 2.0) -> Tuple[float, int]:
    """
    Validate color prediction accuracy using ΔE threshold
    
    Args:
        predicted_colors: Array of predicted Lab colors
        target_colors: Array of target Lab colors  
        threshold: ΔE threshold for acceptance
        
    Returns:
        (average_delta_e, num_accepted)
    """
    delta_es = []
    accepted = 0
    
    for pred, target in zip(predicted_colors, target_colors):
        delta_e = ColorDifferenceCalculator.delta_e_cie76(pred, target)
        delta_es.append(delta_e)
        if delta_e <= threshold:
            accepted += 1
    
    return np.mean(delta_es), accepted