# Cấu trúc Dự án UI - Hệ thống Pha màu Tự động

## Tổng quan

Dự án này xây dựng giao diện người dùng (UI) hoàn chỉnh bằng Kivy framework cho hệ thống pha màu tự động. Giao diện được thiết kế theo tài liệu từ `.memory_bank/ui.md` với 7 màn hình chính.

## Cấu trúc File

```
ui/
├── main.py                      # [6.2 KB] Ứng dụng chính Kivy với các Screen classes
├── main.kv                      # [3.1 KB] Layout chính với menu điều hướng và ScreenManager
│
├── mixbyformulascreen.kv        # [3.6 KB] Giao diện pha màu theo công thức
├── manualdispensescreen.kv      # [2.7 KB] Giao diện chiết màu thủ công
├── scancolorscreen.kv           # [6.7 KB] Giao diện pha màu theo mẫu (đo màu)
├── colorantmanagerscreen.kv     # [5.1 KB] Giao diện quản lý 16 ống màu
├── maintenancescreen.kv         # [6.3 KB] Giao diện bảo trì hệ thống
├── calibrationscreen.kv         # [6.5 KB] Giao diện hiệu chuẩn (có bảo vệ mật khẩu)
│
├── database.py                  # [7.1 KB] Module quản lý SQLite database (stub)
├── requirements.txt             # [181 B] Dependencies cho Kivy và các thư viện
├── __init__.py                  # Package marker
│
├── run.sh                       # [1.2 KB] Script khởi động cho Linux/macOS
├── run.bat                      # [1.2 KB] Script khởi động cho Windows
│
├── README.md                    # [4.8 KB] Hướng dẫn sử dụng chi tiết
└── PROJECT_STRUCTURE.md         # File này - Tổng quan cấu trúc
```

## Kiến trúc Ứng dụng

### 1. main.py - Application Core

**Classes:**
- `ColorMixingApp`: Ứng dụng chính Kivy
- `MixByFormulaScreen`: Màn hình pha màu theo công thức
- `ManualDispenseScreen`: Màn hình chiết màu thủ công
- `ScanColorScreen`: Màn hình pha màu theo mẫu
- `ColorantManagerScreen`: Màn hình quản lý màu
- `ColorantStatusWidget`: Widget custom hiển thị trạng thái ống màu
- `MaintenanceScreen`: Màn hình bảo trì
- `CalibrationScreen`: Màn hình hiệu chuẩn

**Luồng khởi động:**
1. Load các file .kv cho từng screen
2. Load main.kv (layout chính)
3. Khởi tạo ScreenManager
4. Kiểm tra kết nối (UART, Database)

### 2. Layout Files (.kv)

#### main.kv
- BoxLayout horizontal: Menu (20%) + ScreenManager (80%)
- 6 nút điều hướng với màu sắc riêng
- ScreenManager quản lý 6 màn hình

#### mixbyformulascreen.kv
- Spinners: Hệ màu, Mã màu, Thể tích
- TextInput: Tên sản phẩm
- Labels: Base type, Giá tiền
- ScrollView: Hiển thị công thức chi tiết
- Buttons: Pha màu, In nhãn

#### manualdispensescreen.kv
- ColorRowWidget: Custom widget cho mỗi dòng màu
- GridLayout động: Thêm/xóa dòng màu
- Buttons: Thêm màu, Lưu công thức, Pha màu

#### scancolorscreen.kv
- Layout 2 cột: Điều khiển (45%) + Công thức (55%)
- Widget hiển thị màu đã đo (canvas)
- Label hiển thị L*a*b* values
- Delta E display
- Buttons: Đo màu, Tính công thức, Pha màu

#### colorantmanagerscreen.kv
- ColorantStatusWidget: 16 ống màu
- GridLayout 4 cột
- ProgressBar dọc với màu động (xanh/vàng/đỏ)
- Hiển thị % và ml

#### maintenancescreen.kv
- Khu vực khuấy: ToggleButtons cho tốc độ
- Khu vực vệ sinh: TextInput lượng phun
- Khu vực kiểm tra: Status label
- Các buttons điều khiển

#### calibrationscreen.kv
- Password protection: TextInput + Button mở khóa
- Hiệu chuẩn xung: Spinner chọn màu, TextInputs xung
- Trạng thái kết nối
- Warning label

### 3. database.py - Data Layer

**Class ColorDatabase:**
- `init_database()`: Tạo schema SQLite
- `get_color_systems()`: Danh sách hệ màu
- `get_color_codes()`: Mã màu theo hệ
- `get_formula()`: Chi tiết công thức
- `get_colorant_levels()`: Mức màu hiện tại
- `update_colorant_level()`: Cập nhật sau pha màu

**Tables:**
- `color_systems`: Các hệ màu (RAL, Pantone, NCS, Dulux)
- `color_formulas`: Công thức màu
- `formula_details`: Chi tiết từng màu gốc trong công thức
- `colorants`: 16 ống màu với mức hiện tại và calibration

## Tính năng đã Implement

### ✅ Hoàn thành
- [x] Cấu trúc ứng dụng Kivy với ScreenManager
- [x] 6 màn hình chức năng đầy đủ
- [x] Menu điều hướng với màu sắc riêng biệt
- [x] Layout responsive với size_hint
- [x] Custom widgets (ColorantStatusWidget, ColorRowWidget)
- [x] Database schema và sample data
- [x] Password protection cho màn hình Calibration
- [x] Color preview với canvas
- [x] Dynamic form (thêm/xóa dòng màu)
- [x] Progress bars cho mức màu
- [x] Scripts khởi động cho Linux/Windows

### 🔄 Cần tích hợp (TODOs trong code)
- [ ] UART communication layer
- [ ] Kết nối với thiết bị đo màu
- [ ] Tích hợp thuật toán tính công thức từ `/src`
- [ ] In nhãn (thermal printer integration)
- [ ] Real-time status updates
- [ ] Error handling và logging
- [ ] Unit tests

## Nguyên tắc Thiết kế

### 1. Nhất quán (Consistency)
- Màu nền: 0.95, 0.95, 0.95 (light gray)
- Menu background: 0.15, 0.15, 0.2 (dark blue-gray)
- Text color: 0, 0, 0 (black) hoặc 1, 1, 1 (white)
- Font size: 14-24sp tùy theo cấp độ
- Spacing: 10-20 padding, 5-15 spacing

### 2. Màu sắc chức năng
- **Xanh lá (0.2, 0.7, 0.3)**: Nút hành động chính (Pha màu)
- **Xanh dương (0.2-0.3, 0.5-0.6, 0.8-0.9)**: Nút phụ (Thêm, Tính toán)
- **Vàng (0.9, 0.6-0.7, 0.2)**: Lưu, Cảnh báo
- **Đỏ (0.8-0.9, 0.3, 0.3)**: Xóa, Dừng, Khẩn cấp

### 3. Layout Pattern
- Vertical BoxLayout làm container chính
- GridLayout cho form nhập liệu
- ScrollView cho nội dung dài
- Horizontal BoxLayout cho hàng nút

## Dependencies

### Core
- **kivy==2.2.1**: Framework GUI
- **kivy-garden==0.1.5**: Additional widgets

### Support
- **pygame==2.5.2**: Kivy backend
- **pygments==2.16.1**: Syntax highlighting
- **pyserial==3.5**: UART communication
- **sqlite3**: Database (built-in Python)

## Chạy ứng dụng

### Linux/macOS
```bash
cd ui
./run.sh
```

### Windows
```cmd
cd ui
run.bat
```

### Thủ công
```bash
cd ui
pip install -r requirements.txt
python3 main.py
```

## Màu gốc (Colorants)

Hệ thống hỗ trợ 16 ống màu:
1. **AXX** - White Tint
2. **A** - Red Oxide
3. **B** - Yellow Oxide
4. **C** - Black
5. **D** - Blue
6. **E** - Green
7. **L** - Magenta
8. **R** - Red
9. **Y** - Yellow
10. **K** - Orange
11. **T** - Brown
12. **W** - Violet
13. **N** - Cyan
14. **M** - Maroon
15. **P** - Pink
16. **Q** - Turquoise

## Workflow Điển hình

### 1. Pha màu theo công thức
User → Chọn hệ màu → Chọn mã màu → Xem công thức → Nhập tên SP → Nhấn "Pha màu" → UART → Hardware → In nhãn

### 2. Chiết màu thủ công
User → Nhập tên SP → Thêm dòng màu → Chọn màu + nhập lượng → (Lưu công thức) → Pha màu → UART → Hardware

### 3. Pha màu theo mẫu
User → Đo màu → Device → L*a*b* values → Tính công thức (BLL) → Hiển thị → Nhập tên SP → Pha màu → UART → Hardware

## Tích hợp với các Module khác

### Kết nối với /src
```python
from src.color_recognition import ColorDetector
from src.mixing_formula import MixingCalculator
from src.optimization import optimize_formula
```

### UART Communication (TODO)
```python
# Trong main.py
import serial

class UARTController:
    def __init__(self, port='/dev/ttyUSB0', baudrate=9600):
        self.ser = serial.Serial(port, baudrate)
    
    def send_mix_command(self, formula):
        # Gửi lệnh pha màu
        pass
```

## Testing

```bash
# Test database module
cd ui
python3 database.py

# Test UI (visual)
python3 main.py
```

## Troubleshooting

### Lỗi: "ModuleNotFoundError: No module named 'kivy'"
```bash
pip install kivy==2.2.1
```

### Lỗi: "Permission denied: run.sh"
```bash
chmod +x run.sh
```

### Lỗi: "Unable to load kv file"
- Kiểm tra tất cả file .kv có trong thư mục ui/
- Kiểm tra syntax Kv Language

### Lỗi: "sqlite3 not found"
- sqlite3 có sẵn trong Python >= 3.x
- Nếu thiếu: `sudo apt install python3-sqlite3` (Linux)

## Tài liệu tham khảo

- Kivy Documentation: https://kivy.org/doc/stable/
- Kv Language Guide: https://kivy.org/doc/stable/guide/lang.html
- Kivy Garden: https://kivy-garden.github.io/

## License

MIT License - Xem file LICENSE trong thư mục gốc

## Tác giả

Phát triển dựa trên spec từ `.memory_bank/ui.md`
