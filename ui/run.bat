@echo off
REM Script khởi chạy ứng dụng Kivy trên Windows

echo ===================================
echo Hệ thống Pha màu Tự động
echo Color Mixing System
echo ===================================
echo.

REM Kiểm tra Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Lỗi: Python chưa được cài đặt
    pause
    exit /b 1
)

echo Python version:
python --version
echo.

REM Kiểm tra virtual environment
if exist "venv\" (
    echo Kích hoạt virtual environment...
    call venv\Scripts\activate.bat
) else if exist "..\venv\" (
    echo Kích hoạt virtual environment từ thư mục gốc...
    call ..\venv\Scripts\activate.bat
)

REM Kiểm tra và cài đặt dependencies
if not exist ".deps_installed" (
    echo Cài đặt dependencies lần đầu...
    pip install -r requirements.txt
    
    if %errorlevel% equ 0 (
        type nul > .deps_installed
        echo Cài đặt thành công!
    ) else (
        echo Lỗi cài đặt dependencies
        pause
        exit /b 1
    )
) else (
    echo Dependencies đã được cài đặt
)

echo.
echo Khởi động ứng dụng...
echo.

REM Chạy ứng dụng
python main.py

echo.
echo Ứng dụng đã đóng
pause
