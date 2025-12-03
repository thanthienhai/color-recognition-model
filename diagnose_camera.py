import cv2
import platform
import time

def test_camera(index, backend_id, backend_name):
    print(f"\n--- Testing Camera {index} with {backend_name} ---")
    try:
        if backend_id is None:
            cap = cv2.VideoCapture(index)
        else:
            cap = cv2.VideoCapture(index, backend_id)
        
        if not cap.isOpened():
            print(f"❌ Failed to open camera {index}")
            return False
        
        # Try to read a frame
        ret, frame = cap.read()
        if ret and frame is not None:
            h, w = frame.shape[:2]
            print(f"✅ SUCCESS! Resolution: {w}x{h}")
            print(f"   Backend used: {cap.getBackendName()}")
            return True
        else:
            print(f"⚠️ Camera opened but failed to read frame.")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        if 'cap' in locals() and cap.isOpened():
            cap.release()

def main():
    print(f"OpenCV Version: {cv2.__version__}")
    print(f"OS: {platform.system()} {platform.release()}")
    
    print("\nIMPORTANT: Please ensure the 'Camera' app is CLOSED before running this.")
    print("Checking Windows Privacy settings if this fails...\n")

    # 1. Test CAP_ANY (Default)
    print("1. Testing Default Backend (CAP_ANY)...")
    test_camera(0, None, "Default")
    
    # 2. Test DirectShow
    print("2. Testing DirectShow (CAP_DSHOW)...")
    test_camera(0, cv2.CAP_DSHOW, "DirectShow")
    
    # 3. Test Media Foundation
    print("3. Testing Media Foundation (CAP_MSMF)...")
    test_camera(0, cv2.CAP_MSMF, "Media Foundation")

    print("\nDone.")

if __name__ == "__main__":
    main()
