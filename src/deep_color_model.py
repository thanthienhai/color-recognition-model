"""
CNN-based deep learning model for color ratio prediction.
Predicts mixing ratios for 16 base colors from RGB images.
"""

import logging
from pathlib import Path
from typing import Optional, Dict, Tuple, List, Union
import numpy as np

try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    torch = None
    nn = None
    F = None

from device_utils import get_device_manager
from dl_config import MODEL_CONFIG, IMAGENET_MEAN, IMAGENET_STD

logger = logging.getLogger(__name__)

# Import training logger
try:
    from training_logger import TrainingLogger
    TRAINING_LOGGER_AVAILABLE = True
except ImportError:
    TRAINING_LOGGER_AVAILABLE = False
    TrainingLogger = None


if TORCH_AVAILABLE:
    
    class CNNColorRatioNetwork(nn.Module):
        """
        Convolutional Neural Network for predicting color mixing ratios.
        
        Architecture:
            - 4 Convolutional blocks with batch normalization and max pooling
            - 2 Fully connected layers with dropout
            - Softmax output layer for 16 base color ratios
        
        Input: RGB image (224x224x3)
        Output: 16 ratios summing to 1.0 (100%)
        """
        
        def __init__(
            self,
            num_colors: int = 16,
            conv_filters: List[int] = None,
            dense_units: List[int] = None,
            dropout_rates: List[float] = None
        ):
            """
            Initialize the CNN architecture.
            
            Args:
                num_colors: Number of base colors to predict (default: 16)
                conv_filters: List of filter counts for conv layers
                dense_units: List of neuron counts for dense layers
                dropout_rates: List of dropout rates for dense layers
            """
            super(CNNColorRatioNetwork, self).__init__()
            
            # Use config defaults if not provided
            conv_filters = conv_filters or MODEL_CONFIG["conv_filters"]
            dense_units = dense_units or MODEL_CONFIG["dense_units"]
            dropout_rates = dropout_rates or MODEL_CONFIG["dropout_rates"]
            
            self.num_colors = num_colors
            
            # Convolutional Block 1: 3 -> 32 filters
            self.conv1 = nn.Conv2d(3, conv_filters[0], kernel_size=3, padding=1)
            self.bn1 = nn.BatchNorm2d(conv_filters[0])
            self.pool1 = nn.MaxPool2d(kernel_size=2, stride=2)
            
            # Convolutional Block 2: 32 -> 64 filters
            self.conv2 = nn.Conv2d(conv_filters[0], conv_filters[1], kernel_size=3, padding=1)
            self.bn2 = nn.BatchNorm2d(conv_filters[1])
            self.pool2 = nn.MaxPool2d(kernel_size=2, stride=2)
            
            # Convolutional Block 3: 64 -> 128 filters
            self.conv3 = nn.Conv2d(conv_filters[1], conv_filters[2], kernel_size=3, padding=1)
            self.bn3 = nn.BatchNorm2d(conv_filters[2])
            self.pool3 = nn.MaxPool2d(kernel_size=2, stride=2)
            
            # Convolutional Block 4: 128 -> 256 filters
            self.conv4 = nn.Conv2d(conv_filters[2], conv_filters[3], kernel_size=3, padding=1)
            self.bn4 = nn.BatchNorm2d(conv_filters[3])
            self.pool4 = nn.MaxPool2d(kernel_size=2, stride=2)
            
            # Calculate flattened size after conv layers
            # Input: 224x224 -> after 4 pooling layers: 14x14
            self.flatten_size = conv_filters[3] * 14 * 14
            
            # Fully Connected Layers
            self.fc1 = nn.Linear(self.flatten_size, dense_units[0])
            self.dropout1 = nn.Dropout(dropout_rates[0])
            
            self.fc2 = nn.Linear(dense_units[0], dense_units[1])
            self.dropout2 = nn.Dropout(dropout_rates[1])
            
            # Output layer with softmax
            self.fc3 = nn.Linear(dense_units[1], num_colors)
        
        def forward(self, x: torch.Tensor) -> torch.Tensor:
            """
            Forward pass through the network.
            
            Args:
                x: Input tensor of shape (batch_size, 3, 224, 224)
                
            Returns:
                Output tensor of shape (batch_size, num_colors) with softmax activation
            """
            # Conv Block 1
            x = self.conv1(x)
            x = self.bn1(x)
            x = F.relu(x)
            x = self.pool1(x)
            
            # Conv Block 2
            x = self.conv2(x)
            x = self.bn2(x)
            x = F.relu(x)
            x = self.pool2(x)
            
            # Conv Block 3
            x = self.conv3(x)
            x = self.bn3(x)
            x = F.relu(x)
            x = self.pool3(x)
            
            # Conv Block 4
            x = self.conv4(x)
            x = self.bn4(x)
            x = F.relu(x)
            x = self.pool4(x)
            
            # Flatten
            x = x.view(x.size(0), -1)
            
            # FC Layer 1
            x = self.fc1(x)
            x = F.relu(x)
            x = self.dropout1(x)
            
            # FC Layer 2
            x = self.fc2(x)
            x = F.relu(x)
            x = self.dropout2(x)
            
            # Output layer with softmax
            x = self.fc3(x)
            x = F.softmax(x, dim=1)
            
            return x

else:
    # Dummy class when PyTorch not available
    CNNColorRatioNetwork = None


class CNNColorRatioModel:
    """
    High-level interface for CNN color ratio prediction model.
    Handles model loading, saving, inference, and training.
    """
    
    def __init__(
        self,
        model_path: Optional[str] = None,
        device: str = "auto",
        num_colors: int = 16
    ):
        """
        Initialize the CNN color ratio model.
        
        Args:
            model_path: Path to pre-trained model weights (optional)
            device: Device selection - "auto", "cuda", "mps", or "cpu"
            num_colors: Number of base colors (default: 16)
        """
        if not TORCH_AVAILABLE:
            raise ImportError(
                "PyTorch is required for CNNColorRatioModel. "
                "Install with: pip install torch torchvision"
            )
        
        self.num_colors = num_colors
        self.model_path = model_path
        
        # Initialize device manager
        self.device_manager = get_device_manager(device)
        self.device = self.device_manager.device
        
        # Initialize network
        self.network = CNNColorRatioNetwork(num_colors=num_colors)
        self.network = self.device_manager.move_to_device(self.network)
        
        # Model metadata
        self.model_version = None
        self.training_metadata = {}
        
        # Load model if path provided
        if model_path:
            self.load_model(model_path)
        
        logger.info(f"CNNColorRatioModel initialized on device: {self.device}")
    
    def preprocess_image(self, image: np.ndarray):
        """
        Preprocess image for CNN inference.
        
        IMPORTANT: This method performs SINGLE normalization to [0,1] range only.
        No ImageNet statistics are applied, as they are not appropriate for 
        color mixing tasks and would cause double normalization issues.
        
        Args:
            image: RGB image as numpy array (H, W, 3) with values [0, 255]
            
        Returns:
            Preprocessed tensor (1, 3, 224, 224) normalized to [0, 1]
            
        Raises:
            ValueError: If input image has invalid range or shape
        """
        # Validate input shape
        if len(image.shape) != 3 or image.shape[2] != 3:
            raise ValueError(
                f"Input image must have shape (H, W, 3), got {image.shape}"
            )
        
        # Validate input range
        if image.min() < 0 or image.max() > 255:
            raise ValueError(
                f"Input image must have values in [0, 255], "
                f"got range [{image.min()}, {image.max()}]"
            )
        
        # Convert to float and normalize to [0, 1] - SINGLE NORMALIZATION
        image = image.astype(np.float32) / 255.0
        
        # Resize to 224x224 if needed
        if image.shape[:2] != (224, 224):
            import cv2
            image = cv2.resize(image, (224, 224))
        
        # Convert to tensor: (H, W, C) -> (C, H, W)
        image = torch.from_numpy(image).permute(2, 0, 1).float()
        
        # Add batch dimension: (C, H, W) -> (1, C, H, W)
        image = image.unsqueeze(0)
        
        # Move to device
        image = self.device_manager.move_to_device(image)
        
        return image
    
    def predict(self, image: np.ndarray) -> np.ndarray:
        """
        Predict color mixing ratios for a single image.
        
        Args:
            image: RGB image as numpy array (H, W, 3) with values [0, 255]
            
        Returns:
            Numpy array of shape (16,) with ratios summing to 1.0
        """
        self.network.eval()
        
        with torch.no_grad():
            # Preprocess
            input_tensor = self.preprocess_image(image)
            
            # Inference
            output = self.network(input_tensor)
            
            # Convert to numpy
            ratios = output.cpu().numpy()[0]
        
        return ratios
    
    def predict_batch(self, images: List[np.ndarray]) -> np.ndarray:
        """
        Predict color mixing ratios for a batch of images.
        
        Args:
            images: List of RGB images as numpy arrays
            
        Returns:
            Numpy array of shape (batch_size, 16) with ratios
        """
        self.network.eval()
        
        with torch.no_grad():
            # Preprocess all images
            input_tensors = [self.preprocess_image(img) for img in images]
            batch_tensor = torch.cat(input_tensors, dim=0)
            
            # Inference
            output = self.network(batch_tensor)
            
            # Convert to numpy
            ratios = output.cpu().numpy()
        
        return ratios
    
    def get_model_info(self) -> Dict:
        """
        Get information about the model.
        
        Returns:
            Dictionary with model metadata
        """
        return {
            "num_colors": self.num_colors,
            "device": str(self.device),
            "model_version": self.model_version,
            "model_path": self.model_path,
            "training_metadata": self.training_metadata,
            "num_parameters": sum(p.numel() for p in self.network.parameters())
        }

    def load_model(self, path: str) -> bool:
        """
        Load model weights from a checkpoint file.
        
        Args:
            path: Path to model checkpoint (.pth file)
            
        Returns:
            True if loading successful, False otherwise
        """
        try:
            checkpoint_path = Path(path)
            
            if not checkpoint_path.exists():
                logger.error(f"Model file not found: {path}")
                return False
            
            # Load checkpoint
            checkpoint = torch.load(checkpoint_path, map_location=self.device)
            
            # Load model state
            self.network.load_state_dict(checkpoint["model_state_dict"])
            
            # Load metadata
            self.model_version = checkpoint.get("model_version", "unknown")
            self.training_metadata = checkpoint.get("training_metadata", {})
            
            # Update model path
            self.model_path = str(checkpoint_path)
            
            logger.info(f"Model loaded successfully from {path}")
            logger.info(f"Model version: {self.model_version}")
            
            return True
        
        except Exception as e:
            logger.error(f"Failed to load model from {path}: {e}")
            return False
    
    def save_model(
        self,
        path: str,
        model_version: Optional[str] = None,
        training_metadata: Optional[Dict] = None
    ) -> None:
        """
        Save model weights to a checkpoint file.
        
        Args:
            path: Path to save model checkpoint
            model_version: Version string (e.g., "v1.0.0")
            training_metadata: Additional metadata to save
        """
        try:
            save_path = Path(path)
            save_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Prepare checkpoint
            checkpoint = {
                "model_state_dict": self.network.state_dict(),
                "model_version": model_version or self.model_version or "v1.0.0",
                "num_colors": self.num_colors,
                "architecture": {
                    "conv_filters": MODEL_CONFIG["conv_filters"],
                    "dense_units": MODEL_CONFIG["dense_units"],
                    "dropout_rates": MODEL_CONFIG["dropout_rates"]
                },
                "training_metadata": training_metadata or self.training_metadata
            }
            
            # Save checkpoint
            torch.save(checkpoint, save_path)
            
            logger.info(f"Model saved successfully to {path}")
        
        except Exception as e:
            logger.error(f"Failed to save model to {path}: {e}")
            raise
    
    def save_checkpoint(
        self,
        path: str,
        epoch: int,
        optimizer_state: Optional[Dict] = None,
        train_loss: Optional[float] = None,
        val_loss: Optional[float] = None,
        val_delta_e: Optional[float] = None,
        hyperparameters: Optional[Dict] = None
    ) -> None:
        """
        Save a training checkpoint with full training state.
        
        Args:
            path: Path to save checkpoint
            epoch: Current training epoch
            optimizer_state: Optimizer state dict
            train_loss: Training loss
            val_loss: Validation loss
            val_delta_e: Validation Delta E metric
            hyperparameters: Training hyperparameters
        """
        try:
            from datetime import datetime
            
            save_path = Path(path)
            save_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Prepare checkpoint
            checkpoint = {
                "model_state_dict": self.network.state_dict(),
                "optimizer_state_dict": optimizer_state,
                "epoch": epoch,
                "train_loss": train_loss,
                "val_loss": val_loss,
                "val_delta_e": val_delta_e,
                "hyperparameters": hyperparameters or {},
                "model_version": self.model_version,
                "num_colors": self.num_colors,
                "architecture": {
                    "conv_filters": MODEL_CONFIG["conv_filters"],
                    "dense_units": MODEL_CONFIG["dense_units"],
                    "dropout_rates": MODEL_CONFIG["dropout_rates"]
                },
                "training_timestamp": datetime.now().isoformat()
            }
            
            # Save checkpoint
            torch.save(checkpoint, save_path)
            
            logger.info(f"Checkpoint saved to {path} (epoch {epoch})")
        
        except Exception as e:
            logger.error(f"Failed to save checkpoint to {path}: {e}")
            raise
    
    def load_checkpoint(self, path: str) -> Dict:
        """
        Load a training checkpoint to resume training.
        
        Args:
            path: Path to checkpoint file
            
        Returns:
            Dictionary with checkpoint data (epoch, losses, etc.)
        """
        try:
            checkpoint_path = Path(path)
            
            if not checkpoint_path.exists():
                logger.error(f"Checkpoint file not found: {path}")
                return {}
            
            # Load checkpoint
            checkpoint = torch.load(checkpoint_path, map_location=self.device)
            
            # Load model state
            self.network.load_state_dict(checkpoint["model_state_dict"])
            
            # Load metadata
            self.model_version = checkpoint.get("model_version", "unknown")
            
            logger.info(f"Checkpoint loaded from {path}")
            logger.info(f"Resuming from epoch {checkpoint.get('epoch', 0)}")
            
            return checkpoint
        
        except Exception as e:
            logger.error(f"Failed to load checkpoint from {path}: {e}")
            return {}
    
    def train_epoch(
        self,
        train_loader,
        optimizer,
        criterion,
        epoch: int
    ) -> float:
        """
        Train the model for one epoch.
        
        Args:
            train_loader: DataLoader for training data
            optimizer: PyTorch optimizer
            criterion: Loss function
            epoch: Current epoch number
            
        Returns:
            Average training loss for the epoch
        """
        self.network.train()
        total_loss = 0.0
        num_batches = 0
        
        for batch_idx, (images, ratios) in enumerate(train_loader):
            # Move data to device
            images = self.device_manager.move_to_device(images)
            ratios = self.device_manager.move_to_device(ratios)
            
            # Zero gradients
            optimizer.zero_grad()
            
            # Forward pass
            outputs = self.network(images)
            
            # Calculate loss
            loss = criterion(outputs, ratios)
            
            # Backward pass
            loss.backward()
            
            # Update weights
            optimizer.step()
            
            # Accumulate loss
            total_loss += loss.item()
            num_batches += 1
            
            # Log progress
            if (batch_idx + 1) % 10 == 0:
                logger.debug(
                    f"Epoch {epoch}, Batch {batch_idx + 1}/{len(train_loader)}, "
                    f"Loss: {loss.item():.4f}"
                )
        
        avg_loss = total_loss / num_batches
        logger.info(f"Epoch {epoch} - Training Loss: {avg_loss:.4f}")
        
        return avg_loss
    
    def validate_epoch(
        self,
        val_loader,
        criterion,
        epoch: int,
        calculate_delta_e: bool = True
    ) -> Tuple[float, Optional[float]]:
        """
        Validate the model on validation set.
        
        Args:
            val_loader: DataLoader for validation data
            criterion: Loss function
            epoch: Current epoch number
            calculate_delta_e: Whether to calculate Delta E metric
            
        Returns:
            Tuple of (validation loss, mean Delta E)
        """
        self.network.eval()
        total_loss = 0.0
        num_batches = 0
        delta_e_values = []
        
        with torch.no_grad():
            for images, ratios in val_loader:
                # Move data to device
                images = self.device_manager.move_to_device(images)
                ratios = self.device_manager.move_to_device(ratios)
                
                # Forward pass
                outputs = self.network(images)
                
                # Calculate loss
                loss = criterion(outputs, ratios)
                
                # Accumulate loss
                total_loss += loss.item()
                num_batches += 1
                
                # Calculate Delta E if requested
                if calculate_delta_e:
                    # Convert to numpy for Delta E calculation
                    pred_ratios = outputs.cpu().numpy()
                    true_ratios = ratios.cpu().numpy()
                    
                    # Calculate Delta E for each sample in batch
                    for pred, true in zip(pred_ratios, true_ratios):
                        delta_e = self._calculate_delta_e_from_ratios(pred, true)
                        delta_e_values.append(delta_e)
        
        avg_loss = total_loss / num_batches
        mean_delta_e = np.mean(delta_e_values) if delta_e_values else None
        
        logger.info(f"Epoch {epoch} - Validation Loss: {avg_loss:.4f}")
        if mean_delta_e is not None:
            logger.info(f"Epoch {epoch} - Mean Delta E: {mean_delta_e:.2f}")
        
        return avg_loss, mean_delta_e
    
    def _calculate_delta_e_from_ratios(
        self,
        pred_ratios: np.ndarray,
        true_ratios: np.ndarray
    ) -> float:
        """
        Calculate Delta E between predicted and true color ratios.
        
        This is a simplified approximation. For accurate Delta E,
        we would need to reconstruct the actual Lab colors.
        
        Args:
            pred_ratios: Predicted ratios (16,)
            true_ratios: True ratios (16,)
            
        Returns:
            Delta E value
        """
        # Simple L2 distance as proxy for Delta E
        # In production, this should reconstruct Lab colors and use proper Delta E
        return np.linalg.norm(pred_ratios - true_ratios) * 100
    
    def train(
        self,
        train_loader,
        val_loader,
        epochs: int,
        learning_rate: float = 0.001,
        checkpoint_dir: Optional[str] = None,
        checkpoint_interval: int = 5,
        early_stopping_patience: int = 10,
        scheduler_patience: int = 3,
        scheduler_factor: float = 0.5,
        log_dir: Optional[str] = None,
        experiment_name: Optional[str] = None
    ) -> Dict:
        """
        Train the model with validation and checkpointing.
        
        Args:
            train_loader: DataLoader for training data
            val_loader: DataLoader for validation data
            epochs: Number of training epochs
            learning_rate: Initial learning rate
            checkpoint_dir: Directory to save checkpoints
            checkpoint_interval: Save checkpoint every N epochs
            early_stopping_patience: Stop if no improvement for N epochs
            scheduler_patience: Reduce LR if no improvement for N epochs
            scheduler_factor: Factor to reduce LR by
            log_dir: Directory for training logs
            experiment_name: Name for this training experiment
            
        Returns:
            Dictionary with training history
        """
        # Initialize training logger
        training_logger = None
        if TRAINING_LOGGER_AVAILABLE and log_dir:
            training_logger = TrainingLogger(
                log_dir=log_dir,
                experiment_name=experiment_name,
                use_tensorboard=True
            )
            
            # Log hyperparameters
            hyperparameters = {
                'learning_rate': learning_rate,
                'batch_size': train_loader.batch_size,
                'epochs': epochs,
                'early_stopping_patience': early_stopping_patience,
                'scheduler_patience': scheduler_patience,
                'scheduler_factor': scheduler_factor
            }
            training_logger.log_hyperparameters(hyperparameters)
            
            # Log model info
            training_logger.log_model_info(self.get_model_info())
        
        # Initialize optimizer
        optimizer = torch.optim.Adam(self.network.parameters(), lr=learning_rate)
        
        # Initialize loss function (MSE for regression)
        criterion = nn.MSELoss()
        
        # Initialize learning rate scheduler
        scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
            optimizer,
            mode='min',
            factor=scheduler_factor,
            patience=scheduler_patience
        )
        
        # Training history
        history = {
            'train_loss': [],
            'val_loss': [],
            'val_delta_e': [],
            'learning_rates': []
        }
        
        # Early stopping variables
        best_val_loss = float('inf')
        epochs_without_improvement = 0
        
        # Setup checkpoint directory
        if checkpoint_dir:
            checkpoint_path = Path(checkpoint_dir)
            checkpoint_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Starting training for {epochs} epochs")
        logger.info(f"Initial learning rate: {learning_rate}")
        
        try:
            for epoch in range(1, epochs + 1):
                # Train one epoch
                train_loss = self.train_epoch(train_loader, optimizer, criterion, epoch)
                
                # Validate
                val_loss, val_delta_e = self.validate_epoch(val_loader, criterion, epoch)
                
                # Update learning rate scheduler
                scheduler.step(val_loss)
                
                # Get current learning rate
                current_lr = optimizer.param_groups[0]['lr']
                
                # Record history
                history['train_loss'].append(train_loss)
                history['val_loss'].append(val_loss)
                history['val_delta_e'].append(val_delta_e)
                history['learning_rates'].append(current_lr)
                
                # Log to training logger
                if training_logger:
                    training_logger.log_epoch(
                        epoch=epoch,
                        train_loss=train_loss,
                        val_loss=val_loss,
                        val_delta_e=val_delta_e,
                        learning_rate=current_lr
                    )
                
                # Check for improvement
                if val_loss < best_val_loss:
                    best_val_loss = val_loss
                    epochs_without_improvement = 0
                    
                    # Save best model
                    if checkpoint_dir:
                        best_model_path = checkpoint_path / "best_model.pth"
                        self.save_checkpoint(
                            str(best_model_path),
                            epoch=epoch,
                            optimizer_state=optimizer.state_dict(),
                            train_loss=train_loss,
                            val_loss=val_loss,
                            val_delta_e=val_delta_e,
                            hyperparameters={
                                'learning_rate': learning_rate,
                                'batch_size': train_loader.batch_size,
                                'epochs': epochs
                            }
                        )
                        logger.info(f"Best model saved (val_loss: {val_loss:.4f})")
                else:
                    epochs_without_improvement += 1
                
                # Save periodic checkpoint
                if checkpoint_dir and epoch % checkpoint_interval == 0:
                    checkpoint_file = checkpoint_path / f"checkpoint_epoch_{epoch}.pth"
                    self.save_checkpoint(
                        str(checkpoint_file),
                        epoch=epoch,
                        optimizer_state=optimizer.state_dict(),
                        train_loss=train_loss,
                        val_loss=val_loss,
                        val_delta_e=val_delta_e,
                        hyperparameters={
                            'learning_rate': learning_rate,
                            'batch_size': train_loader.batch_size,
                            'epochs': epochs
                        }
                    )
                
                # Early stopping check
                if epochs_without_improvement >= early_stopping_patience:
                    logger.info(
                        f"Early stopping triggered after {epoch} epochs "
                        f"(no improvement for {early_stopping_patience} epochs)"
                    )
                    break
                
                # Log progress
                delta_e_str = f"{val_delta_e:.2f}" if val_delta_e is not None else "N/A"
                logger.info(
                    f"Epoch {epoch}/{epochs} - "
                    f"Train Loss: {train_loss:.4f}, "
                    f"Val Loss: {val_loss:.4f}, "
                    f"Delta E: {delta_e_str}, "
                    f"LR: {current_lr:.6f}"
                )
        
        except KeyboardInterrupt:
            logger.info("Training interrupted by user")
            if checkpoint_dir:
                interrupt_path = checkpoint_path / "interrupted_checkpoint.pth"
                self.save_checkpoint(
                    str(interrupt_path),
                    epoch=epoch,
                    optimizer_state=optimizer.state_dict(),
                    train_loss=train_loss,
                    val_loss=val_loss,
                    val_delta_e=val_delta_e,
                    hyperparameters={
                        'learning_rate': learning_rate,
                        'batch_size': train_loader.batch_size,
                        'epochs': epochs
                    }
                )
                logger.info(f"Checkpoint saved before interruption")
        
        finally:
            # Close training logger
            if training_logger:
                training_logger.close()
        
        logger.info("Training completed")
        logger.info(f"Best validation loss: {best_val_loss:.4f}")
        
        return history
