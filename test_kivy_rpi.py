#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script để kiểm tra Kivy trên Raspberry Pi
"""

import os
import sys

print("🧪 Testing Kivy installation on Raspberry Pi...")
print(f"Python version: {sys.version}")
print(f"Platform: {sys.platform}")

try:
    import kivy
    print(f"✓ Kivy version: {kivy.__version__}")
except ImportError as e:
    print(f"✗ Kivy not installed: {e}")
    sys.exit(1)

try:
    from kivy.app import App
    from kivy.uix.label import Label
    print("✓ Kivy core modules imported successfully")
except ImportError as e:
    print(f"✗ Kivy core import failed: {e}")
    sys.exit(1)

# Test different window providers
providers = ['sdl2', 'pygame', 'x11', 'egl_rpi']

for provider in providers:
    try:
        os.environ['KIVY_WINDOW'] = provider
        from kivy.core.window import Window
        print(f"✓ Window provider '{provider}' available")
    except Exception as e:
        print(f"✗ Window provider '{provider}' failed: {e}")

print("\n📋 Environment variables:")
for key in ['DISPLAY', 'KIVY_WINDOW', 'KIVY_GRAPHICS', 'SDL_VIDEO_DRIVER']:
    value = os.environ.get(key, 'Not set')
    print(f"  {key}: {value}")

print("\n🎯 Try running the app with different backends:")
print("  ./run_rpi.sh          # SDL2 with auto-detection")
print("  ./run_rpi_pygame.sh   # Pygame backend")
print("  KIVY_WINDOW=x11 python ui/main.py  # X11 if available")
print("  KIVY_WINDOW=egl_rpi python ui/main.py  # EGL if available")
