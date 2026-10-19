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


def analyze_quality(
    image_bgr: np.ndarray, 
    image_gray: np.ndarray, 
    preset_config: dict,
    face_boxes: list = None
) -> Tuple[Dict[str, Any], np.ndarray, np.ndarray]:
    """
    Phân tích chất lượng quang học và trích xuất Đặc trưng Toàn cục + Cục bộ khuôn mặt.
    
    Args:
        image_bgr: Ảnh gốc BGR
        image_gray: Ảnh xám Grayscale
        preset_config: Cấu hình dải ngưỡng
        face_boxes: Danh sách bounding boxes khuôn mặt từ face_analyzer
        
    Returns:
        tuple (metrics_dict, laplacian_map_image, clahe_enhanced_image)
    """
    img_h, img_w = image_gray.shape[:2]

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
    max_highlight_ratio = bright_rules.get("max_highlight_ratio", 0.035)
    max_face_highlight = bright_rules.get("max_face_highlight_ratio", 0.04)
    max_face_asym = bright_rules.get("max_face_asymmetry", 28.0)
    min_face_m = bright_rules.get("min_face_mean", 85.0)
    max_face_m = bright_rules.get("max_face_mean", 215.0)
    
    # Tỷ lệ pixel bão hòa sáng / tối toàn ảnh
    highlight_clipping_ratio = float(np.mean(image_gray >= 245))
    shadow_clipping_ratio = float(np.mean(image_gray <= 15))

    # Nhận diện sơ bộ hậu cảnh 4 góc có phải phông nền trắng đồng nhất hay không
    rw = max(int(img_w * 0.12), 10)
    rh = max(int(img_h * 0.12), 10)
    corner_rois = [
        image_gray[0:rh, 0:rw],
        image_gray[0:rh, img_w-rw:img_w],
        image_gray[img_h-rh:img_h, 0:rw],
        image_gray[img_h-rh:img_h, img_w-rw:img_w]
    ]
    corner_means = [float(np.mean(c)) for c in corner_rois]
    is_white_bg = (np.mean(corner_means) >= 200.0) and (abs(corner_means[0] - corner_means[1]) < 25.0) and (abs(corner_means[2] - corner_means[3]) < 25.0)

    # Nếu không phải phông nền trắng đồng nhất mà có pixel >= 245 vượt ngưỡng 3.5% -> Có đèn rọi chói / cháy sáng
    has_scene_glare = (not is_white_bg) and (highlight_clipping_ratio > max_highlight_ratio)

    # 3. Phân tích quang học chuyên sâu trên vùng khuôn mặt cốt lõi (Inner Face ROI)
    face_photometry = {
        "has_face": False,
        "face_mean": round(brightness_mean, 1),
        "face_highlight_ratio": 0.0,
        "face_asymmetry": 0.0,
        "passed": True,
        "issues": []
    }

    if face_boxes and len(face_boxes) > 0:
        fb = face_boxes[0]
        fx, fy = max(0, fb["x"]), max(0, fb["y"])
        fw, fh = min(img_w - fx, fb["width"]), min(img_h - fy, fb["height"])
        if fw > 20 and fh > 20:
            # Lấy vùng ngũ quan bên trong mặt (loại trừ tóc và mép nền ngoài biên box)
            iy1, iy2 = max(0, int(fy + 0.22 * fh)), min(img_h, int(fy + 0.88 * fh))
            ix1, ix2 = max(0, int(fx + 0.18 * fw)), min(img_w, int(fx + 0.82 * fw))
            face_roi_gray = image_gray[iy1:iy2, ix1:ix2]
            
            if face_roi_gray.size > 20:
                f_mean = float(np.mean(face_roi_gray))
                f_high = float(np.mean(face_roi_gray >= 245))
                
                # Đo bất đối xứng chiếu sáng 2 nửa mặt (Left vs Right)
                half_w = face_roi_gray.shape[1] // 2
                left_half_mean = float(np.mean(face_roi_gray[:, :half_w]))
                right_half_mean = float(np.mean(face_roi_gray[:, half_w:]))
                f_asym = abs(left_half_mean - right_half_mean)

                face_issues = []
                # Ngưỡng lóa sáng trên da mặt: 6% diện tích vùng ngũ quan
                if f_high > 0.06:
                    face_issues.append(f"Khuôn mặt bị chói lóa bóng dầu ({f_high*100:.1f}% diện tích mặt bão hòa trắng)")
                if f_asym > max_face_asym:
                    face_issues.append(f"Chiếu sáng lệch một bên mặt (chênh lệch {f_asym:.1f} mức sáng)")
                if f_mean < 80.0:
                    face_issues.append(f"Khuôn mặt bị tối sạm (độ sáng mặt {f_mean:.1f} < 80.0)")
                elif f_mean > 200.0:
                    face_issues.append(f"Khuôn mặt bị cháy sáng quá mức ({f_mean:.1f} > 200.0)")

                face_photometry = {
                    "has_face": True,
                    "face_mean": round(f_mean, 1),
                    "face_highlight_ratio": round(f_high, 4),
                    "face_asymmetry": round(f_asym, 1),
                    "passed": len(face_issues) == 0,
                    "issues": face_issues
                }

    # ĐÁNH GIÁ CHUẨN ĐỘ SÁNG KHOA HỌC:
    # 1. Trung bình toàn ảnh trong dải chuẩn [90, 210]
    # 2. Độ tương phản Std >= 25.0
    # 3. Khoảng cách Bhattacharyya với profile chuẩn <= 0.45
    # 4. Không bị chói lóa / cháy sáng đèn rọi (has_scene_glare == False)
    # 5. Vùng mặt (Face ROI) phải đạt chuẩn quang học, không chói bóng hay lệch sáng gắt
    global_bright_passed = (min_mean <= brightness_mean <= max_mean) and (contrast_std >= min_contrast) and (bhattacharyya_dist <= 0.45) and (not has_scene_glare)
    brightness_passed = global_bright_passed and face_photometry["passed"]
    
    bright_msg = []
    if has_scene_glare:
        bright_msg.append(f"Ảnh bị chói sáng / cháy sáng cục bộ ({highlight_clipping_ratio*100:.1f}% diện tích bị lóa trắng).")
    if face_photometry["issues"]:
        bright_msg.extend(face_photometry["issues"])
    if optical_cls["status"] == "DARK" or brightness_mean < min_mean:
        bright_msg.append(f"Ảnh thiếu sáng nghiêm trọng (Mean: {brightness_mean:.1f}, Skewness: {skewness_val:+.2f}).")
    elif brightness_mean > max_mean:
        bright_msg.append(f"Toàn bộ ảnh bị cháy sáng quá mức (Mean: {brightness_mean:.1f} > {max_mean}).")
    elif contrast_std < min_contrast:
        bright_msg.append(f"Độ tương phản thấp / bạc màu (Std: {contrast_std:.1f} < {min_contrast}).")
        
    if not bright_msg:
        bright_msg.append(f"Độ sáng và phân bố màu sắc đạt chuẩn (Mean: {brightness_mean:.1f}, Bhattacharyya: {bhattacharyya_dist:.3f}).")
        
    # 4. Tự động sinh ảnh cân bằng sáng bằng thuật toán CLAHE
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
            "highlight_clipping_ratio": round(highlight_clipping_ratio, 4),
            "shadow_clipping_ratio": round(shadow_clipping_ratio, 4),
            "bhattacharyya_distance": round(bhattacharyya_dist, 3),
            "chi_square_distance": comparison["chi_square_distance"],
            "threshold_min_mean": min_mean,
            "threshold_max_mean": max_mean,
            "threshold_min_contrast": min_contrast,
            "threshold_max_highlight": max_highlight_ratio,
            "face_photometry": face_photometry,
            "optical_status": "OVEREXPOSED" if (highlight_clipping_ratio > max_highlight_ratio or not face_photometry["passed"]) else optical_cls["status"],
            "optical_label": "Cháy sáng / Chói lóa" if (highlight_clipping_ratio > max_highlight_ratio or not face_photometry["passed"]) else optical_cls["label"],
            "message": " ".join(bright_msg),
            "histogram_data": global_features["histogram_counts"],
            "histogram_normalized_16": global_features["histogram_16"],
            "reference_histogram_16": global_features["reference_histogram_16"]
        },
        "global_feature_vector": global_features["feature_vector_1d"],
        "clahe_enhancement": clahe_metrics
    }
    
    return metrics, laplacian_map, clahe_enhanced_bgr

