"""
Advanced Color Analysis Module V2 - Upgraded for Better Accuracy
Phân tích màu nâng cao với CIEDE2000 và cải thiện thuật toán
"""

import numpy as np
import cv2
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import math


@dataclass
class ColorPrediction:
    """Kết quả dự đoán màu"""
    primary_colors: Dict[str, float]  # Tỉ lệ các màu cơ bản
    dominant_color: str              # Màu chính
    confidence: float                # Độ tin cậy
    rgb_values: Tuple[int, int, int] # Giá trị RGB
    lab_values: Tuple[float, float, float]  # Giá trị Lab
    delta_e_values: Optional[Dict[str, float]] = None  # Delta E to each color


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
            "Đen", "Trắng", "Vàng Chanh", "Đỏ", "Xanh Lá", "Xanh Biển Sâu",
            "Xanh Dương", "Tím", "Nâu", "Vàng Neon", "Xanh Neon",
            "Xanh Lam Neon", "Cam Neon", "Hồng Neon", "Tím Neon", "Vàng Kim"
        ]
        
        # Optimized LAB reference colors for 16 colors (validated and improved)
        self.reference_lab = {
            "Đen": np.array([15.0, 0.0, 0.0]),           # Near black (was 0)
            "Trắng": np.array([95.0, 0.0, 0.0]),         # Near white (was 100)
            "Vàng Chanh": np.array([95.0, -15.0, 90.0]), # Lemon yellow (improved)
            "Đỏ": np.array([53.0, 80.0, 67.0]),          # Pure red (validated)
            "Xanh Lá": np.array([46.0, -52.0, 50.0]),    # Green (improved)
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
    """
    
    def __init__(self):
        self.analyzer = ImprovedColorAnalyzer()
        self.delta_e_calculator = CIEDE2000Calculator()
    
    def analyze_color(self, rgb_values: Tuple[int, int, int], 
                     lab_values: Tuple[float, float, float],
                     method: str = "ciede2000") -> ColorPrediction:
        """
        Analyze color and return prediction
        
        Args:
            rgb_values: RGB values (0-255)
            lab_values: Lab values
            method: "ciede2000" (default) or "simple"
            
        Returns:
            ColorPrediction object
        """
        if method == "ciede2000":
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
        
        return ColorPrediction(
            primary_colors=sorted_colors,
            dominant_color=dominant_color,
            confidence=confidence,
            rgb_values=rgb_values,
            lab_values=lab_values,
            delta_e_values=delta_e_values
        )
    
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
        # Filter colors by significance (> 3%)
        significant_colors = {
            color: percentage
            for color, percentage in color_prediction.primary_colors.items()
            if percentage > 3.0
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
