# Kivy UI Integration Guide for CNN Color Ratio Model

This guide provides complete instructions for integrating the CNN color ratio model into the existing Kivy UI application.

## Overview

The integration adds:
1. Method selection UI (Auto/CNN/CIEDE2000)
2. CNN-based color analysis in ScanColorScreen
3. Confidence and quality indicators
4. Comparison view for predictions
5. Automatic fallback handling

## Architecture

```
ScanColorScreen
├── Method Selector (Dropdown/Toggle)
├── Camera Preview
├── Analysis Button
├── Results Display
│   ├── Dominant Color
│   ├── Confidence Bar
│   ├── Quality Badge
│   ├── Color Ratios
│   └── Mixing Formula
└── Comparison View (Optional)
```

## Implementation Steps

### Step 1: Add Method Selection to UI

**File: `ui/scancolorscreen.kv`**

Add method selector widget:

```yaml
<ScanColorScreen>:
    BoxLayout:
        orientation: 'vertical'
        
        # Method Selection
        BoxLayout:
            size_hint_y: 0.1
            padding: 10
            spacing: 10
            
            Label:
                text: 'Analysis Method:'
                size_hint_x: 0.3
            
            Spinner:
                id: method_spinner
                text: 'Auto'
                values: ['Auto', 'CNN', 'CIEDE2000']
                size_hint_x: 0.7
                on_text: root.on_method_changed(self.text)
        
        # Camera Preview
        Camera:
            id: camera
            resolution: (640, 480)
            play: True
        
        # Analysis Button
        Button:
            text: 'Analyze Color'
            size_hint_y: 0.1
            on_press: root.analyze_color()
        
        # Results Display
        BoxLayout:
            id: results_container
            orientation: 'vertical'
            size_hint_y: 0.4
```

### Step 2: Update ScanColorScreen Python Code

**File: `ui/main.py` or `ui/scancolorscreen.py`**

```python
from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, NumericProperty, DictProperty
from kivy.clock import Clock
import numpy as np
import cv2

from advanced_color_analysis import ColorAnalysisEngineV2

class ScanColorScreen(Screen):
    """Screen for scanning and analyzing colors with CNN support."""
    
    # Properties
    analysis_method = StringProperty('Auto')
    confidence = NumericProperty(0.0)
    quality_score = StringProperty('Unknown')
    inference_time = NumericProperty(0.0)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Initialize color analysis engine with CNN
        self.engine = None
        self.cnn_available = False
        
        # Schedule CNN model loading after UI is ready
        Clock.schedule_once(self.load_cnn_model, 1)
    
    def load_cnn_model(self, dt):
        """Load CNN model on startup."""
        try:
            model_path = "models/color_detection/cnn_color_ratio_v1.pth"
            self.engine = ColorAnalysisEngineV2(cnn_model_path=model_path)
            self.cnn_available = self.engine.cnn_available
            
            if self.cnn_available:
                print(f"✓ CNN model loaded successfully")
                self.show_notification("CNN model loaded", "success")
            else:
                print("⚠ CNN model not available, using CIEDE2000")
                self.show_notification("Using CIEDE2000 method", "warning")
        
        except Exception as e:
            print(f"✗ Failed to load CNN model: {e}")
            # Fallback to CIEDE2000 only
            self.engine = ColorAnalysisEngineV2()
            self.cnn_available = False
            self.show_notification("CNN unavailable, using CIEDE2000", "warning")
    
    def on_method_changed(self, method):
        """Handle method selection change."""
        self.analysis_method = method.lower()
        print(f"Analysis method changed to: {self.analysis_method}")
        
        # Update UI to show method-specific info
        if method == 'CNN' and not self.cnn_available:
            self.show_notification("CNN not available, will use CIEDE2000", "warning")
    
    def analyze_color(self):
        """Analyze color from camera using selected method."""
        if not self.engine:
            self.show_notification("Engine not initialized", "error")
            return
        
        try:
            # Capture image from camera
            camera = self.ids.camera
            image = self.capture_camera_image(camera)
            
            if image is None:
                self.show_notification("Failed to capture image", "error")
                return
            
            # Get average color from center region
            rgb, lab = self.get_center_color(image)
            
            # Preprocess image for CNN if needed
            if self.analysis_method in ['auto', 'cnn']:
                processed_image = self.preprocess_for_cnn(image)
            else:
                processed_image = None
            
            # Analyze color
            prediction = self.engine.analyze_color(
                rgb_values=rgb,
                lab_values=lab,
                method=self.analysis_method,
                image=processed_image
            )
            
            # Update UI with results
            self.display_results(prediction)
            
            # Generate and display mixing formula
            formula = self.engine.get_mixing_formula(
                prediction,
                simplify=True,
                max_colors=8
            )
            self.display_formula(formula)
            
        except Exception as e:
            print(f"Error during analysis: {e}")
            self.show_notification(f"Analysis failed: {str(e)}", "error")
    
    def capture_camera_image(self, camera):
        """Capture image from camera widget."""
        try:
            # Get texture from camera
            texture = camera.texture
            if texture is None:
                return None
            
            # Convert to numpy array
            size = texture.size
            pixels = texture.pixels
            
            # Reshape to image array
            image = np.frombuffer(pixels, dtype=np.uint8)
            image = image.reshape(size[1], size[0], 4)  # RGBA
            
            # Convert RGBA to RGB
            image = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)
            
            return image
        
        except Exception as e:
            print(f"Error capturing image: {e}")
            return None
    
    def get_center_color(self, image):
        """Extract average color from center region of image."""
        h, w = image.shape[:2]
        
        # Define center region (20% of image)
        center_h = int(h * 0.4), int(h * 0.6)
        center_w = int(w * 0.4), int(w * 0.6)
        
        # Extract center region
        center_region = image[center_h[0]:center_h[1], center_w[0]:center_w[1]]
        
        # Calculate average RGB
        avg_rgb = np.mean(center_region, axis=(0, 1))
        rgb = tuple(int(v) for v in avg_rgb)
        
        # Convert to Lab
        lab_img = cv2.cvtColor(
            np.uint8([[avg_rgb]]),
            cv2.COLOR_RGB2LAB
        )
        lab = tuple(float(v) for v in lab_img[0, 0])
        
        return rgb, lab
    
    def preprocess_for_cnn(self, image):
        """Preprocess image for CNN inference."""
        # Resize to 224x224
        processed = cv2.resize(image, (224, 224))
        
        # Ensure RGB format
        if processed.shape[2] == 4:
            processed = cv2.cvtColor(processed, cv2.COLOR_RGBA2RGB)
        
        return processed
    
    def display_results(self, prediction):
        """Display prediction results in UI."""
        # Update properties
        self.confidence = prediction.confidence
        self.quality_score = prediction.quality_score or "Unknown"
        self.inference_time = prediction.inference_time_ms or 0.0
        
        # Update UI labels
        self.ids.dominant_color_label.text = f"Dominant: {prediction.dominant_color}"
        self.ids.confidence_label.text = f"Confidence: {prediction.confidence*100:.1f}%"
        self.ids.quality_label.text = f"Quality: {self.quality_score}"
        self.ids.method_label.text = f"Method: {prediction.prediction_method.upper()}"
        
        if prediction.inference_time_ms:
            self.ids.time_label.text = f"Time: {prediction.inference_time_ms:.1f}ms"
        
        # Update confidence progress bar
        self.ids.confidence_bar.value = prediction.confidence * 100
        
        # Update quality badge color
        self.update_quality_badge(self.quality_score)
        
        # Display top colors
        self.display_color_ratios(prediction.primary_colors)
    
    def update_quality_badge(self, quality):
        """Update quality badge appearance."""
        badge = self.ids.quality_badge
        
        color_map = {
            'Excellent': (0.2, 0.8, 0.2, 1),  # Green
            'Good': (0.5, 0.8, 0.2, 1),       # Yellow-green
            'Acceptable': (0.9, 0.7, 0.2, 1), # Orange
            'Poor': (0.9, 0.2, 0.2, 1)        # Red
        }
        
        badge.background_color = color_map.get(quality, (0.5, 0.5, 0.5, 1))
        badge.text = quality
    
    def display_color_ratios(self, primary_colors):
        """Display color ratios in UI."""
        container = self.ids.ratios_container
        container.clear_widgets()
        
        # Show top 5 colors
        for color_name, percentage in list(primary_colors.items())[:5]:
            # Create ratio display widget
            ratio_widget = self.create_ratio_widget(color_name, percentage)
            container.add_widget(ratio_widget)
    
    def create_ratio_widget(self, color_name, percentage):
        """Create widget to display single color ratio."""
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.label import Label
        from kivy.uix.progressbar import ProgressBar
        
        layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=30)
        
        # Color name
        name_label = Label(
            text=color_name,
            size_hint_x=0.4,
            halign='left'
        )
        layout.add_widget(name_label)
        
        # Progress bar
        progress = ProgressBar(
            max=100,
            value=percentage,
            size_hint_x=0.4
        )
        layout.add_widget(progress)
        
        # Percentage label
        pct_label = Label(
            text=f"{percentage:.1f}%",
            size_hint_x=0.2
        )
        layout.add_widget(pct_label)
        
        return layout
    
    def display_formula(self, formula):
        """Display mixing formula in UI."""
        container = self.ids.formula_container
        container.clear_widgets()
        
        # Create formula display
        from kivy.uix.label import Label
        
        formula_text = "Mixing Formula:\n"
        for color, parts in formula.items():
            formula_text += f"  {color}: {parts} parts\n"
        
        formula_label = Label(
            text=formula_text,
            halign='left',
            valign='top'
        )
        container.add_widget(formula_label)
        
        # Validate and show status
        validation = self.engine.validate_mixing_formula(formula)
        if validation['valid']:
            self.show_notification("Formula valid", "success")
        else:
            self.show_notification(
                f"Formula issues: {', '.join(validation['errors'])}",
                "warning"
            )
    
    def show_notification(self, message, level="info"):
        """Show notification to user."""
        # Implement notification display
        print(f"[{level.upper()}] {message}")
        
        # You can use Kivy's Popup or custom notification widget
        # Example:
        # from kivy.uix.popup import Popup
        # popup = Popup(title=level.capitalize(), content=Label(text=message))
        # popup.open()
```

### Step 3: Add UI Widgets for Results Display

**File: `ui/scancolorscreen.kv`** (continued)

```yaml
        # Results Display Section
        BoxLayout:
            id: results_container
            orientation: 'vertical'
            padding: 10
            spacing: 5
            
            # Dominant Color and Confidence
            BoxLayout:
                size_hint_y: None
                height: 40
                
                Label:
                    id: dominant_color_label
                    text: 'Dominant: --'
                    size_hint_x: 0.5
                
                Label:
                    id: confidence_label
                    text: 'Confidence: --%'
                    size_hint_x: 0.5
            
            # Confidence Progress Bar
            ProgressBar:
                id: confidence_bar
                max: 100
                value: 0
                size_hint_y: None
                height: 20
            
            # Quality Badge and Method
            BoxLayout:
                size_hint_y: None
                height: 40
                spacing: 10
                
                Button:
                    id: quality_badge
                    text: 'Unknown'
                    size_hint_x: 0.4
                    disabled: True
                
                Label:
                    id: method_label
                    text: 'Method: --'
                    size_hint_x: 0.4
                
                Label:
                    id: time_label
                    text: 'Time: --'
                    size_hint_x: 0.2
            
            # Color Ratios
            Label:
                text: 'Color Composition:'
                size_hint_y: None
                height: 30
                bold: True
            
            ScrollView:
                id: ratios_scroll
                size_hint_y: 0.4
                
                BoxLayout:
                    id: ratios_container
                    orientation: 'vertical'
                    size_hint_y: None
                    height: self.minimum_height
            
            # Mixing Formula
            Label:
                text: 'Mixing Formula:'
                size_hint_y: None
                height: 30
                bold: True
            
            ScrollView:
                size_hint_y: 0.3
                
                BoxLayout:
                    id: formula_container
                    orientation: 'vertical'
                    size_hint_y: None
                    height: self.minimum_height
```

### Step 4: Add Comparison View (Optional)

Create a comparison popup to show CNN vs CIEDE2000 side-by-side:

```python
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label

class ComparisonPopup(Popup):
    """Popup to compare CNN and CIEDE2000 predictions."""
    
    def __init__(self, cnn_prediction, ciede_prediction, **kwargs):
        super().__init__(**kwargs)
        
        self.title = "CNN vs CIEDE2000 Comparison"
        self.size_hint = (0.9, 0.9)
        
        # Create layout
        layout = BoxLayout(orientation='horizontal', padding=10, spacing=10)
        
        # CNN results
        cnn_box = self.create_prediction_box("CNN", cnn_prediction)
        layout.add_widget(cnn_box)
        
        # CIEDE2000 results
        ciede_box = self.create_prediction_box("CIEDE2000", ciede_prediction)
        layout.add_widget(ciede_box)
        
        self.content = layout
    
    def create_prediction_box(self, title, prediction):
        """Create box showing prediction results."""
        box = BoxLayout(orientation='vertical', spacing=5)
        
        # Title
        box.add_widget(Label(text=title, bold=True, size_hint_y=None, height=30))
        
        # Dominant color
        box.add_widget(Label(
            text=f"Dominant: {prediction.dominant_color}",
            size_hint_y=None,
            height=25
        ))
        
        # Confidence
        box.add_widget(Label(
            text=f"Confidence: {prediction.confidence*100:.1f}%",
            size_hint_y=None,
            height=25
        ))
        
        # Quality
        box.add_widget(Label(
            text=f"Quality: {prediction.quality_score}",
            size_hint_y=None,
            height=25
        ))
        
        # Top 3 colors
        box.add_widget(Label(text="Top 3 Colors:", bold=True, size_hint_y=None, height=25))
        for i, (color, pct) in enumerate(list(prediction.primary_colors.items())[:3]):
            box.add_widget(Label(
                text=f"{i+1}. {color}: {pct:.1f}%",
                size_hint_y=None,
                height=25
            ))
        
        return box

# Usage in ScanColorScreen:
def show_comparison(self):
    """Show comparison between CNN and CIEDE2000."""
    # Get both predictions
    cnn_pred = self.engine.analyze_color(
        self.current_rgb,
        self.current_lab,
        method="cnn",
        image=self.current_image
    )
    
    ciede_pred = self.engine.analyze_color(
        self.current_rgb,
        self.current_lab,
        method="ciede2000"
    )
    
    # Show comparison popup
    popup = ComparisonPopup(cnn_pred, ciede_pred)
    popup.open()
```

## Testing the Integration

### Unit Tests

Create `tests/test_kivy_integration.py`:

```python
import pytest
from unittest.mock import Mock, patch
import numpy as np

def test_method_selection():
    """Test method selection changes."""
    screen = ScanColorScreen()
    screen.on_method_changed('CNN')
    assert screen.analysis_method == 'cnn'

def test_cnn_fallback():
    """Test fallback when CNN unavailable."""
    with patch('advanced_color_analysis.ColorAnalysisEngineV2') as mock_engine:
        mock_engine.return_value.cnn_available = False
        screen = ScanColorScreen()
        screen.load_cnn_model(0)
        assert screen.cnn_available is False

def test_image_preprocessing():
    """Test image preprocessing for CNN."""
    screen = ScanColorScreen()
    image = np.random.randint(0, 256, (480, 640, 3), dtype=np.uint8)
    processed = screen.preprocess_for_cnn(image)
    assert processed.shape == (224, 224, 3)
```

## Deployment Checklist

- [ ] CNN model file exists at `models/color_detection/cnn_color_ratio_v1.pth`
- [ ] ColorAnalysisEngineV2 is imported correctly
- [ ] Method selector UI is added to scancolorscreen.kv
- [ ] Results display widgets are added
- [ ] Error handling is implemented
- [ ] Fallback to CIEDE2000 works correctly
- [ ] UI updates smoothly without blocking
- [ ] Notifications are displayed to users
- [ ] Formula validation is working
- [ ] UART integration is tested

## Performance Optimization

1. **Async Loading**: Load CNN model asynchronously to avoid UI blocking
2. **Image Caching**: Cache preprocessed images to avoid redundant processing
3. **Batch Processing**: If analyzing multiple colors, use batch inference
4. **GPU Acceleration**: Ensure PyTorch uses GPU if available

## Troubleshooting

### CNN Model Not Loading
- Check model file path
- Verify PyTorch is installed
- Check device compatibility (CPU/GPU)

### Slow Inference
- Use GPU if available
- Reduce image size before preprocessing
- Consider model quantization

### UI Freezing
- Use threading for inference
- Show loading indicator during analysis
- Implement timeout for long operations

## Next Steps

1. Test with real camera images
2. Fine-tune UI layout and colors
3. Add settings screen for model configuration
4. Implement model update mechanism
5. Add analytics and logging
