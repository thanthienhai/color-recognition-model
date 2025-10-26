# Quick Start Guide - Hệ thống Pha màu

## Khởi chạy nhanh trong 3 bước

### Bước 1: Di chuyển vào thư mục UI
```bash
cd color-recognition-model/ui
```

### Bước 2: Chạy script tự động
**Linux/macOS:**
```bash
./run.sh
```

**Windows:**
```cmd
run.bat
```

### Bước 3: Sử dụng
Ứng dụng sẽ mở ra với menu điều hướng bên trái. Nhấn vào các nút để chuyển màn hình!

---

## Hướng dẫn nhanh từng màn hình

### 🎨 Pha màu theo công thức
1. Chọn hệ màu (RAL/Pantone/NCS/Dulux)
2. Chọn mã màu
3. Nhập tên sản phẩm
4. Chọn thể tích
5. Nhấn "Pha màu"

### ✋ Chiết màu bằng tay
1. Nhấn "+ Thêm màu" để thêm dòng
2. Chọn màu gốc và nhập lượng (ml)
3. Nhấn "Pha màu"

### 📷 Pha màu theo mẫu
1. Nhấn "BẮT ĐẦU ĐO MÀU"
2. Đặt mẫu lên thiết bị
3. Nhấn "Tính công thức"
4. Nhấn "Pha màu này"

### 📊 Quản lý màu
- Xem mức màu còn lại trong 16 ống
- Xanh (>30%), Vàng (10-30%), Đỏ (<10%)

### 🔧 Bảo trì
- Khuấy màu: Chọn tốc độ → Bắt đầu
- Vệ sinh: Nhập lượng → Vệ sinh đầu phun

### ⚙️ Hiệu chuẩn
1. Nhập mật khẩu: "admin"
2. Chọn màu gốc
3. Nhập số xung/ml
4. Cập nhật

---

## Troubleshooting nhanh

### Lỗi: "kivy not found"
```bash
pip install kivy==2.2.1
```

### Lỗi: "Permission denied"
```bash
chmod +x run.sh
```

### Ứng dụng không mở
```bash
python3 main.py
```

---

## Liên hệ

**Tài liệu đầy đủ:** Xem README.md, PROJECT_STRUCTURE.md, DEPLOYMENT_GUIDE.md

**Hỗ trợ:** support@colormixing.com
