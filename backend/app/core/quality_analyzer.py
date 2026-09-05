"""
Module 3: Image Quality Analysis (Blur, Brightness & Contrast)
Phụ trách bởi: CHƯƠNG
Nhiệm vụ:
- Kiểm tra độ rõ nét / phát hiện ảnh mờ qua Phương sai toán tử Laplacian: Var(Laplacian).
- Phân tích cường độ sáng trung bình (Mean Intensity) trên ma trận ảnh xám.
- Phân tích độ tương phản qua Độ lệch chuẩn (Standard Deviation) cường độ sáng.
- Trích xuất dữ liệu Histogram (256 bin gom về 16 nhóm) phục vụ trực quan hóa.
"""

import cv2
import numpy as np
from typing import Dict, Any, Tuple


def analyze_quality(image_bgr: np.ndarray, image_gray: np.ndarray, preset_config: dict) -> Tuple[Dict[str, Any], np.ndarray]:
    """
    Phân tích chất lượng quang học của ảnh.
    
    Args:
        image_bgr: Ảnh gốc BGR
        image_gray: Ảnh xám Grayscale
        preset_config: Cấu hình dải ngưỡng
        
    Returns:
        tuple (metrics_dict, laplacian_map_image)
    """
    # 1. Phát hiện ảnh mờ: Tính ma trận Laplacian và phương sai
    # cv2.Laplacian sử dụng kiểu dữ liệu CV_64F để giữ độ chính xác gradient
    laplacian_matrix = cv2.Laplacian(image_gray, cv2.CV_64F)
    laplacian_variance = float(laplacian_matrix.var())
    
    # Chuẩn hóa ma trận Laplacian về ảnh 8-bit [0, 255] để phục vụ trực quan hóa (Visualizer)
    laplacian_abs = np.absolute(laplacian_matrix)
    laplacian_map = np.uint8(np.clip(laplacian_abs / (laplacian_abs.max() + 1e-5) * 255.0, 0, 255))
    
    sharpness_rules = preset_config.get("sharpness", {})
    min_laplacian_var = sharpness_rules.get("min_laplacian_var", 75.0)
    sharpness_passed = (laplacian_variance >= min_laplacian_var)
    
    # 2. Phân tích độ sáng & độ tương phản
    brightness_mean = float(np.mean(image_gray))
    contrast_std = float(np.std(image_gray))
    
    bright_rules = preset_config.get("brightness", {})
    min_mean = bright_rules.get("min_mean", 90.0)
    max_mean = bright_rules.get("max_mean", 210.0)
    min_contrast = bright_rules.get("min_contrast_std", 25.0)
    
    brightness_passed = (min_mean <= brightness_mean <= max_mean) and (contrast_std >= min_contrast)
    
    bright_msg = []
    if brightness_mean < min_mean:
        bright_msg.append(f"Ảnh bị thiếu sáng (Mean {brightness_mean:.1f} < {min_mean}).")
    elif brightness_mean > max_mean:
        bright_msg.append(f"Ảnh bị chói/cháy sáng (Mean {brightness_mean:.1f} > {max_mean}).")
    if contrast_std < min_contrast:
        bright_msg.append(f"Độ tương phản thấp (Std {contrast_std:.1f} < {min_contrast}).")
    if not bright_msg:
        bright_msg.append(f"Độ sáng và độ tương phản đạt chuẩn (Mean {brightness_mean:.1f}, Std {contrast_std:.1f}).")
        
    # 3. Trích xuất Histogram (Gom 256 mức xám thành 16 bins để gửi qua JSON nhẹ nhàng)
    hist = cv2.calcHist([image_gray], [0], None, [16], [0, 256])
    histogram_bins = [int(v[0]) for v in hist]
    
    metrics = {
        "sharpness": {
            "passed": sharpness_passed,
            "laplacian_variance": round(laplacian_variance, 2),
            "threshold_min": min_laplacian_var,
            "message": f"Ảnh rõ nét (Phương sai Laplacian {laplacian_variance:.1f} >= {min_laplacian_var})." if sharpness_passed else f"Ảnh bị mờ/nhòe (Phương sai Laplacian {laplacian_variance:.1f} < {min_laplacian_var})."
        },
        "brightness": {
            "passed": brightness_passed,
            "mean_intensity": round(brightness_mean, 2),
            "contrast_std": round(contrast_std, 2),
            "threshold_min_mean": min_mean,
            "threshold_max_mean": max_mean,
            "threshold_min_contrast": min_contrast,
            "message": " ".join(bright_msg),
            "histogram_data": histogram_bins
        }
    }
    
    return metrics, laplacian_map
