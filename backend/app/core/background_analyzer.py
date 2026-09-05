"""
Module 4: Background Uniformity Analysis
Phụ trách bởi: HUY
Nhiệm vụ:
- Trích xuất 4 vùng ROI đại diện tại 4 góc ảnh (Top-Left, Top-Right, Bottom-Left, Bottom-Right).
- Tính toán độ lệch chuẩn màu sắc (Color Standard Deviation) trên từng ROI và toàn thể 4 góc.
- Đánh giá mức độ đồng nhất của phông nền (Background Uniformity).
- Tạo ảnh vẽ các vùng ROI đại diện phục vụ trực quan hóa (Visualizer).
"""

import cv2
import numpy as np
from typing import Dict, Any, Tuple, List


def analyze_background(image_bgr: np.ndarray, image_gray: np.ndarray, preset_config: dict) -> Tuple[Dict[str, Any], np.ndarray]:
    """
    Phân tích độ đồng nhất của vùng nền đại diện.
    
    Args:
        image_bgr: Ảnh gốc BGR
        image_gray: Ảnh xám Grayscale
        preset_config: Cấu hình dải ngưỡng
        
    Returns:
        tuple (metrics_dict, corner_rois_visual_image)
    """
    img_h, img_w = image_gray.shape[:2]
    
    # 1. Xác định kích thước vùng ROI 4 góc (khoảng 12% chiều rộng và chiều cao)
    roi_w = int(img_w * 0.12)
    roi_h = int(img_h * 0.12)
    
    corners = {
        "top_left": (0, 0, roi_w, roi_h),
        "top_right": (img_w - roi_w, 0, roi_w, roi_h),
        "bottom_left": (0, img_h - roi_h, roi_w, roi_h),
        "bottom_right": (img_w - roi_w, img_h - roi_h, roi_w, roi_h)
    }
    
    corner_stds: List[float] = []
    
    # Tạo bản sao ảnh để vẽ các hộp ROI 4 góc
    visual_img = image_bgr.copy()
    
    for name, (x, y, w, h) in corners.items():
        roi = image_gray[y:y+h, x:x+w]
        std_val = float(np.std(roi))
        corner_stds.append(std_val)
        
        # Vẽ khung ROI 4 góc màu vàng/cam lên ảnh trực quan
        cv2.rectangle(visual_img, (x, y), (x+w, y+h), (0, 215, 255), 2)
        cv2.putText(visual_img, f"Std:{std_val:.1f}", (x + 2, y + h - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 215, 255), 1)
                    
    # Độ lệch chuẩn nền đại diện là trung bình độ lệch chuẩn của 4 góc
    avg_bg_std = float(np.mean(corner_stds))
    
    bg_rules = preset_config.get("background_uniformity", {})
    max_std = bg_rules.get("max_color_std", 18.0)
    bg_passed = (avg_bg_std <= max_std)
    
    metrics = {
        "passed": bg_passed,
        "avg_std_dev": round(avg_bg_std, 2),
        "corners_std_dev": [round(s, 2) for s in corner_stds],
        "threshold_max_std": max_std,
        "message": f"Nền đồng nhất (Độ lệch chuẩn 4 góc {avg_bg_std:.1f} <= {max_std})." if bg_passed else f"Nền không đồng nhất hoặc có vật thể/hoa văn (Độ lệch chuẩn 4 góc {avg_bg_std:.1f} > {max_std})."
    }
    
    return metrics, visual_img
