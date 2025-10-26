
### **Tài Liệu Thiết Kế Giao Diện Người Dùng (UI) - Kivy**

**Framework:** Kivy 2.1+
**Ngôn ngữ:** Python / Kv Language

### \#\# 1. Tổng quan & Nguyên tắc thiết kế

Giao diện được xây dựng dựa trên Kivy để đảm bảo khả năng chạy đa nền tảng (Windows, Linux, macOS) từ một mã nguồn duy nhất. Thiết kế tuân thủ các nguyên tắc sau:

  * **Nhất quán (Consistent):** Sử dụng chung một bộ màu, font chữ và phong cách thiết kế cho tất cả các màn hình. Menu điều hướng chính luôn cố định bên trái.
  * **Rõ ràng (Clear):** Các chức năng được dán nhãn bằng tiếng Việt rõ ràng, font chữ đủ lớn, bố cục không gây rối mắt.
  * **Phản hồi (Responsive):** Cung cấp phản hồi trực quan cho người dùng, ví dụ như thay đổi màu nút khi nhấn, hiển thị thông báo trạng thái, lỗi.

**Cấu trúc Navigation chính:**
Hệ thống sẽ sử dụng một `ScreenManager` để quản lý việc chuyển đổi giữa các màn hình chức năng. Menu dọc bên trái sẽ là thanh điều hướng chính, mỗi nút trên menu sẽ chuyển `ScreenManager` đến màn hình tương ứng.

-----

### \#\# 2. Cấu trúc File Giao diện (.kv)

Để quản lý code hiệu quả, giao diện sẽ được tách thành nhiều file `.kv`.

```
ui/
├── main.kv                 # File kv chính, định nghĩa root widget và ScreenManager
├── mixbyformulascreen.kv   # Giao diện màn hình Pha màu theo công thức
├── manualdispensescreen.kv # Giao diện màn hình Chiết màu bằng tay
├── colorantmanagerscreen.kv# Giao diện màn hình Quản lý màu
├── maintenancescreen.kv    # Giao diện màn hình Khắc phục lỗi
├── calibrationscreen.kv    # Giao diện màn hình Hiệu chuẩn
└── scancolorscreen.kv      # Giao diện màn hình Pha màu theo mẫu
```

-----

### \#\# 3. Mô tả chi tiết các màn hình (Screens)

#### **3.1. Màn hình chính (MainScreen)**

  * **File:** `main.kv`
  * **Mục đích:** Là khung sườn chính của ứng dụng, chứa menu điều hướng và khu vực hiển thị các màn hình chức năng.
  * **Bố cục chính:** `BoxLayout` với `orientation: 'horizontal'`.
      * **Bên trái:** Một `BoxLayout` (với `size_hint_x: 0.2`) chứa các `Button` điều hướng (Pha màu, Chiết màu, Quản lý màu, v.v.).
      * **Bên phải:** Một `ScreenManager` (với `size_hint_x: 0.8`) để chứa và chuyển đổi giữa các màn hình con.
  * **Luồng sự kiện:**
      * `on_press` của mỗi nút điều hướng sẽ thay đổi thuộc tính `current` của `ScreenManager` sang màn hình tương ứng. Ví dụ: `on_press: app.root.ids.screen_manager.current = 'mix_formula_screen'`.

-----

#### **3.2. Màn hình Pha màu theo công thức (MixByFormulaScreen) 🎨**

  * **File:** `mixbyformulascreen.kv`
  * **Mục đích:** Cho phép người dùng chọn một màu từ cơ sở dữ liệu công thức có sẵn và tiến hành pha.
  * **Bố cục chính:** `BoxLayout` với `orientation: 'vertical'`, chia thành các khu vực nhập liệu, hiển thị và hành động.
  * **Các Widget chính:**
      * `Spinner` (id: `system_spinner`): Chọn Thẻ màu/Hệ màu.
      * `Spinner` (id: `code_spinner`): Chọn Mã màu.
      * `TextInput` (id: `product_name_input`): Nhập tên sản phẩm.
      * `Spinner` (id: `volume_spinner`): Chọn thể tích (1 Lít, 5 Lít...).
      * `Label` (id: `base_label`): Hiển thị loại Base tương ứng.
      * `Label` (id: `price_label`): Hiển thị giá tiền.
      * `BoxLayout` (id: `formula_display`): Khu vực để hiển thị động (thêm các `Label` và `Widget` màu) công thức chi tiết.
      * `Button` (text: "Pha màu"): Bắt đầu quá trình pha.
      * `Button` (text: "In nhãn"): Gửi lệnh in.
  * **Luồng sự kiện:**
      * Khi `system_spinner` được chọn, ứng dụng sẽ truy vấn CSDL để cập nhật danh sách cho `code_spinner`.
      * Khi `code_spinner` được chọn, ứng dụng truy vấn CSDL, tính toán và hiển thị công thức, giá tiền vào các `Label` và `formula_display`.
      * `on_press` nút "Pha màu" sẽ gọi hàm trong BLL, truyền vào công thức và thể tích đã chọn để bắt đầu gửi lệnh qua UART.

-----

#### **3.3. Màn hình Chiết màu bằng tay (ManualDispenseScreen)**

  * **File:** `manualdispensescreen.kv`
  * **Mục đích:** Cho phép người dùng tự tạo một công thức bằng cách nhập lượng cho từng màu gốc.
  * **Bố cục chính:** `ScrollView` chứa một `GridLayout` (với `cols: 3`) để hiển thị các dòng nhập liệu màu.
  * **Các Widget chính:**
      * `TextInput` (id: `product_name_input`): Nhập tên sản phẩm.
      * `GridLayout` (id: `manual_grid`): Chứa các dòng nhập liệu. Mỗi dòng là một `BoxLayout` con gồm:
          * `Spinner`: Chọn màu gốc (AXX, C, D...).
          * `TextInput` (chỉ cho nhập số): Nhập lượng (ml).
          * `Button` (icon 'x'): Xóa dòng.
      * `Button` (text: "Thêm màu"): Thêm một dòng mới vào `manual_grid`.
      * `Button` (text: "Lưu công thức màu"): Lưu công thức hiện tại vào CSDL.
      * `Button` (text: "Pha màu"): Bắt đầu pha theo công thức vừa nhập.
  * **Luồng sự kiện:**
      * Nút "Thêm màu" sẽ tạo một bộ widget mới và thêm vào `manual_grid`.
      * Nút "Pha màu" thu thập dữ liệu từ tất cả các dòng trong `manual_grid` và gửi lệnh pha màu qua BLL.

-----

#### **3.4. Màn hình Quản lý màu (ColorantManagerScreen)**

  * **File:** `colorantmanagerscreen.kv`
  * **Mục đích:** Hiển thị trực quan lượng màu còn lại trong 16 ống chứa.
  * **Bố cục chính:** `ScrollView` chứa một `GridLayout` (ví dụ `cols: 8`) để hiển thị trạng thái của từng ống.
  * **Các Widget chính:**
      * Mỗi ô trong `GridLayout` là một Widget tùy chỉnh (ví dụ: `ColorantStatus(BoxLayout)`) chứa:
          * `Label`: Hiển thị tên màu gốc (AXX, D...).
          * `ProgressBar` (với `orientation: 'vertical'`): Thanh trạng thái thể hiện mức màu.
          * `Label`: Hiển thị % hoặc lượng ml còn lại.
  * **Luồng sự kiện:**
      * Khi màn hình được hiển thị (`on_enter`), nó sẽ gọi một hàm trong BLL để truy vấn CSDL, lấy `current_level_ml` của tất cả các màu gốc và cập nhật giá trị cho các `ProgressBar`.

-----

#### **3.5. Màn hình Khắc phục lỗi / Bảo trì (MaintenanceScreen) 🔧**

  * **File:** `maintenancescreen.kv`
  * **Mục đích:** Cung cấp các công cụ để thực hiện bảo trì máy.
  * **Bố cục chính:** `BoxLayout` với `orientation: 'vertical'`.
  * **Các Widget chính:**
      * `Label` (text: "Tốc độ khuấy màu").
      * `ToggleButton` (group: 'stir\_speed'): Các nút chọn tốc độ Thấp/Trung bình/Cao.
      * `Button` (text: "Bắt đầu khuấy"), `Button` (text: "Dừng khuấy").
      * `TextInput` (text: "Lượng màu phun vệ sinh (ml)").
      * `Button` (text: "Vệ sinh đầu phun").
  * **Luồng sự kiện:**
      * Các nút bấm sẽ trực tiếp gọi các hàm trong HAL (qua BLL) để gửi các lệnh đơn giản như `STIR` hoặc `CLEAN_NOZZLE` qua UART.

-----

#### **3.6. Màn hình Hiệu chuẩn (CalibrationScreen) ⚙️**

  * **File:** `calibrationscreen.kv`
  * **Mục đích:** Dành cho kỹ thuật viên để tinh chỉnh các thông số phần cứng. Màn hình này cần được bảo vệ bằng mật khẩu.
  * **Bố cục chính:** `BoxLayout` chứa các khu vực cài đặt. Ban đầu các khu vực này bị vô hiệu hóa (`disabled: True`).
  * **Các Widget chính:**
      * `TextInput` (id: `password_input`, `password: True`): Nhập mật khẩu.
      * `Button` (text: "Mở khóa").
      * **Khu vực Cài đặt xung:**
          * `Spinner`: Chọn màu gốc cần hiệu chuẩn.
          * `TextInput` (id: `pulse_1ml_input`): Nhập số xung/ml.
          * `TextInput` (id: `pulse_01ml_input`): Nhập số xung/0.1ml.
          * `Button` (text: "Cập nhật xung").
      * `Label` (id: `connection_status`): Hiển thị trạng thái kết nối "Đã kết nối" / "Lỗi không có kết nối".
  * **Luồng sự kiện:**
      * Sau khi nhập đúng mật khẩu và nhấn "Mở khóa", các widget cài đặt sẽ được kích hoạt (`disabled: False`).
      * Nút "Cập nhật xung" sẽ lấy giá trị từ các `TextInput` và gửi lệnh `CALIBRATE_PULSE` qua UART.

-----

#### **3.7. Màn hình Pha màu theo mẫu (ScanColorScreen)**

  * **File:** `scancolorscreen.kv`
  * **Mục đích:** Sử dụng thiết bị đo màu để phân tích mẫu và tự động tính toán công thức.
  * **Bố cục chính:** `BoxLayout` chia hai phần chính.
      * **Bên trái:** Điều khiển và hiển thị màu.
      * **Bên phải:** Hiển thị công thức kết quả.
  * **Các Widget chính:**
      * `Button` (text: "Bắt đầu đo màu", size\_hint: (1, 0.3)).
      * `Widget` (id: `scanned_color_preview`): Một ô vuông dùng canvas để vẽ màu vừa đo được.
      * `Label` (id: `lab_value_label`): Hiển thị giá trị L\*a\*b\* của màu.
      * `BoxLayout` (id: `result_formula_display`): Hiển thị công thức được tính toán.
      * `Button` (text: "Pha màu này").
  * **Luồng sự kiện:**
      * `on_press` nút "Bắt đầu đo màu" sẽ kích hoạt hàm giao tiếp với thiết bị đo màu qua HAL.
      * Sau khi nhận được dữ liệu màu (ví dụ: L\*a\*b\*), BLL sẽ tính toán công thức.
      * Kết quả công thức được hiển thị trong `result_formula_display` và màu sắc được cập nhật trên `scanned_color_preview`.
      * Nút "Pha màu này" sẽ hoạt động tương tự như nút "Pha màu" ở các màn hình khác.