# PhotoCheck - Hệ thống kiểm tra chất lượng ảnh thẻ tự động (DIP Core)

Đồ án môn học **Xử lý ảnh số (Digital Image Processing)**  
Nhóm 4 sinh viên: **Hảo (Leader & Frontend/Evaluator), Quân (Face Detection), Chương (Image Quality), Huy (Background & Benchmark)**.

---

## 🌟 Tổng quan kiến trúc
PhotoCheck là hệ thống phân tích và kiểm định chất lượng ảnh thẻ theo phương pháp luận **Explainable DIP** (Toán học & thống kê ma trận điểm ảnh thuần túy, không dùng Deep Learning black-box):
- **Module 1 (Hảo):** Preprocessing, kiểm tra kích thước tối thiểu `600x800 px`, tỷ lệ `3:4` và ma trận Grayscale.
- **Module 2 (Quân):** Nhận diện khuôn mặt (Haar Cascade), đếm số mặt (`count = 1`), đo tỷ lệ `Face Height Ratio = H_face / H_img`.
- **Module 3 (Chương):** Đo độ mờ bằng Phương sai toán tử Laplacian `Var(Laplacian)`, phân tích độ sáng `Mean Intensity` và độ tương phản qua `Histogram`.
- **Module 4 (Huy):** Đo độ đồng nhất phông nền qua độ lệch chuẩn màu `Std Dev` tại 4 góc ROI đại diện.
- **Module 5 (Hảo):** Rule-based Evaluation & Scoring Engine (0 - 100 điểm) và ra kết luận `PASS` / `FAIL`.

---

## 🚀 Hướng dẫn chạy dự án

### 1. Khởi động Backend (FastAPI + OpenCV)
Mở terminal 1 tại thư mục gốc:
```bash
cd d:/xulyanh
uvicorn backend.app.main:app --reload --port 8000
```
Backend API sẽ hoạt động tại: `http://127.0.0.1:8000` (Tài liệu Swagger: `http://127.0.0.1:8000/docs`).

### 2. Khởi động Frontend Web Dashboard (React + Vite)
Mở terminal 2:
```bash
cd d:/xulyanh/frontend
npm run dev
```
Truy cập giao diện Web tại: `http://localhost:5173`.

---

## 📊 Cấu trúc mã nguồn
```
d:/xulyanh/
├── backend/
│   ├── app/
│   │   ├── core/
│   │   │   ├── config.py             # Dải ngưỡng thực nghiệm tập trung (Chương & Team)
│   │   │   ├── preprocessor.py       # Module 1: Kích thước & Tiền xử lý (Hảo)
│   │   │   ├── face_analyzer.py      # Module 2: Nhận diện mặt & Face Ratio (Quân)
│   │   │   ├── quality_analyzer.py   # Module 3: Độ mờ Laplacian & Histogram (Chương)
│   │   │   ├── background_analyzer.py# Module 4: 4 Góc ROI nền (Huy)
│   │   │   └── evaluator.py          # Module 5: Chấm điểm 0-100 & Đánh giá (Hảo)
│   │   ├── pipeline.py               # Image Processing Pipeline & Visualizer Generator
│   │   └── main.py                   # FastAPI REST API Service (Hảo)
│   └── tests/                        # Ảnh test mẫu & Benchmark
├── frontend/                         # React Web Dashboard (Hảo)
│   ├── src/
│   │   ├── App.jsx                   # Web Dashboard hoàn chỉnh
│   │   └── App.css                   # Enterprise SaaS Dark UI
└── KIEN_TRUC_VA_KE_HOACH_DO_AN.md    # Tài liệu kiến trúc và phân công chi tiết
```
