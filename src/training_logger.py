"""
Training metrics logger with TensorBoard and JSON support.
Logs training progress, metrics, and creates visualizations.
"""

import logging
import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import numpy as np

try:
    from torch.utils.tensorboard import SummaryWriter
    TENSORBOARD_AVAILABLE = True
except ImportError:
    TENSORBOARD_AVAILABLE = False
    SummaryWriter = None

logger = logging.getLogger(__name__)


class TrainingLogger:
    """
    Logger for training metrics with TensorBoard and JSON export.
    """
    
    def __init__(
        self,
        log_dir: str = "logs",
        experiment_name: Optional[str] = None,
        use_tensorboard: bool = True
    ):
        """
        Initialize training logger.
        
        Args:
            log_dir: Directory for logs
            experiment_name: Name of experiment (default: timestamp)
            use_tensorboard: Whether to use TensorBoard logging
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Create experiment name
        if experiment_name is None:
            experiment_name = f"training_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.experiment_name = experiment_name
        
        # Create experiment directory
        self.experiment_dir = self.log_dir / experiment_name
        self.experiment_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize TensorBoard writer
        self.use_tensorboard = use_tensorboard and TENSORBOARD_AVAILABLE
        self.writer = None
        
        if self.use_tensorboard:
            tensorboard_dir = self.experiment_dir / "tensorboard"
            self.writer = SummaryWriter(log_dir=str(tensorboard_dir))
            logger.info(f"TensorBoard logging enabled: {tensorboard_dir}")
        elif use_tensorboard and not TENSORBOARD_AVAILABLE:
            logger.warning("TensorBoard requested but not available. Install with: pip install tensorboard")
        
        # Training history
        self.history = {
            'train_loss': [],
            'val_loss': [],
            'val_delta_e': [],
            'learning_rates': [],
            'epochs': []
        }
        
        # Metadata
        self.metadata = {
            'experiment_name': experiment_name,
            'start_time': datetime.now().isoformat(),
            'end_time': None
        }
        
        logger.info(f"Training logger initialized: {self.experiment_dir}")
    
    def log_epoch(
        self,
        epoch: int,
        train_loss: float,
        val_loss: float,
        val_delta_e: Optional[float] = None,
        learning_rate: Optional[float] = None,
        additional_metrics: Optional[Dict] = None
    ):
        """
        Log metrics for one epoch.
        
        Args:
            epoch: Epoch number
            train_loss: Training loss
            val_loss: Validation loss
            val_delta_e: Validation Delta E metric
            learning_rate: Current learning rate
            additional_metrics: Additional metrics to log
        """
        # Update history
        self.history['epochs'].append(epoch)
        self.history['train_loss'].append(train_loss)
        self.history['val_loss'].append(val_loss)
        self.history['val_delta_e'].append(val_delta_e)
        self.history['learning_rates'].append(learning_rate)
        
        # Log to TensorBoard
        if self.writer:
            self.writer.add_scalar('Loss/train', train_loss, epoch)
            self.writer.add_scalar('Loss/validation', val_loss, epoch)
            
            if val_delta_e is not None:
                self.writer.add_scalar('Metrics/delta_e', val_delta_e, epoch)
            
            if learning_rate is not None:
                self.writer.add_scalar('Training/learning_rate', learning_rate, epoch)
            
            # Log additional metrics
            if additional_metrics:
                for key, value in additional_metrics.items():
                    self.writer.add_scalar(f'Metrics/{key}', value, epoch)
        
        # Log to console
        log_msg = (
            f"Epoch {epoch} - "
            f"Train Loss: {train_loss:.4f}, "
            f"Val Loss: {val_loss:.4f}"
        )
        
        if val_delta_e is not None:
            log_msg += f", Delta E: {val_delta_e:.2f}"
        
        if learning_rate is not None:
            log_msg += f", LR: {learning_rate:.6f}"
        
        logger.info(log_msg)
    
    def log_batch(
        self,
        epoch: int,
        batch_idx: int,
        batch_loss: float,
        total_batches: int
    ):
        """
        Log metrics for a single batch.
        
        Args:
            epoch: Current epoch
            batch_idx: Batch index
            batch_loss: Loss for this batch
            total_batches: Total number of batches
        """
        if self.writer:
            global_step = epoch * total_batches + batch_idx
            self.writer.add_scalar('Loss/batch', batch_loss, global_step)
    
    def log_hyperparameters(self, hyperparameters: Dict):
        """
        Log hyperparameters.
        
        Args:
            hyperparameters: Dictionary of hyperparameters
        """
        self.metadata['hyperparameters'] = hyperparameters
        
        if self.writer:
            # TensorBoard hyperparameters
            self.writer.add_text(
                'Hyperparameters',
                json.dumps(hyperparameters, indent=2),
                0
            )
        
        logger.info(f"Hyperparameters: {json.dumps(hyperparameters, indent=2)}")
    
    def log_model_info(self, model_info: Dict):
        """
        Log model architecture information.
        
        Args:
            model_info: Dictionary with model information
        """
        self.metadata['model_info'] = model_info
        
        if self.writer:
            self.writer.add_text(
                'Model',
                json.dumps(model_info, indent=2),
                0
            )
        
        logger.info(f"Model info: {json.dumps(model_info, indent=2)}")
    
    def save_history(self, filename: str = "training_history.json"):
        """
        Save training history to JSON file.
        
        Args:
            filename: Name of JSON file
        """
        history_path = self.experiment_dir / filename
        
        # Convert numpy types to native Python types
        def convert_to_native(obj):
            if isinstance(obj, (np.integer, np.floating)):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, dict):
                return {k: convert_to_native(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_to_native(item) for item in obj]
            return obj
        
        # Prepare data for JSON serialization
        history_data = {
            'metadata': convert_to_native(self.metadata),
            'history': convert_to_native(self.history)
        }
        
        # Save to JSON
        with open(history_path, 'w') as f:
            json.dump(history_data, f, indent=2)
        
        logger.info(f"Training history saved to {history_path}")
    
    def close(self):
        """
        Close the logger and save final data.
        """
        # Update end time
        self.metadata['end_time'] = datetime.now().isoformat()
        
        # Save history
        self.save_history()
        
        # Close TensorBoard writer
        if self.writer:
            self.writer.close()
        
        logger.info("Training logger closed")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
