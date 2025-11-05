#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script để kiểm tra camera preview
"""

import cv2
import numpy as np
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.graphics.texture import Texture
from kivy.clock import Clock


class CameraPreviewTest(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.camera = None
        self.is_active = False
        
        # UI Elements
        self.label = Label(text='Camera Preview Test', size_hint_y=0.1)
        self.image = Image(size_hint_y=0.7)
        
        button_layout = BoxLayout(size_hint_y=0.2)
        self.start_btn = Button(text='Start Camera', size_hint_x=0.5)
        self.stop_btn = Button(text='Stop Camera', size_hint_x=0.5)
        
        self.start_btn.bind(on_press=self.start_camera)
        self.stop_btn.bind(on_press=self.stop_camera)
        
        button_layout.add_widget(self.start_btn)
        button_layout.add_widget(self.stop_btn)
        
        self.add_widget(self.label)
        self.add_widget(self.image)
        self.add_widget(button_layout)
    
    def start_camera(self, instance):
        try:
            print("Bắt đầu camera...")
            self.camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
            
            if not self.camera.isOpened():
                print("Không thể mở camera")
                self.label.text = "Lỗi: Không thể mở camera"
                return
            
            ret, frame = self.camera.read()
            if not ret:
                print("Không thể đọc frame")
                self.label.text = "Lỗi: Không thể đọc frame"
                return
            
            print(f"Camera hoạt động - Frame: {frame.shape}")
            self.label.text = f"Camera hoạt động - {frame.shape}"
            self.is_active = True
            
            # Start preview loop
            Clock.schedule_interval(self.update_frame, 1.0/30.0)
            
        except Exception as e:
            print(f"Lỗi: {e}")
            self.label.text = f"Lỗi: {e}"
    
    def stop_camera(self, instance):
        self.is_active = False
        if self.camera:
            self.camera.release()
            self.camera = None
        self.label.text = "Camera đã dừng"
        Clock.unschedule(self.update_frame)
    
    def update_frame(self, dt):
        if not self.is_active or not self.camera:
            return False
        
        try:
            ret, frame = self.camera.read()
            if ret:
                # Convert BGR to RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Resize if needed
                h, w = frame_rgb.shape[:2]
                max_size = 400
                if max(h, w) > max_size:
                    scale = max_size / max(h, w)
                    new_w = int(w * scale)
                    new_h = int(h * scale)
                    frame_rgb = cv2.resize(frame_rgb, (new_w, new_h))
                    h, w = new_h, new_w
                
                # Create texture
                texture = Texture.create(size=(w, h))
                texture.flip_vertical()
                
                # Convert to bytes and update texture
                buf = frame_rgb.tobytes()
                texture.blit_buffer(buf, colorfmt='rgb', bufferfmt='ubyte')
                
                # Update image
                self.image.texture = texture
                
                return True
            else:
                print("Không đọc được frame")
                return False
                
        except Exception as e:
            print(f"Lỗi update frame: {e}")
            return False


class TestCameraApp(App):
    def build(self):
        return CameraPreviewTest()


if __name__ == '__main__':
    TestCameraApp().run()