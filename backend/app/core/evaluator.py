"""
Module 5: Rule-based Evaluation & Scoring Engine
Phụ trách bởi: HẢO
Nhiệm vụ:
- Tổng hợp kết quả từ 4 Module (Preprocessor, Face, Quality, Background).
- Tính điểm chất lượng Quality Score (thang 0 - 100) theo trọng số quy định.
- Ra kết luận cuối cùng: ĐẠT (PASS) hoặc KHÔNG ĐẠT (FAIL).
- Đưa ra chẩn đoán chi tiết, phân cấp mức độ lỗi sát thực tế (hơi mờ vs mờ nhòe, hơi sáng chói vs cháy sáng, phông nền bị mờ vs bóng đổ...).
- Xuất danh sách lời khuyên khắc phục trực quan, chính xác theo từng lỗi cụ thể.
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
    Động cơ đánh giá tổng hợp, chẩn đoán phân cấp mức độ lỗi sát nghĩa thực tế và sinh lời khuyên khắc phục.
    
    Returns:
        dict gồm verdict, overall_score, summary, reasons, recommendations, checks
    """
    good_points: List[str] = []
    reasons: List[str] = []
    recommendations: List[str] = []
    current_score = 0
    
    # ────────────────────────────────────────────────────────────────────────────
    # 1. TIÊU CHÍ KÍCH THƯỚC & TỈ LỆ KHUNG HÌNH (Chương 1) - TỐI ĐA 15 ĐIỂM
    # ────────────────────────────────────────────────────────────────────────────
    size_passed = preproc_metrics.get("passed", False)
    w = preproc_metrics.get("width", 0)
    h = preproc_metrics.get("height", 0)
    asp = preproc_metrics.get("aspect_ratio", 0.0)
    aspect_passed = preproc_metrics.get("aspect_passed", False)
    res_passed = preproc_metrics.get("resolution_passed", False)
    preproc_metrics["score_max"] = SCORING_WEIGHTS["image_size"]

    if size_passed:
        preproc_metrics["score_earned"] = SCORING_WEIGHTS["image_size"]
        current_score += SCORING_WEIGHTS["image_size"]
        preproc_metrics["friendly_pass"] = f"Khung hình cân đối ({asp:.2f}), kích thước {w}×{h} px đạt chuẩn in ấn sắc nét."
        good_points.append(
            f"Kích thước & Tỉ lệ chuẩn ({w}x{h} px): Khung hình chuẩn tỷ lệ ảnh thẻ ({asp:.3f}) và độ phân giải rõ nét, đảm bảo chất lượng in ấn."
        )
    elif aspect_passed or res_passed:
        # Thư thả: Đạt 1 trong 2 tiêu chí (ví dụ khung hình rất đẹp nhưng độ phân giải hơi nhỏ, hoặc ngược lại)
        partial_score = 10
        preproc_metrics["score_earned"] = partial_score
        current_score += partial_score
        if aspect_passed:
            preproc_metrics["friendly_pass"] = f"Tỉ lệ khung hình rất chuẩn ({asp:.2f}), độ phân giải {w}×{h} px ở mức tạm chấp nhận (+10đ)."
            good_points.append(f"Tỉ lệ khung hình cân đối ({asp:.2f}): Đúng khung ảnh thẻ chuẩn.")
            reasons.append(f"Độ phân giải {w}x{h} px hơi nhỏ hơn mức khuyến nghị 600x800 px khi in kích thước lớn.")
        else:
            preproc_metrics["friendly_pass"] = f"Độ phân giải {w}×{h} px rất nét, tỉ lệ ({asp:.2f}) hơi lệch so với khung chuẩn (+10đ)."
            good_points.append(f"Độ phân giải cao ({w}x{h} px): Ảnh sắc nét, chi tiết tốt.")
            reasons.append(f"Tỉ lệ khung hình ({asp:.2f}) hơi lệch nhẹ so với khung chuẩn 3:4/4:6.")
    else:
        preproc_metrics["score_earned"] = 0
        size_flaws = []
        if not aspect_passed:
            size_flaws.append(f"khung hình bị méo lệch ({asp:.2f} thay vì chuẩn 3:4/4:6)")
        if not res_passed:
            size_flaws.append(f"độ phân giải {w}×{h} px quá bé (dưới 400×500)")
        preproc_metrics["friendly_fail"] = "Ảnh bị " + " và ".join(size_flaws) + "."
        
        if not res_passed:
            reasons.append(f"Độ phân giải rất thấp ({w}x{h} px) – ảnh quá nhỏ, mật độ điểm ảnh không đủ để in ấn rõ nét (chuẩn tối thiểu 400x500 px).")
            recommendations.append("Sử dụng camera có độ phân giải gốc cao hơn hoặc gửi file gốc chất lượng cao.")

        if not aspect_passed:
            reasons.append(f"Tỉ lệ khung hình sai lệch rõ rệt ({asp:.3f}) – ảnh đang ở tỷ lệ màn hình rộng hoặc vuông thay vì ảnh thẻ chân dung.")
            recommendations.append("Cài đặt khung chụp ảnh thẻ tỷ lệ 3:4 hoặc 4:6 trên ứng dụng camera điện thoại trước khi chụp.")

    # ────────────────────────────────────────────────────────────────────────────
    # 2. TIÊU CHÍ SỐ LƯỢNG KHUÔN MẶT (CRITICAL - Chương 7) - TỐI ĐA 25 ĐIỂM
    # ────────────────────────────────────────────────────────────────────────────
    face_count_data = face_metrics.get("face_count", {})
    face_count_passed = face_count_data.get("passed", False)
    detected_faces = face_count_data.get("detected_count", 0)
    face_count_data["score_max"] = SCORING_WEIGHTS["face_count"]
    face_count_data["score_earned"] = SCORING_WEIGHTS["face_count"] if face_count_passed else 0
    
    if face_count_passed:
        current_score += SCORING_WEIGHTS["face_count"]
        face_count_data["friendly_pass"] = "Có duy nhất 1 người chụp, mắt nhìn thẳng vào ống kính máy ảnh."
        good_points.append(
            "Nhận diện chủ thể chuẩn xác: Phát hiện duy nhất 1 khuôn mặt trực diện rõ ràng, góc nhìn thẳng vào ống kính máy ảnh."
        )
    else:
        if detected_faces == 0:
            face_count_data["friendly_fail"] = "Không phát hiện khuôn mặt rõ nét (mặt bị che khuất, quay nghiêng góc hoặc quá tối)."
            reasons.append("Không phát hiện được khuôn mặt trực diện rõ nét – khuôn mặt có thể bị che khuất, quay nghiêng góc quá lớn hoặc quá mờ tối.")
            recommendations.append("Đứng hoặc ngồi thẳng lưng, nhìn thẳng vào ống kính máy ảnh, vén tóc mái không để che mắt/lông mày và tháo khẩu trang.")
        else:
            face_count_data["friendly_fail"] = f"Phát hiện {detected_faces} người trong ảnh (ảnh thẻ chỉ được phép chụp duy nhất 1 người)."
            reasons.append(f"Phát hiện {detected_faces} khuôn mặt trong khung hình – có người đứng lẫn vào hậu cảnh hoặc tranh ảnh hình người lọt vào bức ảnh.")
            recommendations.append("Đảm bảo khung hình chỉ có duy nhất một người chụp, căn góc máy để loại bỏ hoàn toàn người hoặc tranh ảnh phía sau.")

    # ────────────────────────────────────────────────────────────────────────────
    # 3. TIÊU CHÍ TỶ LỆ CHIỀU CAO KHUÔN MẶT & VỊ TRÍ TRỤC (Chương 1 & ICAO) - TỐI ĐA 20 ĐIỂM
    # ────────────────────────────────────────────────────────────────────────────
    face_ratio_data = face_metrics.get("face_height_ratio", {})
    ratio_val = face_ratio_data.get("ratio", 0.0)
    face_ratio_data["score_max"] = SCORING_WEIGHTS["face_height_ratio"]
    
    min_r = face_ratio_data.get("threshold_min", 0.30)
    max_r = face_ratio_data.get("threshold_max", 0.70)
    
    if detected_faces == 1 and (min_r <= ratio_val <= max_r):
        face_ratio_passed = True
        face_ratio_data["passed"] = True
        face_ratio_data["score_earned"] = SCORING_WEIGHTS["face_height_ratio"]
        current_score += SCORING_WEIGHTS["face_height_ratio"]
        face_ratio_data["friendly_pass"] = f"Khuôn mặt chiếm {ratio_val*100:.1f}% chiều cao ảnh (chuẩn {min_r*100:.0f}% - {max_r*100:.0f}%), tỷ lệ đầu và vai cân đối chuẩn ICAO."
        good_points.append(
            f"Bố cục chân dung chuẩn ICAO: Khuôn mặt chiếm {ratio_val*100:.1f}% chiều cao ảnh (nằm trong dải chuẩn {min_r*100:.0f}% - {max_r*100:.0f}%), tỷ lệ đầu và vai cân đối."
        )
    elif detected_faces == 1 and (0.25 <= ratio_val < min_r or max_r < ratio_val <= 0.76):
        # Thư thả: Lệch nhẹ khỏi dải chuẩn một chút (cho 12/20 điểm)
        partial = 12
        face_ratio_passed = True
        face_ratio_data["passed"] = True
        face_ratio_data["score_earned"] = partial
        current_score += partial
        if ratio_val < min_r:
            face_ratio_data["friendly_pass"] = f"Khuôn mặt chiếm {ratio_val*100:.1f}% khung hình, hơi xa nhẹ nhưng vẫn nhìn rõ chân dung (+12đ)."
            good_points.append(f"Khuôn mặt nhìn rõ nét ({ratio_val*100:.1f}% chiều cao ảnh).")
            reasons.append(f"Khuôn mặt hơi nhỏ nhẹ so với khung chuẩn ({ratio_val*100:.1f}% thay vì tối thiểu {min_r*100:.0f}%).")
        else:
            face_ratio_data["friendly_pass"] = f"Khuôn mặt chiếm {ratio_val*100:.1f}% khung hình, hơi cận mặt nhẹ (+12đ)."
            good_points.append(f"Khuôn mặt cận cảnh rõ ràng ({ratio_val*100:.1f}% chiều cao ảnh).")
            reasons.append(f"Khuôn mặt hơi lớn ({ratio_val*100:.1f}% thay vì tối đa {max_r*100:.0f}%), chừa ít khoảng thở đỉnh đầu.")
    else:
        face_ratio_passed = False
        face_ratio_data["passed"] = False
        face_ratio_data["score_earned"] = 0
        if ratio_val < min_r:
            face_ratio_data["friendly_fail"] = f"Người chụp đứng quá xa máy ảnh, mặt chỉ chiếm {ratio_val*100:.1f}% khung hình (yêu cầu từ {min_r*100:.0f}% - {max_r*100:.0f}%)."
        else:
            face_ratio_data["friendly_fail"] = f"Chụp quá sát camera, mặt chiếm {ratio_val*100:.1f}% khung hình quá lớn làm chật bức ảnh."

        if detected_faces == 1:
            if ratio_val < min_r:
                reasons.append(f"Khuôn mặt quá nhỏ (chỉ chiếm {ratio_val*100:.1f}% chiều cao ảnh) – góc chụp quá rộng lấy nhiều phần thân dưới, không đúng bố cục chân dung ảnh thẻ.")
                recommendations.append("Di chuyển máy ảnh lại gần người chụp (khoảng cách tối ưu 1.2m - 1.5m), căn khung hình lấy từ giữa ngực lên đỉnh đầu.")
            elif ratio_val > max_r:
                reasons.append(f"Khuôn mặt quá lớn / chụp cận mặt quá mức (chiếm {ratio_val*100:.1f}% chiều cao) – đỉnh đầu hoặc cằm chạm sát mép ảnh gây mất cân đối.")
                recommendations.append("Lùi máy ảnh ra xa khoảng 30 - 40cm để lấy đúng bố cục chuẩn ảnh thẻ (khuôn mặt chiếm 40% - 60% khung hình).")

    # Kiểm tra thêm độ lệch tâm ngang nếu chỉ có 1 mặt
    if detected_faces == 1:
        center_off = face_ratio_data.get("center_offset", 0.0)
        center_dir = face_ratio_data.get("center_direction", "")
        if center_off > 0.08:
            dir_text = "bên trái" if center_dir == "left" else ("bên phải" if center_dir == "right" else "một bên")
            reasons.append(f"Khuôn mặt bị lệch sang {dir_text} ({center_off*100:.1f}% so với trục giữa) – đầu người chụp không nằm trên đường trục dọc chính tâm bức ảnh.")
            recommendations.append("Bật đường lưới bố cục (Grid 3x3) trên camera điện thoại, căn sao cho sống mũi người chụp nằm chính xác trên đường kẻ dọc trung tâm.")
        elif center_off <= 0.05 and face_ratio_passed:
            good_points.append(f"Độ đối xứng chính tâm: Khuôn mặt căn ngay chính giữa khung hình (độ lệch chỉ {center_off*100:.1f}%), tư thế ngay ngắn chuẩn ảnh thẻ.")

    # ────────────────────────────────────────────────────────────────────────────
    # 4. TIÊU CHÍ ĐỘ RÕ NÉT (Phương sai Laplacian - Chương 2) - TỐI ĐA 15 ĐIỂM
    # ────────────────────────────────────────────────────────────────────────────
    sharp_data = quality_metrics.get("sharpness", {})
    sharp_passed = sharp_data.get("passed", False)
    lap_var = sharp_data.get("laplacian_variance", 0.0)
    sharp_data["score_max"] = SCORING_WEIGHTS["sharpness"]

    if sharp_passed:
        sharp_data["score_earned"] = SCORING_WEIGHTS["sharpness"]
        sharp_data["friendly_pass"] = f"Ảnh rất sắc nét (Điểm nét {lap_var:.1f} >= 75), mắt và tóc rõ từng sợi."
        good_points.append(
            f"Độ rõ nét chi tiết cao: Phương sai Laplacian đạt {lap_var:.1f} (vượt chuẩn 75.0), các đường nét mắt, mũi, miệng và sợi tóc rất căng nét, không bị nhòe mờ hay out nét."
        )
    elif lap_var >= 50.0:
        partial = 8
        sharp_data["score_earned"] = partial
        sharp_data["friendly_pass"] = f"Ảnh độ nét ở mức tạm chấp nhận (Điểm nét {lap_var:.1f}/75, +8đ)."
        good_points.append(f"Đường nét mắt và khuôn mặt vẫn nhận diện rõ ràng ({lap_var:.1f}/75).")
        reasons.append(f"Ảnh hơi mờ nét nhẹ (Phương sai Laplacian {lap_var:.1f}/75) – đường nét quanh mắt, sống mũi và sợi tóc chưa đạt độ căng nét tối ưu.")
        recommendations.append("Chạm trực tiếp ngón tay vào vùng mắt trên màn hình điện thoại để khóa lấy nét (AF Lock), lau sạch mặt kính camera bằng khăn vải mềm và giữ máy thật chắc khi bấm.")
    else:
        sharp_data["score_earned"] = 0
        sharp_data["friendly_fail"] = f"Ảnh bị mờ nhòe do rung tay hoặc lấy nét sai (Điểm nét {lap_var:.1f} < tối thiểu 75)."
        if lap_var >= 20.0:
            reasons.append(f"Ảnh bị mờ nhòe / out nét (Phương sai Laplacian {lap_var:.1f}/75) – ngũ quan bị mềm nét do rung tay khi chụp hoặc máy ảnh lấy nét sai vào hậu cảnh.")
            recommendations.append("Tựa chắc hai khủy tay vào người hoặc đặt điện thoại lên giá đỡ (tripod), bật chế độ hẹn giờ chụp 2 giây để tránh rung máy khi ngón tay bấm màn hình.")
        else:
            reasons.append(f"Ảnh bị nhòe nét nghiêm trọng (Phương sai Laplacian {lap_var:.1f} quá thấp so với chuẩn 75) – rung lắc chuyển động mạnh làm mất hoàn toàn chi tiết đường viền cạnh.")
            recommendations.append("Yêu cầu người chụp ngồi bất động, chụp ở nơi đủ sáng để camera đạt tốc độ chụp nhanh (tránh nhòe chuyển động) và cầm máy chống rung chắc chắn.")

    # ────────────────────────────────────────────────────────────────────────────
    # 5. TIÊU CHÍ ĐỘ SÁNG & ĐẶC TRƯNG TOÀN CỤC (Chương 2 & Chương 6) - TỐI ĐA 15 ĐIỂM
    # ────────────────────────────────────────────────────────────────────────────
    bright_data = quality_metrics.get("brightness", {})
    bright_passed = bright_data.get("passed", False)
    mean_b = bright_data.get("mean_intensity", 128.0)
    std_b = bright_data.get("contrast_std", 35.0)
    high_clip = bright_data.get("highlight_clipping_ratio", 0.0) * 100.0
    face_photo = bright_data.get("face_photometry", {})
    face_high_clip = face_photo.get("face_highlight_ratio", 0.0) * 100.0
    face_asym = face_photo.get("face_asymmetry", 0.0)
    bhatta = bright_data.get("bhattacharyya_distance", 0.0)
    bright_data["score_max"] = SCORING_WEIGHTS["brightness"]

    if bright_passed:
        bright_data["score_earned"] = SCORING_WEIGHTS["brightness"]
        bright_data["friendly_pass"] = f"Ánh sáng hài hòa, khuôn mặt sáng đều, màu sắc khớp chuẩn (Độ lệch {bhatta:.2f} <= 0.50)."
        good_points.append(
            f"Ánh sáng & Phơi sáng hài hòa: Cường độ sáng trung bình {mean_b:.1f}/255 và độ tương phản {std_b:.1f} đạt chuẩn, biểu đồ sắc độ cân đối, không bị chói lóa hay tối sạm."
        )
    elif (85.0 <= mean_b <= 215.0) and face_high_clip <= 5.0 and face_asym <= 30.0:
        partial = 12
        bright_data["score_earned"] = partial
        bright_data["friendly_pass"] = f"Ánh sáng khuôn mặt khá rõ ràng ({mean_b:.1f}/255), phổ màu hơi lệch nhẹ so với mẫu chuẩn (+12đ)."
        good_points.append(f"Khuôn mặt đủ sáng ({mean_b:.1f}/255), nhìn rõ ngũ quan.")
        reasons.append(f"Phổ màu hoặc độ tương phản lệch nhẹ so với ảnh thẻ mẫu (Bhattacharyya {bhatta:.2f}).")
    else:
        bright_data["score_earned"] = 0
        if mean_b < 90.0:
            bright_data["friendly_fail"] = f"Ảnh bị thiếu sáng / tối sạm (Độ sáng {mean_b:.1f} < 90), khuôn mặt bị tối om."
        elif mean_b > 215.0 or high_clip > 10.0:
            bright_data["friendly_fail"] = f"Ảnh bị cháy sáng hoặc lóa đèn flash (Độ sáng {mean_b:.1f} > 215 làm mất chi tiết da)."
        elif bhatta > 0.50:
            bright_data["friendly_fail"] = f"Phổ màu và ánh sáng lệch so với ảnh thẻ mẫu (Độ sai khác {bhatta:.2f} > 0.50)."
        elif face_asym > 25.0:
            bright_data["friendly_fail"] = f"Ánh sáng chiếu lệch một bên mặt (chênh lệch {face_asym:.1f} mức sáng)."
        else:
            bright_data["friendly_fail"] = "Ánh sáng phân bố chưa đồng đều hoặc bị bóng dầu trên khuôn mặt."

        min_m = bright_data.get("threshold_min_mean", 90.0)
        max_m = bright_data.get("threshold_max_mean", 210.0)
        
        # 1. Chẩn đoán chói sáng / cháy sáng (dùng upper_clip để tránh nhầm áo sơ mi trắng phía dưới)
        bg_type = bg_metrics.get("bg_type", "WHITE_BACKGROUND")
        upper_clip = bright_data.get("upper_highlight_ratio", bright_data.get("highlight_clipping_ratio", 0.0)) * 100.0
        is_bg_white = ("WHITE" in bg_type)
        glare_detected = (upper_clip > 4.5 and not is_bg_white) or (mean_b > max_m)
        if glare_detected:
            if upper_clip > 15.0 or mean_b > 225.0:
                reasons.append(f"Ảnh bị cháy sáng nghiêm trọng (Độ sáng {mean_b:.1f}, {upper_clip:.1f}% diện tích trên bị lóa trắng) – nguồn sáng cực mạnh rọi trực diện làm mất hoàn toàn chi tiết da và hậu cảnh.")
                recommendations.append("Tắt đèn chiếu rọi trực diện hoặc tránh đứng sát bóng đèn/cửa sổ nắng gắt; hạ thanh phơi sáng camera xuống (-0.7 đến -1.0 EV).")
            else:
                reasons.append(f"Vùng trên khung hình bị chói lóa ánh đèn ({upper_clip:.1f}% diện tích bị lóa trắng) – có nguồn sáng mạnh hoặc đèn rọi chiếu thẳng vào khung hình gây lóa mắt.")
                recommendations.append("Di chuyển góc chụp tránh nguồn sáng chói phía sau hoặc bên cạnh; để ánh sáng chiếu dịu đều từ phía trước mặt.")
        
        # 2. Chẩn đoán chói lóa trên khuôn mặt
        if face_high_clip > 4.0:
            reasons.append(f"Khuôn mặt bị lóa sáng bóng dầu ({face_high_clip:.1f}% diện tích mặt bị chói trắng) – mất chi tiết vùng trán, gò má hoặc sống mũi.")
            recommendations.append("Dùng giấy thấm dầu lau nhẹ vùng trán và sống mũi trước khi chụp; giảm thanh phơi sáng nhẹ trên camera.")

        # 3. Chẩn đoán bất đối xứng chiếu sáng 2 bên mặt
        if face_asym > 25.0:
            reasons.append(f"Ánh sáng chiếu lệch một bên mặt (chênh lệch {face_asym:.1f} mức sáng giữa hai nửa mặt) – một bên mặt bị sáng gắt trong khi bên kia bị tối bóng.")
            recommendations.append("Ngồi chính diện với nguồn sáng (như cửa sổ hoặc đèn trần), tránh để nguồn sáng rọi mạnh từ một bên tai.")

        # 4. Chẩn đoán thiếu sáng
        if mean_b < min_m:
            if mean_b >= 75.0:
                reasons.append(f"Ảnh hơi thiếu sáng nhẹ (Độ sáng trung bình {mean_b:.1f} < {min_m:.0f}) – tổng thể khuôn mặt hơi tối sạm, chưa đủ độ tươi sáng rạng rỡ của ảnh thẻ chuẩn.")
                recommendations.append("Bật thêm 1 bóng đèn trong phòng hoặc quay mặt chếch 45 độ về phía cửa sổ có ánh sáng tự nhiên ban ngày.")
            else:
                reasons.append(f"Ảnh thiếu sáng nghiêm trọng / quá tối (Độ sáng trung bình {mean_b:.1f} < {min_m:.0f}) – khuôn mặt bị chìm trong bóng tối, xuất hiện nhiều hạt nhiễu (noise) do camera đẩy ISO cao.")
                recommendations.append("Di chuyển ra vị trí có ánh sáng tốt hơn, để nguồn sáng chiếu thẳng vào mặt (tránh chụp ngược sáng trước cửa sổ hoặc đèn trần phía sau).")
        
        # 5. Chẩn đoán độ tương phản
        if std_b < 25.0:
            reasons.append(f"Ảnh bị bạc màu / độ tương phản yếu (Độ lệch chuẩn {std_b:.1f} < 25.0) – ảnh trông mờ đục như phủ một lớp sương mù, thiếu chiều sâu giữa vùng sáng và tối.")
            recommendations.append("Lau sạch ống kính camera bằng vải mềm (dấu vân tay bám trên kính thường gây hiện tượng lóa mờ sương), tránh để nguồn sáng rọi thẳng vào ống kính.")

    # ────────────────────────────────────────────────────────────────────────────
    # 6. TIÊU CHÍ ĐỘ ĐỒNG NHẤT PHÔNG NỀN (Chương 3 & 4) - TỐI ĐA 10 ĐIỂM
    # ────────────────────────────────────────────────────────────────────────────
    bg_passed = bg_metrics.get("passed", False)
    bg_std = bg_metrics.get("avg_std_dev", 0.0)
    max_bg_std = bg_metrics.get("threshold_max_std", 1.5)
    bg_type = bg_metrics.get("bg_type", "WHITE_BACKGROUND")
    bg_name = "xanh dương" if "BLUE" in bg_type else ("trắng" if "WHITE" in bg_type else "chuẩn")
    bg_metrics["score_max"] = SCORING_WEIGHTS["background_uniformity"]

    is_bokeh = bg_metrics.get("is_bokeh_blur", False)
    is_dark_murky = bg_metrics.get("is_dark_murky", False)
    is_cluttered = bg_metrics.get("is_cluttered", False)
    shadow_det = bg_metrics.get("shadow_detected", False)
    h_diff = bg_metrics.get("horizontal_diff", 0.0)
    v_diff = bg_metrics.get("vertical_diff", 0.0)
    c_lum = bg_metrics.get("avg_corner_luminance", 255.0)

    if bg_passed:
        bg_metrics["score_earned"] = SCORING_WEIGHTS["background_uniformity"]
        bg_metrics["friendly_pass"] = f"Phông nền màu {bg_name} trơn phẳng, sạch bóng, không dính bóng đổ hay hoa văn."
        good_points.append(
            f"Phông nền đồng nhất & sạch bóng: Hậu cảnh màu {bg_name} trơn phẳng (độ lệch chuẩn 4 góc {bg_std:.2f} <= {max_bg_std:.1f}), không bị hắt bóng lưng và không lẫn hoa văn phức tạp."
        )
    elif bg_std <= 5.5 and not is_bokeh and not is_cluttered:
        partial = 8
        bg_metrics["score_earned"] = partial
        bg_metrics["friendly_pass"] = f"Phông nền màu {bg_name} trơn, hơi chênh sáng nhẹ giữa các góc (+8đ)."
        good_points.append(f"Phông nền đúng tông màu {bg_name} cơ bản.")
        reasons.append(f"Phông nền hơi chênh sáng giữa các góc (độ lệch chuẩn {bg_std:.2f} > {max_bg_std:.1f}).")
    else:
        bg_metrics["score_earned"] = 0
        bg_metrics["friendly_fail"] = f"Phông nền bị loang lổ, có bóng đổ quanh vai hoặc dính vật thể phía sau (Độ biến thiên màu {bg_std:.1f} > {max_bg_std:.1f})."
        if is_bokeh:
            reasons.append(f"Phông nền bị xóa phông mờ (chụp chế độ chân dung / bokeh làm mờ cảnh phòng/ngoại cảnh, biến thiên màu {bg_std:.1f} > {max_bg_std:.1f}) – không phải phông trơn phẳng đồng nhất của ảnh thẻ.")
            recommendations.append("Tắt chế độ chụp chân dung (Portrait Mode) xóa phông trên điện thoại, chuyển sang chế độ thường ('Photo') và đứng trước một bức tường phẳng trơn 1 màu (trắng hoặc xanh dương).")
        elif is_dark_murky:
            reasons.append(f"Phông nền bị tối mờ, đục màu hoặc không rõ ràng (độ sáng hậu cảnh chỉ đạt {c_lum:.0f}/255) – làm chìm đường viền tóc và vai người chụp.")
            recommendations.append("Bật thêm đèn chiếu sáng bức tường phía sau hoặc chuyển sang góc có ánh sáng tốt hơn để làm rõ ranh giới giữa người và phông nền.")
        elif shadow_det or (bg_std <= 3.5 and not is_cluttered):
            if h_diff > 18.0:
                reasons.append(f"Phông nền bị bóng đổ lệch một bên (chênh lệch sáng tối hai bên {h_diff:.1f} mức sáng) – do nguồn sáng đánh lệch làm tối một bên hậu cảnh.")
            elif v_diff > 25.0:
                reasons.append(f"Phông nền bị bóng đổ quanh vai và cổ (vùng dưới tối hơn phần trên {v_diff:.1f} mức sáng) – người chụp đứng quá sát tường làm hắt bóng lưng.")
            else:
                reasons.append(f"Phông nền có bóng đổ hoặc ánh sáng không đều (Độ lệch chuẩn 4 góc {bg_std:.2f} > {max_bg_std:.1f}) – có vệt bóng tối mờ hắt quanh vai hoặc đỉnh đầu.")
            recommendations.append("Bước người về phía trước cách tường 0.5m - 0.8m để triệt tiêu bóng đổ, đồng thời bố trí nguồn sáng chính diện đều hai bên mặt.")
        elif is_cluttered:
            reasons.append(f"Phông nền bị lẫn chi tiết thừa hoặc hoa văn (Độ lệch chuẩn 4 góc {bg_std:.2f} > {max_bg_std:.1f}) – hậu cảnh có vật thể, khung tranh hoặc nếp gấp rèm cửa.")
            recommendations.append("Dọn sạch các đồ vật phía sau hoặc chọn một mảng tường phẳng mịn hoàn toàn không có hoa văn hay tranh treo.")
        elif bg_type == "CUSTOM_BACKGROUND":
            reasons.append(f"Phông nền không đúng màu quy chuẩn (ảnh thẻ yêu cầu phông nền màu trắng hoặc xanh dương trơn, hiện tại là màu nền tự do).")
            recommendations.append("Chụp lại trước phông nền màu trắng tinh (tiêu chuẩn quốc tế / hộ chiếu) hoặc màu xanh dương trơn (chuẩn thẻ sinh viên / học sinh).")
        else:
            reasons.append(f"Phông nền không đồng nhất (Độ lệch chuẩn 4 góc {bg_std:.2f} > {max_bg_std:.1f}) – màu sắc hậu cảnh chưa đạt độ đồng đều chuẩn ảnh thẻ.")
            recommendations.append("Chọn bức tường trơn phẳng đồng màu, chiếu sáng đều 4 góc hậu cảnh để tạo nền đồng nhất tuyệt đối.")


    # ────────────────────────────────────────────────────────────────────────────
    # KẾT LUẬN TỔNG THỂ (VERDICT RULE) - ĐỒNG BỘ 100% VỚI TỔNG ĐIỂM 6 TIÊU CHÍ:
    # ────────────────────────────────────────────────────────────────────────────
    checks_dict = {
        "image_size": preproc_metrics,
        "face_count": face_count_data,
        "face_height_ratio": face_ratio_data,
        "sharpness": sharp_data,
        "brightness": bright_data,
        "background_uniformity": bg_metrics
    }

    # Tổng điểm số tuyệt đối bằng tổng điểm của 6 tiêu chuẩn, không cắt xén ngầm
    total_score = sum(int(item.get("score_earned", 0)) for item in checks_dict.values())
    total_score = max(0, min(100, total_score))

    core_passed = face_count_passed and face_ratio_passed and sharp_passed and bright_passed and bg_passed

    if not face_count_passed:
        verdict = "FAIL"
        summary = f"Ảnh thẻ KHÔNG ĐẠT tiêu chuẩn ({total_score}/100) do không phát hiện đúng 1 khuôn mặt trực diện hợp lệ (bắt buộc đúng 1 người)."
    elif not core_passed:
        # Nếu có tiêu chí cốt lõi chưa đạt (mờ, phông bẩn, sai sáng, hoặc mặt quá nhỏ):
        # Ảnh được chấm điểm trung thực theo đúng 6 tiêu chuẩn, và nếu >= 50 điểm sẽ xếp loại TẠM ĐẠT
        fail_list = []
        if not sharp_passed:
            fail_list.append("ảnh bị mờ/nhòe")
        if not bright_passed:
            fail_list.append("ánh sáng/màu sắc chưa chuẩn")
        if not bg_passed:
            fail_list.append("phông nền chưa đồng nhất")
        if not face_ratio_passed:
            fail_list.append("tỉ lệ khuôn mặt chưa vừa vặn")
        fail_desc = ", ".join(fail_list) if fail_list else "một số tiêu chuẩn"

        if total_score >= 50:
            verdict = "WARNING"
            summary = f"Ảnh thẻ TẠM ĐẠT / CẦN CẢI THIỆN ({total_score}/100) – Tổng điểm đạt {total_score}đ (đạt yêu cầu từ 50 trở lên), tuy nhiên còn lỗi {fail_desc}, cần chụp lại để đạt chuẩn in ấn tối ưu."
        else:
            verdict = "FAIL"
            summary = f"Ảnh thẻ KHÔNG ĐẠT tiêu chuẩn ({total_score}/100) do vi phạm tiêu chuẩn kỹ thuật ({fail_desc}) và chưa đạt ngưỡng điểm 50."
    elif total_score >= 50:
        verdict = "PASS"
        if len(reasons) == 0:
            summary = f"Ảnh thẻ ĐẠT TIÊU CHUẨN xuất sắc ({total_score}/100) – Thỏa mãn toàn diện 6 tiêu chuẩn kỹ thuật ảnh thẻ."
        else:
            summary = f"Ảnh thẻ ĐẠT TIÊU CHUẨN ({total_score}/100) – Đạt điểm yêu cầu từ 50 trở lên ({len(good_points)} tiêu chí tốt)."
    elif total_score >= 35:
        verdict = "WARNING"
        summary = f"Ảnh thẻ TẠM ĐẠT CHUẨN ({total_score}/100) – Chưa đạt ngưỡng đạt 50 điểm (được {total_score}/100), cần khắc phục {len(reasons)} điểm hạn chế."
    else:
        verdict = "FAIL"
        summary = f"Ảnh thẻ KHÔNG ĐẠT tiêu chuẩn ({total_score}/100) do chưa đạt ngưỡng điểm tối thiểu 50."

    return {
        "verdict": verdict,
        "overall_score": total_score,
        "summary": summary,
        "good_points": good_points,
        "reasons": reasons,
        "recommendations": recommendations,
        "checks": checks_dict
    }
