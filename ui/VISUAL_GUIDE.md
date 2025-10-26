# Visual Guide - Color Mixing System UI

## What You Should See

When you run `python3 main.py`, the application window should look like this:

```
┌────────────────────────────────────────────────────────────────────┐
│                     HỆ THỐNG PHA MÀU                               │
│ ┌─────────────┬──────────────────────────────────────────────────┐│
│ │  MENU (20%) │       MAIN CONTENT AREA (80%)                    ││
│ │             │                                                   ││
│ │ HỆ THỐNG    │   ┌────────────────────────────────────┐         ││
│ │ PHA MÀU     │   │  Screen content appears here       │         ││
│ │             │   │                                    │         ││
│ │ ┌─────────┐ │   │  - Forms                          │         ││
│ │ │Pha màu  │ │   │  - Buttons                        │         ││
│ │ │theo CT  │ │   │  - Data displays                  │         ││
│ │ └─────────┘ │   │  - Charts/graphs                  │         ││
│ │             │   │                                    │         ││
│ │ ┌─────────┐ │   │                                    │         ││
│ │ │Chiết màu│ │   │                                    │         ││
│ │ │bằng tay │ │   │                                    │         ││
│ │ └─────────┘ │   │                                    │         ││
│ │             │   └────────────────────────────────────┘         ││
│ │ ┌─────────┐ │                                                  ││
│ │ │Pha màu  │ │                                                  ││
│ │ │theo mẫu │ │                                                  ││
│ │ └─────────┘ │                                                  ││
│ │             │                                                  ││
│ │ ┌─────────┐ │                                                  ││
│ │ │Quản lý  │ │                                                  ││
│ │ │màu      │ │                                                  ││
│ │ └─────────┘ │                                                  ││
│ │             │                                                  ││
│ │ ┌─────────┐ │                                                  ││
│ │ │Bảo trì  │ │                                                  ││
│ │ └─────────┘ │                                                  ││
│ │             │                                                  ││
│ │ ┌─────────┐ │                                                  ││
│ │ │Hiệu     │ │                                                  ││
│ │ │chuẩn    │ │                                                  ││
│ │ └─────────┘ │                                                  ││
│ └─────────────┴──────────────────────────────────────────────────┘│
└────────────────────────────────────────────────────────────────────┘
```

## Color Scheme

### Menu (Left Sidebar)
- **Background**: Dark blue-gray (RGB: 0.15, 0.15, 0.2)
- **Title text**: White
- **Button backgrounds**:
  - Mixing functions: Blue (0.2, 0.6, 0.8)
  - Management: Green (0.3, 0.7, 0.4)
  - Maintenance: Orange (0.9, 0.6, 0.2)
  - Calibration: Red (0.8, 0.3, 0.3)

### Content Area (Right Side)
- **Background**: Light gray (RGB: 0.95, 0.95, 0.95)
- **Text**: Black
- **Action buttons**: Green (0.2, 0.7, 0.3)
- **Secondary buttons**: Blue (0.3, 0.5, 0.8)

## Screen-by-Screen View

### 1. Pha màu theo công thức (Mix by Formula)

```
┌──────────────────────────────────────────────────────────┐
│  PHA MÀU THEO CÔNG THỨC                                  │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Thẻ màu / Hệ màu: [Chọn hệ màu ▼]                     │
│  Mã màu:           [Chọn mã màu ▼]                      │
│  Tên sản phẩm:     [___________________]                │
│  Thể tích:         [1 Lít ▼]                           │
│  Loại Base:        -                                     │
│  Giá tiền:         0 VNĐ                                │
│                                                          │
│  Công thức chi tiết:                                     │
│  ┌────────────────────────────────────────────────┐     │
│  │ Chọn mã màu để xem công thức                   │     │
│  │                                                 │     │
│  └────────────────────────────────────────────────┘     │
│                                                          │
│  [  Pha màu  ]    [  In nhãn  ]                        │
└──────────────────────────────────────────────────────────┘
```

### 2. Chiết màu bằng tay (Manual Dispense)

```
┌──────────────────────────────────────────────────────────┐
│  CHIẾT MÀU BẰNG TAY                                      │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Tên sản phẩm: [___________________]                    │
│                                                          │
│  Danh sách màu:                                          │
│  ┌────────────────────────────────────────────────┐     │
│  │ [Chọn màu ▼]  [Lượng (ml)]  [X]               │     │
│  │ [Chọn màu ▼]  [Lượng (ml)]  [X]               │     │
│  │ [Chọn màu ▼]  [Lượng (ml)]  [X]               │     │
│  └────────────────────────────────────────────────┘     │
│                                                          │
│  [+ Thêm màu]                                           │
│                                                          │
│  [Lưu công thức]    [  Pha màu  ]                      │
└──────────────────────────────────────────────────────────┘
```

### 3. Pha màu theo mẫu (Scan Color)

```
┌──────────────────────────────────────────────────────────┐
│  PHA MÀU THEO MẪU                                        │
├─────────────────────────┬────────────────────────────────┤
│                         │                                │
│  [BẮT ĐẦU ĐO MÀU]      │  Công thức được tính toán:    │
│                         │                                │
│  Màu đã đo:            │  Tên SP: [____________]       │
│  ┌───────────────────┐ │  Thể tích: [1 Lít ▼]         │
│  │                   │ │                                │
│  │    COLOR BOX     │ │  ┌──────────────────────┐     │
│  │                   │ │  │ Nhấn đo màu để xem   │     │
│  └───────────────────┘ │  │ công thức            │     │
│                         │  └──────────────────────┘     │
│  Giá trị L*a*b*:       │                                │
│  ┌───────────────────┐ │  ΔE: -                        │
│  │ L*: 0.00          │ │                                │
│  │ a*: 0.00          │ │                                │
│  │ b*: 0.00          │ │                                │
│  └───────────────────┘ │                                │
│                         │                                │
│  [Tính công thức]      │  [  Pha màu này  ]            │
└─────────────────────────┴────────────────────────────────┘
```

### 4. Quản lý màu (Colorant Manager)

```
┌──────────────────────────────────────────────────────────┐
│  QUẢN LÝ MÀU                                             │
├──────────────────────────────────────────────────────────┤
│  [Làm mới dữ liệu]                                      │
│                                                          │
│  ┌────┐  ┌────┐  ┌────┐  ┌────┐                        │
│  │AXX │  │ A  │  │ B  │  │ C  │                        │
│  │████│  │███ │  │██  │  │████│                        │
│  │████│  │███ │  │█   │  │████│  Bars show level      │
│  │████│  │██  │  │    │  │███ │  Color-coded:         │
│  │85% │  │65% │  │45% │  │92% │  Green: >30%          │
│  │850ml  │650ml │450ml │920ml│  Yellow: 10-30%       │
│  └────┘  └────┘  └────┘  └────┘  Red: <10%            │
│                                                          │
│  ┌────┐  ┌────┐  ┌────┐  ┌────┐                        │
│  │ D  │  │ E  │  │ L  │  │ R  │                        │
│  │█   │  │████│  │███ │  │████│                        │
│  │    │  │███ │  │██  │  │████│                        │
│  │    │  │███ │  │██  │  │████│                        │
│  │15% │  │78% │  │55% │  │88% │                        │
│  │150ml  │780ml │550ml │880ml│                         │
│  └────┘  └────┘  └────┘  └────┘                        │
│                                                          │
│  ... (12 more tanks)                                    │
└──────────────────────────────────────────────────────────┘
```

### 5. Bảo trì (Maintenance)

```
┌──────────────────────────────────────────────────────────┐
│  BẢO TRÌ HỆ THỐNG                                        │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │ KHUẤY MÀU                                        │   │
│  │                                                  │   │
│  │ Tốc độ khuấy:                                   │   │
│  │ [Thấp]  [Trung bình]  [Cao]                    │   │
│  │                                                  │   │
│  │ [Bắt đầu khuấy]  [Dừng khuấy]                  │   │
│  └──────────────────────────────────────────────────┘   │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │ VỆ SINH ĐẦU PHUN                                │   │
│  │                                                  │   │
│  │ Lượng phun: [50] ml                             │   │
│  │                                                  │   │
│  │ [Vệ sinh đầu phun]                              │   │
│  └──────────────────────────────────────────────────┘   │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │ KIỂM TRA HỆ THỐNG                               │   │
│  │                                                  │   │
│  │ Trạng thái: Sẵn sàng                            │   │
│  │                                                  │   │
│  │ [Kiểm tra kết nối]                              │   │
│  └──────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────┘
```

### 6. Hiệu chuẩn (Calibration)

```
┌──────────────────────────────────────────────────────────┐
│  HIỆU CHUẨN HỆ THỐNG                                     │
├──────────────────────────────────────────────────────────┤
│  Mật khẩu: [*********]  [Mở khóa]                      │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │ HIỆU CHUẨN XUNG                 [LOCKED]         │   │
│  │                                                  │   │
│  │ Chọn màu: [Chọn màu gốc ▼]                     │   │
│  │                                                  │   │
│  │ Xung/1ml:  [________________]                   │   │
│  │                                                  │   │
│  │ Xung/0.1ml: [________________]                  │   │
│  │                                                  │   │
│  │ [Cập nhật xung]                                 │   │
│  └──────────────────────────────────────────────────┘   │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │ TRẠNG THÁI KẾT NỐI                              │   │
│  │                                                  │   │
│  │ Trạng thái: Đang kiểm tra...                    │   │
│  │                                                  │   │
│  │ [Kiểm tra lại kết nối]                          │   │
│  └──────────────────────────────────────────────────┘   │
│                                                          │
│  ⚠ CẢNH BÁO: Chỉ kỹ thuật viên được phép...           │
└──────────────────────────────────────────────────────────┘
```

## Navigation Flow

```
Start
  │
  ├─ Click "Pha màu theo công thức" → Mix by Formula Screen
  │
  ├─ Click "Chiết màu bằng tay" → Manual Dispense Screen
  │
  ├─ Click "Pha màu theo mẫu" → Scan Color Screen
  │
  ├─ Click "Quản lý màu" → Colorant Manager Screen
  │
  ├─ Click "Bảo trì" → Maintenance Screen
  │
  └─ Click "Hiệu chuẩn" → Calibration Screen
```

## Interactive Elements

### Buttons
- **Primary actions**: Green background, white text
- **Secondary actions**: Blue background, white text
- **Destructive actions**: Red background, white text
- **All buttons**: Clickable with visual feedback

### Form Controls
- **TextInput**: White background with gray border
- **Spinner**: Dropdown selector with arrow indicator
- **ToggleButton**: Grouped selection (radio button style)

### Visual Feedback
- **Progress bars**: Vertical, color-coded by level
- **Color preview**: Canvas-drawn color swatch
- **Status labels**: Color-coded text

## Troubleshooting Visual Issues

### If you see a black screen:
✓ **Fixed!** - This was the original issue, now resolved

### If UI elements are missing:
1. Check that all .kv files are present
2. Run `python3 test_ui.py` to validate
3. Check console for error messages

### If colors look wrong:
- Check graphics driver is up to date
- Try different GL backend: `KIVY_GL_BACKEND=angle_sdl2 python3 main.py`

### If text is garbled:
- Ensure UTF-8 encoding support
- Check Vietnamese language font is available

## Window Size

- **Default**: Fullscreen
- **Minimum**: 1024x768
- **Recommended**: 1920x1080 (Full HD)

To run in windowed mode, create `ui/config.ini`:
```ini
[graphics]
width = 1280
height = 720
resizable = 1
fullscreen = 0
```

---

**Visual design follows**: Material Design principles with Vietnamese localization
**Tested on**: Linux (WSL2), Windows 10+
**Status**: ✅ All screens rendering correctly
