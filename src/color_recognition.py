"""
Color recognition module using machine learning and deep learning approaches
Implements SVM, CNN, and YOLO-based color detection algorithms

NOTE: These algorithms are NOT currently used in production.
The system uses CIEDE2000 algorithm from advanced_color_analysis.py instead.
Keeping this code commented out for potential future use.
"""

import cv2
import numpy as np
from typing import List, Tuple, Dict, Optional, Union
import matplotlib.pyplot as plt

# UNUSED: SVM and Deep Learning models - commented out as not used with CIEDE2000
# from sklearn.svm import SVC
# from sklearn.ensemble import RandomForestClassifier
# from sklearn.model_selection import train_test_split, GridSearchCV
# from sklearn.preprocessing import StandardScaler
# from sklearn.metrics import classification_report, confusion_matrix
# import torch
# import torch.nn as nn
# import torch.optim as optim
# from torch.utils.data import Dataset, DataLoader
# import torchvision.transforms as transforms
# import joblib
import os

from .utils import ColorSpaceConverter, ImageProcessor, DataProcessor


# ==============================================================================
# UNUSED CLASSES - Commented out as CIEDE2000 algorithm is used instead
# ==============================================================================

"""
class ColorFeatureExtractor:
    '''Extract color features from images for machine learning models'''
    
    @staticmethod
    def extract_basic_features(image: np.ndarray, 
                             region: Optional[Tuple[int, int, int, int]] = None) -> np.ndarray:
        """
        Extract basic color features (RGB, HSV, Lab statistics)
        
        Args:
            image: Input image
            region: Optional region of interest (x, y, w, h)
            
        Returns:
            Feature vector with color statistics
        """
        if region:
            x, y, w, h = region
            roi = image[y:y+h, x:x+w]
        else:
            roi = image
        
        # RGB features
        rgb_mean = np.mean(roi, axis=(0, 1))
        rgb_std = np.std(roi, axis=(0, 1))
        
        # HSV features
        hsv = ColorSpaceConverter.rgb_to_hsv(roi)
        hsv_mean = np.mean(hsv, axis=(0, 1))
        hsv_std = np.std(hsv, axis=(0, 1))
        
        # Lab features
        lab = ColorSpaceConverter.rgb_to_lab(roi)
        lab_mean = np.mean(lab, axis=(0, 1))
        lab_std = np.std(lab, axis=(0, 1))
        
        # Combine all features
        features = np.concatenate([
            rgb_mean, rgb_std,
            hsv_mean, hsv_std,
            lab_mean, lab_std
        ])
        
        return features
    
    @staticmethod
    def extract_histogram_features(image: np.ndarray, 
                                 bins: int = 32,
                                 region: Optional[Tuple[int, int, int, int]] = None) -> np.ndarray:
        """
        Extract color histogram features
        
        Args:
            image: Input image
            bins: Number of histogram bins
            region: Optional region of interest
            
        Returns:
            Concatenated histogram features
        """
        if region:
            x, y, w, h = region
            roi = image[y:y+h, x:x+w]
        else:
            roi = image
        
        # RGB histograms
        rgb_hists = []
        for i in range(3):
            hist, _ = np.histogram(roi[:, :, i], bins=bins, range=[0, 256])
            rgb_hists.extend(hist)
        
        # HSV histograms
        hsv = ColorSpaceConverter.rgb_to_hsv(roi)
        hsv_hists = []
        for i in range(3):
            if i == 0:  # Hue
                hist, _ = np.histogram(hsv[:, :, i], bins=bins, range=[0, 180])
            else:  # Saturation, Value
                hist, _ = np.histogram(hsv[:, :, i], bins=bins, range=[0, 256])
            hsv_hists.extend(hist)
        
        # Normalize histograms
        rgb_hists = np.array(rgb_hists, dtype=np.float32)
        hsv_hists = np.array(hsv_hists, dtype=np.float32)
        
        rgb_hists = rgb_hists / (np.sum(rgb_hists) + 1e-7)
        hsv_hists = hsv_hists / (np.sum(hsv_hists) + 1e-7)
        
        return np.concatenate([rgb_hists, hsv_hists])


class SVMColorClassifier:
    """SVM-based color classifier with feature engineering"""
    
    def __init__(self, feature_type: str = 'combined'):
        """
        Initialize SVM classifier
        
        Args:
            feature_type: Type of features ('basic', 'histogram', 'combined')
        """
        self.feature_type = feature_type
        self.model = None
        self.scaler = StandardScaler()
        self.label_encoder = {}
        self.reverse_label_encoder = {}
        self.is_trained = False
    
    def _extract_features(self, image: np.ndarray, 
                         region: Optional[Tuple[int, int, int, int]] = None) -> np.ndarray:
        """Extract features based on feature_type"""
        if self.feature_type == 'basic':
            return ColorFeatureExtractor.extract_basic_features(image, region)
        elif self.feature_type == 'histogram':
            return ColorFeatureExtractor.extract_histogram_features(image, region=region)
        elif self.feature_type == 'combined':
            basic = ColorFeatureExtractor.extract_basic_features(image, region)
            histogram = ColorFeatureExtractor.extract_histogram_features(image, region=region)
            return np.concatenate([basic, histogram])
        else:
            raise ValueError(f"Unknown feature type: {self.feature_type}")
    
    def train(self, images: List[np.ndarray], 
              labels: List[str],
              regions: Optional[List[Tuple[int, int, int, int]]] = None,
              test_size: float = 0.2,
              cv_folds: int = 5) -> Dict:
        """
        Train SVM classifier
        
        Args:
            images: List of training images
            labels: List of color labels
            regions: Optional list of regions of interest
            test_size: Test set size ratio
            cv_folds: Cross-validation folds
            
        Returns:
            Training results dictionary
        """
        print("Extracting features...")
        features = []
        for i, image in enumerate(images):
            region = regions[i] if regions else None
            feature = self._extract_features(image, region)
            features.append(feature)
        
        features = np.array(features)
        
        # Encode labels
        unique_labels = list(set(labels))
        self.label_encoder = {label: i for i, label in enumerate(unique_labels)}
        self.reverse_label_encoder = {i: label for label, i in self.label_encoder.items()}
        
        encoded_labels = [self.label_encoder[label] for label in labels]
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            features, encoded_labels, test_size=test_size, random_state=42, stratify=encoded_labels
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Grid search for best parameters
        print("Performing grid search...")
        param_grid = {
            'C': [0.1, 1, 10, 100],
            'kernel': ['linear', 'rbf', 'poly'],
            'gamma': ['scale', 'auto', 0.001, 0.01, 0.1, 1]
        }
        
        svm = SVC(random_state=42)
        grid_search = GridSearchCV(svm, param_grid, cv=cv_folds, 
                                 scoring='accuracy', n_jobs=-1, verbose=1)
        grid_search.fit(X_train_scaled, y_train)
        
        self.model = grid_search.best_estimator_
        
        # Evaluate model
        train_accuracy = self.model.score(X_train_scaled, y_train)
        test_accuracy = self.model.score(X_test_scaled, y_test)
        
        # Predictions for detailed evaluation
        y_pred = self.model.predict(X_test_scaled)
        
        results = {
            'best_params': grid_search.best_params_,
            'train_accuracy': train_accuracy,
            'test_accuracy': test_accuracy,
            'classification_report': classification_report(
                y_test, y_pred, 
                target_names=[self.reverse_label_encoder[i] for i in sorted(self.reverse_label_encoder.keys())]
            ),
            'confusion_matrix': confusion_matrix(y_test, y_pred)
        }
        
        self.is_trained = True
        print(f"Training completed. Test accuracy: {test_accuracy:.3f}")
        
        return results
    
    def predict(self, image: np.ndarray, 
                region: Optional[Tuple[int, int, int, int]] = None) -> Tuple[str, float]:
        """
        Predict color label for image
        
        Args:
            image: Input image
            region: Optional region of interest
            
        Returns:
            (predicted_label, confidence)
        """
        if not self.is_trained:
            raise ValueError("Model not trained. Call train() first.")
        
        features = self._extract_features(image, region)
        features_scaled = self.scaler.transform(features.reshape(1, -1))
        
        prediction = self.model.predict(features_scaled)[0]
        probabilities = self.model.predict_proba(features_scaled)[0]
        confidence = np.max(probabilities)
        
        predicted_label = self.reverse_label_encoder[prediction]
        return predicted_label, confidence
    
    def save_model(self, filepath: str) -> None:
        """Save trained model to file"""
        if not self.is_trained:
            raise ValueError("No trained model to save")
        
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'label_encoder': self.label_encoder,
            'reverse_label_encoder': self.reverse_label_encoder,
            'feature_type': self.feature_type,
            'is_trained': self.is_trained
        }
        
        joblib.dump(model_data, filepath)
        print(f"Model saved to {filepath}")
    
    def load_model(self, filepath: str) -> bool:
        """Load trained model from file"""
        try:
            model_data = joblib.load(filepath)
            self.model = model_data['model']
            self.scaler = model_data['scaler']
            self.label_encoder = model_data['label_encoder']
            self.reverse_label_encoder = model_data['reverse_label_encoder']
            self.feature_type = model_data['feature_type']
            self.is_trained = model_data['is_trained']
            print(f"Model loaded from {filepath}")
            return True
        except Exception as e:
            print(f"Error loading model: {e}")
            return False


class ColorDataset(Dataset):
    """PyTorch Dataset for color recognition"""
    
    def __init__(self, images: List[np.ndarray], labels: List[int], 
                 transform=None, image_size: Tuple[int, int] = (224, 224)):
        self.images = images
        self.labels = labels
        self.transform = transform
        self.image_size = image_size
        
        if self.transform is None:
            self.transform = transforms.Compose([
                transforms.ToPILImage(),
                transforms.Resize(self.image_size),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                                   std=[0.229, 0.224, 0.225])
            ])
    
    def __len__(self):
        return len(self.images)
    
    def __getitem__(self, idx):
        image = self.images[idx]
        label = self.labels[idx]
        
        if self.transform:
            image = self.transform(image)
        
        return image, label


class CNNColorClassifier(nn.Module):
    """CNN-based color classifier"""
    
    def __init__(self, num_classes: int, input_size: Tuple[int, int] = (224, 224)):
        super(CNNColorClassifier, self).__init__()
        self.num_classes = num_classes
        self.input_size = input_size
        
        # Convolutional layers
        self.conv1 = nn.Conv2d(3, 32, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.conv3 = nn.Conv2d(64, 128, kernel_size=3, padding=1)
        self.conv4 = nn.Conv2d(128, 256, kernel_size=3, padding=1)
        
        # Pooling and normalization
        self.pool = nn.MaxPool2d(2, 2)
        self.bn1 = nn.BatchNorm2d(32)
        self.bn2 = nn.BatchNorm2d(64)
        self.bn3 = nn.BatchNorm2d(128)
        self.bn4 = nn.BatchNorm2d(256)
        
        # Calculate the size of flattened features
        self._calculate_fc_input_size()
        
        # Fully connected layers
        self.fc1 = nn.Linear(self.fc_input_size, 512)
        self.fc2 = nn.Linear(512, 256)
        self.fc3 = nn.Linear(256, num_classes)
        
        # Dropout and activation
        self.dropout = nn.Dropout(0.5)
        self.relu = nn.ReLU()
    
    def _calculate_fc_input_size(self):
        """Calculate input size for first FC layer"""
        x = torch.randn(1, 3, *self.input_size)
        x = self.pool(self.relu(self.bn1(self.conv1(x))))
        x = self.pool(self.relu(self.bn2(self.conv2(x))))
        x = self.pool(self.relu(self.bn3(self.conv3(x))))
        x = self.pool(self.relu(self.bn4(self.conv4(x))))
        self.fc_input_size = x.numel()
    
    def forward(self, x):
        # Convolutional layers with pooling and normalization
        x = self.pool(self.relu(self.bn1(self.conv1(x))))
        x = self.pool(self.relu(self.bn2(self.conv2(x))))
        x = self.pool(self.relu(self.bn3(self.conv3(x))))
        x = self.pool(self.relu(self.bn4(self.conv4(x))))
        
        # Flatten
        x = x.view(x.size(0), -1)
        
        # Fully connected layers
        x = self.dropout(self.relu(self.fc1(x)))
        x = self.dropout(self.relu(self.fc2(x)))
        x = self.fc3(x)
        
        return x


class DeepColorClassifier:
    """Deep learning-based color classifier wrapper"""
    
    def __init__(self, num_classes: int, device: str = 'auto'):
        self.num_classes = num_classes
        self.device = self._get_device(device)
        self.model = None
        self.label_encoder = {}
        self.reverse_label_encoder = {}
        self.is_trained = False
    
    def _get_device(self, device: str) -> str:
        """Get appropriate device (CPU/GPU)"""
        if device == 'auto':
            return 'cuda' if torch.cuda.is_available() else 'cpu'
        return device
    
    def train(self, images: List[np.ndarray], labels: List[str],
              epochs: int = 50, batch_size: int = 32, learning_rate: float = 0.001,
              test_size: float = 0.2) -> Dict:
        """
        Train CNN classifier
        
        Args:
            images: List of training images
            labels: List of color labels
            epochs: Number of training epochs
            batch_size: Training batch size
            learning_rate: Learning rate
            test_size: Test set ratio
            
        Returns:
            Training history
        """
        # Encode labels
        unique_labels = list(set(labels))
        self.label_encoder = {label: i for i, label in enumerate(unique_labels)}
        self.reverse_label_encoder = {i: label for label, i in self.label_encoder.items()}
        
        encoded_labels = [self.label_encoder[label] for label in labels]
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            images, encoded_labels, test_size=test_size, random_state=42, stratify=encoded_labels
        )
        
        # Create datasets and dataloaders
        train_dataset = ColorDataset(X_train, y_train)
        test_dataset = ColorDataset(X_test, y_test)
        
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
        test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)
        
        # Initialize model
        self.model = CNNColorClassifier(self.num_classes).to(self.device)
        criterion = nn.CrossEntropyLoss()
        optimizer = optim.Adam(self.model.parameters(), lr=learning_rate)
        scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=20, gamma=0.1)
        
        # Training loop
        train_losses = []
        train_accuracies = []
        test_accuracies = []
        
        print(f"Training on {self.device}...")
        
        for epoch in range(epochs):
            # Training phase
            self.model.train()
            running_loss = 0.0
            correct_train = 0
            total_train = 0
            
            for images_batch, labels_batch in train_loader:
                images_batch = images_batch.to(self.device)
                labels_batch = labels_batch.to(self.device)
                
                optimizer.zero_grad()
                outputs = self.model(images_batch)
                loss = criterion(outputs, labels_batch)
                loss.backward()
                optimizer.step()
                
                running_loss += loss.item()
                _, predicted = torch.max(outputs.data, 1)
                total_train += labels_batch.size(0)
                correct_train += (predicted == labels_batch).sum().item()
            
            scheduler.step()
            
            # Validation phase
            self.model.eval()
            correct_test = 0
            total_test = 0
            
            with torch.no_grad():
                for images_batch, labels_batch in test_loader:
                    images_batch = images_batch.to(self.device)
                    labels_batch = labels_batch.to(self.device)
                    outputs = self.model(images_batch)
                    _, predicted = torch.max(outputs, 1)
                    total_test += labels_batch.size(0)
                    correct_test += (predicted == labels_batch).sum().item()
            
            # Record metrics
            epoch_loss = running_loss / len(train_loader)
            train_acc = 100 * correct_train / total_train
            test_acc = 100 * correct_test / total_test
            
            train_losses.append(epoch_loss)
            train_accuracies.append(train_acc)
            test_accuracies.append(test_acc)
            
            if (epoch + 1) % 10 == 0:
                print(f'Epoch [{epoch+1}/{epochs}], Loss: {epoch_loss:.4f}, '
                      f'Train Acc: {train_acc:.2f}%, Test Acc: {test_acc:.2f}%')
        
        self.is_trained = True
        
        return {
            'train_losses': train_losses,
            'train_accuracies': train_accuracies,
            'test_accuracies': test_accuracies,
            'final_test_accuracy': test_accuracies[-1]
        }
    
    def predict(self, image: np.ndarray) -> Tuple[str, float]:
        """Predict color label for image"""
        if not self.is_trained:
            raise ValueError("Model not trained. Call train() first.")
        
        # Preprocess image
        transform = transforms.Compose([
            transforms.ToPILImage(),
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                               std=[0.229, 0.224, 0.225])
        ])
        
        input_tensor = transform(image).unsqueeze(0).to(self.device)
        
        self.model.eval()
        with torch.no_grad():
            outputs = self.model(input_tensor)
            probabilities = torch.nn.functional.softmax(outputs, dim=1)
            confidence, predicted = torch.max(probabilities, 1)
        
        predicted_label = self.reverse_label_encoder[predicted.item()]
        return predicted_label, confidence.item()


class ColorSegmenter:
    """Segment colors in images using various methods"""
    
    @staticmethod
    def segment_by_color_range(image: np.ndarray, 
                             lower_bound: np.ndarray, 
                             upper_bound: np.ndarray,
                             color_space: str = 'HSV') -> np.ndarray:
        """
        Segment image by color range
        
        Args:
            image: Input image
            lower_bound: Lower color bound
            upper_bound: Upper color bound
            color_space: Color space for segmentation
            
        Returns:
            Binary mask
        """
        if color_space == 'HSV':
            converted = ColorSpaceConverter.rgb_to_hsv(image)
        elif color_space == 'LAB':
            converted = ColorSpaceConverter.rgb_to_lab(image)
        else:
            converted = image
        
        mask = cv2.inRange(converted, lower_bound, upper_bound)
        return mask
    
    @staticmethod
    def segment_by_clustering(image: np.ndarray, 
                            k: int = 8,
                            max_iter: int = 100) -> Tuple[np.ndarray, np.ndarray]:
        """
        Segment image using k-means clustering
        
        Args:
            image: Input image
            k: Number of clusters
            max_iter: Maximum iterations
            
        Returns:
            (segmented_image, cluster_centers)
        """
        # Reshape image to pixel array
        pixel_values = image.reshape((-1, 3))
        pixel_values = np.float32(pixel_values)
        
        # K-means clustering
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, max_iter, 0.2)
        _, labels, centers = cv2.kmeans(pixel_values, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
        
        # Convert back to uint8 and reshape
        centers = np.uint8(centers)
        segmented_data = centers[labels.flatten()]
        segmented_image = segmented_data.reshape(image.shape)
        
        return segmented_image, centers


def create_color_detection_pipeline(model_type: str = 'svm',
                                  calibration_path: Optional[str] = None) -> object:
    '''
    Create complete color detection pipeline
    
    Args:
        model_type: Type of model ('svm', 'cnn')
        calibration_path: Path to camera calibration file
        
    Returns:
        Configured color detection pipeline
    '''
    from .preprocessing import CameraCalibrator, ImagePreprocessor
    
    # Load calibration if available
    calibrator = None
    if calibration_path and os.path.exists(calibration_path):
        calibrator = CameraCalibrator()
        calibrator.load_calibration(calibration_path)
    
    # Create preprocessor
    preprocessor = ImagePreprocessor(calibrator)
    
    # Create classifier
    if model_type == 'svm':
        classifier = SVMColorClassifier(feature_type='combined')
    elif model_type == 'cnn':
        classifier = DeepColorClassifier(num_classes=10)  # Will be updated during training
    else:
        raise ValueError(f"Unknown model type: {model_type}")
    
    class ColorDetectionPipeline:
        def __init__(self, preprocessor, classifier):
            self.preprocessor = preprocessor
            self.classifier = classifier
        
        def preprocess(self, image):
            return self.preprocessor.preprocess_image(image)
        
        def predict(self, image, region=None):
            processed = self.preprocess(image)
            return self.classifier.predict(processed, region)
        
        def train(self, images, labels, **kwargs):
            # Preprocess all training images
            processed_images = [self.preprocess(img) for img in images]
            return self.classifier.train(processed_images, labels, **kwargs)
    
    return ColorDetectionPipeline(preprocessor, classifier)
"""

# ==============================================================================
# END OF UNUSED CLASSES
# ==============================================================================