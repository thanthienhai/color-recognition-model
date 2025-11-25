"""
Device detection and configuration utilities for deep learning models.
Handles GPU/CPU detection and provides device management for PyTorch.
"""

import logging
from typing import Optional, Any, Union

try:
    import torch
    TORCH_AVAILABLE = True
    TorchDevice = torch.device
except ImportError:
    TORCH_AVAILABLE = False
    torch = None
    TorchDevice = Any

logger = logging.getLogger(__name__)


class DeviceManager:
    """
    Manages device selection and configuration for deep learning models.
    Automatically detects GPU availability and provides fallback to CPU.
    """
    
    def __init__(self, device: str = "auto"):
        """
        Initialize device manager.
        
        Args:
            device: Device selection - "auto", "cuda", "mps", or "cpu"
                   "auto" will automatically select the best available device
        """
        if not TORCH_AVAILABLE:
            logger.warning("PyTorch not available, device management disabled")
            self._device = None
            self._device_name = "cpu"
            return
        
        self._device = self._detect_device(device)
        self._device_name = str(self._device)
        self._log_device_info()
    
    def _detect_device(self, device: str) -> Union[TorchDevice, Any]:
        """
        Detect and return the appropriate device.
        
        Args:
            device: Requested device type
            
        Returns:
            torch.device object
        """
        if device == "auto":
            # Check for CUDA (NVIDIA GPU)
            if torch.cuda.is_available():
                return torch.device("cuda")
            
            # Check for MPS (Apple Silicon GPU)
            if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
                return torch.device("mps")
            
            # Fallback to CPU
            return torch.device("cpu")
        
        elif device == "cuda":
            if torch.cuda.is_available():
                return torch.device("cuda")
            else:
                logger.warning("CUDA requested but not available, falling back to CPU")
                return torch.device("cpu")
        
        elif device == "mps":
            if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
                return torch.device("mps")
            else:
                logger.warning("MPS requested but not available, falling back to CPU")
                return torch.device("cpu")
        
        else:
            return torch.device("cpu")
    
    def _log_device_info(self):
        """Log information about the selected device."""
        if not TORCH_AVAILABLE:
            return
        
        device_type = self._device.type
        
        if device_type == "cuda":
            gpu_name = torch.cuda.get_device_name(0)
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1e9
            logger.info(f"Using CUDA device: {gpu_name} ({gpu_memory:.2f} GB)")
        
        elif device_type == "mps":
            logger.info("Using Apple Silicon MPS device")
        
        else:
            logger.info("Using CPU device")
    
    @property
    def device(self) -> Optional[Union[TorchDevice, Any]]:
        """Get the current device."""
        return self._device
    
    @property
    def device_name(self) -> str:
        """Get the device name as string."""
        return self._device_name
    
    def is_gpu_available(self) -> bool:
        """Check if GPU (CUDA or MPS) is available."""
        if not TORCH_AVAILABLE:
            return False
        
        return (torch.cuda.is_available() or 
                (hasattr(torch.backends, "mps") and torch.backends.mps.is_available()))
    
    def get_device_info(self) -> dict:
        """
        Get detailed device information.
        
        Returns:
            Dictionary with device information
        """
        if not TORCH_AVAILABLE:
            return {
                "torch_available": False,
                "device": "cpu",
                "gpu_available": False
            }
        
        info = {
            "torch_available": True,
            "device": self._device_name,
            "gpu_available": self.is_gpu_available()
        }
        
        if self._device.type == "cuda":
            info.update({
                "gpu_name": torch.cuda.get_device_name(0),
                "gpu_memory_gb": torch.cuda.get_device_properties(0).total_memory / 1e9,
                "cuda_version": torch.version.cuda
            })
        
        elif self._device.type == "mps":
            info.update({
                "gpu_name": "Apple Silicon GPU",
                "backend": "MPS"
            })
        
        return info
    
    def move_to_device(self, tensor_or_model):
        """
        Move a tensor or model to the configured device.
        
        Args:
            tensor_or_model: PyTorch tensor or model
            
        Returns:
            Tensor or model on the configured device
        """
        if not TORCH_AVAILABLE or self._device is None:
            return tensor_or_model
        
        return tensor_or_model.to(self._device)
    
    def empty_cache(self):
        """Empty GPU cache if using CUDA."""
        if TORCH_AVAILABLE and self._device.type == "cuda":
            torch.cuda.empty_cache()


# Global device manager instance
_global_device_manager: Optional[DeviceManager] = None


def get_device_manager(device: str = "auto") -> DeviceManager:
    """
    Get or create the global device manager instance.
    
    Args:
        device: Device selection (only used on first call)
        
    Returns:
        DeviceManager instance
    """
    global _global_device_manager
    
    if _global_device_manager is None:
        _global_device_manager = DeviceManager(device)
    
    return _global_device_manager


def get_device(device: str = "auto") -> Optional[Union[TorchDevice, Any]]:
    """
    Get the appropriate device for PyTorch operations.
    
    Args:
        device: Device selection - "auto", "cuda", "mps", or "cpu"
        
    Returns:
        torch.device object or None if PyTorch not available
    """
    manager = get_device_manager(device)
    return manager.device


def is_gpu_available() -> bool:
    """
    Check if GPU is available for PyTorch operations.
    
    Returns:
        True if GPU (CUDA or MPS) is available
    """
    manager = get_device_manager()
    return manager.is_gpu_available()


def get_device_info() -> dict:
    """
    Get detailed information about the current device.
    
    Returns:
        Dictionary with device information
    """
    manager = get_device_manager()
    return manager.get_device_info()
