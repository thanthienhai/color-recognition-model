"""
Training data generator for CNN color ratio model.
Generates synthetic color images with known mixing ratios.
"""

import logging
import random
from typing import Dict, Tuple, List, Optional
from pathlib import Path
from datetime import datetime
import json

import numpy as np
import cv2

try:
    import h5py
    H5PY_AVAILABLE = True
except ImportError:
    H5PY_AVAILABLE = False
    h5py = None

from dl_config import BASE_COLORS, DATA_GEN_CONFIG

logger = logging.getLogger(__name__)


class ColorDataGenerator:
    """
    Generates synthetic training data for color ratio prediction.
    
    Creates images by mathematically mixing base colors with known ratios,
    then applies realistic augmentations to simulate real-world conditions.
    """
    
    def __init__(
        self,
        base_colors: Optional[Dict[str, Tuple[float, float, float]]] = None,
        image_size: Tuple[int, int] = (224, 224),
        min_colors: int = 2,
        max_colors: int = 5
    ):
        """
        Initialize the data generator.
        
        Args:
            base_colors: Dictionary mapping color names to Lab values
            image_size: Output image size (height, width)
            min_colors: Minimum number of colors to mix
            max_colors: Maximum number of colors to mix
        """
        self.base_colors = base_colors or BASE_COLORS
        self.color_names = list(self.base_colors.keys())
        self.num_colors = len(self.color_names)
        self.image_size = image_size
        self.min_colors = min_colors
        self.max_colors = max_colors
        
        # Convert Lab colors to RGB for image generation
        self.base_colors_rgb = self._convert_lab_to_rgb_dict(self.base_colors)
        
        logger.info(f"ColorDataGenerator initialized with {self.num_colors} base colors")
    
    def _convert_lab_to_rgb_dict(
        self, lab_colors: Dict[str, Tuple[float, float, float]]
    ) -> Dict[str, Tuple[int, int, int]]:
        """
        Convert Lab color dictionary to RGB.
        
        Args:
            lab_colors: Dictionary of color names to Lab values
            
        Returns:
            Dictionary of color names to RGB values (0-255)
        """
        rgb_colors = {}
        
        for name, (L, a, b) in lab_colors.items():
            # Create Lab image
            lab_img = np.array([[[L, a, b]]], dtype=np.float32)
            
            # Convert to RGB
            rgb_img = cv2.cvtColor(lab_img, cv2.COLOR_LAB2RGB)
            
            # Extract RGB values and scale to 0-255
            r, g, b = rgb_img[0, 0]
            rgb_colors[name] = (int(r * 255), int(g * 255), int(b * 255))
        
        return rgb_colors
    
    def _select_random_colors(self) -> Tuple[List[str], np.ndarray]:
        """
        Select random colors and generate mixing ratios.
        
        Returns:
            Tuple of (selected color names, ratios array of shape (num_colors,))
        """
        # Select number of colors to mix
        num_selected = random.randint(self.min_colors, self.max_colors)
        
        # Select random colors
        selected_names = random.sample(self.color_names, num_selected)
        
        # Generate random ratios that sum to 1.0
        raw_ratios = np.random.dirichlet(np.ones(num_selected))
        
        # Create full ratio array (16 colors)
        ratios = np.zeros(self.num_colors, dtype=np.float32)
        for i, name in enumerate(selected_names):
            color_idx = self.color_names.index(name)
            ratios[color_idx] = raw_ratios[i]
        
        return selected_names, ratios
    
    def _mix_colors_rgb(
        self, selected_names: List[str], ratios: np.ndarray
    ) -> Tuple[int, int, int]:
        """
        Mix colors in RGB space using ratios.
        
        Args:
            selected_names: List of color names to mix
            ratios: Full ratios array (16 values)
            
        Returns:
            Mixed RGB color (r, g, b) in range 0-255
        """
        mixed_r, mixed_g, mixed_b = 0.0, 0.0, 0.0
        
        for name in selected_names:
            color_idx = self.color_names.index(name)
            ratio = ratios[color_idx]
            
            if ratio > 0:
                r, g, b = self.base_colors_rgb[name]
                mixed_r += r * ratio
                mixed_g += g * ratio
                mixed_b += b * ratio
        
        return (int(mixed_r), int(mixed_g), int(mixed_b))
    
    def _create_solid_color_image(
        self, rgb_color: Tuple[int, int, int]
    ) -> np.ndarray:
        """
        Create a solid color image.
        
        Args:
            rgb_color: RGB color tuple (r, g, b)
            
        Returns:
            Image array of shape (height, width, 3)
        """
        height, width = self.image_size
        image = np.full((height, width, 3), rgb_color, dtype=np.uint8)
        return image
    
    def generate_sample(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generate a single training sample (image, ratios).
        
        Returns:
            Tuple of (image array, ratios array)
            - image: RGB image of shape (height, width, 3), dtype uint8
            - ratios: Mixing ratios of shape (num_colors,), dtype float32, sum=1.0
        """
        # Select colors and generate ratios
        selected_names, ratios = self._select_random_colors()
        
        # Mix colors to get target RGB
        mixed_rgb = self._mix_colors_rgb(selected_names, ratios)
        
        # Create solid color image
        image = self._create_solid_color_image(mixed_rgb)
        
        return image, ratios
    
    def generate_batch(self, batch_size: int) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generate a batch of training samples.
        
        Args:
            batch_size: Number of samples to generate
            
        Returns:
            Tuple of (images array, ratios array)
            - images: Shape (batch_size, height, width, 3)
            - ratios: Shape (batch_size, num_colors)
        """
        images = []
        ratios_list = []
        
        for _ in range(batch_size):
            image, ratios = self.generate_sample()
            images.append(image)
            ratios_list.append(ratios)
        
        images_array = np.array(images, dtype=np.uint8)
        ratios_array = np.array(ratios_list, dtype=np.float32)
        
        return images_array, ratios_array
    
    def generate_dataset(
        self,
        num_samples: int,
        save_path: str,
        apply_augmentation: bool = False
    ) -> None:
        """
        Generate a complete dataset and save to HDF5 file.
        
        Args:
            num_samples: Number of samples to generate
            save_path: Path to save HDF5 file
            apply_augmentation: Whether to apply augmentations
        """
        if not H5PY_AVAILABLE:
            raise ImportError("h5py is required for dataset generation. Install with: pip install h5py")
        
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Generating dataset with {num_samples} samples...")
        
        # Generate all samples
        images_list = []
        ratios_list = []
        
        for i in range(num_samples):
            if (i + 1) % 1000 == 0:
                logger.info(f"Generated {i + 1}/{num_samples} samples")
            
            image, ratios = self.generate_sample()
            
            # Apply augmentation if requested
            if apply_augmentation:
                image = self.apply_augmentations(image)
            
            images_list.append(image)
            ratios_list.append(ratios)
        
        # Convert to arrays
        images_array = np.array(images_list, dtype=np.uint8)
        ratios_array = np.array(ratios_list, dtype=np.float32)
        
        # Save to HDF5
        with h5py.File(save_path, 'w') as f:
            f.create_dataset('images', data=images_array, compression='gzip')
            f.create_dataset('ratios', data=ratios_array, compression='gzip')
            
            # Save metadata
            metadata = {
                'num_samples': num_samples,
                'image_size': self.image_size,
                'num_colors': self.num_colors,
                'color_names': self.color_names,
                'min_colors': self.min_colors,
                'max_colors': self.max_colors,
                'augmentation_applied': apply_augmentation,
                'generation_timestamp': datetime.now().isoformat(),
                'preprocessing_version': 'v2.0.0',  # NEW: Track preprocessing version
                'preprocessing_method': 'single_normalization_0_1',  # NEW: Document method
                'imagenet_normalization': False  # NEW: Explicitly state no ImageNet stats
            }
            f.attrs['metadata'] = json.dumps(metadata)
        
        logger.info(f"Dataset saved to {save_path}")
        logger.info(f"Images shape: {images_array.shape}")
        logger.info(f"Ratios shape: {ratios_array.shape}")
    
    def apply_augmentations(self, image: np.ndarray) -> np.ndarray:
        """
        Apply realistic augmentations to an image.
        
        Augmentations include:
        - Brightness variations
        - Contrast adjustments
        - Gaussian noise
        - Texture overlay
        - Shadow effects
        - Color temperature shifts
        
        Args:
            image: Input RGB image
            
        Returns:
            Augmented image
        """
        augmented = image.copy()
        
        # Get augmentation config
        aug_config = DATA_GEN_CONFIG.get('augmentation', {})
        
        # 1. Brightness variation (±30%)
        brightness_range = aug_config.get('brightness_range', (0.7, 1.3))
        brightness_factor = random.uniform(*brightness_range)
        augmented = self._adjust_brightness(augmented, brightness_factor)
        
        # 2. Contrast adjustment
        contrast_range = aug_config.get('contrast_range', (0.8, 1.2))
        contrast_factor = random.uniform(*contrast_range)
        augmented = self._adjust_contrast(augmented, contrast_factor)
        
        # 3. Gaussian noise
        noise_sigma_range = aug_config.get('noise_sigma_range', (5, 15))
        noise_sigma = random.uniform(*noise_sigma_range)
        augmented = self._add_gaussian_noise(augmented, noise_sigma)
        
        # 4. Texture overlay (20% opacity)
        if random.random() < 0.5:  # Apply texture 50% of the time
            texture_opacity = aug_config.get('texture_opacity', 0.2)
            augmented = self._add_texture(augmented, texture_opacity)
        
        # 5. Shadow effect
        if random.random() < 0.3:  # Apply shadow 30% of the time
            augmented = self._add_shadow(augmented)
        
        # 6. Color temperature shift (±500K)
        if random.random() < 0.4:  # Apply temp shift 40% of the time
            temp_shift = aug_config.get('color_temp_shift', 500)
            temp_delta = random.uniform(-temp_shift, temp_shift)
            augmented = self._adjust_color_temperature(augmented, temp_delta)
        
        return augmented
    
    def _adjust_brightness(self, image: np.ndarray, factor: float) -> np.ndarray:
        """
        Adjust image brightness.
        
        Args:
            image: Input image
            factor: Brightness factor (1.0 = no change, >1.0 = brighter, <1.0 = darker)
            
        Returns:
            Brightness-adjusted image
        """
        adjusted = image.astype(np.float32) * factor
        adjusted = np.clip(adjusted, 0, 255)
        return adjusted.astype(np.uint8)
    
    def _adjust_contrast(self, image: np.ndarray, factor: float) -> np.ndarray:
        """
        Adjust image contrast.
        
        Args:
            image: Input image
            factor: Contrast factor (1.0 = no change, >1.0 = more contrast)
            
        Returns:
            Contrast-adjusted image
        """
        # Convert to float
        img_float = image.astype(np.float32)
        
        # Calculate mean
        mean = np.mean(img_float)
        
        # Apply contrast adjustment
        adjusted = (img_float - mean) * factor + mean
        adjusted = np.clip(adjusted, 0, 255)
        
        return adjusted.astype(np.uint8)
    
    def _add_gaussian_noise(self, image: np.ndarray, sigma: float) -> np.ndarray:
        """
        Add Gaussian noise to image.
        
        Args:
            image: Input image
            sigma: Standard deviation of noise
            
        Returns:
            Noisy image
        """
        noise = np.random.normal(0, sigma, image.shape)
        noisy = image.astype(np.float32) + noise
        noisy = np.clip(noisy, 0, 255)
        return noisy.astype(np.uint8)
    
    def _add_texture(self, image: np.ndarray, opacity: float) -> np.ndarray:
        """
        Add texture overlay to simulate surface materials.
        
        Args:
            image: Input image
            opacity: Texture opacity (0.0 to 1.0)
            
        Returns:
            Image with texture overlay
        """
        height, width = image.shape[:2]
        
        # Generate random texture patterns
        texture_type = random.choice(['perlin', 'grain', 'canvas'])
        
        if texture_type == 'perlin':
            # Perlin-like noise using multiple frequencies
            texture = self._generate_perlin_texture(height, width)
        elif texture_type == 'grain':
            # Fine grain texture
            texture = np.random.randint(-20, 20, (height, width), dtype=np.int16)
        else:  # canvas
            # Canvas-like texture
            texture = self._generate_canvas_texture(height, width)
        
        # Apply texture with opacity
        textured = image.astype(np.float32)
        for c in range(3):
            textured[:, :, c] += texture * opacity
        
        textured = np.clip(textured, 0, 255)
        return textured.astype(np.uint8)
    
    def _generate_perlin_texture(self, height: int, width: int) -> np.ndarray:
        """Generate Perlin-like noise texture."""
        # Simple multi-scale noise
        texture = np.zeros((height, width), dtype=np.float32)
        
        for scale in [4, 8, 16, 32]:
            h_scaled = height // scale
            w_scaled = width // scale
            
            # Generate random noise at this scale
            noise = np.random.randn(h_scaled, w_scaled) * 30
            
            # Resize to full size
            noise_resized = cv2.resize(noise, (width, height), interpolation=cv2.INTER_LINEAR)
            texture += noise_resized / scale
        
        return texture
    
    def _generate_canvas_texture(self, height: int, width: int) -> np.ndarray:
        """Generate canvas-like texture."""
        # Create grid pattern
        texture = np.zeros((height, width), dtype=np.float32)
        
        # Add horizontal and vertical lines
        for i in range(0, height, 3):
            texture[i, :] = random.uniform(-10, 10)
        for j in range(0, width, 3):
            texture[:, j] = random.uniform(-10, 10)
        
        # Blur to smooth
        texture = cv2.GaussianBlur(texture, (5, 5), 1.0)
        
        return texture
    
    def _add_shadow(self, image: np.ndarray) -> np.ndarray:
        """
        Add shadow effect to image.
        
        Args:
            image: Input image
            
        Returns:
            Image with shadow
        """
        height, width = image.shape[:2]
        
        # Create gradient mask for shadow
        shadow_type = random.choice(['linear', 'radial', 'corner'])
        
        if shadow_type == 'linear':
            # Linear gradient shadow
            direction = random.choice(['horizontal', 'vertical'])
            if direction == 'horizontal':
                gradient = np.linspace(0.6, 1.0, width)
                mask = np.tile(gradient, (height, 1))
            else:
                gradient = np.linspace(0.6, 1.0, height)
                mask = np.tile(gradient.reshape(-1, 1), (1, width))
        
        elif shadow_type == 'radial':
            # Radial gradient (vignette)
            center_x, center_y = width // 2, height // 2
            y, x = np.ogrid[:height, :width]
            dist = np.sqrt((x - center_x)**2 + (y - center_y)**2)
            max_dist = np.sqrt(center_x**2 + center_y**2)
            mask = 1.0 - (dist / max_dist) * 0.4
        
        else:  # corner
            # Corner shadow
            corner = random.choice(['top-left', 'top-right', 'bottom-left', 'bottom-right'])
            y, x = np.ogrid[:height, :width]
            
            if corner == 'top-left':
                dist = np.sqrt(x**2 + y**2)
            elif corner == 'top-right':
                dist = np.sqrt((width - x)**2 + y**2)
            elif corner == 'bottom-left':
                dist = np.sqrt(x**2 + (height - y)**2)
            else:  # bottom-right
                dist = np.sqrt((width - x)**2 + (height - y)**2)
            
            max_dist = np.sqrt(width**2 + height**2)
            mask = 1.0 - (dist / max_dist) * 0.5
        
        # Apply shadow mask
        shadowed = image.astype(np.float32)
        for c in range(3):
            shadowed[:, :, c] *= mask
        
        shadowed = np.clip(shadowed, 0, 255)
        return shadowed.astype(np.uint8)
    
    def _adjust_color_temperature(self, image: np.ndarray, temp_delta: float) -> np.ndarray:
        """
        Adjust color temperature of image.
        
        Args:
            image: Input image
            temp_delta: Temperature shift in Kelvin (positive = warmer, negative = cooler)
            
        Returns:
            Temperature-adjusted image
        """
        # Simple color temperature adjustment
        # Positive delta = warmer (more red/yellow)
        # Negative delta = cooler (more blue)
        
        adjusted = image.astype(np.float32)
        
        # Normalize temp_delta to a factor
        factor = temp_delta / 1000.0  # -0.5 to +0.5 for ±500K
        
        if factor > 0:  # Warmer
            # Increase red, slightly increase green
            adjusted[:, :, 0] *= (1.0 + factor * 0.2)  # Red
            adjusted[:, :, 1] *= (1.0 + factor * 0.1)  # Green
            adjusted[:, :, 2] *= (1.0 - factor * 0.1)  # Blue (decrease)
        else:  # Cooler
            # Increase blue, decrease red
            adjusted[:, :, 0] *= (1.0 + factor * 0.2)  # Red (decrease)
            adjusted[:, :, 1] *= (1.0 + factor * 0.05)  # Green (slight decrease)
            adjusted[:, :, 2] *= (1.0 - factor * 0.2)  # Blue (increase)
        
        adjusted = np.clip(adjusted, 0, 255)
        return adjusted.astype(np.uint8)



class ColorRatioDataset:
    """
    PyTorch-compatible dataset for color ratio training.
    Loads data from HDF5 files generated by ColorDataGenerator.
    """
    
    def __init__(self, hdf5_path: str, transform=None):
        """
        Initialize dataset from HDF5 file.
        
        Args:
            hdf5_path: Path to HDF5 dataset file
            transform: Optional transform to apply to images
        """
        if not H5PY_AVAILABLE:
            raise ImportError("h5py is required. Install with: pip install h5py")
        
        self.hdf5_path = Path(hdf5_path)
        self.transform = transform
        
        # Load dataset
        with h5py.File(self.hdf5_path, 'r') as f:
            self.images = f['images'][:]
            self.ratios = f['ratios'][:]
            
            # Load metadata
            if 'metadata' in f.attrs:
                self.metadata = json.loads(f.attrs['metadata'])
            else:
                self.metadata = {}
        
        logger.info(f"Loaded dataset from {hdf5_path}")
        logger.info(f"Dataset size: {len(self.images)} samples")
    
    def __len__(self) -> int:
        """Return dataset size."""
        return len(self.images)
    
    def __getitem__(self, idx: int) -> Tuple[np.ndarray, np.ndarray]:
        """
        Get a single sample.
        
        IMPORTANT: This method performs SINGLE normalization to [0,1] range.
        No ImageNet statistics are applied. This matches the preprocessing
        used in CNNColorRatioModel.preprocess_image().
        
        Args:
            idx: Sample index
            
        Returns:
            Tuple of (image, ratios)
            - image: Normalized to [0,1], shape (3, 224, 224)
            - ratios: Shape (16,), sum=1.0
        """
        image = self.images[idx]
        ratios = self.ratios[idx]
        
        # Convert image to float32 and normalize to [0, 1] - SINGLE NORMALIZATION
        # This matches the preprocessing in CNNColorRatioModel.preprocess_image()
        image = image.astype(np.float32) / 255.0
        
        # Convert to CHW format (PyTorch expects channels first)
        image = np.transpose(image, (2, 0, 1))
        
        # Apply transform if provided
        if self.transform:
            image = self.transform(image)
        
        return image, ratios
    
    def get_batch(self, indices: List[int]) -> Tuple[np.ndarray, np.ndarray]:
        """
        Get a batch of samples.
        
        Args:
            indices: List of sample indices
            
        Returns:
            Tuple of (images array, ratios array)
        """
        images = self.images[indices]
        ratios = self.ratios[indices]
        
        return images, ratios


def create_train_val_test_datasets(
    num_train: int = 10000,
    num_val: int = 2000,
    num_test: int = 1000,
    output_dir: str = "data",
    apply_augmentation: bool = True
) -> Tuple[str, str, str]:
    """
    Create training, validation, and test datasets.
    
    Args:
        num_train: Number of training samples
        num_val: Number of validation samples
        num_test: Number of test samples
        output_dir: Output directory for datasets
        apply_augmentation: Whether to apply augmentations
        
    Returns:
        Tuple of (train_path, val_path, test_path)
    """
    output_dir = Path(output_dir)
    
    # Initialize generator
    generator = ColorDataGenerator()
    
    # Generate training set
    train_path = output_dir / "training" / "train_dataset.h5"
    logger.info("Generating training dataset...")
    generator.generate_dataset(num_train, str(train_path), apply_augmentation=apply_augmentation)
    
    # Generate validation set
    val_path = output_dir / "validation" / "val_dataset.h5"
    logger.info("Generating validation dataset...")
    generator.generate_dataset(num_val, str(val_path), apply_augmentation=False)
    
    # Generate test set
    test_path = output_dir / "test" / "test_dataset.h5"
    logger.info("Generating test dataset...")
    generator.generate_dataset(num_test, str(test_path), apply_augmentation=False)
    
    logger.info("All datasets generated successfully!")
    
    return str(train_path), str(val_path), str(test_path)
