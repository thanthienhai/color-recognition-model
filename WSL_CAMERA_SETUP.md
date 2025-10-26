# WSL Camera Setup Guide

This guide explains how to set up camera access in WSL (Windows Subsystem for Linux) for the color recognition model application.

## Problem Description

When using WSL, you may encounter camera errors like:
```
[ WARN:0@22.492] global cap_v4l.cpp:914 open VIDEOIO(V4L2:/dev/video9): can't open camera by index
[ERROR:0@22.492] global obsensor_uvc_stream_channel.cpp:163 getStreamChannelGroup Camera index out of range
```

This happens because WSL doesn't have direct access to Windows hardware devices like cameras.

## Solutions

### Option 1: Windows Camera Bridge (Recommended)

1. **Install a camera bridge application on Windows:**
   - Download and install "IP Camera Adapter" or "SplitCam"
   - These applications create a virtual camera that can be accessed from WSL

2. **Configure the bridge:**
   - Select your physical camera in the bridge application
   - Set up the virtual camera output

3. **Test in WSL:**
   - Run the application and click "Tìm" (Find) button
   - Look for camera options with "(DirectShow)" or "(Media Foundation)" in the name

### Option 2: IP Camera Setup

1. **Install IP camera software on Windows:**
   - Use applications like "IP Webcam" (for Android phones as temporary solution)
   - Or "Yawcam" for Windows webcams

2. **Get the RTSP/HTTP URL:**
   - Usually looks like: `http://192.168.x.x:8080/video`
   - Or RTSP: `rtsp://192.168.x.x:554/stream`

3. **Configure in the application:**
   - Select "IP Camera (rtsp://)" option
   - Enter the URL when prompted

### Option 3: USB Device Passthrough (Advanced)

1. **Enable USB device passthrough:**
   - Edit `/etc/wsl.conf` on your WSL distribution
   - Add: `automount=true` and configure USB device rules

2. **Connect camera via USB:**
   - Ensure camera is properly connected to Windows
   - Check device manager for camera device ID

3. **Test device access:**
   - Run: `ls /dev/video*` in WSL
   - If devices appear, use V4L2 backend

## Application Features

The updated camera detection system now includes:

- **Multi-backend support:** Tries different OpenCV backends automatically
- **WSL detection:** Automatically switches to Windows-specific backends in WSL
- **Fallback options:** Provides IP camera and bridge alternatives
- **Better error handling:** Shows specific error messages and suggestions

## Troubleshooting

### No cameras found:
1. Ensure your camera works in Windows first
2. Check if camera drivers are properly installed
3. Try different USB ports
4. Restart camera bridge application

### Camera opens but can't capture:
1. Camera might be used by another application
2. Try closing other camera apps (Zoom, Teams, etc.)
3. Restart the camera bridge application

### V4L2 errors in WSL:
1. This is expected behavior - WSL doesn't support V4L2 directly
2. Use Windows backends (DirectShow, Media Foundation) instead
3. Install a camera bridge application

## Testing

Run the camera test script to verify setup:
```bash
python3 wsl_camera_test.py
```

This will test different backends and show which ones work in your environment.

## Updates Made

### Fixed Issues:
1. **Screen Navigation Error**: Fixed `BoxLayout object has no attribute 'get_screen'` by using proper app reference
2. **Camera Backend Support**: Added comprehensive WSL-compatible camera detection with multiple backends
3. **Live Preview**: Added real-time camera preview functionality
4. **UI Improvements**: Split preview area into camera view and detected color display

### New Features:
- **Live Camera Preview**: See camera feed in real-time before capturing
- **Multiple Camera Backends**: Automatic testing of DirectShow, Media Foundation, FFmpeg, GStreamer, V4L2
- **Enhanced UI**: Separate preview and capture areas
- **Automatic Detection**: Camera preview starts when selecting camera from dropdown

### Button Functions:
- **"BẮT ĐẦU PREVIEW"**: Start live camera preview
- **"DỪNG PREVIEW"**: Stop camera preview
- **"ĐO MÀU NGAY"**: Capture frame and analyze color
- **"Tìm"**: Detect available cameras

## Quick Start

1. Install a camera bridge application on Windows (recommended: IP Camera Adapter)
2. Start the bridge and select your camera
3. Run the color recognition application
4. Navigate to "Pha màu theo mẫu" screen
5. Click "Tìm" to detect cameras
6. Select the camera with "(DirectShow)" in the name
7. Click "BẮT ĐẦU PREVIEW" to start live preview
8. Click "ĐO MÀU NGAY" to capture and analyze color
9. Click "DỪNG PREVIEW" when done

## Technical Implementation

### Code Changes:
- `ui/main.py`: Updated ScanColorScreen class with camera management methods
- `ui/scancolorscreen.kv`: Enhanced UI with camera preview area
- Added proper WSL detection and backend switching
- Implemented frame capture and color analysis
- Added automatic camera cleanup when leaving screen

### Error Handling:
- Graceful fallback when cameras aren't available
- Clear error messages for different failure modes
- Automatic camera resource cleanup

For more help, check the application logs for specific error messages.
