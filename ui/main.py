#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main Kivy Application for Color Mixing System
Hệ thống pha màu tự động
"""

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.progressbar import ProgressBar
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.widget import Widget
from kivy.properties import StringProperty, NumericProperty, ListProperty
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.core.window import Window
import os
import sys

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

try:
    from advanced_color_analysis import ColorAnalysisEngine, ColorPrediction
    print("✓ Advanced Color Analysis module loaded successfully")
except ImportError as e:
    print(f"✗ Failed to import advanced color analysis: {e}")
    ColorAnalysisEngine = None
    ColorPrediction = None


class MixByFormulaScreen(Screen):
    """Màn hình pha màu theo công thức"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.formulas = {}
    
    def on_system_selected(self, spinner, text):
        """Xử lý khi chọn hệ màu"""
        print(f"Hệ màu được chọn: {text}")
        # TODO: Truy vấn CSDL và cập nhật code_spinner
    
    def on_code_selected(self, spinner, text):
        """Xử lý khi chọn mã màu"""
        print(f"Mã màu được chọn: {text}")
        # TODO: Truy vấn CSDL và hiển thị công thức, giá
    
    def start_mixing(self):
        """Bắt đầu pha màu"""
        print("Bắt đầu pha màu theo công thức")
        # TODO: Gọi BLL để pha màu qua UART
    
    def print_label(self):
        """In nhãn"""
        print("In nhãn sản phẩm")
        # TODO: Gửi lệnh in


# Load KV file for Simple Manual Screen
Builder.load_file(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'simplemanualscreen.kv'))

class SimpleManualScreen(Screen):
    """Màn hình lấy màu thủ công đơn giản"""
    
    def start_dispense(self):
        """Bắt đầu pha màu"""
        color_name = self.ids.color_spinner.text
        weight_str = self.ids.weight_spinner.text
        
        if color_name == 'Chọn màu':
            self.show_popup("Lỗi", "Vui lòng chọn màu!")
            return
            
        print(f"Bắt đầu pha màu thủ công: {color_name} - {weight_str}")
        
        try:
            # Parse weight
            weight = float(weight_str.replace('g', '').strip())
            
            # Create mixing data
            # Formula only contains the selected color (100% of the weight)
            # But we need to calculate the absolute weight for this color
            # Since it's a single color, the weight of that color IS the total weight
            
            # Convert color name to field name
            field_name = self.convert_color_name_to_field(color_name)
            
            mixing_data = {
                "weight": weight,
                "mixing_formula": {
                    field_name: weight
                }
            }
            
            # Send via UART
            # Send via UART
            self.send_command(mixing_data)
            
        except Exception as e:
            print(f"Lỗi: {e}")
            self.show_popup("Lỗi", str(e))

    def convert_color_name_to_field(self, color_name: str) -> str:
        """Convert color name to numeric index string (0-14)"""
        color_map = {
            "Đen": "13",
            "Trắng": "0",
            "Vàng Chanh": "8",
            "Đỏ": "3",
            "Xanh Biển Sâu": "1",
            "Xanh Dương": "7",
            "Tím": "10",
            "Nâu": "14",
            "Vàng Neon": "5",
            "Xanh Neon": "4",
            "Xanh Lam Neon": "11",
            "Cam Neon": "9",
            "Hồng Neon": "12",
            "Tím Neon": "15",
            "Vàng Kim": "2"
        }
        
        return color_map.get(color_name, "0") # Default to 0 (Black) if not found

    def send_command(self, mixing_data):
        """Send command via UART or save to file"""
        import json
        from kivy.app import App
        
        # Load config (simplified)
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config.json')
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except:
            config = {'uart': {'enabled': False}}
            
        uart_enabled = config.get('uart', {}).get('enabled', False)
        
        # Format message
        from advanced_color_analysis import ColorAnalysisEngine
        engine = ColorAnalysisEngine()
        content = engine.format_uart_message(mixing_data['mixing_formula'])
        
        if uart_enabled:
            # UART logic (simplified copy from SavedColorWidget)
            try:
                import serial
                uart_config = config.get('uart', {})
                port = uart_config.get('port', '/dev/ttyUSB0')
                baudrate = uart_config.get('baudrate', 115200)
                
                ser = serial.Serial(port, baudrate, timeout=1)
                ser.write(content.encode('utf-8'))
                ser.write(b'\n')
                ser.close()
                self.show_popup("Thành công", f"Đã gửi lệnh pha {mixing_data['weight']}g {self.ids.color_spinner.text}")
            except Exception as e:
                self.show_popup("Lỗi UART", str(e))
        else:
            # Save to file
            output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'mixing_formulas/')
            os.makedirs(output_dir, exist_ok=True)
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"manual_{timestamp}.txt"
            filepath = os.path.join(output_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.show_popup("Đã lưu", f"Đã lưu lệnh vào {filename}")

    def show_popup(self, title, message):
        from kivy.uix.popup import Popup
        from kivy.uix.label import Label
        from kivy.uix.button import Button
        from kivy.uix.boxlayout import BoxLayout
        
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(text=message, size_hint_y=0.8))
        close_btn = Button(text='Đóng', size_hint_y=0.2)
        content.add_widget(close_btn)
        
        popup = Popup(title=title, content=content, size_hint=(0.6, 0.5))
        close_btn.bind(on_press=popup.dismiss)
        popup.open()


class ManualDispenseScreen(Screen):
    """Màn hình chiết màu bằng tay"""
    
    def add_color_row(self):
        """Thêm dòng màu mới"""
        print("Thêm dòng màu mới")
        # TODO: Thêm widget mới vào manual_grid
    
    def remove_color_row(self, row_widget):
        """Xóa dòng màu"""
        print(f"Xóa dòng màu: {row_widget}")
        # TODO: Xóa widget khỏi manual_grid
    
    def save_formula(self):
        """Lưu công thức màu"""
        print("Lưu công thức màu vào CSDL")
        # TODO: Lưu vào database
    
    def start_mixing(self):
        """Bắt đầu pha màu thủ công"""
        print("Bắt đầu pha màu theo công thức thủ công")
        # TODO: Thu thập dữ liệu và gửi lệnh qua UART


class SavedColorWidget(BoxLayout):
    """Widget to display a saved color"""
    color_name = StringProperty("")
    color_rgb = ListProperty([255, 255, 255])
    hex_code = StringProperty("#FFFFFF")
    dominant_color = StringProperty("")
    confidence = NumericProperty(0.0)
    description = StringProperty("")
    color_id = StringProperty("")
    color_data = {}  # Store full color data
    formula = {}
    
    def __init__(self, color_data: dict, **kwargs):
        super().__init__(**kwargs)
        self.color_data = color_data  # Store complete data
        self.color_id = color_data.get('id', '')
        self.color_name = color_data.get('name', 'Unnamed')
        self.color_rgb = color_data.get('rgb', [255, 255, 255])
        self.hex_code = color_data.get('hex', '#FFFFFF')
        self.dominant_color = color_data.get('dominant_color', '')
        self.confidence = color_data.get('confidence', 0.0)
        self.description = color_data.get('description', '')
        self.formula = color_data.get('formula', {})
    
    def on_mix_pressed(self):
        """Handle mix button press - Send via UART or save to local JSON"""
        print("=" * 60)
        print(f"BẮT ĐẦU PHA MÀU TỪ MÀU ĐÃ LƯU: {self.color_name}")
        print("=" * 60)
        
        try:
            import json
            import os
            from datetime import datetime
            from kivy.app import App
            
            # Load config
            config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config.json')
            # Check UART config
            uart_enabled = config.get('uart', {}).get('enabled', False)
            
            if uart_enabled:
                self.send_via_uart(mixing_data, config)
            else:
                self.save_to_local(mixing_data, config)
                
        except Exception as e:
            print(f"✗ Lỗi khi pha màu: {e}")
            import traceback
            traceback.print_exc()
            self.show_error_popup("Lỗi", f"Lỗi khi pha màu: {str(e)}")
    
    def convert_color_name_to_field(self, color_name: str) -> str:
        """Convert color name to numeric index string (0-14)"""
        color_map = {
            "Đen": "13",
            "Trắng": "0",
            "Vàng Chanh": "8",
            "Đỏ": "3",
            "Xanh Biển Sâu": "1",
            "Xanh Dương": "7",
            "Tím": "10",
            "Nâu": "14",
            "Vàng Neon": "5",
            "Xanh Neon": "4",
            "Xanh Lam Neon": "11",
            "Cam Neon": "9",
            "Hồng Neon": "12",
            "Tím Neon": "15",
            "Vàng Kim": "2"
        }
        
        return color_map.get(color_name, "0") # Default to 0 (Black) if not found
    
    def save_to_local(self, mixing_data, config):
        """Save mixing formula to local JSON file"""
        import json
        import os
        from datetime import datetime
        
        try:
            output_dir = config.get('output', {}).get('mixing_formulas_directory', 'mixing_formulas/')
            output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), output_dir)
            os.makedirs(output_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            product_name = mixing_data.get('product_name', 'Unnamed').replace(' ', '_')
            filename = f"mixing_{product_name}_{timestamp}.txt"
            filepath = os.path.join(output_dir, filename)
            
            # Format content
            from advanced_color_analysis import ColorAnalysisEngine
            engine = ColorAnalysisEngine()
            content = engine.format_uart_message(mixing_data['mixing_formula'])
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✓ Đã lưu công thức vào: {filepath}")
            print(f"  Màu: {self.dominant_color}")
            print(f"  Số màu cần pha: {len(mixing_data['mixing_formula'])}")
            
            self.show_success_popup(
                "Đã lưu công thức",
                f"File: {filename}\n\nMàu: {self.dominant_color}\nSố màu: {len(mixing_data['mixing_formula'])}"
            )
            
        except Exception as e:
            print(f"✗ Lỗi khi lưu file: {e}")
            self.show_error_popup("Lỗi lưu file", f"Không thể lưu công thức: {str(e)}")
    
    def send_via_uart(self, mixing_data, config):
        """Send mixing formula via UART"""
        import json
        
        try:
            uart_config = config.get('uart', {})
            port = uart_config.get('port', '/dev/ttyUSB0')
            baudrate = uart_config.get('baudrate', 115200)
            timeout = uart_config.get('timeout', 1)
            
            print(f"📡 Đang gửi qua UART: {port} @ {baudrate}")
            
            try:
                import serial
            except ImportError:
                print("✗ PySerial chưa được cài đặt")
                self.show_error_popup(
                    "PySerial chưa cài đặt",
                    "Vui lòng cài đặt: pip install pyserial\n\nTạm thời lưu vào file local."
                )
                self.save_to_local(mixing_data, config)
                return
            
            try:
                ser = serial.Serial(port, baudrate, timeout=timeout)
                
                # Format message
                from advanced_color_analysis import ColorAnalysisEngine
                engine = ColorAnalysisEngine()
                uart_msg = engine.format_uart_message(mixing_data['mixing_formula'])
                
                ser.write(uart_msg.encode('utf-8'))
                ser.write(b'\n')
                ser.close()
                
                print(f"✓ Đã gửi {len(uart_msg)} bytes qua UART")
                
                self.show_success_popup(
                    "Đã gửi lệnh pha màu",
                    f"Port: {port}\n\nMàu: {self.dominant_color}\nSố màu: {len(mixing_data['mixing_formula'])}"
                )
                
            except Exception as se:
                print(f"✗ Lỗi kết nối UART: {se}")
                self.show_error_popup("Lỗi UART", f"Không thể kết nối {port}\n\nTạm thời lưu vào file local.")
                self.save_to_local(mixing_data, config)
                
        except Exception as e:
            print(f"✗ Lỗi khi gửi UART: {e}")
            self.show_error_popup("Lỗi UART", f"Không thể gửi dữ liệu: {str(e)}")
    
    def show_success_popup(self, title, message):
        """Show success popup"""
        from kivy.uix.popup import Popup
        from kivy.uix.label import Label
        from kivy.uix.button import Button
        from kivy.uix.boxlayout import BoxLayout
        
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(text=message, size_hint_y=0.8, color=(0.2, 0.6, 0.2, 1)))
        close_btn = Button(text='OK', size_hint_y=0.2, background_color=(0.2, 0.7, 0.3, 1))
        content.add_widget(close_btn)
        
        popup = Popup(title=f'✓ {title}', content=content, size_hint=(0.6, 0.5))
        close_btn.bind(on_press=popup.dismiss)
        popup.open()
    
    def show_error_popup(self, title, message):
        """Show error popup"""
        from kivy.uix.popup import Popup
        from kivy.uix.label import Label
        from kivy.uix.button import Button
        from kivy.uix.boxlayout import BoxLayout
        
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(text=message, size_hint_y=0.8, color=(0.8, 0.2, 0.2, 1)))
        close_btn = Button(text='Đóng', size_hint_y=0.2, background_color=(0.8, 0.3, 0.3, 1))
        content.add_widget(close_btn)
        
        popup = Popup(title=f'✗ {title}', content=content, size_hint=(0.6, 0.5))
        close_btn.bind(on_press=popup.dismiss)
        popup.open()


class ColorantManagerScreen(Screen):
    """Màn hình quản lý màu đã lưu"""
    total_colors = NumericProperty(0)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.color_storage = None
        self.all_colors = []
        self.filtered_colors = []
    
    def on_enter(self):
        """Called when screen is entered"""
        self.load_color_storage()
        self.refresh_saved_colors()
    
    def load_color_storage(self):
        """Load color storage module"""
        try:
            from color_storage import color_storage
            self.color_storage = color_storage
            print(f"✓ Color storage loaded: {len(self.color_storage.get_all_colors())} colors")
        except Exception as e:
            print(f"✗ Error loading color storage: {e}")
    
    def refresh_saved_colors(self):
        """Refresh the display of saved colors"""
        if not self.color_storage:
            self.load_color_storage()
        
        if self.color_storage:
            self.all_colors = self.color_storage.get_all_colors()
            self.filtered_colors = self.all_colors.copy()
            self.total_colors = len(self.all_colors)
            self.display_colors(self.filtered_colors)
        else:
            print("✗ Color storage not available")
    
    def display_colors(self, colors_list):
        """Display colors in grid"""
        grid = self.ids.saved_colors_grid
        grid.clear_widgets()
        
        for color_data in colors_list:
            color_widget = SavedColorWidget(color_data)
            grid.add_widget(color_widget)
        
        print(f"Displayed {len(colors_list)} colors")
    
    def search_colors(self, query):
        """Search colors by query"""
        if not query or query.strip() == '':
            self.filtered_colors = self.all_colors.copy()
        else:
            self.filtered_colors = self.color_storage.search_colors(query)
        
        self.display_colors(self.filtered_colors)
    
    def clear_search(self):
        """Clear search filter"""
        if hasattr(self.ids, 'search_input'):
            self.ids.search_input.text = ''
        self.filtered_colors = self.all_colors.copy()
        self.display_colors(self.filtered_colors)


class ColorantStatusWidget(BoxLayout):
    """Widget hiển thị trạng thái một ống màu"""
    colorant_name = StringProperty("")
    level_percent = NumericProperty(100)
    level_ml = NumericProperty(0)


class MaintenanceScreen(Screen):
    """Màn hình bảo trì"""
    
    def start_stirring(self):
        """Bắt đầu khuấy"""
        print("Bắt đầu khuấy màu")
        # TODO: Gửi lệnh STIR qua UART
    
    def stop_stirring(self):
        """Dừng khuấy"""
        print("Dừng khuấy màu")
        # TODO: Gửi lệnh dừng qua UART
    
    def clean_nozzle(self):
        """Vệ sinh đầu phun"""
        print("Vệ sinh đầu phun")
        # TODO: Gửi lệnh CLEAN_NOZZLE qua UART


class CalibrationScreen(Screen):
    """Màn hình hiệu chuẩn"""
    is_unlocked = False
    
    def unlock(self, password):
        """Mở khóa màn hình hiệu chuẩn"""
        # TODO: Kiểm tra mật khẩu
        if password == "admin":  # Placeholder
            self.is_unlocked = True
            print("Đã mở khóa màn hình hiệu chuẩn")
            # TODO: Enable các widget
        else:
            print("Sai mật khẩu")
    
    def update_pulse_calibration(self):
        """Cập nhật hiệu chuẩn xung"""
        print("Cập nhật hiệu chuẩn xung")
        # TODO: Gửi lệnh CALIBRATE_PULSE qua UART


class ScanColorScreen(Screen):
    """Màn hình pha màu theo mẫu"""
    scanned_color = ListProperty([1, 1, 1])
    lab_values = ListProperty([0, 0, 0])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.camera = None
        self.camera_index = None
        self.camera_backend = None
        self.is_camera_active = False
        self.current_prediction = None  # Store latest prediction
        
        # Load configuration
        self.config = self.load_config()
        
        # Initialize color analysis engine
        if ColorAnalysisEngine:
            self.color_analyzer = ColorAnalysisEngine()
            print("✓ Color Analysis Engine initialized")
        else:
            self.color_analyzer = None
            print("✗ Color Analysis Engine not available")
    
    def load_config(self):
        """Load configuration from config.json"""
        import json
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config.json')
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            print(f"✓ Config loaded: UART={'enabled' if config.get('uart', {}).get('enabled', False) else 'disabled'}")
            return config
        except Exception as e:
            print(f"✗ Error loading config: {e}")
            return {
                'uart': {'enabled': False},
                'output': {'mixing_formulas_directory': 'mixing_formulas/'}
            }
    
    def convert_color_name_to_field(self, color_name: str) -> str:
        """Convert color name to numeric index string (0-14)"""
        color_map = {
            "Đen": "13",
            "Trắng": "0",
            "Vàng Chanh": "8",
            "Đỏ": "3",
            "Xanh Biển Sâu": "1",
            "Xanh Dương": "7",
            "Tím": "10",
            "Nâu": "14",
            "Vàng Neon": "5",
            "Xanh Neon": "4",
            "Xanh Lam Neon": "11",
            "Cam Neon": "9",
            "Hồng Neon": "12",
            "Tím Neon": "15",
            "Vàng Kim": "2"
        }
        
        return color_map.get(color_name, "0") # Default to 0 (Black) if not found
    
    def on_leave(self):
        """Khi rời màn hình, dừng camera"""
        self.stop_camera_preview()
    
    def start_scanning(self):
        """Bắt đầu đo màu - WSL compatible"""
        print("Bắt đầu đo màu")
        
        try:
            import cv2
            import numpy as np
            
            # Get selected camera from spinner - fix navigation
            app = App.get_running_app()
            scan_screen = app.root.ids.screen_manager.get_screen('scan_color_screen')
            camera_spinner = scan_screen.ids.camera_spinner
            selected_camera = camera_spinner.text
            
            print(f"Camera được chọn: {selected_camera}")
            
            # Parse camera selection
            camera_index = 0
            backend = cv2.CAP_ANY
            
            if "Camera" in selected_camera:
                # Extract camera index from "Camera X (Backend)" format
                parts = selected_camera.split()
                if parts[1].isdigit():
                    camera_index = int(parts[1])
                
                # Check for specific backend
                if "DirectShow" in selected_camera:
                    backend = cv2.CAP_DSHOW
                elif "Media Foundation" in selected_camera:
                    backend = cv2.CAP_MSMF
                elif "FFmpeg" in selected_camera:
                    backend = cv2.CAP_FFMPEG
                elif "GStreamer" in selected_camera:
                    backend = cv2.CAP_GSTREAMER
                elif "V4L2" in selected_camera:
                    backend = cv2.CAP_V4L2
            else:
                # Handle special cases for WSL
                if "IP Camera" in selected_camera:
                    print("Sử dụng IP camera - cần cấu hình RTSP URL")
                    # TODO: Implement IP camera configuration
                    return
                elif "USB Camera" in selected_camera or "Webcam" in selected_camera:
                    print("Sử dụng camera bridge - cần thiết lập Windows bridge")
                    # TODO: Implement Windows bridge configuration
                    return
                else:
                    print("Không xác định được loại camera")
                    return
            
            # Initialize camera
            cap = cv2.VideoCapture(camera_index, backend)
            
            if not cap.isOpened():
                print(f"Không thể mở camera {camera_index} với backend {backend}")
                return
            
            print(f"Đã mở camera {camera_index} thành công")
            
            # Try to capture a frame
            ret, frame = cap.read()
            if ret:
                print(f"Đã捕获 hình ảnh {frame.shape}")
                
                # Convert to RGB and calculate average color
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Calculate average color (simple color detection)
                avg_color = np.mean(frame_rgb, axis=(0, 1))
                avg_color_normalized = avg_color / 255.0
                
                # Convert to Lab color space
                frame_lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
                avg_lab = np.mean(frame_lab, axis=(0, 1))
                
                # Update UI with detected color
                self.scanned_color = avg_color_normalized.tolist()
                self.lab_values = avg_lab.tolist()
                
                print(f"Màu phát hiện: RGB={avg_color_normalized}, Lab={avg_lab}")
                
                # Update the display
                app = App.get_running_app()
                scan_screen = app.root.ids.screen_manager.get_screen('scan_color_screen')
                lab_label = scan_screen.ids.lab_value_label
                lab_label.text = f'L*: {avg_lab[0]:.2f}  |  a*: {avg_lab[1]:.2f}  |  b*: {avg_lab[2]:.2f}'
                
            else:
                print("Không thể捕获 hình ảnh từ camera")
            
            cap.release()
            
        except ImportError:
            print("OpenCV chưa được cài đặt")
        except Exception as e:
            print(f"Lỗi khi quét màu: {e}")
            import traceback
            traceback.print_exc()
    
    def stop_camera_preview(self):
        """Dừng preview camera"""        
        self.is_camera_active = False
        
        # Unschedule any running updates
        Clock.unschedule(self.update_camera_preview)
        
        if self.camera is not None:
            self.camera.release()
            self.camera = None
            print("✓ Đã dừng camera preview và giải phóng camera")
        else:
            print("✓ Camera preview đã dừng")
    
    def start_camera_preview(self):
        """Bắt đầu preview camera - WSL compatible"""        
        try:
            import cv2
            import numpy as np
            from kivy.core.image import Image as CoreImage
            
            # Get selected camera
            app = App.get_running_app()
            scan_screen = app.root.ids.screen_manager.get_screen('scan_color_screen')
            camera_spinner = scan_screen.ids.camera_spinner
            selected_camera = camera_spinner.text
            
            print(f"Camera được chọn: {selected_camera}")
            
            # Handle WSL-specific camera options
            if "IP Camera" in selected_camera:
                print("IP Camera được chọn - cần cấu hình URL")
                self.setup_ip_camera()
                return
            elif "Windows Webcam Bridge" in selected_camera:
                print("Windows Webcam Bridge được chọn - cần cài đặt bridge software")
                self.setup_windows_bridge()
                return
            elif "USB Camera" in selected_camera:
                print("USB Camera Passthrough được chọn - cần cấu hình WSL USB")
                self.setup_usb_passthrough()
                return
            elif "Android Phone" in selected_camera:
                print("Android Phone Camera được chọn")
                self.setup_android_camera()
                return
            elif "---" in selected_camera:
                print("Vui lòng chọn một camera thực tế")
                return
            
            if "Camera" not in selected_camera:
                print("Vui lòng chọn camera hợp lệ")
                return
            
            # Parse camera selection for DirectShow/Media Foundation
            camera_index = 0
            backend = cv2.CAP_DSHOW  # Default to DirectShow for WSL
            
            parts = selected_camera.split()
            if len(parts) >= 2 and parts[1].isdigit():
                camera_index = int(parts[1])
            
            if "DirectShow" in selected_camera:
                backend = cv2.CAP_DSHOW
                print(f"Sử dụng DirectShow backend cho Camera {camera_index}")
            elif "Media Foundation" in selected_camera:
                backend = cv2.CAP_MSMF
                print(f"Sử dụng Media Foundation backend cho Camera {camera_index}")
            else:
                print(f"Sử dụng default backend (DirectShow) cho Camera {camera_index}")
                backend = cv2.CAP_DSHOW
            
            # Stop existing camera if active
            self.stop_camera_preview()
            
            # Start new camera with specific backend
            print(f"Đang thử mở Camera {camera_index} với backend {backend}")
            self.camera = cv2.VideoCapture(camera_index, backend)
            
            if not self.camera.isOpened():
                print(f"✗ Không thể mở camera {camera_index} với backend {backend}")
                
                # Try alternative backend for WSL
                if backend == cv2.CAP_DSHOW:
                    print("Thử backup backend Media Foundation...")
                    self.camera = cv2.VideoCapture(camera_index, cv2.CAP_MSMF)
                    if self.camera.isOpened():
                        backend = cv2.CAP_MSMF
                        print("✓ Media Foundation backend hoạt động!")
                    else:
                        print("✗ Media Foundation cũng không hoạt động")
                        return
                else:
                    return
            
            # Test if we can actually read a frame
            ret, test_frame = self.camera.read()
            if ret and test_frame is not None:
                print(f"✓ Camera {camera_index} hoạt động - Frame size: {test_frame.shape}")
            else:
                print(f"✗ Camera {camera_index} mở được nhưng không đọc được frame")
                self.camera.release()
                self.camera = None
                return
            
            self.camera_index = camera_index
            self.camera_backend = backend
            self.is_camera_active = True
            
            print(f"✓ Đã mở camera {camera_index} thành công với backend {backend}")
            
            # Start preview loop với delay nhỏ
            Clock.schedule_once(lambda dt: self.update_camera_preview(), 0.5)
            
        except Exception as e:
            print(f"Lỗi khi bắt đầu preview: {e}")
            import traceback
            traceback.print_exc()
    
    def update_camera_preview(self):
        """Cập nhật preview camera"""        
        if not self.is_camera_active or self.camera is None:
            Clock.unschedule(self.update_camera_preview)
            return False
        
        try:
            import cv2
            import numpy as np
            from kivy.graphics.texture import Texture
            
            ret, frame = self.camera.read()
            if ret:
                # Convert BGR to RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Resize frame to fit preview area
                h, w = frame_rgb.shape[:2]
                max_size = 400
                if max(h, w) > max_size:
                    scale = max_size / max(h, w)
                    new_w = int(w * scale)
                    new_h = int(h * scale)
                    frame_rgb = cv2.resize(frame_rgb, (new_w, new_h))
                    h, w = new_h, new_w
                
                # Create texture directly from numpy array
                texture = Texture.create(size=(w, h))
                texture.flip_vertical()
                
                # Convert frame to bytes and blit to texture
                # Draw ROI rectangle on preview
                preview_h, preview_w, _ = frame_rgb.shape
                center_x, center_y = preview_w // 2, preview_h // 2
                roi_size = 50 # Half size (total 100x100)
                
                # Draw green rectangle (0, 255, 0) - thickness 2
                cv2.rectangle(frame_rgb, 
                             (center_x - roi_size, center_y - roi_size),
                             (center_x + roi_size, center_y + roi_size),
                             (0, 255, 0), 2)

                buf = frame_rgb.tobytes()
                texture.blit_buffer(buf, colorfmt='rgb', bufferfmt='ubyte')
                
                # Update preview widget
                try:
                    app = App.get_running_app()
                    if app and app.root:
                        scan_screen = app.root.ids.screen_manager.get_screen('scan_color_screen')
                        camera_preview = scan_screen.ids.camera_preview
                        camera_preview.texture = texture
                        
                        # Force refresh
                        camera_preview.canvas.ask_update()
                        
                        print(f"✓ Preview updated: {w}x{h}")
                except Exception as ui_error:
                    print(f"Lỗi UI update: {ui_error}")
                
                # Schedule next update
                Clock.schedule_once(lambda dt: self.update_camera_preview(), 1.0/30.0)
                return True
                
            else:
                print("Không đọc được frame từ camera")
                self.stop_camera_preview()
                return False
                
        except Exception as e:
            print(f"Lỗi khi cập nhật preview: {e}")
            import traceback
            traceback.print_exc()
            self.stop_camera_preview()
            return False
    
    def capture_and_analyze(self):
        """Chụp ảnh và phân tích màu với AI"""
        if self.camera is None or not self.is_camera_active:
            print("Camera không hoạt động")
            return
        
        try:
            import cv2
            import numpy as np
            
            ret, frame = self.camera.read()
            if ret:
                # Convert to RGB and Lab
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame_lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
                
                # Calculate average color from center ROI (Region of Interest)
                h, w, _ = frame_rgb.shape
                center_x, center_y = w // 2, h // 2
                roi_size = 50  # 100x100 pixel area
                
                # Extract ROI
                roi_rgb = frame_rgb[center_y-roi_size:center_y+roi_size, 
                                  center_x-roi_size:center_x+roi_size]
                roi_lab = frame_lab[center_y-roi_size:center_y+roi_size, 
                                  center_x-roi_size:center_x+roi_size]
                
                # Process input image using robust K-Means and Standard Lab conversion
                if self.color_analyzer:
                    rgb_int, lab_float = self.color_analyzer.process_input_image(roi_rgb)
                    
                    # Update properties for UI
                    self.scanned_color = [x/255.0 for x in rgb_int]
                    self.lab_values = list(lab_float)
                else:
                    # Fallback if analyzer not available
                    avg_color = np.mean(roi_rgb, axis=(0, 1))
                    self.scanned_color = (avg_color / 255.0).tolist()
                    self.lab_values = [0, 0, 0] # Placeholder
                    rgb_int = tuple(int(x) for x in avg_color)
                    lab_float = (0, 0, 0)
                
                print(f"Màu phát hiện: RGB={rgb_int}, Lab={lab_float}")
                
                # AI Color Analysis
                if self.color_analyzer:
                    try:
                        # Analyze using CIEDE2000 (Industry Standard)
                        color_prediction = self.color_analyzer.analyze_color(
                            rgb_values=rgb_int,
                            lab_values=lab_float,
                            method="ciede2000",  # Use CIEDE2000 explicitly
                            image=roi_rgb        # Pass ROI image (prepared for future)
                        )
                        
                        # Display results
                        self.display_color_analysis(color_prediction)
                        
                    except Exception as ai_error:
                        print(f"AI analysis error: {ai_error}")
                        # Fallback to basic display
                        self.display_basic_color_info(lab_float)
                else:
                    # No AI available, show basic info
                    self.display_basic_color_info(lab_float)
                
            else:
                print("Không thể chụp ảnh")
                
        except Exception as e:
            print(f"Lỗi khi phân tích màu: {e}")
            import traceback
            traceback.print_exc()
    
    def display_color_analysis(self, prediction):
        """Hiển thị kết quả phân tích AI đơn giản và hiệu quả"""
        try:
            # Store prediction for later use (mixing)
            self.current_prediction = prediction
            
            app = App.get_running_app()
            scan_screen = app.root.ids.screen_manager.get_screen('scan_color_screen')
            
            # Update Lab values label
            lab_label = scan_screen.ids.lab_value_label
            l, a, b = prediction.lab_values
            lab_label.text = f'L*: {l:.2f}  |  a*: {a:.2f}  |  b*: {b:.2f}'
            
            # Clear and update formula display
            formula_display = scan_screen.ids.result_formula_display
            formula_display.clear_widgets()
            
            # Create simple but effective display
            self._create_simple_color_display(formula_display, prediction)
            
        except Exception as e:
            print(f"Error displaying AI analysis: {e}")
            import traceback
            traceback.print_exc()
            # Fallback to basic info
            self.display_basic_color_info(prediction.lab_values)
    
    def _create_simple_color_display(self, container, prediction):
        """Tạo hiển thị màu dưới dạng bảng"""
        from kivy.uix.label import Label
        from kivy.uix.gridlayout import GridLayout

        # Main title
        title_text = f'{prediction.dominant_color} ({prediction.confidence:.1%})'
        title_label = Label(
            text=title_text,
            font_size='18sp',
            bold=True,
            size_hint_y=None,
            height=40,
            color=(0.1, 0.4, 0.7, 1)
        )
        container.add_widget(title_label)

        # Create a grid layout for color components
        grid = GridLayout(cols=2, size_hint_y=None)
        grid.bind(minimum_height=grid.setter('height'))

        # Add headers
        grid.add_widget(Label(
            text="Màu sắc",
            font_size='16sp',
            bold=True,
            size_hint_y=None,
            height=30,
            color=(0.2, 0.2, 0.2, 1)
        ))
        grid.add_widget(Label(
            text="Tỷ lệ (%)",
            font_size='16sp',
            bold=True,
            size_hint_y=None,
            height=30,
            color=(0.2, 0.2, 0.2, 1)
        ))

        # Add rows for each color component
        sorted_colors = sorted(prediction.primary_colors.items(), key=lambda x: x[1], reverse=True)[:5]
        for color_name, percentage in sorted_colors:
            if percentage > 1.0:
                grid.add_widget(Label(
                    text=color_name,
                    font_size='14sp',
                    size_hint_y=None,
                    height=30,
                    color=(0.2, 0.2, 0.2, 1)
                ))
                grid.add_widget(Label(
                    text=f"{percentage:.1f}%",
                    font_size='14sp',
                    size_hint_y=None,
                    height=30,
                    color=(0.2, 0.2, 0.2, 1)
                ))

        # Add the grid to the container
        container.add_widget(grid)

        # Separator
        separator = Label(
            text='─' * 40,
            font_size='12sp',
            size_hint_y=None,
            height=20,
            color=(0.7, 0.7, 0.7, 1)
        )
        container.add_widget(separator)

        # Mixing formula section with beautiful design
        if self.color_analyzer:
            try:
                mixing_formula = self.color_analyzer.get_mixing_formula(prediction)
                print(f"✓ Mixing formula generated: {mixing_formula}")
            except Exception as e:
                print(f"✗ Error getting mixing formula: {e}")
                mixing_formula = None
            
            if mixing_formula:
                # Formula title
                formula_title = Label(
                    text='CÔNG THỨC PHA',
                    font_size='16sp',
                    bold=True,
                    size_hint_y=None,
                    height=35,
                    color=(0.15, 0.5, 0.25, 1)
                )
                container.add_widget(formula_title)
                
                # Create grid for formula
                formula_grid = GridLayout(cols=3, size_hint_y=None, spacing=5, padding=[10, 5, 10, 5])
                formula_grid.bind(minimum_height=formula_grid.setter('height'))
                
                # Add headers
                formula_grid.add_widget(Label(
                    text="Màu sắc",
                    font_size='14sp',
                    bold=True,
                    size_hint_y=None,
                    height=28,
                    color=(0.3, 0.3, 0.3, 1)
                ))
                formula_grid.add_widget(Label(
                    text="Số phần",
                    font_size='14sp',
                    bold=True,
                    size_hint_y=None,
                    height=28,
                    color=(0.3, 0.3, 0.3, 1)
                ))
                formula_grid.add_widget(Label(
                    text="Tỷ lệ",
                    font_size='14sp',
                    bold=True,
                    size_hint_y=None,
                    height=28,
                    color=(0.3, 0.3, 0.3, 1)
                ))
                
                # Calculate total parts
                total_parts = sum(mixing_formula.values())
                
                # Add formula rows
                for color_name, parts in mixing_formula.items():
                    percentage = (parts / total_parts) * 100 if total_parts > 0 else 0
                    
                    formula_grid.add_widget(Label(
                        text=color_name,
                        font_size='13sp',
                        size_hint_y=None,
                        height=28,
                        color=(0.2, 0.2, 0.2, 1),
                        bold=True
                    ))
                    formula_grid.add_widget(Label(
                        text=f"{parts}",
                        font_size='13sp',
                        size_hint_y=None,
                        height=28,
                        color=(0.15, 0.5, 0.25, 1),
                        bold=True
                    ))
                    formula_grid.add_widget(Label(
                        text=f"{percentage:.1f}%",
                        font_size='13sp',
                        size_hint_y=None,
                        height=28,
                        color=(0.5, 0.5, 0.5, 1)
                    ))
                
                container.add_widget(formula_grid)
                
                # Total summary
                summary_label = Label(
                    text=f'Tổng: {total_parts} phần',
                    font_size='13sp',
                    bold=True,
                    size_hint_y=None,
                    height=30,
                    color=(0.15, 0.5, 0.25, 1)
                )
                container.add_widget(summary_label)
        
        print(f"✓ Beautiful color display created: {prediction.dominant_color}")
    
    def _get_mixing_formula_simple(self, prediction):
        """Tạo công thức pha màu đơn giản"""
        # Filter colors > 5%
        significant_colors = {
            color: percentage 
            for color, percentage in prediction.primary_colors.items()
            if percentage > 5.0
        }
        
        if not significant_colors:
            return {prediction.dominant_color: 100.0}
        
        # Normalize to 100%
        total = sum(significant_colors.values())
        if total > 0:
            normalized = {
                color: (percentage / total) * 100
                for color, percentage in significant_colors.items()
            }
            return normalized
        else:
            return {prediction.dominant_color: 100.0}
    
    def display_basic_color_info(self, lab_values):
        """Hiển thị thông tin màu cơ bản khi AI không khả dụng"""
        try:
            app = App.get_running_app()
            scan_screen = app.root.ids.screen_manager.get_screen('scan_color_screen')
            lab_label = scan_screen.ids.lab_value_label
            l, a, b = lab_values
            lab_label.text = f'L*: {l:.2f}  |  a*: {a:.2f}  |  b*: {b:.2f}'
            
            # Basic color info
            formula_display = scan_screen.ids.result_formula_display
            formula_display.clear_widgets()
            
            info_label = Label(
                text='Phân tích màu cơ bản\nAI chưa khả dụng',
                font_size='14sp',
                size_hint_y=None,
                height=60,
                color=(0.5, 0.5, 0.5, 1)
            )
            formula_display.add_widget(info_label)
            
        except Exception as e:
            print(f"Error displaying basic color info: {e}")

    def setup_ip_camera(self):
        """Setup IP Camera connection"""
        print("=== IP Camera Setup ===")
        print("Để sử dụng IP Camera trong WSL:")
        print("1. Cài đặt IP Webcam app trên điện thoại Android")
        print("2. Mở app và Start server")
        print("3. Nhập URL: http://IP_PHONE:8080/video")
        print("Hoặc sử dụng DroidCam OBS trên Windows")

        # TODO: Add IP URL input dialog
        # self.show_ip_url_dialog()
    
    def setup_windows_bridge(self):
        """Setup Windows Webcam Bridge"""
        print("=== Windows Webcam Bridge Setup ===")
        print("Cần cài đặt bridge software trên Windows:")
        print("1. IP Camera Adapter (miễn phí)")
        print("2. SplitCam (miễn phí)") 
        print("3. DroidCam (miễn phí)")
        print("4. Cài đặt và cấu hình Windows bridge")
        print("5. Chọn lại camera từ danh sách")
        
        # Refresh camera list after bridge setup        
        Clock.schedule_once(lambda dt: self.refresh_cameras_after_bridge(), 1.0)
    
    def setup_usb_passthrough(self):
        """Setup USB Camera Passthrough"""
        print("=== USB Camera Passthrough Setup ===")
        print("Để sử dụng USB Camera trong WSL:")
        print("1. Cắm camera vào Windows")
        print("2. Kiểm tra camera hoạt động trên Windows")
        print("3. Cấu hình WSL USB forwarding:")
        print("   - Edit /etc/wsl.conf")
        print("   - Add: usbip.enable=true")
        print("   - Restart WSL")
        print("4. Hoặc sử dụng Windows camera bridge (khuyến khích)")
        
    def setup_android_camera(self):
        """Setup Android Phone Camera"""
        print("=== Android Phone Camera Setup ===")
        print("Sử dụng điện thoại làm camera:")
        print("1. Cài 'IP Webcam' app trên Android")
        print("2. Mở app và chọn 'Start server'")
        print("3. Ghi chú URL hiển thị (ví dụ: http://192.168.1.100:8080)")
        print("4. Kết nối cùng Wi-Fi với WSL")
        print("5. Sử dụng URL để kết nối")
        
        
    def refresh_cameras_after_bridge(self):
        """Refresh camera list after bridge setup"""
        print("Đàm mới danh sách camera...")
        app = App.get_running_app()
        app.find_cameras()        # TODO: Giao tiếp với thiết bị đo màu qua HAL
        # TODO: Cập nhật scanned_color và lab_values
    
    def calculate_formula(self):
        """Tính toán công thức pha màu từ màu đã đo"""
        print(f"Tính công thức cho màu L*a*b*: {self.lab_values}")

        if not self.color_analyzer:
            print("❌ AI Color Analyzer không khả dụng")
            return

        try:
            # Tạo mock prediction từ lab_values hiện tại
            # Giả sử RGB mặc định từ Lab (đơn giản hóa)
            import cv2
            import numpy as np

            # Convert Lab back to RGB (approximate)
            lab_array = np.uint8([[self.lab_values]])
            rgb_approx = cv2.cvtColor(lab_array, cv2.COLOR_LAB2RGB)[0][0]
            rgb_int = tuple(int(x) for x in rgb_approx)

            # Analyze color để có prediction đầy đủ
            prediction = self.color_analyzer.analyze_color(
                rgb_values=rgb_int,
                lab_values=tuple(self.lab_values),
                method="combined"
            )

            # Lấy mixing formula dạng số phần
            mixing_formula = self.color_analyzer.get_mixing_formula(prediction)
            
            print(f"✓ Formula calculated: {mixing_formula}")

            # Cập nhật UI hiển thị với design đẹp
            app = App.get_running_app()
            scan_screen = app.root.ids.screen_manager.get_screen('scan_color_screen')
            formula_display = scan_screen.ids.result_formula_display
            formula_display.clear_widgets()
            
            # Use the same beautiful display function
            self.display_color_analysis(prediction)

        except Exception as e:
            print(f"Lỗi khi tính công thức: {e}")
            import traceback
            traceback.print_exc()
    
    def save_current_color(self):
        """Save the currently analyzed color"""
        if not self.current_prediction:
            print("⚠ Chưa có kết quả phân tích màu để lưu")
            return
        
        try:
            from color_storage import color_storage
            from kivy.uix.popup import Popup
            from kivy.uix.boxlayout import BoxLayout
            from kivy.uix.textinput import TextInput
            from kivy.uix.button import Button
            from kivy.uix.label import Label
            
            # Create popup for color name input
            content = BoxLayout(orientation='vertical', padding=10, spacing=10)
            
            content.add_widget(Label(
                text='Nhập tên màu:',
                size_hint_y=0.3,
                font_size='16sp'
            ))
            
            name_input = TextInput(
                hint_text='Ví dụ: Xanh Biển Nhạt',
                multiline=False,
                size_hint_y=0.3,
                font_size='14sp'
            )
            content.add_widget(name_input)
            
            desc_input = TextInput(
                hint_text='Mô tả (tùy chọn)',
                multiline=True,
                size_hint_y=0.4,
                font_size='14sp'
            )
            content.add_widget(desc_input)
            
            button_box = BoxLayout(spacing=10, size_hint_y=0.3)
            
            popup = Popup(
                title='Lưu màu',
                content=content,
                size_hint=(0.7, 0.5)
            )
            
            def save_callback(instance):
                color_name = name_input.text.strip() or f"Màu {self.current_prediction.dominant_color}"
                description = desc_input.text.strip()
                
                # Get formula
                formula = self.color_analyzer.get_mixing_formula(
                    self.current_prediction,
                    simplify=True,
                    max_colors=8
                )
                
                # Save to storage
                color_id = color_storage.add_color(
                    name=color_name,
                    rgb=self.current_prediction.rgb_values,
                    lab=self.current_prediction.lab_values,
                    dominant_color=self.current_prediction.dominant_color,
                    confidence=self.current_prediction.confidence,
                    formula=formula,
                    description=description
                )
                
                print(f"✅ Đã lưu màu: {color_name} ({color_id})")
                popup.dismiss()
            
            save_btn = Button(text='Lưu', background_color=(0.3, 0.7, 0.4, 1))
            save_btn.bind(on_press=save_callback)
            button_box.add_widget(save_btn)
            
            cancel_btn = Button(text='Hủy', background_color=(0.7, 0.3, 0.3, 1))
            cancel_btn.bind(on_press=popup.dismiss)
            button_box.add_widget(cancel_btn)
            
            content.add_widget(button_box)
            popup.open()
            
        except Exception as e:
            print(f"❌ Lỗi khi lưu màu: {e}")
            import traceback
            traceback.print_exc()
    
    def start_mixing(self):
        """Pha màu theo mẫu đã đo - Send via UART or save to local JSON"""
        print("=" * 60)
        print("BẮT ĐẦU PHA MÀU")
        print("=" * 60)
        
        if not self.current_prediction:
            print("✗ Chưa có dữ liệu màu. Vui lòng đo màu trước!")
            self.show_error_popup("Chưa có dữ liệu màu", "Vui lòng nhấn 'Đo màu (AI)' trước khi pha màu.")
            return
        
        if not self.color_analyzer:
            print("✗ Color analyzer không khả dụng")
            self.show_error_popup("Lỗi hệ thống", "Color analyzer không khả dụng.")
            return
        
        try:
            # Get mixing formula
            mixing_formula = self.color_analyzer.get_mixing_formula(self.current_prediction)
            
            if not mixing_formula:
                print("✗ Không thể tạo công thức pha màu")
                self.show_error_popup("Lỗi", "Không thể tạo công thức pha màu.")
                return
            
            # Get product info from UI
            app = App.get_running_app()
            scan_screen = app.root.ids.screen_manager.get_screen('scan_color_screen')
            product_name = scan_screen.ids.product_name_input.text or "Unnamed"
            weight_str = scan_screen.ids.volume_spinner.text or "1kg"

            # Convert weight string to grams (e.g., "1kg" -> 1000, "500g" -> 500)
            try:
                weight_str = weight_str.lower().strip()
                if 'kg' in weight_str:
                    weight = float(weight_str.replace('kg', '').strip()) * 1000
                elif 'g' in weight_str:
                    weight = float(weight_str.replace('g', '').strip())
                else:
                    weight = float(weight_str) # Assume grams if no unit
            except ValueError:
                weight = 100.0  # Default fallback (100g)

            # Convert parts to absolute weights (grams) with field names
            total_parts = sum(mixing_formula.values())
            formula_weights = {}
            
            for color, parts in mixing_formula.items():
                percentage = parts / total_parts if total_parts > 0 else 0
                # Calculate absolute weight for this color
                color_weight = percentage * weight
                
                # Convert color name to field name (e.g., "Tím Neon" -> "tim_neon")
                field_name = self.convert_color_name_to_field(color)
                formula_weights[field_name] = round(color_weight, 2)  # Round to 2 decimal places
            
            # Create JSON data (simplified)
            import json
            from datetime import datetime

            mixing_data = {
                "weight": weight,  # Total weight in grams
                "mixing_formula": formula_weights # Absolute weights for each color
            }
            
            # Check UART config
            uart_enabled = self.config.get('uart', {}).get('enabled', False)
            
            if uart_enabled:
                # Send via UART
                self.send_via_uart(mixing_data)
            else:
                # Save to local file
                self.save_to_local(mixing_data)
            
        except Exception as e:
            print(f"✗ Lỗi khi pha màu: {e}")
            import traceback
            traceback.print_exc()
            self.show_error_popup("Lỗi", f"Lỗi khi pha màu: {str(e)}")
    
    def save_to_local(self, mixing_data):
        """Save mixing formula to local JSON file"""
        import json
        from datetime import datetime
        
        try:
            # Create directory if not exists
            output_dir = self.config.get('output', {}).get('mixing_formulas_directory', 'mixing_formulas/')
            os.makedirs(output_dir, exist_ok=True)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            product_name = mixing_data.get('product_name', 'Unnamed').replace(' ', '_')
            filename = f"mixing_{product_name}_{timestamp}.txt"
            filepath = os.path.join(output_dir, filename)
            
            # Format content
            from advanced_color_analysis import ColorAnalysisEngine
            engine = ColorAnalysisEngine()
            content = engine.format_uart_message(mixing_data['mixing_formula'])
            
            # Save to file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✓ Đã lưu công thức vào: {filepath}")
            print(f"  Màu chủ đạo: {self.current_prediction.dominant_color}")
            print(f"  Số màu cần pha: {len(mixing_data['mixing_formula'])}")

            # Show success popup
            self.show_success_popup(
                "Đã lưu công thức",
                f"File: {filename}\nĐường dẫn: {output_dir}\n\nMàu: {self.current_prediction.dominant_color}\nSố màu: {len(mixing_data['mixing_formula'])}"
            )
            
        except Exception as e:
            print(f"✗ Lỗi khi lưu file: {e}")
            import traceback
            traceback.print_exc()
            self.show_error_popup("Lỗi lưu file", f"Không thể lưu công thức: {str(e)}")
    
    def send_via_uart(self, mixing_data):
        """Send mixing formula via UART"""
        import json
        
        try:
            uart_config = self.config.get('uart', {})
            port = uart_config.get('port', '/dev/ttyUSB0')
            baudrate = uart_config.get('baudrate', 115200)
            timeout = uart_config.get('timeout', 1)
            
            print(f"📡 Đang gửi qua UART: {port} @ {baudrate}")
            
            # Try to import serial
            try:
                import serial
            except ImportError:
                print("✗ PySerial chưa được cài đặt")
                print("  Vui lòng cài đặt: pip install pyserial")
                self.show_error_popup(
                    "PySerial chưa cài đặt",
                    "Vui lòng cài đặt: pip install pyserial\n\nTạm thời lưu vào file local."
                )
                # Fallback to local save
                self.save_to_local(mixing_data)
                return
            
            # Open serial port
            try:
                ser = serial.Serial(port, baudrate, timeout=timeout)
                
                # Format message
                from advanced_color_analysis import ColorAnalysisEngine
                engine = ColorAnalysisEngine()
                uart_msg = engine.format_uart_message(mixing_data['mixing_formula'])
                
                # Send data
                ser.write(uart_msg.encode('utf-8'))
                ser.write(b'\n')  # Add newline terminator
                
                print(f"✓ Đã gửi {len(uart_msg)} bytes qua UART")
                print(f"  Màu chủ đạo: {self.current_prediction.dominant_color}")
                print(f"  Số màu cần pha: {len(mixing_data['mixing_formula'])}")

                # Close port
                ser.close()

                # Show success popup
                self.show_success_popup(
                    "Đã gửi lệnh pha màu",
                    f"Port: {port}\n\nMàu: {self.current_prediction.dominant_color}\nSố màu: {len(mixing_data['mixing_formula'])}\n\nHệ thống đang pha màu..."
                )
                
            except serial.SerialException as se:
                print(f"✗ Lỗi kết nối UART: {se}")
                self.show_error_popup(
                    "Lỗi UART",
                    f"Không thể kết nối {port}\n\n{str(se)}\n\nTạm thời lưu vào file local."
                )
                # Fallback to local save
                self.save_to_local(mixing_data)
                
        except Exception as e:
            print(f"✗ Lỗi khi gửi UART: {e}")
            import traceback
            traceback.print_exc()
            self.show_error_popup("Lỗi UART", f"Không thể gửi dữ liệu: {str(e)}")
    
    def show_success_popup(self, title, message):
        """Show success popup message"""
        from kivy.uix.popup import Popup
        from kivy.uix.label import Label
        from kivy.uix.button import Button
        from kivy.uix.boxlayout import BoxLayout
        
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(
            text=message,
            size_hint_y=0.8,
            color=(0.2, 0.6, 0.2, 1)
        ))
        
        close_btn = Button(
            text='OK',
            size_hint_y=0.2,
            background_color=(0.2, 0.7, 0.3, 1)
        )
        content.add_widget(close_btn)
        
        popup = Popup(
            title=f'✓ {title}',
            content=content,
            size_hint=(0.6, 0.5)
        )
        close_btn.bind(on_press=popup.dismiss)
        popup.open()
    
    def show_error_popup(self, title, message):
        """Show error popup message"""
        from kivy.uix.popup import Popup
        from kivy.uix.label import Label
        from kivy.uix.button import Button
        from kivy.uix.boxlayout import BoxLayout
        
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(
            text=message,
            size_hint_y=0.8,
            color=(0.8, 0.2, 0.2, 1)
        ))
        
        close_btn = Button(
            text='Đóng',
            size_hint_y=0.2,
            background_color=(0.8, 0.3, 0.3, 1)
        )
        content.add_widget(close_btn)
        
        popup = Popup(
            title=f'✗ {title}',
            content=content,
            size_hint=(0.6, 0.5)
        )
        close_btn.bind(on_press=popup.dismiss)
        popup.open()
    
    def test_ai_color_analysis(self):
        """Test AI color analysis với màu mẫu"""
        if not self.color_analyzer:
            print("❌ AI Color Analyzer không khả dụng")
            return
        
        # Test với một số màu mẫu
        test_colors = [
            ("Đỏ", (255, 0, 0), (53.23, 80.11, 67.22)),
            ("Xanh lá", (0, 255, 0), (87.74, -86.18, 83.18)),
            ("Vàng", (255, 255, 0), (97.14, -21.55, 94.48)),
            ("Tím", (128, 0, 128), (29.78, 58.93, -36.49)),
        ]
        
        print("\n🧪 Testing AI Color Analysis:")
        print("=" * 50)
        
        for color_name, rgb, lab in test_colors:
            try:
                prediction = self.color_analyzer.analyze_color(
                    rgb_values=rgb,
                    lab_values=lab,
                    method="combined"
                )
                
                print(f"\n🎨 Test: {color_name}")
                print(f"Input RGB: {rgb}")
                print(f"Detected: {prediction.dominant_color} ({prediction.confidence:.1%})")
                print(f"Top 3 components:")
                
                top_3 = list(prediction.primary_colors.items())[:3]
                for comp_color, percentage in top_3:
                    print(f"  • {comp_color}: {percentage:.1f}%")
                
                # Display this test result on UI
                self.scanned_color = [x/255.0 for x in rgb]
                self.lab_values = list(lab)
                self.display_color_analysis(prediction)
                
            except Exception as e:
                print(f"❌ Error testing {color_name}: {e}")
        
        print("=" * 50)


import cv2


class ColorMixingApp(App):
    """Ứng dụng chính"""
    
    def build(self):
        """Xây dựng giao diện"""
        # Load các file .kv
        kv_path = os.path.dirname(os.path.abspath(__file__))
        
        # Load AI display widgets first
        ai_widgets_kv_path = os.path.join(kv_path, 'ai_display_widgets.kv')
        if os.path.exists(ai_widgets_kv_path):
            Builder.load_file(ai_widgets_kv_path)
            print(f"Loaded: ai_display_widgets.kv")
        
        # Load các screen .kv files
        kv_files = [
            'mixbyformulascreen.kv',
            'manualdispensescreen.kv',
            'colorantmanagerscreen.kv',
            'maintenancescreen.kv',
            'calibrationscreen.kv',
            'scancolorscreen.kv'
        ]
        
        for kv_file in kv_files:
            kv_file_path = os.path.join(kv_path, kv_file)
            if os.path.exists(kv_file_path):
                Builder.load_file(kv_file_path)
                print(f"Loaded: {kv_file}")
        
        # Load main.kv cuối cùng
        main_kv_path = os.path.join(kv_path, 'main.kv')
        print(f"Loading main.kv from: {main_kv_path}")
        return Builder.load_file(main_kv_path)

    def find_cameras(self):
        """Tìm các camera có sẵn và cập nhật Spinner - WSL compatible"""
        print("Đang tìm camera...")
        camera_list = []
        
        try:
            import cv2
            
            # Check if running in WSL
            import platform
            is_wsl = 'microsoft' in platform.uname().release.lower() or 'wsl' in platform.uname().release.lower()
            
            if is_wsl:
                print("Phát hiện WSL environment, chỉ thử Windows backends...")
                
                # For WSL, ONLY try Windows-specific backends, skip V4L2
                backends_to_try = [
                    cv2.CAP_DSHOW,    # DirectShow (Windows) - BEST for WSL
                    cv2.CAP_MSMF,     # Media Foundation (Windows) - Good for WSL
                ]
                
                backend_names = ["DirectShow", "Media Foundation"]
                
                for backend_idx, backend in enumerate(backends_to_try):
                    print(f"Thử backend: {backend_names[backend_idx]}")
                    try:
                        for i in range(3):  # Only check first 3 cameras
                            cap = cv2.VideoCapture(i, backend)
                            if cap.isOpened():
                                # Try to read a frame to ensure it works
                                ret, frame = cap.read()
                                if ret and frame is not None:
                                    camera_list.append(f"Camera {i} ({backend_names[backend_idx]})")
                                    print(f"✓ Camera {i} hoạt động với {backend_names[backend_idx]} - {frame.shape}")
                                    cap.release()
                                else:
                                    print(f"✗ Camera {i} mở được nhưng không đọc được frame với {backend_names[backend_idx]}")
                                    cap.release()
                            else:
                                cap.release()
                    except Exception as e:
                        print(f"Lỗi với backend {backend_names[backend_idx]}: {e}")
                        continue
                
                # Always add WSL-specific options
                wsl_options = [
                    "--- WSL Camera Methods ---",
                    "IP Camera (RTSP/HLS)",
                    "Windows Webcam Bridge",
                    "USB Camera Passthrough",
                    "Android Phone Camera"
                ]
                camera_list.extend(wsl_options)
                
            else:
                # Standard camera detection for non-WSL systems
                print("Standard camera detection...")
                for i in range(10):
                    cap = cv2.VideoCapture(i)
                    if cap.isOpened():
                        ret, frame = cap.read()
                        if ret and frame is not None:
                            camera_list.append(f"Camera {i}")
                            print(f"✓ Camera {i} - {frame.shape}")
                            cap.release()
                        else:
                            cap.release()
                            break
            
        except ImportError:
            print("OpenCV chưa được cài đặt")
            camera_list = ["Cần cài đặt OpenCV (pip install opencv-python)"]
        except Exception as e:
            print(f"Lỗi khi tìm camera: {e}")
            camera_list = ["Lỗi phát hiện camera"]
        
        print(f"Tìm thấy: {camera_list}")
        
        # Cập nhật Spinner trên màn hình ScanColorScreen
        try:
            scan_screen = self.root.ids.screen_manager.get_screen('scan_color_screen')
            camera_spinner = scan_screen.ids.camera_spinner
            
            if camera_list:
                camera_spinner.values = camera_list
                camera_spinner.text = camera_list[0]
            else:
                camera_spinner.text = "Không có camera"
                camera_spinner.values = []
        except Exception as e:
            print(f"Lỗi khi cập nhật UI: {e}")
    
    def on_start(self):
        """Khi ứng dụng khởi động"""
        print("Hệ thống pha màu tự động khởi động")

        # Raspberry Pi specific configuration
        import platform
        is_raspberry_pi = 'raspberry' in platform.uname().release.lower() or 'rpi' in platform.uname().release.lower()

        if is_raspberry_pi:
            print("🎯 Phát hiện Raspberry Pi - cấu hình đặc biệt")
            try:
                # Disable fullscreen on RPi to avoid FB config issues
                Window.fullscreen = False
                print("✓ Đã tắt chế độ toàn màn hình cho Raspberry Pi")

                # Try to maximize window instead
                Window.maximize()
                print("✓ Đã maximize cửa sổ")
            except Exception as e:
                print(f"⚠ Không thể cấu hình cửa sổ: {e}")
        else:
            # Set fullscreen mode only if display is available (for other systems)
            try:
                # Check if we have a valid display
                if hasattr(Window, '_window') and Window._window:
                    Window.fullscreen = True
                    print("✓ Đã kích hoạt chế độ toàn màn hình")
                else:
                    print("⚠ Không thể kích hoạt toàn màn hình - không có display hợp lệ")
            except Exception as e:
                print(f"⚠ Không thể kích hoạt toàn màn hình: {e}")

        # TODO: Kiểm tra kết nối UART, khởi tạo CSDL


if __name__ == '__main__':
    ColorMixingApp().run()
