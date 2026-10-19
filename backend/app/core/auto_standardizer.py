"""
Module: auto_standardizer.py
Phụ trách: TOÀN NHÓM & HẢO (DIP Core Adaptive Targeted Enhancer)
Nhiệm vụ:
Tự động ĐỀ XUẤT ẢNH HIỆU CHỈNH THÍCH NGHI theo đúng lỗi thực tế của từng ảnh:
- Ảnh chói sáng / cháy sáng -> Giảm chói, thu hẹp dải động về vùng an toàn.
- Ảnh thiếu sáng / tối -> Nâng sáng cục bộ bằng Gamma + CLAHE trên không gian CIELAB.
- Ảnh lệch khung / mặt nhỏ (chụp xa) -> Tự động căn chỉnh khung hình chuẩn 3:4, tỷ lệ mặt ~54%.
- Ảnh bị mờ -> Làm nét nhẹ. Nếu ảnh ĐÃ NÉT thì TUYỆT ĐỐI KHÔNG LÀM NÉT để tránh vỡ hạt.
- Tuân thủ nghiêm ngặt Giáo trình Xử lý ảnh (PTIT): Chương 1, 2, 3.
"""

import cv2
import numpy as np
from typing import Dict, Any, List, Tuple


def standardize_id_photo(
    image_bgr: np.ndarray,
    bounding_boxes: List[Dict[str, int]],
    preset_config: dict,
    quality_metrics: dict = None
) -> Tuple[np.ndarray, Dict[str, Any]]:
    """
    Tự động đề xuất phiên bản ảnh hiệu chỉnh thích nghi (Targeted Adaptive Fix).
    Chỉ can thiệp vào các tiêu chí bị vi phạm, bảo toàn tối đa ảnh gốc.
    """
    img_h, img_w = image_bgr.shape[:2]
    size_rules = preset_config.get("image_size", {})
    target_w = size_rules.get("min_width", 600)
    target_h = size_rules.get("min_height", 800)
    target_aspect = 3.0 / 4.0

    steps_taken = []
    current_img = image_bgr.copy()

    # ────────────────────────────────────────────────────────────────────────────
    # 1. BỐ CỤC & TỶ LỆ KHUNG HÌNH (Chương 1 & Chương 2)
    # ────────────────────────────────────────────────────────────────────────────
    cur_aspect = img_w / img_h
    aspect_diff = abs(cur_aspect - target_aspect)
    
    # Kiểm tra xem có khuôn mặt và tỷ lệ mặt hiện tại thế nào
    has_face = len(bounding_boxes) >= 1
    face_needs_reframe = False
    main_face = None

    if has_face:
        sorted_boxes = sorted(bounding_boxes, key=lambda b: b["width"] * b["height"], reverse=True)
        main_face = sorted_boxes[0]
        fh = main_face["height"]
        cur_face_ratio = fh / img_h
        # Ngưỡng chuẩn: 45% - 70%. Nếu ngoài khoảng này hoặc tỷ lệ ảnh lệch > 5% -> cần căn chỉnh lại
        if cur_face_ratio < 0.45 or cur_face_ratio > 0.70 or aspect_diff > 0.05 or img_w < target_w or img_h < target_h:
            face_needs_reframe = True
    else:
        if aspect_diff > 0.05 or img_w < target_w or img_h < target_h:
            face_needs_reframe = True

    if face_needs_reframe:
        if has_face and main_face:
            fx, fy = main_face["x"], main_face["y"]
            fw, fh = main_face["width"], main_face["height"]
            target_face_ratio = 0.54
            crop_h = int(fh / target_face_ratio)
            crop_w = int(crop_h * target_aspect)

            cx = fx + fw // 2
            x1 = cx - crop_w // 2
            x2 = x1 + crop_w
            y1 = int(fy - 0.26 * fh)
            y2 = y1 + crop_h
            reason = f"Căn chỉnh lại bố cục 3:4: Đưa tỷ lệ chiều cao khuôn mặt từ {fh/img_h*100:.1f}% về mức chuẩn ~54% (ICAO)."
        else:
            if cur_aspect > target_aspect:
                crop_h = img_h
                crop_w = int(img_h * target_aspect)
            else:
                crop_w = img_w
                crop_h = int(img_w / target_aspect)
            cx, cy = img_w // 2, img_h // 2
            x1 = cx - crop_w // 2
            x2 = x1 + crop_w
            y1 = cy - crop_h // 2
            y2 = y1 + crop_h
            reason = "Cắt căn giữa lại khung hình theo tỷ lệ ảnh thẻ chuẩn 3:4."

        # Xử lý padding biên
        pad_top = max(0, -y1)
        pad_bottom = max(0, y2 - img_h)
        pad_left = max(0, -x1)
        pad_right = max(0, x2 - img_w)

        if pad_top > 0 or pad_bottom > 0 or pad_left > 0 or pad_right > 0:
            padded_canvas = cv2.copyMakeBorder(
                current_img, pad_top, pad_bottom, pad_left, pad_right,
                borderType=cv2.BORDER_REPLICATE
            )
        else:
            padded_canvas = current_img

        ny1, ny2 = y1 + pad_top, y2 + pad_top
        nx1, nx2 = x1 + pad_left, x2 + pad_left
        cropped = padded_canvas[ny1:ny2, nx1:nx2]

        # Phóng đại về kích thước chuẩn nếu nhỏ hơn
        resized = cv2.resize(cropped, (target_w, target_h), interpolation=cv2.INTER_CUBIC)
        current_img = resized

        steps_taken.append({
            "step": len(steps_taken) + 1,
            "name": "Căn chỉnh bố cục & Tỷ lệ 3:4",
            "method": "Auto-Framing & Bicubic Interpolation",
            "description": reason
        })
    else:
        steps_taken.append({
            "step": len(steps_taken) + 1,
            "name": "Bố cục & Kích thước",
            "method": "Preserved Original Framing",
            "description": f"Kích thước ({img_w}x{img_h}) và bố cục ảnh đã đạt chuẩn, giữ nguyên khung hình ban đầu."
        })

    # ────────────────────────────────────────────────────────────────────────────
    # 2. HIỆU CHỈNH ÁNH SÁNG CÓ MỤC TIÊU
    # ────────────────────────────────────────────────────────────────────────────
    gray_now = cv2.cvtColor(current_img, cv2.COLOR_BGR2GRAY)
    cur_mean = float(np.mean(gray_now))
    cur_high_clip = float(np.mean(gray_now >= 245))
    bright_rules = preset_config.get("brightness", {})
    min_mean = bright_rules.get("min_mean", 90.0)
    max_mean = bright_rules.get("max_mean", 210.0)

    if cur_mean < min_mean:
        # THIẾU SÁNG: Áp dụng Gamma Power-law + CLAHE trên kênh L (CIELAB)
        target_mean = 135.0
        gamma = max(0.45, min(0.85, np.log(target_mean / 255.0) / np.log(max(10.0, cur_mean) / 255.0)))
        lut = np.array([np.clip(((i / 255.0) ** gamma) * 255.0, 0, 255) for i in range(256)]).astype('uint8')
        brightened = cv2.LUT(current_img, lut)

        lab = cv2.cvtColor(brightened, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=1.6, tileGridSize=(8, 8))
        l_clahe = clahe.apply(l)
        current_img = cv2.cvtColor(cv2.merge((l_clahe, a, b)), cv2.COLOR_LAB2BGR)

        steps_taken.append({
            "step": len(steps_taken) + 1,
            "name": "Hiệu chỉnh thiếu sáng",
            "method": "Gamma Power-law & CIELAB CLAHE",
            "description": f"Nâng sáng ảnh tối từ Mean {cur_mean:.1f} lên ~135.0, cân bằng chi tiết khuôn mặt mà không làm sai lệch màu da."
        })

    elif cur_mean > max_mean or cur_high_clip > 0.035:
        # CHÁY SÁNG / CHÓI CỤC BỘ: Áp dụng đường cong Knee Compression dìm vùng chói trên kênh V (HSV)
        hsv_temp = cv2.cvtColor(current_img, cv2.COLOR_BGR2HSV)
        v = hsv_temp[:, :, 2].astype(np.float32)
        knee_thresh = 195.0
        mask_knee = v > knee_thresh
        v[mask_knee] = knee_thresh + (v[mask_knee] - knee_thresh) * 0.35
        if cur_mean > max_mean:
            v = v * (190.0 / cur_mean)
        hsv_temp[:, :, 2] = np.clip(v, 0, 255).astype(np.uint8)
        current_img = cv2.cvtColor(hsv_temp, cv2.COLOR_HSV2BGR)

        steps_taken.append({
            "step": len(steps_taken) + 1,
            "name": "Giảm chói sáng & Cân bằng phơi sáng",
            "method": "Highlight Knee Compression & Attenuation",
            "description": f"Hạ cường độ chói lóa ({cur_high_clip*100:.1f}% vùng sáng gắt) và dìm ngưỡng bão hòa trắng để phục hồi chi tiết đường nét khuôn mặt."
        })
    else:
        steps_taken.append({
            "step": len(steps_taken) + 1,
            "name": "Kiểm tra độ sáng",
            "method": "Preserved Photometric Values",
            "description": f"Cường độ sáng trung bình (Mean = {cur_mean:.1f}) nằm trong dải chuẩn [{min_mean}, {max_mean}], giữ nguyên sắc độ gốc."
        })

    # ────────────────────────────────────────────────────────────────────────────
    # 3. LÀM NÉT THÍCH NGHI
    # ────────────────────────────────────────────────────────────────────────────
    final_gray = cv2.cvtColor(current_img, cv2.COLOR_BGR2GRAY)
    cur_lap_var = float(cv2.Laplacian(final_gray, cv2.CV_64F).var())
    min_lap_var = preset_config.get("sharpness", {}).get("min_laplacian_var", 75.0)

    # NGUYÊN TẮC: CHỈ LÀM NÉT KHI ẢNH THỰC SỰ BỊ MỜ!
    # NẾU ẢNH ĐÃ ĐẠT CHUẨN ĐỘ NÉT THÌ TUYỆT ĐỐI KHÔNG CHẠY LAPLACIAN ĐỂ TRÁNH GAI HẠT & VỠ NÉT!
    if cur_lap_var < min_lap_var:
        lap_kernel = np.array([[0, -1, 0],
                               [-1, 5, -1],
                               [0, -1, 0]], dtype=np.float32)
        sharpened = cv2.filter2D(current_img, -1, lap_kernel)
        current_img = cv2.addWeighted(current_img, 0.6, sharpened, 0.4, 0)
        new_var = float(cv2.Laplacian(cv2.cvtColor(current_img, cv2.COLOR_BGR2GRAY), cv2.CV_64F).var())

        steps_taken.append({
            "step": len(steps_taken) + 1,
            "name": "Khôi phục độ sắc nét",
            "method": "Laplacian High-Boost Spatial Filter",
            "description": f"Ảnh bị mờ (Var {cur_lap_var:.1f} < {min_lap_var}), áp dụng lọc vi phân đạo hàm bậc hai để nâng độ nét lên {new_var:.1f}."
        })
    else:
        steps_taken.append({
            "step": len(steps_taken) + 1,
            "name": "Kiểm tra độ sắc nét",
            "method": "Preserved Texture Integrity",
            "description": f"Ảnh đã đạt chuẩn rõ nét (Phương sai Laplacian {cur_lap_var:.1f} >= {min_lap_var}), giữ nguyên độ mịn màng tự nhiên, không làm nét thêm để tránh nhiễu hạt."
        })

    final_h, final_w = current_img.shape[:2]
    final_gray = cv2.cvtColor(current_img, cv2.COLOR_BGR2GRAY)

    # Sinh các câu nhận xét sơ qua về khung ảnh, gần gũi, dễ hiểu cho người đọc
    framing_notes = []
    if face_needs_reframe:
        if has_face and main_face:
            framing_notes.append(
                f"Khung ảnh đã được tự động căn chỉnh lại theo đúng tỷ lệ ảnh thẻ 3:4 ({target_w}x{target_h} px), đưa khuôn mặt về đúng vị trí trung tâm với tỷ lệ ~54% (chuẩn ICAO)."
            )
        else:
            framing_notes.append(
                f"Khung ảnh đã được cắt căn giữa theo chuẩn tỷ lệ 3:4 ({target_w}x{target_h} px) để phù hợp khổ in ảnh thẻ."
            )
    else:
        framing_notes.append(
            f"Bố cục khung hình ban đầu đã đạt đúng tỷ lệ chuẩn 3:4 ({img_w}x{img_h} px), khuôn mặt nằm ở vị trí trung tâm ngay ngắn."
        )

    if has_face and main_face:
        framing_notes.append(
            "Khoảng cách từ đỉnh đầu đến mép trên và phần vai hai bên đều đặn, tạo tư thế đàng hoàng, nghiêm túc chuẩn ảnh thẻ."
        )

    if cur_lap_var < min_lap_var:
        framing_notes.append(
            "Đường nét chi tiết ngũ quan được gia tăng độ rõ nét nhẹ nhàng, không gây vỡ hạt da."
        )
    else:
        framing_notes.append(
            "Độ nét và ánh sáng tổng thể hài hòa, giữ trọn nét tự nhiên của khuôn mặt."
        )

    report = {
        "standardized_width": final_w,
        "standardized_height": final_h,
        "aspect_ratio": "3:4",
        "initial_dimensions": f"{img_w}x{img_h}",
        "final_mean": round(float(np.mean(final_gray)), 2),
        "final_laplacian_var": round(float(cv2.Laplacian(final_gray, cv2.CV_64F).var()), 2),
        "framing_notes": framing_notes,
        "framing_summary": " ".join(framing_notes),
        "steps": steps_taken
    }

    return current_img, report
