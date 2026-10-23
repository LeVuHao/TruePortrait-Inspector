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


# Vector phân bố Histogram tham chiếu chuẩn nền trắng (ICAO White Background)
REFERENCE_HIST_16_WHITE = np.array([
    0.0172, 0.0241, 0.0229, 0.0251, 0.0339, 0.0396, 
    0.0407, 0.0416, 0.0438, 0.0432, 0.0377, 0.0296, 
    0.0203, 0.0168, 0.0070, 0.5562
], dtype=np.float32)

# Vector phân bố Histogram tham chiếu chuẩn nền xanh (Vietnam Student / Standard Blue Background)
REFERENCE_HIST_16_BLUE = np.array([
    0.0200, 0.0300, 0.0350, 0.0300, 0.0250, 0.0350, 
    0.0950, 0.2800, 0.2200, 0.0850, 0.0550, 0.0400, 
    0.0300, 0.0250, 0.0250, 0.0700
], dtype=np.float32)
REFERENCE_HIST_16_BLUE = REFERENCE_HIST_16_BLUE / np.sum(REFERENCE_HIST_16_BLUE)

REFERENCE_HIST_16 = REFERENCE_HIST_16_WHITE

REFERENCE_MEAN_WHITE = 193.4
REFERENCE_STD_WHITE = 77.7
REFERENCE_MEAN_BLUE = 142.0
REFERENCE_STD_BLUE = 60.5

REFERENCE_MEAN = REFERENCE_MEAN_WHITE
REFERENCE_STD = REFERENCE_STD_WHITE


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
    img_h, img_w = image_gray.shape[:2]

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
    
    # 3. Phân tích không gian màu HSV & Nhận diện màu phông nền sơ bộ
    image_hsv = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV)
    sat_channel = image_hsv[:, :, 1]
    val_channel = image_hsv[:, :, 2]
    mean_saturation = float(np.mean(sat_channel))
    mean_value = float(np.mean(val_channel))
    
    # Lấy mẫu màu 4 góc nền
    rw = max(int(img_w * 0.12), 10)
    rh = max(int(img_h * 0.12), 10)
    corner_rois_hsv = [
        image_hsv[0:rh, 0:rw],
        image_hsv[0:rh, img_w-rw:img_w],
        image_hsv[img_h-rh:img_h, 0:rw],
        image_hsv[img_h-rh:img_h, img_w-rw:img_w]
    ]
    corner_pixels_hsv = np.vstack([c.reshape(-1, 3) for c in corner_rois_hsv])
    median_hsv = np.median(corner_pixels_hsv, axis=0)
    med_h, med_s, med_v = float(median_hsv[0]), float(median_hsv[1]), float(median_hsv[2])

    is_blue_bg = (85 <= med_h <= 135) and (med_s >= 30)
    is_white_bg = (med_s < 45) and (med_v >= 170)

    # 4. Đo khoảng cách so sánh với Profile ảnh chuẩn tham chiếu thích ứng
    d_white = float(cv2.compareHist(
        hist_norm_16.reshape(-1, 1), 
        REFERENCE_HIST_16_WHITE.reshape(-1, 1), 
        cv2.HISTCMP_BHATTACHARYYA
    ))
    d_blue = float(cv2.compareHist(
        hist_norm_16.reshape(-1, 1), 
        REFERENCE_HIST_16_BLUE.reshape(-1, 1), 
        cv2.HISTCMP_BHATTACHARYYA
    ))

    chi_white = float(cv2.compareHist(
        hist_norm_16.reshape(-1, 1), 
        REFERENCE_HIST_16_WHITE.reshape(-1, 1), 
        cv2.HISTCMP_CHISQR
    ))
    chi_blue = float(cv2.compareHist(
        hist_norm_16.reshape(-1, 1), 
        REFERENCE_HIST_16_BLUE.reshape(-1, 1), 
        cv2.HISTCMP_CHISQR
    ))

    # Nếu phát hiện phông nền xanh (hoặc histogram khớp với phông xanh tốt hơn nhiều), chọn profile phông xanh
    if is_blue_bg or (d_blue < d_white and not is_white_bg):
        bhattacharyya_dist = d_blue
        chi_square_dist = chi_blue
        target_ref_hist = REFERENCE_HIST_16_BLUE
        ref_mean = REFERENCE_MEAN_BLUE
        ref_std = REFERENCE_STD_BLUE
        ref_bg_type = "BLUE_BACKGROUND"
    else:
        bhattacharyya_dist = d_white
        chi_square_dist = chi_white
        target_ref_hist = REFERENCE_HIST_16_WHITE
        ref_mean = REFERENCE_MEAN_WHITE
        ref_std = REFERENCE_STD_WHITE
        ref_bg_type = "WHITE_BACKGROUND"

    # 5. Phân loại trạng thái quang học dựa trên Đặc trưng Toàn cục
    # Loại trừ phần áo phía dưới khi đo highlight ratio để tránh nhầm áo sơ mi trắng với chói sáng
    upper_h = int(img_h * 0.65)
    upper_highlight_ratio = float(np.mean(image_gray[:upper_h, :] >= 245))

    if is_white_bg:
        is_overexposed = (mean_val > 222.0)
    else:
        is_overexposed = (mean_val > 215.0) or (upper_highlight_ratio > 0.05)

    is_dark = (mean_val < 90.0) or (bhattacharyya_dist > 0.55 and skewness_val > 0.6)
    is_low_contrast = (std_val < 25.0)
    
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
        "reference_histogram_16": [round(float(v), 4) for v in target_ref_hist],
        "comparison": {
            "bhattacharyya_distance": round(bhattacharyya_dist, 3),
            "chi_square_distance": round(chi_square_dist, 3),
            "reference_mean": ref_mean,
            "reference_std": ref_std,
            "reference_bg_type": ref_bg_type
        },
        "optical_classification": {
            "status": optical_status,
            "label": status_label,
            "passed": (optical_status == "OPTIMAL")
        },
        "feature_vector_1d": global_feature_vector,
        "vector_dimension": len(global_feature_vector)
    }


def enhance_portrait_smooth_sharp(image_bgr: np.ndarray) -> Tuple[np.ndarray, Dict[str, Any]]:
    """
    Thuật toán Làm Mịn Da & Tăng Cường Độ Nét Chân Dung Chuẩn Giáo Trình XLA (DIP):
    1. Làm mịn da bảo toàn cạnh (Edge-Preserving Skin Smoothing - Chương 3 DIP):
       - Áp dụng Bilateral Filter (Lọc song phương).
       - Làm mờ hạt nhiễu, lỗ chân lông và làm mịn da nhưng bảo toàn nguyên vẹn 100% 
         các đường biên cạnh có độ dốc lớn (mắt, con ngươi, sống mũi, bờ môi, viền tóc).
    2. Tăng cường độ nét chi tiết (High-Boost Sharpening / Unsharp Masking - Chương 3.6 DIP):
       - Trích xuất mặt nạ chi tiết biên tần số cao: mask = f_smooth - GaussianBlur(f_smooth).
       - Khuếch đại viền mắt, sợi tóc, chân mày giúp ảnh nét căng, sắc sảo như app chỉnh ảnh điện thoại.
    3. Thích ứng ánh sáng tự nhiên (Adaptive Natural Tone):
       - Nếu ảnh bị thiếu sáng (< 90), nâng sáng nhẹ nhàng bằng Gamma Power-law mà không làm cháy trắng phông nền.
       
    Args:
        image_bgr: Ảnh gốc BGR
        
    Returns:
        tuple (enhanced_image_bgr, metrics_after)
    """
    img_gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    mean_val = float(np.mean(img_gray))
    work_img = image_bgr.copy()
    
    # Nếu ảnh quá tối thì nâng sáng dịu bằng Gamma trước
    if mean_val < 90.0:
        gamma = 0.72
        lut = np.array([np.clip(((i / 255.0) ** gamma) * 255.0, 0, 255) for i in range(256)]).astype('uint8')
        work_img = cv2.LUT(work_img, lut)
        
    # Bước 1: Lọc song phương (Bilateral Filter) làm mịn da mặt nhưng giữ nguyên viền mắt, mũi, miệng
    # d=9: Bán kính lân cận; sigmaColor=45: Ngưỡng chênh lệch màu; sigmaSpace=45: Không gian tọa độ
    smooth = cv2.bilateralFilter(work_img, d=9, sigmaColor=45, sigmaSpace=45)
    
    # Bước 2: Unsharp Masking (High-Boost Filter) làm nét đanh sợi tóc, con ngươi mắt và viền môi
    # Công thức DIP: f_sharp = smooth + k * (smooth - gaussian_blur)
    gaussian = cv2.GaussianBlur(smooth, (0, 0), sigmaX=2.0)
    enhanced_bgr = cv2.addWeighted(smooth, 1.45, gaussian, -0.45, 0)
    
    # Tính toán thông số sau khi làm mịn và tăng nét
    enhanced_gray = cv2.cvtColor(enhanced_bgr, cv2.COLOR_BGR2GRAY)
    new_mean = float(np.mean(enhanced_gray))
    new_std = float(np.std(enhanced_gray))
    new_lap_var = float(cv2.Laplacian(enhanced_gray, cv2.CV_64F).var())
    new_hist = cv2.calcHist([enhanced_gray], [0], None, [16], [0, 256]).flatten()
    new_hist_norm = (new_hist / (enhanced_gray.size + 1e-7)).tolist()
    
    metrics_after = {
        "new_mean": round(new_mean, 2),
        "new_std": round(new_std, 2),
        "new_laplacian_var": round(new_lap_var, 2),
        "new_histogram_16": [round(float(v), 4) for v in new_hist_norm]
    }
    
    return enhanced_bgr, metrics_after


# Alias tương thích ngược để không ảnh hưởng đến các module khác
enhance_lighting_clahe = enhance_portrait_smooth_sharp


