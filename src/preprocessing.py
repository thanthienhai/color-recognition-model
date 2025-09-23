"""
Preprocessing module for color calibration and image preparation
Handles camera calibration, color correction, and image preprocessing
"""

import cv2
import numpy as np
from typing import Tuple, List, Optional, Union
import matplotlib.pyplot as plt
from sklearn.neural_network import MLPRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import Pipeline
import joblib
import os

from .utils import ColorSpaceConverter, ImageProcessor


class ColorChecker:
    """Color checker pattern for camera calibration"""
    
    # Standard 24-patch Macbeth ColorChecker values in CIE Lab
    STANDARD_LAB_VALUES = np.array([
        [37.986, 13.555, 14.059],   # Dark skin
        [65.711, 18.130, 17.810],   # Light skin  
        [49.927, -4.880, -21.925],  # Blue sky
        [43.139, -13.095, 21.905],  # Foliage
        [55.112, 8.844, -25.399],   # Blue flower
        [70.719, -33.397, -0.199],  # Bluish green
        [62.661, 36.067, 57.096],   # Orange
        [40.020, 10.410, -45.964],  # Purple blue
        [51.124, 48.239, 16.248],   # Moderate red
        [30.325, 22.976, -21.587],  # Purple
        [72.532, -23.709, 57.255],  # Yellow green
        [71.941, 19.363, 67.857],   # Orange yellow
        [28.778, 14.179, -50.297],  # Blue
        [55.261, -38.342, 31.370],  # Green
        [42.101, 53.378, 28.190],   # Red
        [81.733, 4.039, 79.819],    # Yellow
        [51.935, 49.986, -14.574],  # Magenta
        [51.038, -28.631, -28.638], # Cyan
        [96.539, -0.425, 1.186],    # White
        [81.257, -0.638, -0.335],   # Neutral 8
        [66.766, -0.734, -0.504],   # Neutral 6.5
        [50.867, -0.153, -0.270],   # Neutral 5
        [35.656, -0.421, -1.231],   # Neutral 3.5
        [20.461, -0.079, -0.973]    # Black
    ])
    
    def __init__(self):
        self.patch_positions = None
        self.detected_colors = None
        self.calibration_matrix = None
    
    def detect_color_checker(self, image: np.ndarray, 
                           grid_size: Tuple[int, int] = (6, 4)) -> bool:
        """
        Detect color checker patches in image
        
        Args:
            image: Input image containing color checker
            grid_size: Grid dimensions (cols, rows)
            
        Returns:
            True if detection successful
        """
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # Find contours
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filter contours by area and aspect ratio
        patch_contours = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 500:  # Minimum patch area
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = w / h
                if 0.8 <= aspect_ratio <= 1.2:  # Square-like patches
                    patch_contours.append((x, y, w, h))
        
        # Sort patches by position (top-to-bottom, left-to-right)
        patch_contours.sort(key=lambda x: (x[1], x[0]))
        
        if len(patch_contours) < 24:
            print(f"Only found {len(patch_contours)} patches, expected 24")
            return False
        
        # Take first 24 patches
        self.patch_positions = patch_contours[:24]
        
        # Extract colors from patches
        self.detected_colors = []
        for x, y, w, h in self.patch_positions:
            patch = image[y:y+h, x:x+w]
            avg_color = np.mean(patch, axis=(0, 1))
            self.detected_colors.append(avg_color)
        
        self.detected_colors = np.array(self.detected_colors)
        return True
    
    def visualize_detection(self, image: np.ndarray) -> np.ndarray:
        """Visualize detected color checker patches"""
        if self.patch_positions is None:
            return image
        
        vis_image = image.copy()
        for i, (x, y, w, h) in enumerate(self.patch_positions):
            cv2.rectangle(vis_image, (x, y), (x+w, y+h), (255, 0, 0), 2)
            cv2.putText(vis_image, str(i), (x, y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
        
        return vis_image


class CameraCalibrator:
    """Camera color calibration using color checker"""
    
    def __init__(self, method: str = 'neural_network'):
        """
        Initialize calibrator
        
        Args:
            method: Calibration method ('linear', 'polynomial', 'neural_network')
        """
        self.method = method
        self.model = None
        self.color_checker = ColorChecker()
        self.is_calibrated = False
    
    def calibrate(self, calibration_image: np.ndarray) -> bool:
        """
        Calibrate camera using color checker image
        
        Args:
            calibration_image: Image containing color checker
            
        Returns:
            True if calibration successful
        """
        # Detect color checker patches
        if not self.color_checker.detect_color_checker(calibration_image):
            print("Failed to detect color checker")
            return False
        
        # Get detected RGB colors
        detected_rgb = self.color_checker.detected_colors
        
        # Convert to Lab color space
        detected_lab = np.array([ColorSpaceConverter.rgb_to_lab(rgb) for rgb in detected_rgb])
        target_lab = ColorChecker.STANDARD_LAB_VALUES
        
        # Train calibration model
        if self.method == 'linear':
            self.model = LinearRegression()
            self.model.fit(detected_lab, target_lab)
            
        elif self.method == 'polynomial':
            self.model = Pipeline([
                ('poly', PolynomialFeatures(degree=2)),
                ('linear', LinearRegression())
            ])
            self.model.fit(detected_lab, target_lab)
            
        elif self.method == 'neural_network':
            self.model = MLPRegressor(
                hidden_layer_sizes=(100, 50),
                activation='relu',
                solver='adam',
                max_iter=1000,
                random_state=42
            )
            self.model.fit(detected_lab, target_lab)
        
        else:
            raise ValueError(f"Unknown calibration method: {self.method}")
        
        self.is_calibrated = True
        print(f"Camera calibrated using {self.method} method")
        
        # Calculate calibration accuracy
        predicted_lab = self.model.predict(detected_lab)
        avg_delta_e = np.mean([
            np.sqrt(np.sum((pred - target) ** 2))
            for pred, target in zip(predicted_lab, target_lab)
        ])
        print(f"Average calibration error (ΔE): {avg_delta_e:.2f}")
        
        return True
    
    def apply_calibration(self, image: np.ndarray) -> np.ndarray:
        """
        Apply color calibration to image
        
        Args:
            image: Input image to calibrate
            
        Returns:
            Calibrated image
        """
        if not self.is_calibrated:
            raise ValueError("Camera not calibrated. Call calibrate() first.")
        
        # Convert image to Lab
        h, w, c = image.shape
        image_flat = image.reshape(-1, 3)
        lab_flat = np.array([ColorSpaceConverter.rgb_to_lab(rgb) for rgb in image_flat])
        
        # Apply calibration
        calibrated_lab_flat = self.model.predict(lab_flat)
        
        # Convert back to RGB
        calibrated_rgb_flat = np.array([
            ColorSpaceConverter.lab_to_rgb(lab) for lab in calibrated_lab_flat
        ])
        
        calibrated_image = calibrated_rgb_flat.reshape(h, w, c)
        return calibrated_image.astype(np.uint8)
    
    def save_calibration(self, filepath: str) -> None:
        """Save calibration model to file"""
        if not self.is_calibrated:
            raise ValueError("No calibration model to save")
        
        calibration_data = {
            'method': self.method,
            'model': self.model,
            'is_calibrated': self.is_calibrated
        }
        joblib.dump(calibration_data, filepath)
        print(f"Calibration saved to {filepath}")
    
    def load_calibration(self, filepath: str) -> bool:
        """Load calibration model from file"""
        if not os.path.exists(filepath):
            print(f"Calibration file not found: {filepath}")
            return False
        
        try:
            calibration_data = joblib.load(filepath)
            self.method = calibration_data['method']
            self.model = calibration_data['model']
            self.is_calibrated = calibration_data['is_calibrated']
            print(f"Calibration loaded from {filepath}")
            return True
        except Exception as e:
            print(f"Error loading calibration: {e}")
            return False


class LightingCorrector:
    """Correct for lighting conditions and shadows"""
    
    @staticmethod
    def correct_illumination(image: np.ndarray, method: str = 'gray_world') -> np.ndarray:
        """
        Correct image illumination
        
        Args:
            image: Input image
            method: Correction method ('gray_world', 'white_patch', 'shades_of_gray')
            
        Returns:
            Illumination-corrected image
        """
        image_float = image.astype(np.float32) / 255.0
        
        if method == 'gray_world':
            # Gray world assumption: average color should be gray
            mean_rgb = np.mean(image_float, axis=(0, 1))
            gray_mean = np.mean(mean_rgb)
            correction_factors = gray_mean / mean_rgb
            corrected = image_float * correction_factors
            
        elif method == 'white_patch':
            # White patch assumption: brightest point should be white
            max_rgb = np.max(image_float, axis=(0, 1))
            correction_factors = 1.0 / max_rgb
            corrected = image_float * correction_factors
            
        elif method == 'shades_of_gray':
            # Shades of gray with Minkowski norm
            p = 6  # Minkowski norm parameter
            mean_rgb_p = np.mean(image_float ** p, axis=(0, 1)) ** (1/p)
            gray_mean_p = np.mean(mean_rgb_p)
            correction_factors = gray_mean_p / mean_rgb_p
            corrected = image_float * correction_factors
            
        else:
            raise ValueError(f"Unknown illumination correction method: {method}")
        
        # Clip values and convert back to uint8
        corrected = np.clip(corrected, 0, 1)
        return (corrected * 255).astype(np.uint8)
    
    @staticmethod
    def remove_shadows(image: np.ndarray) -> np.ndarray:
        """Remove shadows using morphological operations"""
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # Create background model using morphological opening
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (20, 20))
        background = cv2.morphologyEx(gray, cv2.MORPH_OPEN, kernel)
        
        # Normalize image by background
        normalized = cv2.divide(gray, background, scale=255)
        
        # Convert back to 3-channel
        normalized_3ch = cv2.cvtColor(normalized, cv2.COLOR_GRAY2RGB)
        
        # Maintain original color ratios
        ratio = image.astype(np.float32) / (gray[:, :, np.newaxis] + 1e-7)
        result = normalized_3ch.astype(np.float32) * ratio
        
        return np.clip(result, 0, 255).astype(np.uint8)


class ImagePreprocessor:
    """Complete image preprocessing pipeline"""
    
    def __init__(self, calibrator: Optional[CameraCalibrator] = None):
        self.calibrator = calibrator
        self.lighting_corrector = LightingCorrector()
    
    def preprocess_image(self, image: np.ndarray, 
                        apply_calibration: bool = True,
                        correct_lighting: bool = True,
                        lighting_method: str = 'gray_world',
                        remove_shadows: bool = False,
                        target_size: Optional[Tuple[int, int]] = None) -> np.ndarray:
        """
        Complete preprocessing pipeline
        
        Args:
            image: Input image
            apply_calibration: Whether to apply camera calibration
            correct_lighting: Whether to correct illumination
            lighting_method: Lighting correction method
            remove_shadows: Whether to remove shadows
            target_size: Resize image to this size (width, height)
            
        Returns:
            Preprocessed image
        """
        processed = image.copy()
        
        # Resize if specified
        if target_size:
            processed = cv2.resize(processed, target_size)
        
        # Remove shadows
        if remove_shadows:
            processed = self.lighting_corrector.remove_shadows(processed)
        
        # Correct lighting
        if correct_lighting:
            processed = self.lighting_corrector.correct_illumination(processed, lighting_method)
        
        # Apply camera calibration
        if apply_calibration and self.calibrator and self.calibrator.is_calibrated:
            processed = self.calibrator.apply_calibration(processed)
        
        return processed
    
    def create_preprocessing_report(self, original: np.ndarray, 
                                  processed: np.ndarray) -> None:
        """Create visualization report of preprocessing steps"""
        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        
        # Original image
        axes[0, 0].imshow(original)
        axes[0, 0].set_title('Original Image')
        axes[0, 0].axis('off')
        
        # Processed image
        axes[0, 1].imshow(processed)
        axes[0, 1].set_title('Processed Image')
        axes[0, 1].axis('off')
        
        # Difference
        diff = np.abs(original.astype(np.float32) - processed.astype(np.float32))
        axes[0, 2].imshow(diff / 255.0)
        axes[0, 2].set_title('Difference')
        axes[0, 2].axis('off')
        
        # Histograms
        for i, (img, title) in enumerate([(original, 'Original'), (processed, 'Processed')]):
            ax = axes[1, i]
            colors = ['red', 'green', 'blue']
            for c, color in enumerate(colors):
                ax.hist(img[:, :, c].flatten(), bins=50, alpha=0.7, 
                       color=color, label=f'{color.upper()}')
            ax.set_title(f'{title} Histogram')
            ax.legend()
        
        # Color space analysis
        orig_lab = ColorSpaceConverter.rgb_to_lab(np.mean(original, axis=(0, 1)))
        proc_lab = ColorSpaceConverter.rgb_to_lab(np.mean(processed, axis=(0, 1)))
        
        axes[1, 2].bar(['L', 'a', 'b'], orig_lab, alpha=0.7, label='Original')
        axes[1, 2].bar(['L', 'a', 'b'], proc_lab, alpha=0.7, label='Processed')
        axes[1, 2].set_title('Average Lab Values')
        axes[1, 2].legend()
        
        plt.tight_layout()
        plt.show()


def batch_preprocess_images(input_dir: str, output_dir: str, 
                          calibrator: Optional[CameraCalibrator] = None,
                          **preprocessing_kwargs) -> None:
    """
    Batch preprocess images in a directory
    
    Args:
        input_dir: Input directory path
        output_dir: Output directory path
        calibrator: Camera calibrator (optional)
        **preprocessing_kwargs: Arguments for preprocessing
    """
    os.makedirs(output_dir, exist_ok=True)
    preprocessor = ImagePreprocessor(calibrator)
    
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
    image_files = [f for f in os.listdir(input_dir) 
                   if any(f.lower().endswith(ext) for ext in image_extensions)]
    
    print(f"Processing {len(image_files)} images...")
    
    for i, filename in enumerate(image_files):
        try:
            # Load image
            input_path = os.path.join(input_dir, filename)
            image = ImageProcessor.load_image(input_path)
            
            # Preprocess
            processed = preprocessor.preprocess_image(image, **preprocessing_kwargs)
            
            # Save
            output_path = os.path.join(output_dir, filename)
            ImageProcessor.save_image(processed, output_path)
            
            print(f"Processed {i+1}/{len(image_files)}: {filename}")
            
        except Exception as e:
            print(f"Error processing {filename}: {e}")
    
    print("Batch preprocessing completed!")