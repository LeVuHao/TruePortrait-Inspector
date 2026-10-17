"""
Module 4: Background Uniformity & Segmentation Analysis
Phụ trách bởi: HUY & NHÓM PHOTOCHECK

Cơ sở lý thuyết bám sát Giáo trình & Slide bài giảng:
1. Slide 3 (Xử lý ảnh màu - Ch03):
   - Chuyển đổi không gian màu RGB -> HSV (Hue, Saturation, Value).
   - Phân đoạn màu (Color Segmentation): Nhận diện miền màu phông nền dựa trên màu hạt giống (Seed Color)
     và ngưỡng sai khác màu trong không gian HSV.
2. Slide 4 (Hình thái học - Ch04):
   - Phép mở (Morphological Opening) với phần tử cấu trúc SE 5x5: Khử nhiễu lốm đốm.
   - Phép đóng (Morphological Closing) với SE 7x7: Điền đầy các khe hở và làm mịn đường viền phông nền.
   - Trích xuất thành phần liên thông (Connected Components): Cô lập thành phần phông nền liên thông lớn nhất bao quanh chủ thể.
3. Đánh giá độ đồng nhất:
   - Tính độ lệch chuẩn màu (Std Dev) trên toàn bộ miền phông nền đã phân đoạn kết hợp 4 góc ROI.
"""

import cv2
import numpy as np
from typing import Dict, Any, List, Tuple


def segment_background_hsv_morphology(
    image_bgr: np.ndarray, 
    corners_coords: List[Tuple[int, int, int, int]]
) -> Tuple[np.ndarray, float, str]:
    """
    Phân đoạn vùng phông nền bằng không gian màu HSV và Xử lý hình thái học (Morphology).
    
    Args:
        image_bgr: Ảnh gốc BGR
        corners_coords: Tọa độ 4 góc ROI (x, y, w, h)
        
    Returns:
        tuple (bg_mask_binary, bg_segmented_std, detected_bg_type)
    """
    img_h, img_w = image_bgr.shape[:2]
    image_hsv = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV)
    
    # 1. Thu thập mẫu màu nền từ 4 góc (Background Seeds)
    seed_pixels = []
    for (x, y, w, h) in corners_coords:
        roi_hsv = image_hsv[y:y+h, x:x+w]
        seed_pixels.append(roi_hsv.reshape(-1, 3))
    all_seeds = np.vstack(seed_pixels)
    
    median_hsv = np.median(all_seeds, axis=0)
    med_h, med_s, med_v = median_hsv[0], median_hsv[1], median_hsv[2]
    
    # Nhận diện loại phông nền
    if med_s < 40 and med_v > 160:
        detected_bg_type = "WHITE_BACKGROUND"
        # Ngưỡng màu nền trắng (S thấp, V cao)
        lower_bound = np.array([0, 0, 140], dtype=np.uint8)
        upper_bound = np.array([180, 50, 255], dtype=np.uint8)
    elif 85 <= med_h <= 135:
        detected_bg_type = "BLUE_BACKGROUND"
        # Ngưỡng màu nền xanh (H trong dải xanh dương)
        lower_bound = np.array([max(0, med_h - 25), max(30, med_s - 50), max(50, med_v - 70)], dtype=np.uint8)
        upper_bound = np.array([min(180, med_h + 25), min(255, med_s + 60), min(255, med_v + 60)], dtype=np.uint8)
    else:
        detected_bg_type = "CUSTOM_BACKGROUND"
        lower_bound = np.array([max(0, med_h - 20), max(0, med_s - 45), max(40, med_v - 60)], dtype=np.uint8)
        upper_bound = np.array([min(180, med_h + 20), min(255, med_s + 45), min(255, med_v + 60)], dtype=np.uint8)
        
    # 2. Tạo mặt nạ nhị phân thô bằng phân đoạn màu HSV (Slide 3)
    raw_mask = cv2.inRange(image_hsv, lower_bound, upper_bound)
    
    # 3. Áp dụng các phép toán hình thái học (Slide 4: Mathematical Morphology)
    # Phần tử cấu trúc SE hình elip 5x5 và 7x7
    se_open = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    se_close = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    
    # Phép mở (Opening): Xóa các điểm nhiễu li ti
    mask_open = cv2.morphologyEx(raw_mask, cv2.MORPH_OPEN, se_open)
    # Phép đóng (Closing): Nối liền các khoảng trống và làm mịn đường viền
    mask_clean = cv2.morphologyEx(mask_open, cv2.MORPH_CLOSE, se_close)
    
    # 4. Trích xuất thành phần liên thông (Connected Components) giữ lại vùng nền lớn nhất
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(mask_clean, connectivity=8)
    
    # Tìm nhãn nền chứa các góc ảnh
    bg_final_mask = np.zeros_like(mask_clean)
    corner_points = [(5, 5), (img_w - 5, 5), (5, img_h - 5), (img_w - 5, img_h - 5)]
    bg_labels = set()
    for (cx, cy) in corner_points:
        lbl = labels[cy, cx]
        if lbl > 0:
            bg_labels.add(lbl)
            
    if bg_labels:
        for lbl in bg_labels:
            bg_final_mask[labels == lbl] = 255
    else:
        # Nếu không bắt được nhãn góc, lấy thành phần có diện tích lớn nhất (sau background=0)
        if num_labels > 1:
            largest_label = 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA])
            bg_final_mask[labels == largest_label] = 255
        else:
            bg_final_mask = mask_clean
            
    # 5. Tính độ lệch chuẩn màu sắc trên miền nền đã phân đoạn
    bg_pixels = image_bgr[bg_final_mask == 255]
    if len(bg_pixels) > 50:
        std_b = float(np.std(bg_pixels[:, 0]))
        std_g = float(np.std(bg_pixels[:, 1]))
        std_r = float(np.std(bg_pixels[:, 2]))
        bg_segmented_std = (std_b + std_g + std_r) / 3.0
    else:
        bg_segmented_std = 25.0
        
    return bg_final_mask, bg_segmented_std, detected_bg_type


def analyze_background(
    image_bgr: np.ndarray,
    image_gray: np.ndarray,
    preset_config: dict
) -> Tuple[Dict[str, Any], np.ndarray]:
    """
    Phân tích độ đồng nhất phông nền kết hợp Phân đoạn màu HSV (Slide 3),
    Hình thái học Morphology (Slide 4) và Thống kê 4 góc ROI.
    """
    img_h, img_w = image_gray.shape[:2]

    # 1. Xác định kích thước vùng ROI 4 góc (12% chiều rộng, 12% chiều cao)
    roi_w = max(int(img_w * 0.12), 10)
    roi_h = max(int(img_h * 0.12), 10)

    corners: Dict[str, Tuple[int, int, int, int]] = {
        "top_left":     (0,               0,               roi_w, roi_h),
        "top_right":    (img_w - roi_w,   0,               roi_w, roi_h),
        "bottom_left":  (0,               img_h - roi_h,   roi_w, roi_h),
        "bottom_right": (img_w - roi_w,   img_h - roi_h,   roi_w, roi_h),
    }

    # 2. Phân đoạn màu HSV & Morphology toàn miền nền
    corner_coords = list(corners.values())
    bg_mask, bg_segmented_std, bg_type = segment_background_hsv_morphology(image_bgr, corner_coords)

    # 3. Tính toán chỉ số thống kê 4 góc ROI
    corner_stds_gray:  List[float] = []
    corner_stds_color: List[float] = []
    corner_combined:   List[float] = []
    corner_details:    List[Dict]  = []

    visual_img = image_bgr.copy()

    # Phủ lớp màu Cyan bán trong suốt lên vùng nền đã phân đoạn bằng Morphology
    overlay = visual_img.copy()
    overlay[bg_mask == 255] = [230, 200, 150]  # Light cyan-blue tint
    cv2.addWeighted(overlay, 0.25, visual_img, 0.75, 0, visual_img)

    for name, (x, y, w, h) in corners.items():
        roi_gray = image_gray[y: y + h, x: x + w]
        roi_bgr  = image_bgr [y: y + h, x: x + w]

        gray_std = float(np.std(roi_gray))
        b_std = float(np.std(roi_bgr[:, :, 0]))
        g_std = float(np.std(roi_bgr[:, :, 1]))
        r_std = float(np.std(roi_bgr[:, :, 2]))
        color_std = (b_std + g_std + r_std) / 3.0

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

        # Vẽ khung ROI 4 góc
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
    avg_bg_std    = float(np.mean(corner_combined))

    # 5. Đối chiếu ngưỡng
    bg_rules = preset_config.get("background_uniformity", {})
    max_std  = bg_rules.get("max_color_std", 18.0)
    bg_passed = (avg_bg_std <= max_std)

    # 6. Vẽ thông số lên ảnh
    status_color = (0, 200, 80) if bg_passed else (0, 60, 230)
    cv2.putText(
        visual_img,
        f"HSV+Morph BG: {'PASS' if bg_passed else 'FAIL'} (Avg={avg_bg_std:.1f}, {bg_type})",
        (10, 22),
        cv2.FONT_HERSHEY_SIMPLEX, 0.55, status_color, 2, cv2.LINE_AA
    )

    if bg_passed:
        message = (
            f"Phông nền đồng nhất ({bg_type}) — Phân đoạn HSV & Morphology đạt chuẩn, "
            f"Std 4 góc: {avg_bg_std:.2f} <= {max_std}."
        )
    else:
        message = (
            f"Phông nền không đồng nhất hoặc có vật thể/hoa văn — "
            f"Chỉ số biến thiên màu: {avg_bg_std:.2f} > ngưỡng {max_std}."
        )

    metrics: Dict[str, Any] = {
        "passed":             bg_passed,
        "avg_std_dev":        round(avg_bg_std, 2),
        "avg_gray_std":       round(avg_gray_std, 2),
        "avg_color_std":      round(avg_color_std, 2),
        "segmented_bg_std":   round(bg_segmented_std, 2),
        "bg_type":            bg_type,
        "corners_std_dev":    [round(c, 2) for c in corner_combined],
        "corner_details":     corner_details,
        "threshold_max_std":  max_std,
        "message":            message,
    }

    return metrics, visual_img
