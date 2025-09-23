"""
Color Recognition and Mixing System

A comprehensive system for automated color recognition and paint mixing formula calculation.
Combines computer vision, machine learning, and physical color models for industrial applications.

Main modules:
- preprocessing: Camera calibration and image preprocessing
- color_recognition: SVM and deep learning-based color classification  
- mixing_formula: Kubelka-Munk physical color mixing models
- optimization: Multi-objective optimization algorithms
- utils: Common utilities and helper functions
- app: Main application interface

Example usage:
    from src.app import ColorRecognitionPipeline
    
    pipeline = ColorRecognitionPipeline()
    result = pipeline.process_single_image('path/to/image.jpg', 'output/dir/')
"""

__version__ = "1.0.0"
__author__ = "Color Recognition Team"
__email__ = "contact@colorrecognition.com"

# Version information
VERSION_INFO = {
    'major': 1,
    'minor': 0,
    'patch': 0,
    'release': 'stable'
}

def get_version():
    """Get version string"""
    return __version__

def get_version_info():
    """Get detailed version information"""
    return VERSION_INFO