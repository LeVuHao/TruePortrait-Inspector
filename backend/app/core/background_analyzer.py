"""
Module 4: Background Uniformity Analysis
Phụ trách bởi: HUY

Thuật toán:
    1. Trích xuất 4 vùng ROI tại 4 góc ảnh (mỗi góc chiếm ~12% chiều rộng & chiều cao).
    2. Với mỗi ROI, tính toán 2 chỉ số:
       - Gray Std Dev: Độ lệch chuẩn cường độ xám → đo sự biến thiên sáng tối.
       - Color Std Dev: Độ lệch chuẩn trung bình trên 3 kênh BGR → đo sự biến thiên màu sắc.
    3. Kết hợp 2 chỉ số thành chỉ số đồng nhất tổng hợp (Combined Std):
       combined_std = 0.5 * gray_std + 0.5 * color_std
    4. Tính trung bình combined_std qua 4 góc → avg_bg_std.
    5. Đánh giá: avg_bg_std <= max_color_std → Nền đồng nhất (PASS).

Lý do học thuật:
    - Nền ảnh thẻ chuẩn (trắng, xanh nhạt) có cả cường độ sáng ĐỀU lẫn màu sắc ĐỀU.
    - Chỉ dùng gray_std có thể bỏ lọt nền có màu biến thiên nhưng sáng đều.
    - Kết hợp cả 2 kênh cho kết quả phân loại chặt chẽ và khoa học hơn.
"""

import cv2
import numpy as np
from typing import Dict, Any, List, Tuple


# ---------------------------------------------------------------------------
# HÀM PHÂN TÍCH CHÍNH (Interface Contract với Pipeline)
# ---------------------------------------------------------------------------

def analyze_background(
    image_bgr: np.ndarray,
    image_gray: np.ndarray,
    preset_config: dict
) -> Tuple[Dict[str, Any], np.ndarray]:
    """
    Phân tích độ đồng nhất của vùng nền đại diện tại 4 góc ảnh.

    Args:
        image_bgr   : Ảnh gốc BGR (np.ndarray, H x W x 3).
        image_gray  : Ảnh xám Grayscale (np.ndarray, H x W).
        preset_config: Cấu hình ngưỡng từ config.py.

    Returns:
        tuple:
            - metrics (dict): Các chỉ số kết quả phân tích nền.
            - visual_img (np.ndarray): Ảnh BGR có vẽ khung 4 góc ROI & số liệu.
    """
    img_h, img_w = image_gray.shape[:2]

    # 1. Xác định kích thước vùng ROI 4 góc (12% chiều rộng, 12% chiều cao)
    roi_w = max(int(img_w * 0.12), 10)
    roi_h = max(int(img_h * 0.12), 10)

    # Định nghĩa 4 góc theo format (x, y, w, h) — góc trên-trái của vùng ROI
    corners: Dict[str, Tuple[int, int, int, int]] = {
        "top_left":     (0,           0,           roi_w, roi_h),
        "top_right":    (img_w - roi_w, 0,          roi_w, roi_h),
        "bottom_left":  (0,           img_h - roi_h, roi_w, roi_h),
        "bottom_right": (img_w - roi_w, img_h - roi_h, roi_w, roi_h),
    }

    # 2. Tính toán chỉ số cho từng vùng ROI
    corner_stds_gray:  List[float] = []
    corner_stds_color: List[float] = []
    corner_combined:   List[float] = []
    corner_details:    List[Dict]  = []

    visual_img = image_bgr.copy()

    for name, (x, y, w, h) in corners.items():
        # Trích xuất vùng ROI
        roi_gray = image_gray[y: y + h, x: x + w]
        roi_bgr  = image_bgr [y: y + h, x: x + w]

        # Tính Std Dev trên ảnh xám
        gray_std = float(np.std(roi_gray))

        # Tính Std Dev trung bình trên 3 kênh màu BGR
        b_std = float(np.std(roi_bgr[:, :, 0]))
        g_std = float(np.std(roi_bgr[:, :, 1]))
        r_std = float(np.std(roi_bgr[:, :, 2]))
        color_std = (b_std + g_std + r_std) / 3.0

        # Chỉ số tổng hợp (weighted average)
        combined = 0.5 * gray_std + 0.5 * color_std

        corner_stds_gray.append(gray_std)
        corner_stds_color.append(color_std)
        corner_combined.append(combined)
        corner_details.append({
            "name":       name,
            "gray_std":   round(gray_std, 2),
            "color_std":  round(color_std, 2),
            "combined":   round(combined, 2),
        })

        # 3. Vẽ khung ROI và thông số lên ảnh trực quan
        cv2.rectangle(visual_img, (x, y), (x + w, y + h), (0, 200, 255), 2)
        label_y = y + h - 6 if y < img_h // 2 else y + 14
        cv2.putText(
            visual_img,
            f"S:{combined:.1f}",
            (x + 3, label_y),
            cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 200, 255), 1, cv2.LINE_AA
        )

    # 4. Chỉ số tổng hợp cuối cùng: trung bình 4 góc
    avg_gray_std  = float(np.mean(corner_stds_gray))
    avg_color_std = float(np.mean(corner_stds_color))
    avg_bg_std    = float(np.mean(corner_combined))   # Chỉ số đánh giá chính

    # 5. Đối chiếu với ngưỡng cấu hình
    bg_rules = preset_config.get("background_uniformity", {})
    max_std  = bg_rules.get("max_color_std", 18.0)

    bg_passed = (avg_bg_std <= max_std)

    # 6. Vẽ chỉ số tổng hợp lên góc trên-trái ảnh
    status_color = (0, 200, 80) if bg_passed else (0, 60, 230)
    cv2.putText(
        visual_img,
        f"BG Uniformity: {'PASS' if bg_passed else 'FAIL'} (Avg={avg_bg_std:.1f})",
        (10, 22),
        cv2.FONT_HERSHEY_SIMPLEX, 0.55, status_color, 2, cv2.LINE_AA
    )

    # 7. Đóng gói kết quả
    if bg_passed:
        message = (
            f"Nền đồng nhất — Chỉ số tổng hợp 4 góc: {avg_bg_std:.2f} "
            f"<= ngưỡng {max_std}."
        )
    else:
        message = (
            f"Nền không đồng nhất hoặc có vật thể / hoa văn — "
            f"Chỉ số tổng hợp 4 góc: {avg_bg_std:.2f} > ngưỡng {max_std}."
        )

    metrics: Dict[str, Any] = {
        "passed":           bg_passed,
        "avg_std_dev":      round(avg_bg_std, 2),    # Chỉ số tổng hợp chính
        "avg_gray_std":     round(avg_gray_std, 2),
        "avg_color_std":    round(avg_color_std, 2),
        "corners_std_dev":  [round(c, 2) for c in corner_combined],
        "corner_details":   corner_details,
        "threshold_max_std": max_std,
        "message":          message,
    }

    return metrics, visual_img
