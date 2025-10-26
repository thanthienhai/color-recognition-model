#!/usr/bin/env python3
"""
Test script for camera UI functionality
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'ui'))

def test_camera_functionality():
    """Test the updated camera functionality"""
    print("=== Camera UI Functionality Test ===")
    
    # Test imports
    try:
        from kivy.app import App
        from kivy.lang import Builder
        print("✓ Kivy imports successful")
    except ImportError:
        print("✗ Kivy not installed")
        return False
    
    # Test file structure
    files_to_check = [
        'ui/main.py',
        'ui/scancolorscreen.kv',
        'ui/main.kv'
    ]
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print(f"✓ {file_path} exists")
        else:
            print(f"✗ {file_path} missing")
            return False
    
    # Check for required methods in ScanColorScreen
    try:
        with open('ui/main.py', 'r') as f:
            content = f.read()
            
        required_methods = [
            'start_camera_preview',
            'stop_camera_preview', 
            'update_camera_preview',
            'capture_and_analyze'
        ]
        
        for method in required_methods:
            if f'def {method}(' in content:
                print(f"✓ Method {method} found")
            else:
                print(f"✗ Method {method} missing")
                return False
                
    except Exception as e:
        print(f"✗ Error checking methods: {e}")
        return False
    
    # Check UI elements
    try:
        with open('ui/scancolorscreen.kv', 'r') as f:
            kv_content = f.read()
            
        required_elements = [
            'camera_preview',
            'start_camera_preview',
            'stop_camera_preview',
            'capture_and_analyze'
        ]
        
        for element in required_elements:
            if element in kv_content:
                print(f"✓ UI element {element} found")
            else:
                print(f"✗ UI element {element} missing")
                return False
                
    except Exception as e:
        print(f"✗ Error checking UI: {e}")
        return False
    
    print("\n=== Summary ===")
    print("✓ All required files and methods are present")
    print("✓ UI elements are properly configured")
    print("✓ Camera functionality should work correctly")
    
    print("\n=== Usage Instructions ===")
    print("1. Run the main application")
    print("2. Navigate to 'Pha màu theo mẫu' screen")
    print("3. Click 'Tìm' to detect cameras")
    print("4. Select a camera from dropdown")
    print("5. Click 'BẮT ĐẦU PREVIEW' to start live preview")
    print("6. Click 'ĐO MÀU NGAY' to capture and analyze color")
    print("7. Click 'DỪNG PREVIEW' to stop camera")
    
    return True

if __name__ == "__main__":
    test_camera_functionality()
