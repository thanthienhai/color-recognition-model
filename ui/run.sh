#!/bin/bash
# Script khởi chạy ứng dụng Kivy

echo "==================================="
echo "Hệ thống Pha màu Tự động"
echo "Color Mixing System"
echo "==================================="
echo ""

# Kiểm tra Python
if ! command -v python3 &> /dev/null; then
    echo "Lỗi: Python3 chưa được cài đặt"
    exit 1
fi

echo "Python version:"
python3 --version
echo ""

# Kiểm tra virtual environment
if [ -d "venv" ]; then
    echo "Kích hoạt virtual environment..."
    source venv/bin/activate
elif [ -d "../venv" ]; then
    echo "Kích hoạt virtual environment từ thư mục gốc..."
    source ../venv/bin/activate
fi

# Kiểm tra và cài đặt dependencies
if [ ! -f ".deps_installed" ]; then
    echo "Cài đặt dependencies lần đầu..."
    pip install -r requirements.txt
    
    if [ $? -eq 0 ]; then
        touch .deps_installed
        echo "Cài đặt thành công!"
    else
        echo "Lỗi cài đặt dependencies"
        exit 1
    fi
else
    echo "Dependencies đã được cài đặt"
fi

echo ""
echo "Khởi động ứng dụng..."
echo ""

# Chạy ứng dụng
python3 main.py

echo ""
echo "Ứng dụng đã đóng"
