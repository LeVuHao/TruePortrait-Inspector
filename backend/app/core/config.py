"""
Module Configuration - Quản lý cấu hình dải ngưỡng thực nghiệm tập trung
Phụ trách bởi: CHƯƠNG & Cả nhóm
Lưu ý học thuật: Các giá trị dưới đây là giá trị khởi tạo tham khảo,
sẽ được hiệu chỉnh qua thực nghiệm trên tập dataset có Ground Truth.
"""

# Preset mặc định cho đồ án
DEFAULT_PRESET = "STANDARD_ID_PHOTO"

PRESET_CONFIGS = {
    "STANDARD_ID_PHOTO": {
        "description": "Chuẩn ảnh thẻ sinh viên / hồ sơ học tập (Aspect Ratio 3:4)",
        "image_size": {
            "target_aspect_ratio": 3.0 / 4.0,  # 0.75
            "aspect_ratio_tolerance": 0.08,    # Cho phép sai số +- 8%
            "min_width": 600,
            "min_height": 800,
        },
        "face_count": {
            "required_count": 1,
        },
        "face_height_ratio": {
            # Chiều cao Bounding box khuôn mặt / Chiều cao tổng thể ảnh
            "min_ratio": 0.45,
            "max_ratio": 0.70,
        },
        "brightness": {
            # Mean intensity trên không gian Grayscale [0, 255]
            "min_mean": 90.0,
            "max_mean": 210.0,
            # Độ lệch chuẩn đánh giá độ tương phản
            "min_contrast_std": 25.0,
        },
        "sharpness": {
            # Phương sai của toán tử Laplacian (Variance of Laplacian)
            "min_laplacian_var": 75.0,
        },
        "background_uniformity": {
            # Độ lệch chuẩn màu (Std Dev) tối đa tại các vùng ROI nền 4 góc
            "max_color_std": 1.5,
        }
    }
}

# Trọng số điểm cho từng tiêu chí trong thang điểm 100 (Evaluation Engine)
SCORING_WEIGHTS = {
    "image_size": 15,
    "face_count": 25,          # Tiêu chí sống còn
    "face_height_ratio": 20,
    "sharpness": 15,
    "brightness": 15,
    "background_uniformity": 10
}
