"""
Module 2: Face Detection & Face Geometry Analysis
Phụ trách bởi: QUÂN
Nhiệm vụ:
- Phát hiện khuôn mặt bằng Haar Cascade (hoặc OpenCV DNN).
- Đếm số lượng khuôn mặt (yêu cầu duy nhất 1 mặt).
- Trích xuất Bounding Box (x, y, w, h).
- Tính toán Face Height Ratio: H_face / H_image.
- Kiểm tra độ cân đối vị trí khuôn mặt trên khung hình.
"""

import cv2
import numpy as np
import os
from typing import Dict, Any, List


# Khởi tạo mô hình Haar Cascade từ OpenCV chuẩn
HAAR_CASCADE_PATH = os.path.join(cv2.data.haarcascades, "haarcascade_frontalface_default.xml")
face_cascade = cv2.CascadeClassifier(HAAR_CASCADE_PATH)


def analyze_face(image_bgr: np.ndarray, image_gray: np.ndarray, preset_config: dict) -> Dict[str, Any]:
    """
    Phát hiện khuôn mặt và phân tích hình học khuôn mặt.
    
    Args:
        image_bgr: Ảnh gốc BGR
        image_gray: Ảnh xám Grayscale
        preset_config: Cấu hình dải ngưỡng
        
    Returns:
        dict kết quả nhận diện khuôn mặt
    """
    img_h, img_w = image_gray.shape[:2]
    
    # 1. Phát hiện khuôn mặt bằng Haar Cascade
    # scaleFactor=1.1, minNeighbors=5, minSize=(int(img_w * 0.15), int(img_h * 0.15))
    faces = face_cascade.detectMultiScale(
        image_gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(int(img_w * 0.15), int(img_h * 0.15))
    )
    
    face_count = len(faces)
    
    face_count_rule = preset_config.get("face_count", {})
    required_count = face_count_rule.get("required_count", 1)
    face_count_passed = (face_count == required_count)
    
    bounding_boxes: List[Dict[str, int]] = []
    face_height_ratio = 0.0
    face_size_passed = False
    face_center_offset = 0.0
    size_message = ""
    
    ratio_rules = preset_config.get("face_height_ratio", {})
    min_ratio = ratio_rules.get("min_ratio", 0.45)
    max_ratio = ratio_rules.get("max_ratio", 0.70)
    
    for (x, y, w, h) in faces:
        bounding_boxes.append({
            "x": int(x),
            "y": int(y),
            "width": int(w),
            "height": int(h)
        })
        
    if face_count == 1:
        x, y, w, h = faces[0]
        # Tính tỷ lệ chiều cao khuôn mặt so với chiều cao ảnh
        face_height_ratio = float(h) / float(img_h)
        face_size_passed = (min_ratio <= face_height_ratio <= max_ratio)
        
        # Độ lệch tâm ngang của khuôn mặt (khoảng cách tâm mặt đến trục giữa ảnh)
        face_center_x = x + w / 2.0
        img_center_x = img_w / 2.0
        face_center_offset = abs(face_center_x - img_center_x) / float(img_w)
        
        if face_height_ratio < min_ratio:
            size_message = f"Khuôn mặt chiếm {face_height_ratio*100:.1f}% chiều cao ảnh (nhỏ hơn ngưỡng thực nghiệm {min_ratio*100:.0f}%)."
        elif face_height_ratio > max_ratio:
            size_message = f"Khuôn mặt chiếm {face_height_ratio*100:.1f}% chiều cao ảnh (quá gần, vượt ngưỡng {max_ratio*100:.0f}%)."
        else:
            size_message = f"Tỷ lệ chiều cao khuôn mặt đạt chuẩn ({face_height_ratio*100:.1f}%)."
    elif face_count == 0:
        size_message = "Không phát hiện khuôn mặt nào trong khung hình."
    else:
        size_message = f"Phát hiện {face_count} khuôn mặt (Yêu cầu duy nhất 1 khuôn mặt)."
        
    return {
        "face_count": {
            "passed": face_count_passed,
            "detected_count": int(face_count),
            "required_count": int(required_count),
            "message": "Ảnh có đúng 1 khuôn mặt." if face_count_passed else f"Phát hiện {face_count} khuôn mặt (chuẩn = {required_count})."
        },
        "face_height_ratio": {
            "passed": face_size_passed if face_count == 1 else False,
            "ratio": round(face_height_ratio, 3),
            "threshold_min": min_ratio,
            "threshold_max": max_ratio,
            "center_offset": round(face_center_offset, 3),
            "message": size_message
        },
        "bounding_boxes": bounding_boxes
    }
