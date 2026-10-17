"""
Module Core DIP: Global Feature Extractor & Statistical Photometric Analyzer
Phụ trách bởi: HẢO (Team Leader)

Nhiệm vụ học thuật:
1. Trích xuất bộ 4 mô-men thống kê mức xám (Statistical Moments):
   - Bậc 1: Mean (Cường độ sáng trung bình mu)
   - Bậc 2: Standard Deviation (Độ tương phản sigma)
   - Bậc 3: Skewness (Độ lệch phân bố sáng/tối S)
   - Bậc 4: Kurtosis (Độ nhọn phân bố K)
2. Trích xuất Grayscale Histogram (16 bins) và chuẩn hóa xác suất L1 (sum = 1.0).
3. Trích xuất đặc trưng màu sắc không gian HSV (Mean Saturation, Mean Value).
4. Đo khoảng cách phân bố với Profile ảnh thẻ chuẩn (Reference Ideal ID Profile) qua:
   - Bhattacharyya Distance (dB)
   - Chi-Square Distance (chi^2)
5. Thuật toán tự động cân bằng sáng (CLAHE - Contrast Limited Adaptive Histogram Equalization).
"""

import cv2
import numpy as np
from typing import Dict, Any, Tuple, List


# Vector phân bố Histogram tham chiếu chuẩn (Tính toán từ thực nghiệm 50 ảnh chuẩn PASS)
REFERENCE_HIST_16 = np.array([
    0.0172, 0.0241, 0.0229, 0.0251, 0.0339, 0.0396, 
    0.0407, 0.0416, 0.0438, 0.0432, 0.0377, 0.0296, 
    0.0203, 0.0168, 0.0070, 0.5562
], dtype=np.float32)

REFERENCE_MEAN = 193.4
REFERENCE_STD = 77.7


def extract_global_features(
    image_bgr: np.ndarray, 
    image_gray: np.ndarray
) -> Dict[str, Any]:
    """
    Trích xuất toàn bộ vector đặc trưng toàn cục của bức ảnh.
    
    Args:
        image_bgr: Ảnh gốc BGR
        image_gray: Ảnh xám Grayscale
        
    Returns:
        dict chứa các mô-men thống kê, histogram chuẩn hóa, khoảng cách Bhattacharyya và phân loại
    """
    # 1. Bộ 4 mô-men thống kê mức xám
    mean_val = float(np.mean(image_gray))
    std_val = float(np.std(image_gray))
    
    # Skewness (Mô-men chuẩn hóa bậc 3)
    # S < 0: Phân bố nghiêng về bên phải (nhiều điểm sáng/trắng)
    # S > 0: Phân bố nghiêng về bên trái (nhiều điểm tối/đen)
    diff = image_gray - mean_val
    skewness_val = float(np.mean((diff / (std_val + 1e-7)) ** 3))
    
    # Kurtosis (Mô-men chuẩn hóa bậc 4 - Excess Kurtosis)
    kurtosis_val = float(np.mean((diff / (std_val + 1e-7)) ** 4) - 3.0)
    
    # 2. Histogram 16 bins & Chuẩn hóa L1
    hist_raw = cv2.calcHist([image_gray], [0], None, [16], [0, 256])
    total_pixels = float(image_gray.size)
    hist_norm_16 = (hist_raw / (total_pixels + 1e-7)).flatten().astype(np.float32)
    hist_list = [round(float(v), 4) for v in hist_norm_16]
    hist_counts = [int(v[0]) for v in hist_raw]
    
    # 3. Phân tích không gian màu HSV
    image_hsv = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV)
    sat_channel = image_hsv[:, :, 1]
    val_channel = image_hsv[:, :, 2]
    mean_saturation = float(np.mean(sat_channel))
    mean_value = float(np.mean(val_channel))
    
    # 4. Đo khoảng cách so sánh với Profile ảnh chuẩn tham chiếu (Bhattacharyya & Chi-Square)
    bhattacharyya_dist = float(cv2.compareHist(
        hist_norm_16.reshape(-1, 1), 
        REFERENCE_HIST_16.reshape(-1, 1), 
        cv2.HISTCMP_BHATTACHARYYA
    ))
    chi_square_dist = float(cv2.compareHist(
        hist_norm_16.reshape(-1, 1), 
        REFERENCE_HIST_16.reshape(-1, 1), 
        cv2.HISTCMP_CHISQR
    ))
    
    # 5. Phân loại trạng thái quang học dựa trên Đặc trưng Toàn cục
    # Ngưỡng thực nghiệm xác định từ tập dataset 350 ảnh
    is_dark = (mean_val < 90.0) or (bhattacharyya_dist > 0.60 and skewness_val > 0.5)
    is_overexposed = (mean_val > 215.0)
    is_low_contrast = (std_val < 30.0)
    
    if is_dark:
        optical_status = "DARK"
        status_label = "Thiếu sáng / Tối om"
    elif is_overexposed:
        optical_status = "OVEREXPOSED"
        status_label = "Cháy sáng / Quá phơi sáng"
    elif is_low_contrast:
        optical_status = "LOW_CONTRAST"
        status_label = "Bạc màu / Tương phản yếu"
    else:
        optical_status = "OPTIMAL"
        status_label = "Đạt chuẩn quang học"
        
    # Vector đặc trưng toàn cục 1D (21 chiều)
    # [Mean, Std, Skewness, Kurtosis, Mean_Sat, Mean_Val, bin_0, ..., bin_15]
    global_feature_vector = [
        round(mean_val, 2),
        round(std_val, 2),
        round(skewness_val, 3),
        round(kurtosis_val, 3),
        round(mean_saturation, 2),
        round(mean_value, 2)
    ] + hist_list

    return {
        "statistical_moments": {
            "mean": round(mean_val, 2),
            "std_dev": round(std_val, 2),
            "skewness": round(skewness_val, 3),
            "kurtosis": round(kurtosis_val, 3),
            "mean_saturation": round(mean_saturation, 2),
            "mean_value": round(mean_value, 2)
        },
        "histogram_16": hist_list,
        "histogram_counts": hist_counts,
        "reference_histogram_16": [round(float(v), 4) for v in REFERENCE_HIST_16],
        "comparison": {
            "bhattacharyya_distance": round(bhattacharyya_dist, 3),
            "chi_square_distance": round(chi_square_dist, 3),
            "reference_mean": REFERENCE_MEAN,
            "reference_std": REFERENCE_STD
        },
        "optical_classification": {
            "status": optical_status,
            "label": status_label,
            "passed": (optical_status == "OPTIMAL")
        },
        "feature_vector_1d": global_feature_vector,
        "vector_dimension": len(global_feature_vector)
    }


def enhance_lighting_clahe(image_bgr: np.ndarray) -> Tuple[np.ndarray, Dict[str, Any]]:
    """
    Thuật toán tự động hiệu chỉnh và cân bằng sáng toàn cục (CLAHE) trên không gian màu LAB.
    Giữ nguyên màu da tự nhiên và tăng cường độ tương phản hài hòa.
    
    Args:
        image_bgr: Ảnh gốc BGR
        
    Returns:
        tuple (enhanced_image_bgr, metrics_after)
    """
    # 1. Chuyển đổi sang không gian màu CIELAB
    lab = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2LAB)
    l_channel, a_channel, b_channel = cv2.split(lab)
    
    # 2. Áp dụng CLAHE (Contrast Limited Adaptive Histogram Equalization) trên kênh L (Luminance)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    cl = clahe.apply(l_channel)
    
    # 3. Gộp lại và chuyển về BGR
    enhanced_lab = cv2.merge((cl, a_channel, b_channel))
    enhanced_bgr = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)
    
    # 4. Tính toán số liệu sau khi cải thiện
    enhanced_gray = cv2.cvtColor(enhanced_bgr, cv2.COLOR_BGR2GRAY)
    new_mean = float(np.mean(enhanced_gray))
    new_std = float(np.std(enhanced_gray))
    new_hist = cv2.calcHist([enhanced_gray], [0], None, [16], [0, 256]).flatten()
    new_hist_norm = (new_hist / (enhanced_gray.size + 1e-7)).tolist()
    
    metrics_after = {
        "new_mean": round(new_mean, 2),
        "new_std": round(new_std, 2),
        "new_histogram_16": [round(float(v), 4) for v in new_hist_norm]
    }
    
    return enhanced_bgr, metrics_after
