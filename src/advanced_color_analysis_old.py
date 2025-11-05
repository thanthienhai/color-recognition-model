"""
Advanced Color Analysis Module for Deep Learning-based Color Recognition
Phân tích màu sâu với 12 màu cơ bản
"""

import numpy as np
import cv2
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import json
import os


@dataclass
class ColorPrediction:
    """Kết quả dự đoán màu"""
    primary_colors: Dict[str, float]  # Tỉ lệ các màu cơ bản
    dominant_color: str              # Màu chính
    confidence: float                # Độ tin cậy
    rgb_values: Tuple[int, int, int] # Giá trị RGB
    lab_values: Tuple[float, float, float]  # Giá trị Lab


class DeepColorAnalyzer(nn.Module):
    """
    Mô hình Deep Learning để phân tích màu thành 16 màu cơ bản
    """
    
    def __init__(self, input_features=6, hidden_size=128, num_colors=16):
        super(DeepColorAnalyzer, self).__init__()
        
        # Define 16 basic colors
        self.color_names = [
            "Đen", "Trắng", "Vàng Chanh", "Đỏ", "Xanh Lá", "Xanh Biển Sâu",
            "Xanh Dương", "Tím", "Nâu", "Vàng Neon", "Xanh Neon",
            "Xanh Lam Neon", "Cam Neon", "Hồng Neon", "Tím Neon", "Vàng Kim"
        ]

        # Neural network layers
        self.feature_net = nn.Sequential(
            nn.Linear(input_features, hidden_size),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(hidden_size, hidden_size),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(hidden_size, 64),
            nn.ReLU(),
        )

        # Color composition predictor
        self.color_predictor = nn.Linear(64, num_colors)
        
        # Initialize reference colors
        self._init_reference_colors()
    
    def _init_reference_colors(self):
        """Khởi tạo màu tham chiếu cho 16 màu cơ bản"""
        # RGB values for 16 basic colors
        self.reference_colors = {
            "Đen": np.array([0, 0, 0]),
            "Trắng": np.array([255, 255, 255]),
            "Vàng Chanh": np.array([255, 244, 79]),
            "Đỏ": np.array([255, 0, 0]),
            "Xanh Lá": np.array([0, 128, 0]),
            "Xanh Biển Sâu": np.array([0, 191, 255]),
            "Xanh Dương": np.array([0, 0, 255]),
            "Tím": np.array([128, 0, 128]),
            "Nâu": np.array([150, 75, 0]),
            "Vàng Neon": np.array([204, 255, 0]),
            "Xanh Neon": np.array([0, 255, 0]),
            "Xanh Lam Neon": np.array([0, 255, 255]),
            "Cam Neon": np.array([255, 95, 0]),
            "Hồng Neon": np.array([255, 0, 255]),
            "Tím Neon": np.array([153, 0, 255]),
            "Vàng Kim": np.array([255, 215, 0])
        }
        
        # Convert to LAB color space for better color matching
        self.reference_lab = {}
        for name, rgb in self.reference_colors.items():
            # Create a 1x1 image with the color
            color_img = np.uint8([[rgb]])
            lab = cv2.cvtColor(color_img, cv2.COLOR_RGB2LAB)[0][0]
            self.reference_lab[name] = lab.astype(np.float32)
    
    def forward(self, x):
        """Forward pass của mô hình"""
        features = self.feature_net(x)
        color_composition = torch.softmax(self.color_predictor(features), dim=1)
        return color_composition
    
    def extract_features(self, rgb_values: Tuple[int, int, int], 
                        lab_values: Tuple[float, float, float]) -> np.ndarray:
        """
        Trích xuất features từ giá trị RGB và Lab
        
        Args:
            rgb_values: Giá trị RGB (0-255)
            lab_values: Giá trị Lab
            
        Returns:
            Feature vector
        """
        r, g, b = rgb_values
        l, a, lab_b = lab_values
        
        # Normalize RGB to 0-1
        rgb_norm = np.array([r/255.0, g/255.0, b/255.0])
        
        # Normalize Lab values
        l_norm = l / 100.0  # L: 0-100
        a_norm = (a + 128) / 255.0  # a: -128 to 127
        b_norm = (lab_b + 128) / 255.0  # b: -128 to 127
        
        # Combine features
        features = np.array([
            rgb_norm[0], rgb_norm[1], rgb_norm[2],  # RGB normalized
            l_norm, a_norm, b_norm                   # Lab normalized
        ], dtype=np.float32)
        
        return features


class TraditionalColorAnalyzer:
    """
    Phân tích màu truyền thống dựa trên khoảng cách màu sắc
    """
    
    def __init__(self):
        self.color_names = [
            "Đen", "Trắng", "Vàng Chanh", "Đỏ", "Xanh Lá", "Xanh Biển Sâu",
            "Xanh Dương", "Tím", "Nâu", "Vàng Neon", "Xanh Neon",
            "Xanh Lam Neon", "Cam Neon", "Hồng Neon", "Tím Neon", "Vàng Kim"
        ]
        
        # Define color ranges in HSV for better color detection
        self.hsv_ranges = {
            "Đen": [(0, 0, 0), (180, 255, 50)],
            "Trắng": [(0, 0, 200), (180, 30, 255)],
            "Vàng Chanh": [(50, 50, 70), (65, 255, 255)],
            "Đỏ": [(0, 50, 50), (10, 255, 255), (170, 50, 50), (180, 255, 255)],
            "Xanh Lá": [(35, 50, 50), (85, 255, 255)],
            "Xanh Biển Sâu": [(90, 50, 50), (105, 255, 255)],
            "Xanh Dương": [(105, 50, 50), (135, 255, 255)],
            "Tím": [(135, 50, 50), (160, 255, 255)],
            "Nâu": [(8, 50, 20), (20, 255, 200)],
            "Vàng Neon": [(45, 50, 50), (70, 255, 255)],
            "Xanh Neon": [(30, 50, 50), (50, 255, 255)],
            "Xanh Lam Neon": [(80, 50, 50), (100, 255, 255)],
            "Cam Neon": [(5, 50, 50), (15, 255, 255)],
            "Hồng Neon": [(150, 50, 50), (170, 255, 255)],
            "Tím Neon": [(120, 50, 50), (145, 255, 255)],
            "Vàng Kim": [(40, 50, 50), (55, 255, 255)]
        }
        
        # LAB reference colors
        self.reference_lab = {
            "Đen": np.array([0.0, 0.0, 0.0]),
            "Trắng": np.array([100.0, 0.0, 0.0]),
            "Vàng Chanh": np.array([97.5, -10.0, 80.0]),
            "Đỏ": np.array([53.23, 80.11, 67.22]),
            "Xanh Lá": np.array([46.0, -51.0, 48.0]),
            "Xanh Biển Sâu": np.array([70.0, -20.0, -40.0]),
            "Xanh Dương": np.array([32.30, 79.19, -107.86]),
            "Tím": np.array([29.78, 58.93, -36.49]),
            "Nâu": np.array([37.52, 35.68, 33.94]),
            "Vàng Neon": np.array([97.0, -15.0, 85.0]),
            "Xanh Neon": np.array([87.74, -86.18, 83.18]),
            "Xanh Lam Neon": np.array([91.11, -48.09, -14.13]),
            "Cam Neon": np.array([70.0, 40.0, 70.0]),
            "Hồng Neon": np.array([60.0, 98.0, -60.0]),
            "Tím Neon": np.array([35.0, 70.0, -50.0]),
            "Vàng Kim": np.array([87.0, -5.0, 75.0])
        }
    
    def analyze_color_by_distance(self, lab_values: Tuple[float, float, float]) -> Dict[str, float]:
        """
        Phân tích màu dựa trên khoảng cách CIE Lab
        
        Args:
            lab_values: Giá trị Lab của màu cần phân tích
            
        Returns:
            Dictionary chứa tỉ lệ tương ứng với mỗi màu cơ bản
        """
        input_lab = np.array(lab_values)
        distances = {}
        
        for color_name, ref_lab in self.reference_lab.items():
            delta_e = self._calculate_delta_e(input_lab, ref_lab)
            distances[color_name] = delta_e
        
       
        max_distance = max(distances.values())
        similarities = {}
        for color_name, distance in distances.items():
            similarity = max_distance - distance
            similarities[color_name] = max(0, similarity)
        
        total_similarity = sum(similarities.values())
        if total_similarity > 0:
            percentages = {color: (sim / total_similarity) * 100 
                          for color, sim in similarities.items()}
        else:
            percentages = {color: 100.0 / len(self.color_names) 
                          for color in self.color_names}
        
        return percentages
    
    def _calculate_delta_e(self, lab1: np.ndarray, lab2: np.ndarray) -> float:
        """
        Tính Delta E (CIE76) - khoảng cách màu sắc
        
        Args:
            lab1, lab2: Giá trị Lab của hai màu
            
        Returns:
            Khoảng cách Delta E
        """
        delta_l = lab1[0] - lab2[0]
        delta_a = lab1[1] - lab2[1]
        delta_b = lab1[2] - lab2[2]
        
        delta_e = np.sqrt(delta_l**2 + delta_a**2 + delta_b**2)
        return delta_e
    
    def analyze_color_by_hsv(self, rgb_values: Tuple[int, int, int]) -> Dict[str, float]:
        """
        Phân tích màu dựa trên HSV ranges
        
        Args:
            rgb_values: Giá trị RGB
            
        Returns:
            Dictionary chứa tỉ lệ tương ứng với mỗi màu cơ bản
        """
        # Convert RGB to HSV
        rgb_array = np.uint8([[rgb_values]])
        hsv = cv2.cvtColor(rgb_array, cv2.COLOR_RGB2HSV)[0][0]
        h, s, v = hsv[0], hsv[1], hsv[2]
        
        matches = {}
        
        for color_name, ranges in self.hsv_ranges.items():
            match_score = 0
            
            # Some colors have multiple ranges (like red)
            if len(ranges) == 4:  # Two ranges
                lower1, upper1, lower2, upper2 = ranges
                if (lower1[0] <= h <= upper1[0] and lower1[1] <= s <= upper1[1] and lower1[2] <= v <= upper1[2]) or \
                   (lower2[0] <= h <= upper2[0] and lower2[1] <= s <= upper2[1] and lower2[2] <= v <= upper2[2]):
                    match_score = 1.0
            else:  # Single range
                lower, upper = ranges
                if lower[0] <= h <= upper[0] and lower[1] <= s <= upper[1] and lower[2] <= v <= upper[2]:
                    match_score = 1.0
            
            matches[color_name] = match_score
        
        # If no exact match, calculate proximity
        if sum(matches.values()) == 0:
            return self._calculate_hsv_proximity(hsv)
        
        # Normalize to percentages
        total_matches = sum(matches.values())
        if total_matches > 0:
            percentages = {color: (match / total_matches) * 100 
                          for color, match in matches.items()}
        else:
            percentages = {color: 0.0 for color in self.color_names}
        
        return percentages
    
    def _calculate_hsv_proximity(self, hsv: np.ndarray) -> Dict[str, float]:
        """Tính độ gần gũi khi không có match chính xác"""
        # Simple proximity calculation based on hue primarily
        h, s, v = hsv[0], hsv[1], hsv[2]
        
        proximities = {}
        
        # Define center hues for each color
        center_hues = {
            "Đỏ": 0, "Cam Neon": 10, "Vàng Kim": 45, "Vàng Chanh": 55, "Vàng Neon": 60,
            "Xanh Neon": 35, "Xanh Lá": 60, "Xanh Lam Neon": 90, "Xanh Biển Sâu": 100,
            "Xanh Dương": 120, "Tím Neon": 130, "Tím": 145, "Hồng Neon": 155
        }
        
        for color_name, center_hue in center_hues.items():
            # Calculate hue distance (circular)
            hue_dist = min(abs(h - center_hue), 180 - abs(h - center_hue))
            proximity = max(0, 60 - hue_dist) / 60.0  # Max distance = 60
            proximities[color_name] = proximity
        
        # Handle achromatic colors (low saturation)
        if s < 30:
            if v < 50:
                proximities["Đen"] = 1.0
            elif v > 200:
                proximities["Trắng"] = 1.0
            else:
                proximities["Xám"] = 1.0
        
        # Brown is special case
        if 8 <= h <= 20 and s > 50 and 20 <= v <= 200:
            proximities["Nâu"] = 0.8
        
        return proximities


class ColorAnalysisEngine:
    """
    Engine chính để phân tích màu sắc
    """
    
    def __init__(self, model_path: Optional[str] = None):
        self.traditional_analyzer = TraditionalColorAnalyzer()
        self.deep_analyzer = None
        
        # Load deep learning model if available
        if model_path and os.path.exists(model_path):
            self.load_deep_model(model_path)
        else:
            # Create a basic model for now
            self.deep_analyzer = DeepColorAnalyzer()
    
    def load_deep_model(self, model_path: str):
        """Load trained deep learning model"""
        try:
            self.deep_analyzer = DeepColorAnalyzer()
            self.deep_analyzer.load_state_dict(torch.load(model_path, map_location='cpu'))
            self.deep_analyzer.eval()
            print(f"✓ Loaded deep learning model from {model_path}")
        except Exception as e:
            print(f"✗ Failed to load model: {e}")
            self.deep_analyzer = DeepColorAnalyzer()
    
    def analyze_color(self, rgb_values: Tuple[int, int, int], 
                     lab_values: Tuple[float, float, float],
                     method: str = "combined") -> ColorPrediction:
        """
        Phân tích màu và trả về tỉ lệ 12 màu cơ bản
        
        Args:
            rgb_values: Giá trị RGB
            lab_values: Giá trị Lab
            method: "traditional", "deep", or "combined"
            
        Returns:
            ColorPrediction object
        """
        
        if method == "traditional":
            # Use traditional color analysis
            lab_percentages = self.traditional_analyzer.analyze_color_by_distance(lab_values)
            hsv_percentages = self.traditional_analyzer.analyze_color_by_hsv(rgb_values)
            
            # Combine Lab and HSV results
            combined_percentages = {}
            for color in self.traditional_analyzer.color_names:
                lab_score = lab_percentages.get(color, 0)
                hsv_score = hsv_percentages.get(color, 0)
                # Weight Lab more heavily as it's more perceptually accurate
                combined_percentages[color] = (lab_score * 0.7) + (hsv_score * 0.3)
        
        elif method == "deep" and self.deep_analyzer:
            # Use deep learning model
            features = self.deep_analyzer.extract_features(rgb_values, lab_values)
            features_tensor = torch.FloatTensor(features).unsqueeze(0)
            
            with torch.no_grad():
                predictions = self.deep_analyzer(features_tensor)
                percentages_array = predictions.numpy()[0] * 100
            
            combined_percentages = {
                color: float(percentages_array[i]) 
                for i, color in enumerate(self.deep_analyzer.color_names)
            }
        
        else:  # combined method
            # Use both traditional and deep learning, then average
            lab_percentages = self.traditional_analyzer.analyze_color_by_distance(lab_values)
            
            if self.deep_analyzer:
                try:
                    features = self.deep_analyzer.extract_features(rgb_values, lab_values)
                    features_tensor = torch.FloatTensor(features).unsqueeze(0)
                    
                    with torch.no_grad():
                        predictions = self.deep_analyzer(features_tensor)
                        deep_percentages_array = predictions.numpy()[0] * 100
                    
                    deep_percentages = {
                        color: float(deep_percentages_array[i]) 
                        for i, color in enumerate(self.deep_analyzer.color_names)
                    }
                    
                    # Combine traditional and deep learning results
                    combined_percentages = {}
                    for color in self.traditional_analyzer.color_names:
                        traditional_score = lab_percentages.get(color, 0)
                        deep_score = deep_percentages.get(color, 0)
                        combined_percentages[color] = (traditional_score * 0.4) + (deep_score * 0.6)
                        
                except Exception as e:
                    print(f"Deep learning analysis failed: {e}")
                    combined_percentages = lab_percentages
            else:
                combined_percentages = lab_percentages
        
        # Find dominant color
        dominant_color = max(combined_percentages, key=combined_percentages.get)
        confidence = combined_percentages[dominant_color] / 100.0
        
        # Sort colors by percentage
        sorted_colors = dict(sorted(combined_percentages.items(), 
                                  key=lambda x: x[1], reverse=True))
        
        return ColorPrediction(
            primary_colors=sorted_colors,
            dominant_color=dominant_color,
            confidence=confidence,
            rgb_values=rgb_values,
            lab_values=lab_values
        )
    
    def get_mixing_formula(self, color_prediction: ColorPrediction) -> Dict[str, int]:
        """
        Tạo công thức pha màu dựa trên phân tích (tỉ lệ dạng số phần)

        Args:
            color_prediction: Kết quả phân tích màu

        Returns:
            Dictionary chứa tỉ lệ pha màu dạng số nguyên (vd: {color: parts})
        """
        # Filter out colors with very low percentages
        significant_colors = {
            color: percentage
            for color, percentage in color_prediction.primary_colors.items()
            if percentage > 5.0  # Only include colors > 5%
        }

        if not significant_colors:
            # If no significant colors, use the dominant one
            significant_colors = {
                color_prediction.dominant_color: 100.0
            }

        # Convert percentages to ratios by scaling to integers
        # Find a common denominator to convert to integers
        # Use multiplier to avoid floating point precision issues
        multiplier = 1000
        ratios = {color: int(percentage * multiplier) for color, percentage in significant_colors.items()}

        # Find GCD of all ratios
        import math
        gcd_value = math.gcd(*ratios.values())

        # Simplify ratios
        simplified_ratios = {color: ratio // gcd_value for color, ratio in ratios.items()}

        return simplified_ratios


# Global instance
color_engine = ColorAnalysisEngine()