# Hướng dẫn Triển khai (Deployment Guide)
# Color Mixing System UI

## Tổng quan Dự án

**Tổng số dòng code:** ~1,889 dòng
- Python code: 405 dòng (main.py + database.py)
- Kivy layouts: 1,042 dòng (7 files .kv)
- Documentation: 442 dòng (README + PROJECT_STRUCTURE)

**Files:** 15 files
- 2 Python modules
- 7 Kivy layout files
- 2 Script files (run.sh, run.bat)
- 4 Documentation files

## Yêu cầu Hệ thống

### Tối thiểu
- **OS**: Linux, Windows 10+, macOS 10.14+
- **Python**: 3.8 - 3.11
- **RAM**: 2 GB
- **Storage**: 500 MB (cho dependencies)
- **Display**: 1024x768 minimum resolution

### Khuyến nghị
- **OS**: Linux Ubuntu 20.04+ hoặc Windows 11
- **Python**: 3.10
- **RAM**: 4 GB
- **Storage**: 1 GB
- **Display**: 1920x1080 Full HD

## Cài đặt từ đầu

### Bước 1: Clone Repository
```bash
git clone https://github.com/your-repo/color-recognition-model.git
cd color-recognition-model/ui
```

### Bước 2: Tạo Virtual Environment (Khuyến nghị)

**Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
```

### Bước 3: Cài đặt Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Nếu gặp lỗi với Kivy trên Linux:**
```bash
# Cài đặt system dependencies
sudo apt-get update
sudo apt-get install -y python3-pip build-essential git
sudo apt-get install -y libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev
sudo apt-get install -y libportmidi-dev libswscale-dev libavformat-dev libavcodec-dev zlib1g-dev
```

### Bước 4: Khởi chạy

**Sử dụng script (Khuyến nghị):**

Linux/macOS:
```bash
./run.sh
```

Windows:
```cmd
run.bat
```

**Hoặc chạy trực tiếp:**
```bash
python3 main.py
```

## Cấu hình

### Database

Database SQLite sẽ được tự động tạo ở `color_mixing.db` khi khởi chạy lần đầu.

**Vị trí:** `ui/color_mixing.db`

**Sample data** đã được seed tự động:
- 4 hệ màu: RAL, Pantone, NCS, Dulux
- 16 màu gốc với mức hiện tại

### UART Configuration (TODO)

Chỉnh sửa trong `main.py`:
```python
# Thêm vào ColorMixingApp.on_start()
self.uart = serial.Serial(
    port='/dev/ttyUSB0',  # Linux
    # port='COM3',        # Windows
    baudrate=9600,
    timeout=1
)
```

### Display Settings

Kivy sẽ tự động fullscreen. Để chạy windowed mode, tạo file `ui/config.ini`:
```ini
[graphics]
width = 1280
height = 720
resizable = 1
fullscreen = 0
```

## Triển khai Production

### 1. Đóng gói thành Executable

**Sử dụng PyInstaller:**

```bash
pip install pyinstaller

# Linux/macOS
pyinstaller --onefile --windowed --name ColorMixingSystem main.py

# Windows
pyinstaller --onefile --windowed --icon=icon.ico --name ColorMixingSystem main.py
```

**Output:** `dist/ColorMixingSystem` (hoặc `.exe` trên Windows)

### 2. Tạo Installer

**Linux (Debian/Ubuntu):**
```bash
# Tạo .deb package
sudo apt install debhelper
# Tạo cấu trúc DEBIAN/control và build
```

**Windows:**
- Sử dụng NSIS hoặc Inno Setup
- Tạo setup wizard với icon và shortcuts

**macOS:**
- Sử dụng `py2app`
- Tạo .dmg installer

### 3. Docker Container

**Dockerfile:**
```dockerfile
FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY ui/ /app/
RUN pip install -r requirements.txt

CMD ["python", "main.py"]
```

**Build & Run:**
```bash
docker build -t color-mixing-ui .
docker run -it --rm -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix color-mixing-ui
```

## Testing

### Unit Tests (TODO)
```bash
cd ui
pytest tests/
```

### Manual Testing Checklist

- [ ] Màn hình "Pha màu theo công thức"
  - [ ] Chọn hệ màu
  - [ ] Chọn mã màu
  - [ ] Hiển thị công thức
  - [ ] Nút "Pha màu" hoạt động
  - [ ] Nút "In nhãn" hoạt động

- [ ] Màn hình "Chiết màu bằng tay"
  - [ ] Thêm dòng màu
  - [ ] Xóa dòng màu
  - [ ] Nhập lượng cho từng màu
  - [ ] Lưu công thức
  - [ ] Pha màu

- [ ] Màn hình "Pha màu theo mẫu"
  - [ ] Nút đo màu
  - [ ] Hiển thị màu đã đo
  - [ ] Hiển thị L*a*b*
  - [ ] Tính công thức
  - [ ] Pha màu

- [ ] Màn hình "Quản lý màu"
  - [ ] Hiển thị 16 ống
  - [ ] Progress bars chính xác
  - [ ] Màu sắc thay đổi theo mức
  - [ ] Làm mới dữ liệu

- [ ] Màn hình "Bảo trì"
  - [ ] Chọn tốc độ khuấy
  - [ ] Bắt đầu/Dừng khuấy
  - [ ] Vệ sinh đầu phun

- [ ] Màn hình "Hiệu chuẩn"
  - [ ] Bảo vệ mật khẩu
  - [ ] Mở khóa thành công
  - [ ] Chọn màu
  - [ ] Cập nhật xung
  - [ ] Kiểm tra kết nối

## Maintenance

### Backup Database
```bash
# Backup
cp ui/color_mixing.db ui/backups/color_mixing_$(date +%Y%m%d).db

# Restore
cp ui/backups/color_mixing_20240101.db ui/color_mixing.db
```

### Logs

Thêm logging trong `main.py`:
```python
import logging

logging.basicConfig(
    filename='color_mixing.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
```

### Updates

```bash
cd color-recognition-model
git pull origin main
cd ui
pip install -r requirements.txt --upgrade
python3 main.py
```

## Troubleshooting

### Lỗi thường gặp

**1. "ModuleNotFoundError: No module named 'kivy'"**
```bash
pip install kivy==2.2.1
```

**2. "[ERROR] Unable to load kv file"**
- Kiểm tra tất cả file .kv trong thư mục ui/
- Kiểm tra syntax Kv (indentation)

**3. "serial.serialutil.SerialException: could not open port"**
- Kiểm tra device có kết nối: `ls /dev/tty*` (Linux)
- Thêm user vào group dialout: `sudo usermod -a -G dialout $USER`

**4. "sqlite3.OperationalError: unable to open database file"**
- Kiểm tra quyền ghi trong thư mục ui/
- `chmod 755 ui/`

**5. "Kivy window is blank/black"**
- Cập nhật graphics driver
- Thử chạy với: `KIVY_GL_BACKEND=angle_sdl2 python main.py`

### Debug Mode

```bash
# Chạy với verbose logging
KIVY_LOG_LEVEL=debug python3 main.py
```

## Performance Optimization

### Giảm thời gian khởi động
- Precompile .pyc: `python -m compileall ui/`
- Sử dụng PyPy thay vì CPython (nếu tương thích)

### Giảm memory usage
- Giới hạn cache: Thêm trong `config.ini`
```ini
[graphics]
maxfps = 60
```

### Cải thiện responsiveness
- Sử dụng `Clock.schedule_once()` cho async tasks
- Tránh block UI thread với network/file operations

## Security

### Bảo mật mật khẩu
Thay thế plaintext password check:
```python
import hashlib

def check_password(input_pwd):
    hashed = hashlib.sha256(input_pwd.encode()).hexdigest()
    stored_hash = "8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918"  # "admin"
    return hashed == stored_hash
```

### Bảo vệ database
```python
# Encrypt SQLite
# pip install sqlcipher3
import sqlcipher3

db = sqlcipher3.connect('color_mixing.db')
db.execute("PRAGMA key='your-secret-key'")
```

## Hỗ trợ

**Email:** support@colormixing.com
**GitHub Issues:** https://github.com/your-repo/color-recognition-model/issues
**Documentation:** https://docs.colormixing.com

## Changelog

### Version 1.0.0 (Initial Release)
- ✅ 7 màn hình chức năng đầy đủ
- ✅ Database SQLite với sample data
- ✅ Custom widgets (ColorantStatusWidget, ColorRowWidget)
- ✅ Menu điều hướng
- ✅ Password protection cho Calibration
- ✅ Scripts khởi động Linux/Windows

### Version 1.1.0 (Planned)
- 🔄 UART communication
- 🔄 Color device integration
- 🔄 Thermal printer support
- 🔄 Real-time logging
- 🔄 English language support

## License

MIT License - See LICENSE file for details

---

**Build date:** 2024-10-15
**Python version:** 3.8+
**Kivy version:** 2.2.1
