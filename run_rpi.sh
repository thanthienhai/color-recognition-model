#!/bin/bash
# Script để chạy ứng dụng trên Raspberry Pi
# Chạy: ./run_rpi.sh

echo "🚀 Khởi động ứng dụng pha màu trên Raspberry Pi..."
echo "💡 Nếu gặp lỗi, thử chạy: sudo ./run_rpi.sh"

# Set environment variables for Raspberry Pi
export KIVY_CONFIG_FILE=kivy_rpi.ini

# Try different backends in order
# Option 1: SDL2 with RPi
export KIVY_WINDOW=sdl2
export KIVY_GRAPHICS=gles
export SDL_VIDEO_DRIVER=rpi
export SDL_FBDEV=/dev/fb0
export SDL_VIDEODRIVER=rpi
export SDL_AUDIODRIVER=dummy

# Option 2: Use pygame (more compatible with older RPi)
# export KIVY_WINDOW=pygame
# export KIVY_GRAPHICS=gl

# Option 3: Use egl_rpi (if available)
# export KIVY_WINDOW=egl_rpi
# export KIVY_GRAPHICS=gles

# Check if X11 is available
if command -v xset &> /dev/null && xset q &> /dev/null; then
    echo "✓ Phát hiện X11 desktop environment"
    export KIVY_WINDOW=x11
    export DISPLAY=:0
    python ui/main.py
else
    echo "⚠ Không có X11, thử framebuffer..."
    # Try direct framebuffer first
    export SDL_VIDEO_DRIVER=rpi
    export SDL_FBDEV=/dev/fb0

    if python ui/main.py 2>/dev/null; then
        echo "✓ Chạy thành công với framebuffer"
    else
        echo "⚠ Framebuffer thất bại, thử virtual framebuffer..."
        xvfb-run -a python ui/main.py
    fi
fi
