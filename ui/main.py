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
import os


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


class ColorantManagerScreen(Screen):
    """Màn hình quản lý màu"""
    
    def on_enter(self):
        """Khi vào màn hình"""
        self.update_colorant_levels()
    
    def update_colorant_levels(self):
        """Cập nhật mức màu"""
        print("Cập nhật mức màu từ CSDL")
        # TODO: Truy vấn CSDL và cập nhật ProgressBar


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
                lab_label.text = f'L*: {avg_lab[0]:.2f}\\na*: {avg_lab[1]:.2f}\\nb*: {avg_lab[2]:.2f}'
                
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
        if self.camera is not None:
            self.camera.release()
            self.camera = None
            print("Đã dừng camera preview")
    
    def start_camera_preview(self):
        """Bắt đầu preview camera - WSL compatible"""
        try:
            import cv2
            import numpy as np
            from kivy.core.image import Image as CoreImage
            from kivy.clock import Clock
            
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
            
            # Start preview loop
            self.update_camera_preview()
            
        except Exception as e:
            print(f"Lỗi khi bắt đầu preview: {e}")
            import traceback
            traceback.print_exc()
    
    def update_camera_preview(self):
        """Cập nhật preview camera"""
        if not self.is_camera_active or self.camera is None:
            return
        
        try:
            import cv2
            import numpy as np
            from kivy.core.image import Image as CoreImage
            from kivy.clock import Clock
            
            ret, frame = self.camera.read()
            if ret:
                # Convert BGR to RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Resize frame to fit preview area
                h, w = frame_rgb.shape[:2]
                max_size = 300
                if max(h, w) > max_size:
                    scale = max_size / max(h, w)
                    new_w = int(w * scale)
                    new_h = int(h * scale)
                    frame_rgb = cv2.resize(frame_rgb, (new_w, new_h))
                
                # Convert to Kivy format
                buf = cv2.flip(frame_rgb, 0).tobytes()
                texture = CoreImage(np.frombuffer(buf, dtype=np.uint8), 
                                   size=(frame_rgb.shape[1], frame_rgb.shape[0])).texture
                
                # Update preview
                app = App.get_running_app()
                scan_screen = app.root.ids.screen_manager.get_screen('scan_color_screen')
                scan_screen.ids.camera_preview.texture = texture
                
        except Exception as e:
            print(f"Lỗi khi cập nhật preview: {e}")
        
        # Schedule next update
        if self.is_camera_active:
            Clock.schedule_once(lambda dt: self.update_camera_preview(), 0.03)  # ~30 FPS
    
    def capture_and_analyze(self):
        """Chụp ảnh và phân tích màu"""
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
                
                # Calculate average color
                avg_color = np.mean(frame_rgb, axis=(0, 1))
                avg_color_normalized = avg_color / 255.0
                
                avg_lab = np.mean(frame_lab, axis=(0, 1))
                
                # Update properties
                self.scanned_color = avg_color_normalized.tolist()
                self.lab_values = avg_lab.tolist()
                
                print(f"Màu phát hiện: RGB={avg_color_normalized}, Lab={avg_lab}")
                
                # Update display
                app = App.get_running_app()
                scan_screen = app.root.ids.screen_manager.get_screen('scan_color_screen')
                lab_label = scan_screen.ids.lab_value_label
                lab_label.text = f'L*: {avg_lab[0]:.2f}\\na*: {avg_lab[1]:.2f}\\nb*: {avg_lab[2]:.2f}'
                
            else:
                print("Không thể chụp ảnh")
                
        except Exception as e:
            print(f"Lỗi khi phân tích màu: {e}")
            import traceback
            traceback.print_exc()

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
        from kivy.clock import Clock
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
        app.find_cameras()

        # TODO: Giao tiếp với thiết bị đo màu qua HAL
        # TODO: Cập nhật scanned_color và lab_values
    
    def calculate_formula(self):
        """Tính toán công thức"""
        print(f"Tính công thức cho màu L*a*b*: {self.lab_values}")
        # TODO: Gọi BLL để tính toán công thức
    
    def start_mixing(self):
        """Pha màu theo mẫu đã đo"""
        print("Bắt đầu pha màu theo mẫu")
        # TODO: Gửi lệnh pha màu qua UART


import cv2


class ColorMixingApp(App):
    """Ứng dụng chính"""
    
    def build(self):
        """Xây dựng giao diện"""
        # Load các file .kv
        kv_path = os.path.dirname(os.path.abspath(__file__))
        
        # Load các screen .kv files trước
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
        # TODO: Kiểm tra kết nối UART, khởi tạo CSDL


if __name__ == '__main__':
    ColorMixingApp().run()
