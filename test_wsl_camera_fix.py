#!/usr/bin/env python3
"""
Test the WSL camera fix
"""

import platform

def test_wsl_detection():
    """Test WSL detection and camera backend selection"""
    print("=== WSL Camera Fix Test ===")
    
    # Test WSL detection
    is_wsl = 'microsoft' in platform.uname().release.lower() or 'wsl' in platform.uname().release.lower()
    print(f"WSL detected: {is_wsl}")
    print(f"Platform: {platform.uname()}")
    
    if is_wsl:
        print("\n=== WSL Camera Setup Instructions ===")
        print("Since you're in WSL, follow these steps:")
        print("1. Install IP Camera Adapter on Windows")
        print("2. Start the camera bridge software")
        print("3. Run the color recognition application")
        print("4. Click 'Tìm' to detect cameras")
        print("5. Select camera with DirectShow backend")
        print("6. Click 'BẮT ĐẦU PREVIEW' to start")
        print("\nRecommended software:")
        print("- IP Camera Adapter (free)")
        print("- SplitCam (free)")
        print("- DroidCam (free)")
        
        print("\n=== Alternative Options ===")
        print("- Use Android phone with IP Webcam app")
        print("- Use USB camera with Windows bridge")
        
    return is_wsl

if __name__ == "__main__":
    wsl_detected = test_wsl_detection()
    
    if wsl_detected:
        print("\n== SOLUTION ==")
        print("The V4L2 error occurs because WSL doesn't support direct camera access.")
        print("You need to use Windows camera bridge software to make cameras available to WSL.")
    else:
        print("\n== REGULAR SYSTEM ==")
        print("Camera should work directly with OpenCV.")
