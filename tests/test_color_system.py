"""
Unit tests for the color recognition and mixing system
"""

import unittest
import numpy as np
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils import ColorSpaceConverter, ColorDifferenceCalculator, ImageProcessor
from preprocessing import CameraCalibrator, ColorChecker
from color_recognition import SVMColorClassifier, ColorFeatureExtractor
from mixing_formula import KubelkaMunkModel, MixingOptimizer, create_standard_pigments


class TestColorSpaceConverter(unittest.TestCase):
    """Test color space conversion functions"""
    
    def test_rgb_to_lab_conversion(self):
        """Test RGB to Lab conversion"""
        # Test white color
        white_rgb = np.array([255, 255, 255])
        white_lab = ColorSpaceConverter.rgb_to_lab(white_rgb)
        
        # Lab white should be approximately [100, 0, 0]
        self.assertAlmostEqual(white_lab[0], 100, delta=5)
        self.assertAlmostEqual(white_lab[1], 0, delta=5)
        self.assertAlmostEqual(white_lab[2], 0, delta=5)
    
    def test_lab_to_rgb_conversion(self):
        """Test Lab to RGB conversion"""
        # Test round trip conversion
        original_rgb = np.array([128, 64, 192])
        lab = ColorSpaceConverter.rgb_to_lab(original_rgb)
        converted_rgb = ColorSpaceConverter.lab_to_rgb(lab)
        
        # Should be close to original (within tolerance for conversion)
        np.testing.assert_allclose(original_rgb, converted_rgb, atol=10)
    
    def test_rgb_to_hsv_conversion(self):
        """Test RGB to HSV conversion"""
        red_rgb = np.array([255, 0, 0])
        red_hsv = ColorSpaceConverter.rgb_to_hsv(red_rgb)
        
        # Red should have hue ~0, saturation ~255, value ~255
        self.assertAlmostEqual(red_hsv[0], 0, delta=5)
        self.assertAlmostEqual(red_hsv[1], 255, delta=5)
        self.assertAlmostEqual(red_hsv[2], 255, delta=5)


class TestColorDifferenceCalculator(unittest.TestCase):
    """Test color difference calculations"""
    
    def test_delta_e_cie76_identical_colors(self):
        """Test ΔE calculation for identical colors"""
        color = np.array([50, 10, -20])
        delta_e = ColorDifferenceCalculator.delta_e_cie76(color, color)
        self.assertAlmostEqual(delta_e, 0, delta=1e-6)
    
    def test_delta_e_cie76_different_colors(self):
        """Test ΔE calculation for different colors"""
        color1 = np.array([50, 0, 0])
        color2 = np.array([60, 10, 10])
        delta_e = ColorDifferenceCalculator.delta_e_cie76(color1, color2)
        
        # Should be greater than 0
        self.assertGreater(delta_e, 0)
        # Should be reasonable value
        self.assertLess(delta_e, 100)
    
    def test_delta_e_ciede2000(self):
        """Test CIEDE2000 ΔE calculation"""
        color1 = np.array([50, 0, 0])
        color2 = np.array([52, 2, 2])
        delta_e = ColorDifferenceCalculator.delta_e_ciede2000(color1, color2)
        
        # Should be small for similar colors
        self.assertGreater(delta_e, 0)
        self.assertLess(delta_e, 10)


class TestCameraCalibrator(unittest.TestCase):
    """Test camera calibration functionality"""
    
    def test_calibrator_initialization(self):
        """Test calibrator can be initialized"""
        calibrator = CameraCalibrator(method='linear')
        self.assertEqual(calibrator.method, 'linear')
        self.assertFalse(calibrator.is_calibrated)
    
    def test_color_checker_creation(self):
        """Test color checker initialization"""
        checker = ColorChecker()
        self.assertIsNotNone(checker.STANDARD_LAB_VALUES)
        self.assertEqual(len(checker.STANDARD_LAB_VALUES), 24)


class TestColorFeatureExtractor(unittest.TestCase):
    """Test feature extraction for color recognition"""
    
    def test_basic_feature_extraction(self):
        """Test basic feature extraction"""
        # Create test image
        test_image = np.full((50, 50, 3), [128, 64, 192], dtype=np.uint8)
        
        features = ColorFeatureExtractor.extract_basic_features(test_image)
        
        # Should return feature vector
        self.assertIsInstance(features, np.ndarray)
        # Should have expected number of features (RGB, HSV, Lab means and stds)
        self.assertEqual(len(features), 18)  # 3*2 + 3*2 + 3*2
    
    def test_histogram_feature_extraction(self):
        """Test histogram feature extraction"""
        test_image = np.random.randint(0, 256, (32, 32, 3), dtype=np.uint8)
        
        features = ColorFeatureExtractor.extract_histogram_features(test_image, bins=16)
        
        # Should return feature vector
        self.assertIsInstance(features, np.ndarray)
        # Should have expected number of features (RGB + HSV histograms)
        self.assertEqual(len(features), 16*6)  # 16 bins * 6 channels


class TestKubelkaMunkModel(unittest.TestCase):
    """Test Kubelka-Munk color mixing model"""
    
    def setUp(self):
        """Set up test model with standard pigments"""
        self.km_model = KubelkaMunkModel()
        self.pigments = create_standard_pigments()
        
        for pigment in self.pigments:
            self.km_model.add_pigment(pigment)
    
    def test_model_initialization(self):
        """Test model can be initialized"""
        self.assertIsNotNone(self.km_model.wavelengths)
        self.assertGreater(len(self.km_model.pigments), 0)
    
    def test_pigment_addition(self):
        """Test pigments can be added to model"""
        initial_count = len(self.km_model.pigments)
        
        # Create a test pigment
        from mixing_formula import Pigment
        test_pigment = Pigment(
            name="Test_Pigment",
            cost_per_unit=1.0,
            density=1.0,
            absorption_spectrum=np.ones(len(self.km_model.wavelengths)),
            scattering_spectrum=np.ones(len(self.km_model.wavelengths)),
            wavelengths=self.km_model.wavelengths.copy()
        )
        
        self.km_model.add_pigment(test_pigment)
        self.assertEqual(len(self.km_model.pigments), initial_count + 1)
    
    def test_color_prediction(self):
        """Test color prediction from concentrations"""
        # Test mixture
        concentrations = {
            'Titanium_White': 0.5,
            'Carbon_Black': 0.1,
            'Chrome_Yellow': 0.0,
            'Ultramarine_Blue': 0.0,
            'Cadmium_Red': 0.0
        }
        
        predicted_lab = self.km_model.predict_color(concentrations)
        
        # Should return valid Lab color
        self.assertIsInstance(predicted_lab, np.ndarray)
        self.assertEqual(len(predicted_lab), 3)
        
        # L should be in reasonable range
        self.assertGreaterEqual(predicted_lab[0], 0)
        self.assertLessEqual(predicted_lab[0], 100)


class TestMixingOptimizer(unittest.TestCase):
    """Test mixing formula optimization"""
    
    def setUp(self):
        """Set up test optimizer"""
        km_model = KubelkaMunkModel()
        pigments = create_standard_pigments()
        
        for pigment in pigments:
            km_model.add_pigment(pigment)
            
        self.optimizer = MixingOptimizer(km_model)
    
    def test_optimizer_initialization(self):
        """Test optimizer can be initialized"""
        self.assertIsNotNone(self.optimizer.km_model)
        self.assertGreater(len(self.optimizer.pigment_names), 0)
    
    def test_optimization(self):
        """Test formula optimization"""
        # Target: light gray
        target_lab = np.array([70, 0, 0])
        
        result = self.optimizer.optimize_formula(
            target_lab,
            method='minimize',
            max_iterations=100
        )
        
        # Should return result dictionary
        self.assertIsInstance(result, dict)
        self.assertIn('concentrations', result)
        self.assertIn('predicted_lab', result)
        self.assertIn('delta_e', result)
        self.assertIn('success', result)
        
        # ΔE should be reasonable
        self.assertGreater(result['delta_e'], 0)
        self.assertLess(result['delta_e'], 50)  # Should not be terrible


class TestImageProcessor(unittest.TestCase):
    """Test image processing utilities"""
    
    def test_create_color_swatch(self):
        """Test color swatch creation"""
        color = [255, 128, 64]
        swatch = ImageProcessor.create_color_swatch(color, size=(50, 50))
        
        self.assertEqual(swatch.shape, (50, 50, 3))
        np.testing.assert_array_equal(swatch[0, 0], color)
    
    def test_extract_color_patch(self):
        """Test color patch extraction"""
        # Create test image with known color
        test_color = [100, 150, 200]
        test_image = np.full((100, 100, 3), test_color, dtype=np.uint8)
        
        # Extract patch
        bbox = (25, 25, 50, 50)
        extracted_color = ImageProcessor.extract_color_patch(test_image, bbox)
        
        np.testing.assert_array_almost_equal(extracted_color, test_color)


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)