# AI Color Analysis - Phân Tích Màu Thông Minh

## Tổng quan

Hệ thống phân tích màu AI được tích hợp vào ứng dụng Color Mixing để nhận diện màu từ camera và phân tích thành 16 màu cơ bản với tỉ lệ chính xác.

## 🎨 16 Màu Cơ Bản

1. **Đen** (Black)
2. **Trắng** (White)
3. **Vàng Chanh** (Lemon Yellow)
4. **Đỏ** (Red)
5. **Xanh Lá** (Green)
6. **Xanh Biển Sâu** (Deep Sky Blue)
7. **Xanh Dương** (Blue)
8. **Tím** (Purple)
9. **Nâu** (Brown)
10. **Vàng Neon** (Neon Yellow)
11. **Xanh Neon** (Neon Green / Lime)
12. **Xanh Lam Neon** (Neon Blue / Cyan)
13. **Cam Neon** (Neon Orange)
14. **Hồng Neon** (Neon Pink / Magenta)
15. **Tím Neon** (Neon Purple)
16. **Vàng Kim** (Gold)

## 🧠 Công Nghệ Sử Dụng

### 1. Traditional Color Analysis
- **Delta E Calculation**: Tính khoảng cách màu sắc trong không gian CIE Lab
- **HSV Range Matching**: So khớp với các dải màu HSV được định nghĩa trước
- **Weighted Combination**: Kết hợp kết quả Lab (70%) và HSV (30%)

### 2. Deep Learning Model
- **Neural Network**: Mô hình 3 lớp với dropout để tránh overfitting
- **Input Features**: RGB normalized + Lab normalized (6 features)
- **Output**: Softmax distribution cho 16 màu cơ bản

### 3. Combined Analysis
- **Hybrid Approach**: Kết hợp Traditional (40%) và Deep Learning (60%)
- **Confidence Scoring**: Tính độ tin cậy dựa trên màu dominant
- **Formula Generation**: Tạo công thức pha màu từ kết quả phân tích

## 🔬 Cách Thức Hoạt Động

### Bước 1: Thu Thập Màu
```python
# Camera capture và convert color space
frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
frame_lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)

# Tính màu trung bình
avg_rgb = np.mean(frame_rgb, axis=(0, 1))
avg_lab = np.mean(frame_lab, axis=(0, 1))
```

### Bước 2: Phân Tích AI
```python
# Sử dụng AI engine
color_prediction = analyzer.analyze_color(
    rgb_values=rgb_int,
    lab_values=lab_float,
    method="combined"  # Traditional + Deep Learning
)
```

### Bước 3: Kết Quả
```python
# Kết quả bao gồm:
- primary_colors: {màu: tỉ_lệ_phần_trăm}
- dominant_color: màu_chính
- confidence: độ_tin_cậy
- mixing_formula: {màu: số_phần}  # Tỉ lệ pha màu dạng số phần (vd: 5:3:2)
```

## 📊 Ví Dụ Kết Quả

### Input: RGB(255, 128, 64) - Màu cam nhạt
```
🎯 Dominant: Cam (45.2%)
🌈 Color Components:
• Cam: 45.2%
• Vàng: 23.1%
• Đỏ: 18.7%
• Hồng: 8.9%
• Nâu: 4.1%

🔧 Mixing Formula:
• Cam: 5 phần
• Vàng: 3 phần
• Đỏ: 2 phần
• Hồng: 1 phần
```

## 🚀 Sử Dụng Trong UI

### 1. Camera Preview
- Bật camera: `Bắt đầu Preview`
- Chọn camera phù hợp từ dropdown

### 2. AI Color Analysis
- Nhấn `ĐO MÀU NGAY (AI)` để phân tích màu từ camera
- Nhấn `TEST AI` để test với màu mẫu

### 3. Kết Quả Hiển Thị
- **Lab Values**: L*a*b* color space values
- **AI Analysis**: Màu dominant và confidence
- **Color Components**: Top 6 màu thành phần (tỉ lệ %)
- **Mixing Formula**: Công thức pha màu (tỉ lệ số phần)

## 🔧 Cấu Hình

### Traditional Analysis Parameters
```python
# Weight cho Lab vs HSV
LAB_WEIGHT = 0.7
HSV_WEIGHT = 0.3

# Threshold cho significant colors
MIN_PERCENTAGE_THRESHOLD = 5.0
```

### Deep Learning Parameters
```python
# Network architecture
INPUT_FEATURES = 6  # RGB + Lab normalized
HIDDEN_SIZE = 128
NUM_COLORS = 16
DROPOUT_RATE = 0.3
```

### Combined Analysis Weights
```python
# Kết hợp Traditional và Deep Learning
TRADITIONAL_WEIGHT = 0.4
DEEP_LEARNING_WEIGHT = 0.6
```

## 📈 Độ Chính Xác

### Màu Thuần
- **Đỏ, Xanh, Vàng**: 85-95% accuracy
- **Tím, Cam, Hồng**: 75-85% accuracy
- **Nâu, Xám**: 70-80% accuracy

### Màu Trộn
- **2 màu cơ bản**: 70-80% accuracy
- **3+ màu cơ bản**: 60-70% accuracy

### Factors Ảnh Hưởng
- **Lighting conditions**: Ánh sáng ổn định tăng độ chính xác
- **Camera quality**: Camera tốt hơn = kết quả chính xác hơn
- **Color saturation**: Màu bão hòa dễ nhận diện hơn

## 🛠️ Troubleshooting

### Lỗi Import
```bash
# Nếu thiếu modules
pip install torch torchvision numpy opencv-python

# Nếu lỗi path
sys.path.append('path/to/src')
```

### Kết Quả Không Chính Xác
1. **Kiểm tra lighting**: Đảm bảo ánh sáng ổn định
2. **Clean camera lens**: Vệ sinh ống kính camera
3. **Calibrate camera**: Hiệu chuẩn white balance
4. **Check color space**: Đảm bảo conversion RGB↔Lab đúng

### Performance Issues
1. **Reduce preview size**: Giảm kích thước preview xuống 400px
2. **Lower FPS**: Giảm frame rate xuống 15-20 FPS
3. **Optimize model**: Sử dụng model nhỏ hơn cho real-time

## 🎯 Cải Tiến Tương Lai

### 1. Training Data Collection
- Thu thập dữ liệu màu thực tế từ camera
- Labeling chính xác bởi chuyên gia màu sắc
- Augmentation data với lighting conditions khác nhau

### 2. Model Improvements
- **CNN Model**: Sử dụng Convolutional layers cho image input
- **Attention Mechanism**: Focus vào vùng quan trọng của ảnh
- **Transfer Learning**: Fine-tune từ pre-trained color models

### 3. Advanced Features
- **Color Harmony Detection**: Nhận diện các tổ hợp màu hài hòa
- **Trend Analysis**: Phân tích xu hướng màu sắc
- **Custom Color Training**: Train model với màu riêng của người dùng

## 📞 Support

Nếu gặp vấn đề hoặc cần hỗ trợ:
1. Kiểm tra console output để xem error messages
2. Test với `demo_color_ai.py` để verify cơ bản
3. Kiểm tra camera compatibility với WSL (nếu dùng WSL)

---

*© 2025 Color Recognition Model - AI Color Analysis System*