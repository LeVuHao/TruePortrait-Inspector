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
from .global_feature_extractor import extract_global_features, enhance_lighting_clahe


def analyze_quality(image_bgr: np.ndarray, image_gray: np.ndarray, preset_config: dict) -> Tuple[Dict[str, Any], np.ndarray, np.ndarray]:
    """
    Phân tích chất lượng quang học và trích xuất Đặc trưng Toàn cục của ảnh.
    
    Args:
        image_bgr: Ảnh gốc BGR
        image_gray: Ảnh xám Grayscale
        preset_config: Cấu hình dải ngưỡng
        
    Returns:
        tuple (metrics_dict, laplacian_map_image, clahe_enhanced_image)
    """
    # 1. Phát hiện ảnh mờ: Tính ma trận Laplacian và phương sai
    laplacian_matrix = cv2.Laplacian(image_gray, cv2.CV_64F)
    laplacian_variance = float(laplacian_matrix.var())
    
    laplacian_abs = np.absolute(laplacian_matrix)
    laplacian_map = np.uint8(np.clip(laplacian_abs / (laplacian_abs.max() + 1e-5) * 255.0, 0, 255))
    
    sharpness_rules = preset_config.get("sharpness", {})
    min_laplacian_var = sharpness_rules.get("min_laplacian_var", 75.0)
    sharpness_passed = (laplacian_variance >= min_laplacian_var)
    
    # 2. Trích xuất chuyên sâu Đặc trưng Toàn cục (Global Features Core)
    global_features = extract_global_features(image_bgr, image_gray)
    moments = global_features["statistical_moments"]
    comparison = global_features["comparison"]
    optical_cls = global_features["optical_classification"]
    
    brightness_mean = moments["mean"]
    contrast_std = moments["std_dev"]
    skewness_val = moments["skewness"]
    kurtosis_val = moments["kurtosis"]
    bhattacharyya_dist = comparison["bhattacharyya_distance"]
    
    bright_rules = preset_config.get("brightness", {})
    min_mean = bright_rules.get("min_mean", 90.0)
    max_mean = bright_rules.get("max_mean", 210.0)
    min_contrast = bright_rules.get("min_contrast_std", 25.0)
    
    # Tiêu chí đạt chuẩn độ sáng kết hợp cả Mean, Std và khoảng cách Bhattacharyya
    brightness_passed = (min_mean <= brightness_mean <= max_mean) and (contrast_std >= min_contrast) and (bhattacharyya_dist <= 0.45)
    
    bright_msg = []
    if optical_cls["status"] == "DARK":
        bright_msg.append(f"Ảnh thiếu sáng nghiêm trọng (Mean: {brightness_mean:.1f}, Skewness: {skewness_val:+.2f}, Bhattacharyya: {bhattacharyya_dist:.3f}).")
    elif optical_cls["status"] == "OVEREXPOSED":
        bright_msg.append(f"Ảnh bị chói/cháy sáng (Mean: {brightness_mean:.1f} > {max_mean}).")
    elif optical_cls["status"] == "LOW_CONTRAST":
        bright_msg.append(f"Độ tương phản thấp / bạc màu (Std: {contrast_std:.1f} < {min_contrast}).")
    else:
        bright_msg.append(f"Độ sáng và phân bố màu sắc đạt chuẩn (Mean: {brightness_mean:.1f}, Bhattacharyya: {bhattacharyya_dist:.3f}).")
        
    # 3. Tự động sinh ảnh cân bằng sáng bằng thuật toán CLAHE
    clahe_enhanced_bgr, clahe_metrics = enhance_lighting_clahe(image_bgr)
    
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
            "skewness": round(skewness_val, 3),
            "kurtosis": round(kurtosis_val, 3),
            "mean_saturation": moments["mean_saturation"],
            "bhattacharyya_distance": round(bhattacharyya_dist, 3),
            "chi_square_distance": comparison["chi_square_distance"],
            "threshold_min_mean": min_mean,
            "threshold_max_mean": max_mean,
            "threshold_min_contrast": min_contrast,
            "optical_status": optical_cls["status"],
            "optical_label": optical_cls["label"],
            "message": " ".join(bright_msg),
            "histogram_data": global_features["histogram_counts"],
            "histogram_normalized_16": global_features["histogram_16"],
            "reference_histogram_16": global_features["reference_histogram_16"]
        },
        "global_feature_vector": global_features["feature_vector_1d"],
        "clahe_enhancement": clahe_metrics
    }
    
    return metrics, laplacian_map, clahe_enhanced_bgr

