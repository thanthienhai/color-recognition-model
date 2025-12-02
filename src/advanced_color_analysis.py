"""
Advanced Color Analysis Module V2 - Upgraded for Better Accuracy
Phân tích màu nâng cao với CIEDE2000 và cải thiện thuật toán
"""

import numpy as np
import cv2
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import math
import logging

# Setup logger
logger = logging.getLogger(__name__)

# Import prediction logger
try:
    from prediction_logger import get_prediction_logger
    PREDICTION_LOGGER_AVAILABLE = True
except ImportError:
    PREDICTION_LOGGER_AVAILABLE = False
    get_prediction_logger = None
    logger.warning("PredictionLogger not available")


@dataclass
class ColorPrediction:
    """Kết quả dự đoán màu"""
    primary_colors: Dict[str, float]  # Tỉ lệ các màu cơ bản
    dominant_color: str              # Màu chính
    confidence: float                # Độ tin cậy
    rgb_values: Tuple[int, int, int] # Giá trị RGB
    lab_values: Tuple[float, float, float]  # Giá trị Lab
    delta_e_values: Optional[Dict[str, float]] = None  # Delta E to each color
    prediction_method: str = "ciede2000"  # Method used: "cnn" or "ciede2000"
    model_version: Optional[str] = None  # CNN model version if applicable
    inference_time_ms: Optional[float] = None  # Inference time in milliseconds
    quality_score: Optional[str] = None  # Quality classification


class CIEDE2000Calculator:
    """
    Implement CIEDE2000 color difference formula
    Industry standard for perceptually uniform color differences
    """
    
    @staticmethod
    def calculate_delta_e_2000(lab1: Tuple[float, float, float], 
                               lab2: Tuple[float, float, float],
                               kL: float = 1.0, kC: float = 1.0, kH: float = 1.0) -> float:
        """
        Calculate CIEDE2000 color difference
        
        Args:
            lab1, lab2: Lab color values (L, a, b)
            kL, kC, kH: Weighting factors (default 1.0 for standard illuminants)
            
        Returns:
            Delta E 2000 value
        """
        L1, a1, b1 = lab1
        L2, a2, b2 = lab2
        
        # Calculate C (chroma) and h (hue angle)
        C1 = math.sqrt(a1**2 + b1**2)
        C2 = math.sqrt(a2**2 + b2**2)
        
        # Calculate average C
        C_bar = (C1 + C2) / 2.0
        
        # Calculate G factor
        G = 0.5 * (1 - math.sqrt(C_bar**7 / (C_bar**7 + 25**7)))
        
        # Calculate a' (modified a)
        a1_prime = a1 * (1 + G)
        a2_prime = a2 * (1 + G)
        
        # Calculate C' (modified chroma)
        C1_prime = math.sqrt(a1_prime**2 + b1**2)
        C2_prime = math.sqrt(a2_prime**2 + b2**2)
        
        # Calculate h' (modified hue angle in degrees)
        h1_prime = math.degrees(math.atan2(b1, a1_prime)) % 360
        h2_prime = math.degrees(math.atan2(b2, a2_prime)) % 360
        
        # Calculate differences
        delta_L_prime = L2 - L1
        delta_C_prime = C2_prime - C1_prime
        
        # Calculate delta h'
        if C1_prime * C2_prime == 0:
            delta_h_prime = 0
        else:
            delta_h = h2_prime - h1_prime
            if abs(delta_h) <= 180:
                delta_h_prime = delta_h
            elif delta_h > 180:
                delta_h_prime = delta_h - 360
            else:
                delta_h_prime = delta_h + 360
        
        # Calculate delta H'
        delta_H_prime = 2 * math.sqrt(C1_prime * C2_prime) * math.sin(math.radians(delta_h_prime / 2))
        
        # Calculate averages for weighting factors
        L_bar_prime = (L1 + L2) / 2.0
        C_bar_prime = (C1_prime + C2_prime) / 2.0
        
        # Calculate average h'
        if C1_prime * C2_prime == 0:
            h_bar_prime = h1_prime + h2_prime
        else:
            if abs(h1_prime - h2_prime) <= 180:
                h_bar_prime = (h1_prime + h2_prime) / 2.0
            elif h1_prime + h2_prime < 360:
                h_bar_prime = (h1_prime + h2_prime + 360) / 2.0
            else:
                h_bar_prime = (h1_prime + h2_prime - 360) / 2.0
        
        # Calculate T
        T = 1 - 0.17 * math.cos(math.radians(h_bar_prime - 30)) + \
            0.24 * math.cos(math.radians(2 * h_bar_prime)) + \
            0.32 * math.cos(math.radians(3 * h_bar_prime + 6)) - \
            0.20 * math.cos(math.radians(4 * h_bar_prime - 63))
        
        # Calculate SL, SC, SH
        SL = 1 + (0.015 * (L_bar_prime - 50)**2) / math.sqrt(20 + (L_bar_prime - 50)**2)
        SC = 1 + 0.045 * C_bar_prime
        SH = 1 + 0.015 * C_bar_prime * T
        
        # Calculate RT (rotation term)
        delta_theta = 30 * math.exp(-((h_bar_prime - 275) / 25)**2)
        RC = 2 * math.sqrt(C_bar_prime**7 / (C_bar_prime**7 + 25**7))
        RT = -RC * math.sin(math.radians(2 * delta_theta))
        
        # Calculate final Delta E 2000
        delta_E = math.sqrt(
            (delta_L_prime / (kL * SL))**2 +
            (delta_C_prime / (kC * SC))**2 +
            (delta_H_prime / (kH * SH))**2 +
            RT * (delta_C_prime / (kC * SC)) * (delta_H_prime / (kH * SH))
        )
        
        return delta_E


class ImprovedColorAnalyzer:
    """
    Upgraded color analyzer with CIEDE2000 and better algorithms
    Using original 16 colors only
    """
    
    def __init__(self):
        # Original 16 colors from the system
        self.color_names = [
            "Đen", "Trắng", "Vàng Chanh", "Đỏ", "Xanh Biển Sâu",
            "Xanh Dương", "Tím", "Nâu", "Vàng Neon", "Xanh Neon",
            "Xanh Lam Neon", "Cam Neon", "Hồng Neon", "Tím Neon", "Vàng Kim"
        ]
        
        # Optimized LAB reference colors for 16 colors (validated and improved)
        self.reference_lab = {
            "Đen": np.array([15.0, 0.0, 0.0]),           # Near black (was 0)
            "Trắng": np.array([95.0, 0.0, 0.0]),         # Near white (was 100)
            "Vàng Chanh": np.array([95.0, -15.0, 90.0]), # Lemon yellow (improved)
            "Đỏ": np.array([53.0, 80.0, 67.0]),          # Pure red (validated)
            "Xanh Biển Sâu": np.array([72.0, -25.0, -38.0]), # Deep sky blue (improved)
            "Xanh Dương": np.array([32.0, 79.0, -108.0]), # Pure blue (validated)
            "Tím": np.array([30.0, 59.0, -36.0]),        # Purple (validated)
            "Nâu": np.array([40.0, 25.0, 35.0]),         # Brown (improved)
            "Vàng Neon": np.array([94.0, -20.0, 93.0]),  # Neon yellow (improved)
            "Xanh Neon": np.array([87.0, -85.0, 83.0]),  # Neon green (validated)
            "Xanh Lam Neon": np.array([90.0, -48.0, -14.0]), # Neon cyan (improved)
            "Cam Neon": np.array([67.0, 55.0, 70.0]),    # Neon orange (improved)
            "Hồng Neon": np.array([60.0, 98.0, -60.0]),  # Neon pink/magenta (improved)
            "Tím Neon": np.array([40.0, 70.0, -65.0]),   # Neon purple (improved)
            "Vàng Kim": np.array([85.0, 5.0, 80.0])      # Golden yellow (improved)
        }
        
        self.delta_e_calculator = CIEDE2000Calculator()
    
    def analyze_color(self, rgb_values: Tuple[int, int, int], 
                     lab_values: Tuple[float, float, float],
                     temperature: float = 3.0) -> Dict[str, float]:
        """
        Analyze color using CIEDE2000 with exponential similarity
        
        Args:
            rgb_values: RGB color values (0-255)
            lab_values: Lab color values
            temperature: Controls the "softness" of color matching (higher = softer)
            
        Returns:
            Dictionary of color percentages
        """
        input_lab = np.array(lab_values)
        delta_e_values = {}
        
        # Calculate CIEDE2000 distance to each reference color
        for color_name, ref_lab in self.reference_lab.items():
            delta_e = self.delta_e_calculator.calculate_delta_e_2000(
                input_lab, ref_lab
            )
            delta_e_values[color_name] = delta_e
        
        # Convert distances to similarities using exponential decay
        # Lower Delta E = higher similarity
        similarities = {}
        for color_name, delta_e in delta_e_values.items():
            # Use exponential decay: similarity = exp(-delta_e / temperature)
            # This gives smooth, intuitive results
            similarity = math.exp(-delta_e / temperature)
            similarities[color_name] = similarity
        
        # Normalize to percentages
        total_similarity = sum(similarities.values())
        if total_similarity > 0:
            percentages = {
                color: (sim / total_similarity) * 100 
                for color, sim in similarities.items()
            }
        else:
            # Fallback: equal distribution
            percentages = {
                color: 100.0 / len(self.color_names) 
                for color in self.color_names
            }
        
        return percentages, delta_e_values
    
    def analyze_with_constraints(self, rgb_values: Tuple[int, int, int], 
                                 lab_values: Tuple[float, float, float],
                                 max_colors: int = 5,
                                 min_percentage: float = 3.0) -> Dict[str, float]:
        """
        Analyze color with constraints for cleaner results
        
        Args:
            rgb_values: RGB values
            lab_values: Lab values
            max_colors: Maximum number of colors to return
            min_percentage: Minimum percentage threshold
            
        Returns:
            Filtered dictionary of color percentages
        """
        percentages, delta_e_values = self.analyze_color(rgb_values, lab_values)
        
        # Filter by minimum percentage
        filtered = {
            color: pct for color, pct in percentages.items()
            if pct >= min_percentage
        }
        
        # Sort and take top N
        sorted_colors = sorted(filtered.items(), key=lambda x: x[1], reverse=True)
        top_colors = dict(sorted_colors[:max_colors])
        
        # Renormalize to 100%
        total = sum(top_colors.values())
        if total > 0:
            normalized = {
                color: (pct / total) * 100
                for color, pct in top_colors.items()
            }
        else:
            normalized = top_colors
        
        return normalized


class ColorAnalysisEngineV2:
    """
    Upgraded Color Analysis Engine with better algorithms
    Supports both CIEDE2000 and CNN-based analysis
    """
    
    def __init__(self, cnn_model_path: Optional[str] = None):
        self.analyzer = ImprovedColorAnalyzer()
        self.delta_e_calculator = CIEDE2000Calculator()
        
        # CNN model integration
        self.cnn_model = None
        self.cnn_available = False
        
        # Try to load CNN model if path provided
        if cnn_model_path:
            self._load_cnn_model(cnn_model_path)
    
    def _get_quality_from_delta_e(self, delta_e: float) -> str:
        """
        Get quality classification from Delta E value.
        
        Args:
            delta_e: Delta E value
            
        Returns:
            Quality string: "Excellent", "Good", "Acceptable", or "Poor"
        """
        if delta_e < 1.0:
            return "Excellent"
        elif delta_e < 2.0:
            return "Good"
        elif delta_e < 4.0:
            return "Acceptable"
        else:
            return "Poor"
    
    def _load_cnn_model(self, model_path: str) -> bool:
        """
        Load CNN model for color ratio prediction.
        
        Args:
            model_path: Path to CNN model checkpoint
            
        Returns:
            True if loading successful, False otherwise
        """
        try:
            from deep_color_model import CNNColorRatioModel
            
            self.cnn_model = CNNColorRatioModel(model_path=model_path)
            self.cnn_available = True
            print(f"CNN model loaded successfully from {model_path}")
            return True
        
        except ImportError:
            print("PyTorch not available, CNN model disabled")
            return False
        
        except Exception as e:
            print(f"Failed to load CNN model: {e}")
            return False
    
    def analyze_color(self, rgb_values: Tuple[int, int, int], 
                     lab_values: Tuple[float, float, float],
                     method: str = "auto",
                     image: Optional[np.ndarray] = None) -> ColorPrediction:
        """
        Analyze color and return prediction
        
        Args:
            rgb_values: RGB values (0-255)
            lab_values: Lab values
            method: "auto" (default), "cnn", "ciede2000", or "simple"
            image: Optional image array for CNN analysis (224x224x3)
            
        Returns:
            ColorPrediction object
        """
        # Method selection logic
        if method == "auto":
            # Try CNN first if available, fallback to CIEDE2000
            if self.cnn_available and image is not None:
                try:
                    return self._analyze_with_cnn(rgb_values, lab_values, image)
                except Exception as e:
                    print(f"CNN analysis failed: {e}, falling back to CIEDE2000")
                    method = "ciede2000"
            else:
                method = "ciede2000"
        
        if method == "cnn":
            if not self.cnn_available:
                raise ValueError("CNN model not available. Use method='ciede2000' or load CNN model.")
            if image is None:
                raise ValueError("Image required for CNN analysis")
            return self._analyze_with_cnn(rgb_values, lab_values, image)
        
        elif method == "ciede2000":
            percentages, delta_e_values = self.analyzer.analyze_color(
                rgb_values, lab_values, temperature=3.5
            )
        else:
            # Fallback to simple distance
            percentages, delta_e_values = self.analyzer.analyze_color(
                rgb_values, lab_values, temperature=5.0
            )
        
        # Sort by percentage
        sorted_colors = dict(sorted(percentages.items(), 
                                   key=lambda x: x[1], reverse=True))
        
        # Find dominant color
        dominant_color = max(sorted_colors, key=sorted_colors.get)
        confidence = sorted_colors[dominant_color] / 100.0
        
        # Get quality score from Delta E
        min_delta_e = min(delta_e_values.values()) if delta_e_values else None
        quality_score = self._get_quality_from_delta_e(min_delta_e) if min_delta_e is not None else None
        
        return ColorPrediction(
            primary_colors=sorted_colors,
            dominant_color=dominant_color,
            confidence=confidence,
            rgb_values=rgb_values,
            lab_values=lab_values,
            delta_e_values=delta_e_values,
            quality_score=quality_score
        )
    
    def process_input_image(self, image_rgb: np.ndarray) -> Tuple[Tuple[int, int, int], Tuple[float, float, float]]:
        """
        Process input image (ROI) to extract dominant color and convert to Standard Lab.
        Uses K-Means clustering for robust color extraction.
        
        Args:
            image_rgb: Input RGB image (ROI)
            
        Returns:
            Tuple of ((r,g,b), (L,a,b)) where L,a,b are in Standard scale
        """
        # 1. Extract dominant color using K-Means (k=1)
        # Reshape to list of pixels
        pixels = image_rgb.reshape(-1, 3).astype(np.float32)
        
        # Define criteria = ( type, max_iter, epsilon )
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
        
        # Run k-means
        # k=1 to find the single most dominant color (centroid)
        _, labels, centers = cv2.kmeans(pixels, 1, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
        
        # Get the dominant color (RGB)
        dominant_rgb = centers[0].astype(np.uint8)
        rgb_int = tuple(int(x) for x in dominant_rgb)
        
        # 2. Convert to Lab
        # Create a 1x1 pixel image for conversion
        pixel_img = np.array([[dominant_rgb]], dtype=np.uint8)
        
        # Convert to Lab using OpenCV
        pixel_lab_cv = cv2.cvtColor(pixel_img, cv2.COLOR_RGB2LAB)[0][0]
        
        # 3. Convert OpenCV Lab to Standard Lab
        # OpenCV L: 0..255 -> Standard L: 0..100
        # OpenCV a: 0..255 -> Standard a: -128..127
        # OpenCV b: 0..255 -> Standard b: -128..127
        std_L = float(pixel_lab_cv[0]) * 100.0 / 255.0
        std_a = float(pixel_lab_cv[1]) - 128.0
        std_b = float(pixel_lab_cv[2]) - 128.0
        
        lab_std = (std_L, std_a, std_b)
        
        return rgb_int, lab_std
    
    def _analyze_with_cnn(self, rgb_values: Tuple[int, int, int],
                         lab_values: Tuple[float, float, float],
                         image: np.ndarray) -> ColorPrediction:
        """
        Analyze color using CNN model.
        
        Args:
            rgb_values: RGB values (0-255)
            lab_values: Lab values
            image: Image array (H, W, 3) with RGB values [0, 255]
            
        Returns:
            ColorPrediction object
        """
        import time
        
        # Measure inference time
        start_time = time.time()
        ratios = self.cnn_model.predict(image)
        inference_time_ms = (time.time() - start_time) * 1000
        
        # Convert ratios to percentages
        percentages = {
            color_name: float(ratio * 100)
            for color_name, ratio in zip(self.analyzer.color_names, ratios)
        }
        
        # Sort by percentage
        sorted_colors = dict(sorted(percentages.items(), 
                                   key=lambda x: x[1], reverse=True))
        
        # Find dominant color
        dominant_color = max(sorted_colors, key=sorted_colors.get)
        confidence = sorted_colors[dominant_color] / 100.0
        
        # Calculate Delta E values for reference
        delta_e_values = {}
        input_lab = np.array(lab_values)
        for color_name, ref_lab in self.analyzer.reference_lab.items():
            delta_e = self.delta_e_calculator.calculate_delta_e_2000(
                input_lab, ref_lab
            )
            delta_e_values[color_name] = delta_e
        
        # Get minimum Delta E for quality score
        min_delta_e = min(delta_e_values.values())
        quality_score = self._get_quality_from_delta_e(min_delta_e)
        
        # Get model version
        model_version = self.cnn_model.model_version if hasattr(self.cnn_model, 'model_version') else None
        
        return ColorPrediction(
            primary_colors=sorted_colors,
            dominant_color=dominant_color,
            confidence=confidence,
            rgb_values=rgb_values,
            lab_values=lab_values,
            delta_e_values=delta_e_values,
            prediction_method="cnn",
            model_version=model_version,
            inference_time_ms=inference_time_ms,
            quality_score=quality_score
        )
    
    def preprocess_image_for_cnn(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocess image for CNN inference.
        
        Applies:
        - Resize to 224x224
        - Color normalization
        - ImageNet normalization
        
        Args:
            image: Input image (H, W, 3) with RGB values [0, 255]
            
        Returns:
            Preprocessed image ready for CNN
        """
        # Resize to 224x224 if needed
        if image.shape[:2] != (224, 224):
            image = cv2.resize(image, (224, 224))
        
        # Ensure RGB format and uint8
        if image.dtype != np.uint8:
            image = np.clip(image, 0, 255).astype(np.uint8)
        
        return image
    
    def get_mixing_formula(self, color_prediction: ColorPrediction,
                          simplify: bool = True,
                          max_colors: int = 8) -> Dict[str, int]:
        """
        Generate mixing formula with improved algorithm
        
        Args:
            color_prediction: Color prediction result
            simplify: Whether to simplify ratios
            max_colors: Maximum colors in formula
            
        Returns:
            Dictionary of color parts (integers)
        """
        # Filter colors by significance (> 0.1%)
        significant_colors = {
            color: percentage
            for color, percentage in color_prediction.primary_colors.items()
            if percentage > 0.1
        }
        
        if not significant_colors:
            significant_colors = {
                color_prediction.dominant_color: 100.0
            }
        
        # Limit to max_colors
        if len(significant_colors) > max_colors:
            sorted_colors = sorted(significant_colors.items(), 
                                  key=lambda x: x[1], reverse=True)
            significant_colors = dict(sorted_colors[:max_colors])
            
            # Renormalize
            total = sum(significant_colors.values())
            significant_colors = {
                color: (pct / total) * 100
                for color, pct in significant_colors.items()
            }
        
        # Convert to integer ratios
        multiplier = 1000
        ratios = {
            color: int(percentage * multiplier) 
            for color, percentage in significant_colors.items()
        }
        
        if simplify:
            # Simplify using GCD
            import math
            gcd_value = math.gcd(*ratios.values())
            ratios = {color: ratio // gcd_value for color, ratio in ratios.items()}
        
        return ratios
    
    def validate_mixing_formula(self, formula: Dict[str, int]) -> Dict[str, any]:
        """
        Validate mixing formula for correctness and UART compatibility.
        
        Args:
            formula: Dictionary of color names to integer parts
            
        Returns:
            Dictionary with validation results
        """
        validation_result = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'total_parts': 0,
            'num_colors': len(formula)
        }
        
        # Check if formula is empty
        if not formula:
            validation_result['valid'] = False
            validation_result['errors'].append("Formula is empty")
            return validation_result
        
        # Calculate total parts
        total_parts = sum(formula.values())
        validation_result['total_parts'] = total_parts
        
        # Check all values are positive integers
        for color, parts in formula.items():
            if not isinstance(parts, int):
                validation_result['valid'] = False
                validation_result['errors'].append(f"{color}: value must be integer, got {type(parts)}")
            elif parts <= 0:
                validation_result['valid'] = False
                validation_result['errors'].append(f"{color}: value must be positive, got {parts}")
        
        # Check color names are valid
        valid_colors = set(self.analyzer.color_names)
        for color in formula.keys():
            if color not in valid_colors:
                validation_result['valid'] = False
                validation_result['errors'].append(f"Invalid color name: {color}")
        
        # Check UART compatibility (reasonable number of parts)
        if total_parts > 1000:
            validation_result['warnings'].append(
                f"Total parts ({total_parts}) is very large, may cause UART issues"
            )
        
        # Check number of colors
        if len(formula) > 8:
            validation_result['warnings'].append(
                f"Formula has {len(formula)} colors, more than recommended maximum of 8"
            )
        
        return validation_result
    
    def export_formula_to_json(
        self,
        formula: Dict[str, int],
        color_prediction: ColorPrediction,
        save_path: str,
        include_metadata: bool = True
    ) -> None:
        """
        Export mixing formula to JSON file.
        
        Args:
            formula: Mixing formula dictionary
            color_prediction: Color prediction result
            save_path: Path to save JSON file
            include_metadata: Whether to include metadata
        """
        import json
        from datetime import datetime
        from pathlib import Path
        
        # Create output directory if needed
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Prepare formula data
        formula_data = {
            'formula': formula,
            'total_parts': sum(formula.values())
        }
        
        # Add metadata if requested
        if include_metadata:
            formula_data['metadata'] = {
                'timestamp': datetime.now().isoformat(),
                'target_rgb': color_prediction.rgb_values,
                'target_lab': color_prediction.lab_values,
                'dominant_color': color_prediction.dominant_color,
                'confidence': color_prediction.confidence,
                'prediction_method': color_prediction.prediction_method,
                'model_version': color_prediction.model_version,
                'quality_score': color_prediction.quality_score
            }
        
        # Save to JSON
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(formula_data, f, indent=2, ensure_ascii=False)
    
    def format_uart_message(self, formula: Dict[str, int]) -> str:
        """
        Format mixing formula as UART message.
        Format: @mau1{T1,K1},mau2{T2,K2},mau3{T3,K3},mau4{T4,K4},mau5{T5,K5}#
        
        Args:
            formula: Mixing formula dictionary
            
        Returns:
            UART-formatted message string
        """
        # Hardware color mapping
        # Maps color name to Machine ID (T)
        hardware_map = {
            "Đen": "13",
            "Trắng": "0",
            "Vàng Chanh": "8",
            "Đỏ": "3",
            "Xanh Biển Sâu": "1",
            "Xanh Dương": "7",
            "Tím": "10",
            "Nâu": "14",
            "Vàng Neon": "5",
            "Xanh Neon": "4",
            "Xanh Lam Neon": "11",
            "Cam Neon": "9",
            "Hồng Neon": "12",
            "Tím Neon": "15",
            "Vàng Kim": "2"
        }
        
        items = list(formula.items())
        # Sort by weight desc
        items.sort(key=lambda x: x[1], reverse=True)
        
        formatted_items = []
        used_ids = set()
        
        # Process existing colors
        for i in range(5):
            if i < len(items):
                name_or_id, weight = items[i]
                
                # Determine Color ID (T)
                if str(name_or_id) in hardware_map.values():
                    # Already an ID
                    color_id = str(name_or_id)
                else:
                    # Look up ID by name
                    color_id = hardware_map.get(str(name_or_id), "0")
                    if color_id == "0" and str(name_or_id) != "Trắng":
                         # 0 is White, so if it's not White but got 0, it's unknown
                         # But wait, "Trắng" maps to "0".
                         # If name is unknown, what ID to use?
                         # Maybe keep 0 or log warning.
                         print(f"Warning: Unknown color {name_or_id}, using ID 0")
                
                formatted_items.append(f"mau{i+1}{{{color_id},{weight}}}")
                used_ids.add(color_id)
            else:
                # Fill with random color, K=0
                # Pick a random ID not in used_ids
                import random
                all_ids = list(hardware_map.values())
                available_ids = [id for id in all_ids if id not in used_ids]
                if not available_ids:
                    available_ids = all_ids
                
                random_id = random.choice(available_ids)
                
                formatted_items.append(f"mau{i+1}{{{random_id},0}}")
                used_ids.add(random_id)
                
        return "@" + ",".join(formatted_items) + "#"
    
    def save_formula_to_file(
        self,
        formula: Dict[str, int],
        color_prediction: ColorPrediction,
        output_dir: str = "mixing_formulas",
        filename: Optional[str] = None
    ) -> str:
        """
        Save mixing formula to file in mixing_formulas directory.
        
        Args:
            formula: Mixing formula dictionary
            color_prediction: Color prediction result
            output_dir: Output directory
            filename: Optional filename (auto-generated if None)
            
        Returns:
            Path to saved file
        """
        from datetime import datetime
        from pathlib import Path
        
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Generate filename if not provided
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            dominant = color_prediction.dominant_color.replace(" ", "_")
            filename = f"formula_{dominant}_{timestamp}.json"
        
        # Full path
        save_path = output_path / filename
        
        # Export to JSON
        self.export_formula_to_json(
            formula,
            color_prediction,
            str(save_path),
            include_metadata=True
        )
        
        return str(save_path)
    
    def calculate_color_distance(self, lab1: Tuple[float, float, float],
                                 lab2: Tuple[float, float, float]) -> float:
        """
        Calculate CIEDE2000 distance between two colors
        
        Args:
            lab1, lab2: Lab color values
            
        Returns:
            Delta E 2000 value
        """
        return self.delta_e_calculator.calculate_delta_e_2000(lab1, lab2)
    
    def get_color_quality_score(self, color_prediction: ColorPrediction) -> Dict[str, any]:
        """
        Get quality metrics for the color analysis
        
        Returns:
            Dictionary with quality metrics
        """
        # Calculate metrics
        top_color_pct = list(color_prediction.primary_colors.values())[0]
        top_3_sum = sum(list(color_prediction.primary_colors.values())[:3])
        num_significant = sum(1 for pct in color_prediction.primary_colors.values() if pct > 5.0)
        
        # Get closest delta E
        if color_prediction.delta_e_values:
            min_delta_e = min(color_prediction.delta_e_values.values())
            closest_color = min(color_prediction.delta_e_values.items(), 
                              key=lambda x: x[1])[0]
        else:
            min_delta_e = None
            closest_color = None
        
        return {
            "confidence": color_prediction.confidence,
            "dominant_percentage": top_color_pct,
            "top_3_coverage": top_3_sum,
            "num_significant_colors": num_significant,
            "min_delta_e": min_delta_e,
            "closest_reference_color": closest_color,
            "quality_rating": self._calculate_quality_rating(
                top_color_pct, min_delta_e
            )
        }
    
    def _calculate_quality_rating(self, dominant_pct: float, 
                                  min_delta_e: Optional[float]) -> str:
        """Calculate overall quality rating"""
        if min_delta_e is not None:
            if min_delta_e < 2.0 and dominant_pct > 50:
                return "Excellent"
            elif min_delta_e < 5.0 and dominant_pct > 30:
                return "Good"
            elif min_delta_e < 10.0:
                return "Fair"
            else:
                return "Poor"
        else:
            if dominant_pct > 50:
                return "Good"
            elif dominant_pct > 30:
                return "Fair"
            else:
                return "Poor"


# Global instance
color_engine_v2 = ColorAnalysisEngineV2()


# Backward compatibility alias
ColorAnalysisEngine = ColorAnalysisEngineV2
color_engine = color_engine_v2
