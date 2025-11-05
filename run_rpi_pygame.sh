#!/bin/bash
# Script để chạy ứng dụng với pygame backend trên Raspberry Pi

echo "🚀 Khởi động ứng dụng pha màu với pygame backend..."

# Set environment variables for pygame
export KIVY_WINDOW=pygame
export KIVY_GRAPHICS=gl
export SDL_AUDIODRIVER=dummy

# Disable fullscreen in code by setting environment
export KIVY_NO_FULLSCREEN=1

# Run the application
python ui/main.py
