"""
Custom UI Widgets for AI Color Analysis Display
Các widget tùy chỉnh để hiển thị kết quả phân tích màu AI
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.progressbar import ProgressBar
from kivy.properties import StringProperty, NumericProperty, ListProperty
from kivy.graphics import Color, RoundedRectangle, Line, Ellipse
import colorsys


class ColorComponentBar(BoxLayout):
    """Widget hiển thị thanh phần trăm cho từng màu component"""
    color_name = StringProperty("")
    percentage = NumericProperty(0.0)
    
    def __init__(self, color_name="", percentage=0.0, **kwargs):
        super().__init__(**kwargs)
        self.color_name = color_name
        self.percentage = percentage


class MixingFormulaCard(BoxLayout):
    """Card hiển thị công thức pha màu với màu sắc trực quan"""
    color_name = StringProperty("")
    percentage = NumericProperty(0.0)
    color_rgb = ListProperty([128, 128, 128])  # Default gray
    bg_color = ListProperty([0.95, 0.95, 0.95])  # Light gray background
    
    def __init__(self, color_name="", percentage=0.0, color_rgb=None, **kwargs):
        super().__init__(**kwargs)
        self.color_name = color_name
        self.percentage = percentage
        
        if color_rgb:
            self.color_rgb = color_rgb
            # Generate complementary background color
            self.bg_color = self._get_complementary_bg(color_rgb)
    
    def _get_complementary_bg(self, rgb):
        """Tạo màu nền phù hợp dựa trên màu chính"""
        r, g, b = [x/255.0 for x in rgb]
        h, s, v = colorsys.rgb_to_hsv(r, g, b)
        
        # Create a very light version of the color
        bg_h = h
        bg_s = min(0.15, s * 0.3)  # Very low saturation
        bg_v = max(0.95, 1 - v * 0.1)  # Very high brightness
        
        bg_r, bg_g, bg_b = colorsys.hsv_to_rgb(bg_h, bg_s, bg_v)
        return [bg_r, bg_g, bg_b]


class AIAnalysisPanel(BoxLayout):
    """Panel chính hiển thị kết quả phân tích AI"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Color reference for 12 basic colors
        self.color_references = {
            "Đỏ": [255, 0, 0],
            "Cam": [255, 165, 0],
            "Vàng": [255, 255, 0],
            "Xanh lá": [0, 255, 0],
            "Xanh dương": [0, 0, 255],
            "Tím": [128, 0, 128],
            "Hồng": [255, 192, 203],
            "Nâu": [165, 42, 42],
            "Đen": [0, 0, 0],
            "Trắng": [255, 255, 255],
            "Xám": [128, 128, 128],
            "Xanh lam": [0, 255, 255]
        }
    
    def update_analysis_result(self, prediction):
        """Cập nhật kết quả phân tích AI"""
        try:
            # Update confidence
            confidence_label = self.ids.confidence_label
            confidence_label.text = f'Độ tin cậy: {prediction.confidence:.1%}'
            
            # Update dominant color
            dominant_color_label = self.ids.dominant_color_label
            dominant_percentage_label = self.ids.dominant_percentage_label
            dominant_color_preview = self.ids.dominant_color_preview
            
            dominant_color = prediction.dominant_color
            dominant_percentage = prediction.primary_colors[dominant_color]
            
            dominant_color_label.text = f'Màu chính: {dominant_color}'
            dominant_percentage_label.text = f'Tỉ lệ: {dominant_percentage:.1f}%'
            
            # Update dominant color preview
            self._update_color_preview(dominant_color_preview, dominant_color)
            
            # Update color components
            self._update_color_components(prediction.primary_colors)
            
            # Update mixing formula
            mixing_formula = self._get_mixing_formula(prediction)
            self._update_mixing_formula(mixing_formula)
            
        except Exception as e:
            print(f"Error updating AI analysis panel: {e}")
    
    def _update_color_preview(self, widget, color_name):
        """Cập nhật preview màu dominant"""
        color_rgb = self.color_references.get(color_name, [128, 128, 128])
        r, g, b = [x/255.0 for x in color_rgb]
        
        with widget.canvas:
            widget.canvas.clear()
            Color(r, g, b, 1)
            RoundedRectangle(pos=widget.pos, size=widget.size, radius=[5,])
            Color(0, 0, 0, 0.3)
            Line(rounded_rectangle=[widget.x, widget.y, widget.width, widget.height, 5], width=2)
    
    def _update_color_components(self, color_percentages):
        """Cập nhật danh sách thành phần màu"""
        components_list = self.ids.color_components_list
        components_list.clear_widgets()
        
        # Sort colors by percentage and take top 6
        sorted_colors = sorted(color_percentages.items(), key=lambda x: x[1], reverse=True)[:6]
        
        for color_name, percentage in sorted_colors:
            if percentage > 1.0:  # Only show colors > 1%
                component_bar = ColorComponentBar(
                    color_name=color_name,
                    percentage=percentage
                )
                components_list.add_widget(component_bar)
    
    def _get_mixing_formula(self, prediction):
        """Tạo công thức pha màu từ prediction"""
        # Filter colors > 5% for mixing formula
        significant_colors = {
            color: percentage 
            for color, percentage in prediction.primary_colors.items()
            if percentage > 5.0
        }
        
        if not significant_colors:
            # If no significant colors, use dominant
            return {prediction.dominant_color: 100.0}
        
        # Normalize to 100%
        total = sum(significant_colors.values())
        normalized = {
            color: (percentage / total) * 100
            for color, percentage in significant_colors.items()
        }
        
        return normalized
    
    def _update_mixing_formula(self, formula):
        """Cập nhật công thức pha màu"""
        formula_list = self.ids.mixing_formula_list
        formula_list.clear_widgets()
        
        # Sort by percentage
        sorted_formula = sorted(formula.items(), key=lambda x: x[1], reverse=True)
        
        for color_name, percentage in sorted_formula:
            color_rgb = self.color_references.get(color_name, [128, 128, 128])
            
            formula_card = MixingFormulaCard(
                color_name=color_name,
                percentage=percentage,
                color_rgb=color_rgb
            )
            formula_list.add_widget(formula_card)
    
    def show_loading(self):
        """Hiển thị trạng thái đang phân tích"""
        self.ids.confidence_label.text = "Đang phân tích..."
        self.ids.dominant_color_label.text = "Màu chính: Đang xử lý..."
        self.ids.dominant_percentage_label.text = "Tỉ lệ: --"
        
        # Clear components and formula
        self.ids.color_components_list.clear_widgets()
        self.ids.mixing_formula_list.clear_widgets()
        
        # Add loading message
        loading_label = Label(
            text="🔄 AI đang phân tích màu sắc...",
            font_size='14sp',
            size_hint_y=None,
            height=40,
            color=(0.5, 0.5, 0.5, 1)
        )
        self.ids.color_components_list.add_widget(loading_label)
    
    def show_error(self, error_message="Lỗi phân tích"):
        """Hiển thị lỗi phân tích"""
        self.ids.confidence_label.text = "Lỗi phân tích"
        self.ids.dominant_color_label.text = f"Lỗi: {error_message}"
        self.ids.dominant_percentage_label.text = "Vui lòng thử lại"
        
        # Clear components and formula
        self.ids.color_components_list.clear_widgets()
        self.ids.mixing_formula_list.clear_widgets()
        
        error_label = Label(
            text=f"❌ {error_message}",
            font_size='14sp',
            size_hint_y=None,
            height=40,
            color=(0.8, 0.2, 0.2, 1)
        )
        self.ids.color_components_list.add_widget(error_label)