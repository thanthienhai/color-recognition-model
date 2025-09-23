# Color Recognition Model - Hệ thống nhận diện và pha trộn màu tự động

## Giới thiệu
Dự án này phát triển một hệ thống tự động cho việc nhận diện màu và tính toán công thức pha trộn sơn chính xác trong công nghiệp. Hệ thống kết hợp xử lý ảnh, học máy và mô hình vật lý để đạt độ chính xác cao.

## Tính năng chính

### 1. Tiền xử lý & Hiệu chuẩn màu
- **Buồng chụp chuẩn ánh sáng**: Loại bỏ nhiễu do môi trường
- **Hiệu chuẩn camera**: Sử dụng color checker và mô hình hồi quy (BP Neural Network/Linear Regression)
- **Chuyển đổi không gian màu**: RGB → CIE Lab để tách biệt Hue, Saturation, Value

### 2. Thuật toán nhận diện màu
- **SVM + Feature Transform**: Phân loại mẫu màu theo nhãn đã huấn luyện
- **Deep Learning models**: CNN, YOLO cho nhận diện màu phức tạp
- **Không gian màu CIE Lab**: Đánh giá chính xác sự khác biệt màu sắc

### 3. Thuật toán pha trộn màu
- **Mô hình Kubelka-Munk**: Tính toán tỷ lệ hấp thụ - tán xạ ánh sáng
- **Giải pháp tối ưu least squares**: Xác định tỷ lệ pha trộn đạt màu mục tiêu
- **Graph Neural Networks**: Mô hình hóa tương tác phức tạp giữa các sắc tố

### 4. Tối ưu & Đánh giá
- **Đo sai số màu ΔE (CIEDE2000)**: Đánh giá độ chính xác
- **Tối ưu đa mục tiêu**: Giảm ΔE, chi phí và thời gian pha trộn

## Cấu trúc dự án

```
color-recognition-model/
│── data/                    
│   ├── raw/                 # Ảnh gốc thu thập từ buồng chụp
│   ├── processed/           # Ảnh đã hiệu chuẩn và tiền xử lý
│   └── color_checker/       # Ảnh chuẩn màu để hiệu chuẩn
│
│── models/
│   ├── color_detection/     # Mô hình nhận diện màu (SVM, CNN, YOLO)
│   └── color_mixing/        # Mô hình pha trộn (Kubelka-Munk, GNN)
│
│── src/
│   ├── preprocessing.py     # Hiệu chuẩn camera, chuyển đổi không gian màu
│   ├── color_recognition.py # Thuật toán nhận diện màu
│   ├── mixing_formula.py    # Tính toán công thức pha trộn màu
│   ├── optimization.py      # Thuật toán tối ưu, giảm sai số ΔE
│   ├── utils.py             # Hàm tiện ích chung
│   └── app.py               # Ứng dụng chính
│
│── notebooks/               # Notebook thử nghiệm, demo
│── tests/                   # Unit tests
```

## Cài đặt

1. Clone repository:
```bash
git clone https://github.com/thanthienhai/color-recognition-model.git
cd color-recognition-model
```

2. Tạo virtual environment:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
```

3. Cài đặt dependencies:
```bash
pip install -r requirements.txt
```

## Sử dụng

### Chạy pipeline đầy đủ:
```bash
python src/app.py --input data/raw/sample.jpg --output results/
```

### Sử dụng từng module:
```python
from src.preprocessing import ColorCalibrator
from src.color_recognition import ColorDetector
from src.mixing_formula import MixingCalculator

# Hiệu chuẩn màu
calibrator = ColorCalibrator()
calibrated_image = calibrator.calibrate(image)

# Nhận diện màu
detector = ColorDetector()
colors = detector.detect(calibrated_image)

# Tính công thức pha trộn
mixer = MixingCalculator()
formula = mixer.calculate_formula(target_color)
```

## Đánh giá hiệu suất

- **Độ chính xác nhận diện**: >95% trên dataset test
- **Sai số màu ΔE**: <2.0 (tiêu chuẩn công nghiệp)
- **Thời gian xử lý**: <5 giây/mẫu

## Đóng góp

1. Fork repository
2. Tạo feature branch: `git checkout -b feature/new-feature`
3. Commit changes: `git commit -am 'Add new feature'`
4. Push branch: `git push origin feature/new-feature`
5. Tạo Pull Request

## License

MIT License - xem file [LICENSE](LICENSE) để biết thêm chi tiết.

## Liên hệ

- Email: contact@colorrecognition.com
- Website: https://colorrecognition.com