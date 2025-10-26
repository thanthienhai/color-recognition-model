# Giao diện Kivy - Hệ thống Pha màu tự động

## Giới thiệu

Giao diện người dùng được xây dựng bằng Kivy framework để điều khiển hệ thống pha màu tự động. Hệ thống cung cấp các tính năng chính:

- Pha màu theo công thức có sẵn
- Chiết màu bằng tay (tự tạo công thức)
- Pha màu theo mẫu (sử dụng thiết bị đo màu)
- Quản lý mức màu trong 16 ống chứa
- Bảo trì hệ thống
- Hiệu chuẩn (dành cho kỹ thuật viên)

## Cài đặt

### Yêu cầu hệ thống

- Python 3.8+
- Linux/Windows/macOS

### Cài đặt dependencies

```bash
cd ui
pip install -r requirements.txt
```

### Chạy ứng dụng

```bash
python main.py
```

hoặc

```bash
python3 main.py
```

## Cấu trúc file

```
ui/
├── main.py                      # Ứng dụng chính
├── main.kv                      # Layout chính với menu điều hướng
├── mixbyformulascreen.kv        # Màn hình pha màu theo công thức
├── manualdispensescreen.kv      # Màn hình chiết màu thủ công
├── scancolorscreen.kv           # Màn hình pha màu theo mẫu
├── colorantmanagerscreen.kv     # Màn hình quản lý màu
├── maintenancescreen.kv         # Màn hình bảo trì
├── calibrationscreen.kv         # Màn hình hiệu chuẩn
├── requirements.txt             # Dependencies
└── README.md                    # File này
```

## Sử dụng

### Màn hình chính

Sau khi khởi động, menu điều hướng sẽ xuất hiện bên trái với các nút:
- **Pha màu theo công thức**: Chọn màu từ database công thức có sẵn
- **Chiết màu bằng tay**: Tự tạo công thức bằng cách nhập lượng từng màu
- **Pha màu theo mẫu**: Sử dụng thiết bị đo màu để phân tích mẫu
- **Quản lý màu**: Xem trạng thái và mức màu còn lại
- **Bảo trì**: Khuấy màu, vệ sinh đầu phun
- **Hiệu chuẩn**: Cài đặt kỹ thuật (yêu cầu mật khẩu)

### Pha màu theo công thức

1. Chọn hệ màu (RAL, Pantone, NCS, Dulux)
2. Chọn mã màu cụ thể
3. Nhập tên sản phẩm
4. Chọn thể tích
5. Xem công thức chi tiết và giá
6. Nhấn "Pha màu" để bắt đầu
7. Có thể in nhãn sau khi pha xong

### Chiết màu bằng tay

1. Nhập tên sản phẩm
2. Thêm các dòng màu bằng nút "+ Thêm màu"
3. Chọn màu gốc và nhập lượng (ml) cho mỗi dòng
4. Có thể xóa dòng bằng nút "X"
5. Lưu công thức vào database (nếu cần)
6. Nhấn "Pha màu" để bắt đầu

### Pha màu theo mẫu

1. Nhấn "BẮT ĐẦU ĐO MÀU"
2. Đặt mẫu lên thiết bị đo màu
3. Hệ thống sẽ hiển thị màu và giá trị L*a*b*
4. Nhấn "Tính công thức" để tự động tính toán
5. Xem công thức và sai số ΔE
6. Nhập tên sản phẩm và chọn thể tích
7. Nhấn "Pha màu này" để bắt đầu

### Quản lý màu

- Xem trực quan mức màu còn lại trong 16 ống
- Thanh tiến trình màu xanh (>30%), vàng (10-30%), đỏ (<10%)
- Hiển thị phần trăm và lượng ml còn lại
- Nhấn "Làm mới dữ liệu" để cập nhật

### Bảo trì

**Khuấy màu:**
- Chọn tốc độ: Thấp/Trung bình/Cao
- Nhấn "Bắt đầu khuấy" hoặc "Dừng khuấy"

**Vệ sinh đầu phun:**
- Nhập lượng phun (ml)
- Nhấn "Vệ sinh đầu phun"

### Hiệu chuẩn

⚠️ **Chỉ dành cho kỹ thuật viên**

1. Nhập mật khẩu và nhấn "Mở khóa"
2. Chọn màu gốc cần hiệu chuẩn
3. Nhập số xung cho 1ml và 0.1ml
4. Nhấn "Cập nhật xung"
5. Kiểm tra trạng thái kết nối UART

## Tích hợp backend

Các phương thức trong file `main.py` đã được chuẩn bị để tích hợp với:

- **Database**: SQLite để lưu công thức, mức màu
- **UART Communication**: Gửi lệnh đến phần cứng
- **Color Device API**: Giao tiếp với thiết bị đo màu
- **Business Logic Layer (BLL)**: Tính toán công thức, tối ưu hóa

## TODO - Tích hợp

Các phần cần hoàn thiện:

- [ ] Kết nối SQLite database
- [ ] Implement UART communication layer
- [ ] Tích hợp thuật toán tính công thức từ `/src`
- [ ] API cho thiết bị đo màu
- [ ] In nhãn (thermal printer)
- [ ] Logging và error handling
- [ ] Unit tests

## Ghi chú kỹ thuật

- Kivy 2.2.1 (tương thích Python 3.8-3.11)
- Kv Language để định nghĩa giao diện declarative
- ScreenManager quản lý chuyển đổi màn hình
- Custom widgets cho tái sử dụng
- Responsive layout với size_hint

## Hỗ trợ

Liên hệ: contact@colorrecognition.com
