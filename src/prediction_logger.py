"""
Comprehensive logging system for CNN color predictions.
Tracks all predictions, inference times, methods used, and fallback events.
"""

import logging
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, Any
from logging.handlers import RotatingFileHandler


class PredictionLogger:
    """
    Logger for color predictions with rotation and structured logging.
    """
    
    def __init__(
        self,
        log_dir: str = "logs/predictions",
        max_bytes: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5
    ):
        """
        Initialize prediction logger.
        
        Args:
            log_dir: Directory for log files
            max_bytes: Maximum size of log file before rotation
            backup_count: Number of backup files to keep
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup main logger
        self.logger = logging.getLogger('prediction_logger')
        self.logger.setLevel(logging.INFO)
        
        # Remove existing handlers
        self.logger.handlers = []
        
        # Add rotating file handler
        log_file = self.log_dir / "predictions.log"
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count
        )
        file_handler.setLevel(logging.INFO)
        
        # Add console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)
        
        # Set format
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        # Setup JSON logger for structured data
        self.json_log_file = self.log_dir / "predictions.jsonl"
        
        self.logger.info("PredictionLogger initialized")
    
    def log_prediction(
        self,
        rgb_values: tuple,
        lab_values: tuple,
        prediction_method: str,
        dominant_color: str,
        confidence: float,
        primary_colors: Dict[str, float],
        inference_time_ms: Optional[float] = None,
        quality_score: Optional[str] = None,
        model_version: Optional[str] = None,
        delta_e: Optional[float] = None,
        additional_info: Optional[Dict] = None
    ):
        """
        Log a color prediction.
        
        Args:
            rgb_values: RGB color values
            lab_values: Lab color values
            prediction_method: Method used (cnn/ciede2000)
            dominant_color: Predicted dominant color
            confidence: Confidence score
            primary_colors: Dictionary of color percentages
            inference_time_ms: Inference time in milliseconds
            quality_score: Quality classification
            model_version: CNN model version if applicable
            delta_e: Delta E value if available
            additional_info: Additional metadata
        """
        # Create log entry
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'rgb': rgb_values,
            'lab': lab_values,
            'method': prediction_method,
            'dominant_color': dominant_color,
            'confidence': confidence,
            'primary_colors': primary_colors,
            'inference_time_ms': inference_time_ms,
            'quality_score': quality_score,
            'model_version': model_version,
            'delta_e': delta_e
        }
        
        if additional_info:
            log_entry.update(additional_info)
        
        # Log to text file
        self.logger.info(
            f"Prediction: {prediction_method.upper()} - "
            f"Dominant: {dominant_color} ({confidence*100:.1f}%) - "
            f"Quality: {quality_score} - "
            f"Time: {inference_time_ms:.1f}ms" if inference_time_ms else ""
        )
        
        # Log to JSON file
        self._log_json(log_entry)
    
    def log_error(
        self,
        error_type: str,
        error_message: str,
        context: Optional[Dict] = None
    ):
        """
        Log an error event.
        
        Args:
            error_type: Type of error (model_loading, inference, validation, etc.)
            error_message: Error message
            context: Additional context information
        """
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'event_type': 'error',
            'error_type': error_type,
            'error_message': error_message,
            'context': context or {}
        }
        
        self.logger.error(f"{error_type}: {error_message}")
        self._log_json(log_entry)
    
    def log_fallback(
        self,
        from_method: str,
        to_method: str,
        reason: str,
        context: Optional[Dict] = None
    ):
        """
        Log a fallback event.
        
        Args:
            from_method: Original method that failed
            to_method: Fallback method used
            reason: Reason for fallback
            context: Additional context
        """
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'event_type': 'fallback',
            'from_method': from_method,
            'to_method': to_method,
            'reason': reason,
            'context': context or {}
        }
        
        self.logger.warning(
            f"Fallback: {from_method} -> {to_method} - Reason: {reason}"
        )
        self._log_json(log_entry)
    
    def log_model_load(
        self,
        model_path: str,
        success: bool,
        model_version: Optional[str] = None,
        device: Optional[str] = None,
        error_message: Optional[str] = None
    ):
        """
        Log model loading event.
        
        Args:
            model_path: Path to model file
            success: Whether loading was successful
            model_version: Model version if loaded
            device: Device used (cpu/cuda/mps)
            error_message: Error message if failed
        """
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'event_type': 'model_load',
            'model_path': model_path,
            'success': success,
            'model_version': model_version,
            'device': device,
            'error_message': error_message
        }
        
        if success:
            self.logger.info(
                f"Model loaded: {model_path} (v{model_version}) on {device}"
            )
        else:
            self.logger.error(
                f"Model load failed: {model_path} - {error_message}"
            )
        
        self._log_json(log_entry)
    
    def _log_json(self, entry: Dict):
        """Write entry to JSON log file."""
        try:
            with open(self.json_log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(entry, ensure_ascii=False) + '\n')
        except Exception as e:
            self.logger.error(f"Failed to write JSON log: {e}")
    
    def get_statistics(self, hours: int = 24) -> Dict[str, Any]:
        """
        Get prediction statistics for the last N hours.
        
        Args:
            hours: Number of hours to analyze
            
        Returns:
            Dictionary with statistics
        """
        from datetime import timedelta
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        stats = {
            'total_predictions': 0,
            'cnn_predictions': 0,
            'ciede2000_predictions': 0,
            'fallback_events': 0,
            'errors': 0,
            'avg_inference_time_ms': 0,
            'quality_distribution': {},
            'dominant_colors': {}
        }
        
        try:
            if not self.json_log_file.exists():
                return stats
            
            inference_times = []
            
            with open(self.json_log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        entry = json.loads(line)
                        entry_time = datetime.fromisoformat(entry['timestamp'])
                        
                        if entry_time < cutoff_time:
                            continue
                        
                        event_type = entry.get('event_type', 'prediction')
                        
                        if event_type == 'prediction' or 'method' in entry:
                            stats['total_predictions'] += 1
                            
                            method = entry.get('method', '')
                            if method == 'cnn':
                                stats['cnn_predictions'] += 1
                            elif method == 'ciede2000':
                                stats['ciede2000_predictions'] += 1
                            
                            # Inference time
                            if entry.get('inference_time_ms'):
                                inference_times.append(entry['inference_time_ms'])
                            
                            # Quality distribution
                            quality = entry.get('quality_score', 'Unknown')
                            stats['quality_distribution'][quality] = \
                                stats['quality_distribution'].get(quality, 0) + 1
                            
                            # Dominant colors
                            dominant = entry.get('dominant_color', 'Unknown')
                            stats['dominant_colors'][dominant] = \
                                stats['dominant_colors'].get(dominant, 0) + 1
                        
                        elif event_type == 'fallback':
                            stats['fallback_events'] += 1
                        
                        elif event_type == 'error':
                            stats['errors'] += 1
                    
                    except json.JSONDecodeError:
                        continue
            
            # Calculate average inference time
            if inference_times:
                stats['avg_inference_time_ms'] = sum(inference_times) / len(inference_times)
        
        except Exception as e:
            self.logger.error(f"Failed to calculate statistics: {e}")
        
        return stats


# Global logger instance
_prediction_logger = None


def get_prediction_logger(
    log_dir: str = "logs/predictions",
    max_bytes: int = 10 * 1024 * 1024,
    backup_count: int = 5
) -> PredictionLogger:
    """
    Get or create global prediction logger instance.
    
    Args:
        log_dir: Directory for log files
        max_bytes: Maximum size of log file before rotation
        backup_count: Number of backup files to keep
        
    Returns:
        PredictionLogger instance
    """
    global _prediction_logger
    
    if _prediction_logger is None:
        _prediction_logger = PredictionLogger(
            log_dir=log_dir,
            max_bytes=max_bytes,
            backup_count=backup_count
        )
    
    return _prediction_logger
