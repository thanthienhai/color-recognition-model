#!/usr/bin/env python3
"""
WSL Camera Detection Test Script
Test script to verify camera functionality in WSL environment
"""

import sys
import os
import platform

def test_camera_detection():
    """Test camera detection with various backends"""
    
    print("=== WSL Camera Detection Test ===")
    print(f"Python version: {sys.version}")
    print(f"Platform: {platform.platform()}")
    print(f"uname: {platform.uname()}")
    
    # Check if we're in WSL
    global is_wsl
    is_wsl = 'microsoft' in platform.uname().release.lower() or 'wsl' in platform.uname().release.lower()
    print(f"WSL detected: {is_wsl}")
    
    try:
        import cv2
        print(f"OpenCV version: {cv2.__version__}")
        
        # Get available backends
        try:
            backends = cv2.videoio_registry.getBackends()
            print(f"Available backends: {backends}")
        except:
            print("Could not get backends list")
        
        # Test different backends
        backends_to_test = [
            (cv2.CAP_ANY, "ANY"),
            (cv2.CAP_V4L2, "V4L2"),
            (cv2.CAP_FFMPEG, "FFMPEG"),
            (cv2.CAP_GSTREAMER, "GSTREAMER"),
        ]
        
        # Add Windows-specific backends if in WSL
        if is_wsl:
            backends_to_test.extend([
                (cv2.CAP_DSHOW, "DSHOW"),
                (cv2.CAP_MSMF, "MSMF"),
            ])
        
        print("\n=== Testing Camera Backends ===")
        
        for backend, name in backends_to_test:
            print(f"\nTesting {name} backend...")
            
            for i in range(3):  # Test first 3 camera indices
                try:
                    cap = cv2.VideoCapture(i, backend)
                    if cap.isOpened():
                        # Try to read a frame
                        ret, frame = cap.read()
                        if ret:
                            print(f"  ✓ Camera {i} with {name}: {frame.shape}")
                            cap.release()
                            break
                        else:
                            print(f"  ✗ Camera {i} with {name}: Opened but can't read frame")
                            cap.release()
                    else:
                        cap.release()
                except Exception as e:
                    print(f"  ✗ Camera {i} with {name}: Error - {e}")
        
    except ImportError:
        print("OpenCV not installed. Please install with:")
        print("pip install opencv-python")
        return False
    except Exception as e:
        print(f"Error during testing: {e}")
        return False
    
    return True

def check_wsl_camera_setup():
    """Check WSL-specific camera setup requirements"""
    
    print("\n=== WSL Camera Setup Check ===")
    
    if is_wsl:
        print("WSL environment detected. Camera access requires:")
        print("1. USB camera passthrough configuration")
        print("2. Windows camera bridge application")
        print("3. IP camera setup (alternative)")
        print("\nRecommendations:")
        print("- Use Windows camera bridge application like 'IP Camera Adapter'")
        print("- Configure USB device passthrough in WSL config")
        print("- Consider using IP camera for better WSL compatibility")
    else:
        print("Not in WSL environment")

if __name__ == "__main__":
    test_camera_detection()
    check_wsl_camera_setup()
