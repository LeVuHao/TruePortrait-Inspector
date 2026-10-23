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
            # Hỗ trợ cả 2 chuẩn ảnh thẻ thông dụng: 3:4 (0.75) và 4:6 (0.667)
            "target_aspect_ratio": 3.0 / 4.0,  # 0.75
            "aspect_ratio_tolerance": 0.12,    # Dải cho phép [0.63 - 0.87], bao quát cả ảnh thẻ 4x6 (0.67) và 3x4 (0.75)
            "min_width": 400,                  # Chuẩn in 300 DPI ảnh 3x4cm cần ~354x472 px
            "min_height": 500,                 # Thư thả cho ảnh chụp điện thoại / gửi online
        },
        "face_count": {
            "required_count": 1,
        },
        "face_height_ratio": {
            # Chiều cao Bounding box khuôn mặt (Haar Cascade) / Chiều cao tổng thể ảnh
            # Về mặt thị giác máy tính: Khung Haar mặt (lông mày đến cằm) chỉ chiếm ~65% - 70% chiều cao thực của đầu (đỉnh tóc đến cằm).
            # Chuẩn ICAO Doc 9303 quy định đầu chiếm 50% - 70%. Khi quy đổi sang Haar box tương ứng dải thực nghiệm chuẩn là 30% - 70%.
            "min_ratio": 0.30,
            "max_ratio": 0.70,
        },
        "brightness": {
            # Mean intensity trên không gian Grayscale [0, 255]
            "min_mean": 90.0,
            "max_mean": 215.0,
            # Độ lệch chuẩn đánh giá độ tương phản
            "min_contrast_std": 25.0,
            # Tỷ lệ pixel bão hòa trắng bốc cháy (>= 245) tối đa cho phép
            "max_highlight_ratio": 0.045,
            # Tỷ lệ pixel cháy sáng trên vùng khuôn mặt (Face ROI) tối đa
            "max_face_highlight_ratio": 0.04,
            # Độ chênh lệch ánh sáng tối đa giữa 2 nửa mặt trái/phải (Asymmetric Lighting)
            "max_face_asymmetry": 28.0,
            # Dải cường độ sáng trung bình cho phép trực tiếp trên vùng khuôn mặt
            "min_face_mean": 85.0,
            "max_face_mean": 215.0,
        },
        "sharpness": {
            # Phương sai của toán tử Laplacian (Variance of Laplacian)
            "min_laplacian_var": 75.0,
        },
        "background_uniformity": {
            # Độ lệch chuẩn màu (Std Dev) tối đa tại các vùng ROI nền 4 góc (thực tế cảm biến camera 2.0 - 5.0)
            "max_color_std": 6.0,
        }
    }
}

# Trọng số điểm cho từng tiêu chí trong thang điểm 100 (Evaluation Engine)
SCORING_WEIGHTS = {
    "image_size": 15,
    "face_count": 15,          # Đã điều chỉnh về 15 điểm theo yêu cầu
    "face_height_ratio": 20,
    "sharpness": 15,
    "brightness": 20,          # Phân tán thêm 5đ (15 -> 20đ)
    "background_uniformity": 15 # Phân tán thêm 5đ (10 -> 15đ)
}
