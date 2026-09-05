"""
Module 5: Rule-based Evaluation & Scoring Engine
Phụ trách bởi: HẢO
Nhiệm vụ:
- Tổng hợp kết quả từ 4 Module (Preprocessor, Face, Quality, Background).
- Tính điểm chất lượng Quality Score (thang 0 - 100) theo trọng số quy định.
- Ra kết luận cuối cùng: ĐẠT (PASS) hoặc KHÔNG ĐẠT (FAIL).
- Tổng hợp danh sách nguyên nhân vi phạm (Failure Reasons) và lời khuyên khắc phục (Recommendations).
"""

from typing import Dict, Any, List
from .config import SCORING_WEIGHTS


def evaluate_photo(
    preproc_metrics: Dict[str, Any],
    face_metrics: Dict[str, Any],
    quality_metrics: Dict[str, Any],
    bg_metrics: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Động cơ đánh giá tổng hợp và tính điểm chất lượng ảnh thẻ.
    
    Returns:
        dict gồm verdict, overall_score, summary, reasons, recommendations, checks
    """
    reasons: List[str] = []
    recommendations: List[str] = []
    current_score = 0
    
    # 1. Tiêu chí kích thước & tỉ lệ ảnh
    size_passed = preproc_metrics.get("passed", False)
    if size_passed:
        current_score += SCORING_WEIGHTS["image_size"]
    else:
        if not preproc_metrics.get("resolution_passed", False):
            reasons.append(f"Độ phân giải ảnh chưa đạt mức tối thiểu ({preproc_metrics.get('width')}x{preproc_metrics.get('height')} < {preproc_metrics.get('min_resolution')}).")
            recommendations.append("Sử dụng ảnh có độ phân giải cao hơn hoặc chụp gần hơn để đảm bảo độ nét.")
        if not preproc_metrics.get("aspect_passed", False):
            reasons.append(f"Tỉ lệ khung hình chưa đúng chuẩn 3:4 (Hiện tại: {preproc_metrics.get('aspect_ratio')}).")
            recommendations.append("Cắt (crop) ảnh theo đúng tỉ lệ chuẩn 3:4 trước khi tải lên.")
            
    # 2. Tiêu chí số lượng khuôn mặt (CRITICAL)
    face_count_data = face_metrics.get("face_count", {})
    face_count_passed = face_count_data.get("passed", False)
    detected_faces = face_count_data.get("detected_count", 0)
    
    if face_count_passed:
        current_score += SCORING_WEIGHTS["face_count"]
    else:
        if detected_faces == 0:
            reasons.append("Không tìm thấy khuôn mặt nào trong ảnh.")
            recommendations.append("Chụp trực diện khuôn mặt, không bị che khuất bởi mũ, tóc hoặc khẩu trang.")
        else:
            reasons.append(f"Phát hiện {detected_faces} khuôn mặt trong khung hình (Yêu cầu duy nhất 1 mặt).")
            recommendations.append("Đảm bảo khung hình chỉ có duy nhất một người chụp.")
            
    # 3. Tiêu chí tỷ lệ chiều cao khuôn mặt (Face Height Ratio)
    face_ratio_data = face_metrics.get("face_height_ratio", {})
    face_ratio_passed = face_ratio_data.get("passed", False)
    
    if face_ratio_passed:
        current_score += SCORING_WEIGHTS["face_height_ratio"]
    else:
        if detected_faces == 1:
            ratio_val = face_ratio_data.get("ratio", 0.0)
            min_r = face_ratio_data.get("threshold_min", 0.45)
            max_r = face_ratio_data.get("threshold_max", 0.70)
            if ratio_val < min_r:
                reasons.append(f"Khuôn mặt chiếm {ratio_val*100:.1f}% chiều cao ảnh (quá nhỏ so với ngưỡng {min_r*100:.0f}%).")
                recommendations.append("Di chuyển lại gần máy ảnh hoặc crop bớt phần thân dưới để khuôn mặt chiếm tỷ lệ lớn hơn.")
            elif ratio_val > max_r:
                reasons.append(f"Khuôn mặt chiếm {ratio_val*100:.1f}% chiều cao ảnh (quá sát khung hình).")
                recommendations.append("Đứng xa máy ảnh một chút để giữ tỷ lệ cân đối giữa đầu và vai.")
                
    # 4. Tiêu chí độ rõ nét (Sharpness / Laplacian)
    sharp_data = quality_metrics.get("sharpness", {})
    sharp_passed = sharp_data.get("passed", False)
    if sharp_passed:
        current_score += SCORING_WEIGHTS["sharpness"]
    else:
        reasons.append(f"Ảnh bị mờ nét (Phương sai Laplacian: {sharp_data.get('laplacian_variance')} < {sharp_data.get('threshold_min')}).")
        recommendations.append("Giữ chắc máy ảnh, lau sạch ống kính và lấy nét trực tiếp vào mắt/khuôn mặt.")
        
    # 5. Tiêu chí độ sáng & tương phản (Brightness)
    bright_data = quality_metrics.get("brightness", {})
    bright_passed = bright_data.get("passed", False)
    if bright_passed:
        current_score += SCORING_WEIGHTS["brightness"]
    else:
        mean_b = bright_data.get("mean_intensity", 0.0)
        min_m = bright_data.get("threshold_min_mean", 90.0)
        max_m = bright_data.get("threshold_max_mean", 210.0)
        if mean_b < min_m:
            reasons.append(f"Ảnh bị thiếu sáng / quá tối (Độ sáng {mean_b:.1f} < {min_m}).")
            recommendations.append("Bật đèn phòng hoặc đứng trước nguồn sáng thuận chiều để khuôn mặt rõ ràng.")
        elif mean_b > max_m:
            reasons.append(f"Ảnh bị cháy sáng / lóa (Độ sáng {mean_b:.1f} > {max_m}).")
            recommendations.append("Giảm độ phơi sáng hoặc tránh nguồn sáng chiếu quá gắt vào mặt.")
        else:
            reasons.append("Độ tương phản ảnh chưa đạt mức tối thiểu.")
            recommendations.append("Cải thiện nguồn sáng để tách rõ khuôn mặt khỏi phông nền.")
            
    # 6. Tiêu chí độ đồng nhất nền (Background Uniformity)
    bg_passed = bg_metrics.get("passed", False)
    if bg_passed:
        current_score += SCORING_WEIGHTS["background_uniformity"]
    else:
        reasons.append(f"Phông nền không đồng nhất (Độ lệch chuẩn 4 góc {bg_metrics.get('avg_std_dev')} > {bg_metrics.get('threshold_max_std')}).")
        recommendations.append("Chụp trước phông nền trơn (tường trắng hoặc xanh nhạt), không có vật thể hoặc họa tiết phía sau.")
        
    # KẾT LUẬN TỔNG THỂ (VERDICT RULE):
    # Một ảnh chỉ ĐẠT nếu không vi phạm tiêu chí bắt buộc sống còn (Face count) và đạt đa số các tiêu chí còn lại
    all_mandatory_passed = face_count_passed and size_passed and sharp_passed and bright_passed
    all_passed = all_mandatory_passed and face_ratio_passed and bg_passed
    
    verdict = "PASS" if (all_passed and current_score >= 80) else "FAIL"
    
    if verdict == "PASS":
        summary = f"Ảnh thẻ đạt tiêu chuẩn với số điểm chất lượng {current_score}/100."
    else:
        summary = f"Ảnh thẻ KHÔNG ĐẠT tiêu chuẩn ({current_score}/100) do có {len(reasons)} tiêu chí chưa thỏa mãn."
        
    return {
        "verdict": verdict,
        "overall_score": int(current_score),
        "summary": summary,
        "reasons": reasons,
        "recommendations": recommendations,
        "checks": {
            "image_size": preproc_metrics,
            "face_count": face_count_data,
            "face_height_ratio": face_ratio_data,
            "sharpness": sharp_data,
            "brightness": bright_data,
            "background_uniformity": bg_metrics
        }
    }
