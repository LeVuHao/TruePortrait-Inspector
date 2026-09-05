"""
Module 1: Preprocessor & Image Resolution Analysis
Phụ trách bởi: HẢO
Nhiệm vụ:
- Đọc và decode file ảnh an toàn (JPG, JPEG, PNG).
- Kiểm tra kích thước (width, height), tỷ lệ khung hình (Aspect Ratio), độ phân giải tối thiểu.
- Tiền xử lý: Tạo bản sao Grayscale phục vụ các bước xử lý ảnh phía sau.
"""

import cv2
import numpy as np
from typing import Tuple, Dict, Any


def preprocess_image(file_bytes: bytes, preset_config: dict) -> Tuple[np.ndarray, np.ndarray, Dict[str, Any]]:
    """
    Tiền xử lý dữ liệu byte ảnh upload.
    
    Args:
        file_bytes: Mảng byte của file ảnh upload.
        preset_config: Cấu hình dải ngưỡng của preset hiện tại.
        
    Returns:
        tuple (image_bgr, image_gray, metrics_dict)
    """
    # 1. Decode ảnh sang mảng NumPy BGR
    nparr = np.frombuffer(file_bytes, np.uint8)
    image_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if image_bgr is None:
        raise ValueError("Không thể giải mã dữ liệu ảnh. File không đúng định dạng hoặc bị hỏng.")
        
    height, width = image_bgr.shape[:2]
    
    # 2. Chuyển đổi sang ảnh xám Grayscale phục vụ các thuật toán xử lý ảnh tiếp theo
    image_gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    
    # 3. Phân tích kích thước & Aspect Ratio
    size_rules = preset_config.get("image_size", {})
    target_aspect = size_rules.get("target_aspect_ratio", 0.75) # 3/4
    tolerance = size_rules.get("aspect_ratio_tolerance", 0.08)
    min_w = size_rules.get("min_width", 600)
    min_h = size_rules.get("min_height", 800)
    
    current_aspect = width / float(height)
    aspect_diff = abs(current_aspect - target_aspect)
    aspect_passed = aspect_diff <= tolerance
    res_passed = (width >= min_w) and (height >= min_h)
    
    size_passed = aspect_passed and res_passed
    
    # Tạo thông báo giải thích nếu có lỗi
    messages = []
    if not res_passed:
        messages.append(f"Độ phân giải {width}x{height} chưa đạt tối thiểu quy ước ({min_w}x{min_h}).")
    if not aspect_passed:
        messages.append(f"Tỉ lệ khung hình {current_aspect:.2f} chưa khớp chuẩn 3:4 ({target_aspect:.2f} ± {tolerance}).")
        
    metrics = {
        "passed": size_passed,
        "width": int(width),
        "height": int(height),
        "aspect_ratio": round(current_aspect, 3),
        "aspect_ratio_target": "3:4 (0.75)",
        "min_resolution": f"{min_w}x{min_h}",
        "resolution_passed": res_passed,
        "aspect_passed": aspect_passed,
        "message": " ".join(messages) if messages else "Kích thước và tỉ lệ khung hình đạt chuẩn."
    }
    
    return image_bgr, image_gray, metrics
