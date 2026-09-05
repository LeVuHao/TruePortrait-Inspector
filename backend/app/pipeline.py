"""
Central Image Processing Pipeline & Visualizer Generator
Phụ trách bởi: HẢO & CẢ NHÓM
Nhiệm vụ:
- Tiếp nhận file ảnh đầu vào, gọi lần lượt 4 module xử lý ảnh.
- Sinh các ảnh trực quan hóa trung gian dạng base64:
  1. original: Ảnh gốc
  2. grayscale: Ảnh xám
  3. laplacian_map: Ma trận cạnh viền Laplacian
  4. face_bbox: Ảnh gốc có vẽ Bounding Box khuôn mặt
  5. background_rois: Ảnh gốc có vẽ 4 góc ROI phân tích nền
"""

import cv2
import base64
import numpy as np
from typing import Dict, Any

from .core.config import PRESET_CONFIGS, DEFAULT_PRESET
from .core.preprocessor import preprocess_image
from .core.face_analyzer import analyze_face
from .core.quality_analyzer import analyze_quality
from .core.background_analyzer import analyze_background
from .core.evaluator import evaluate_photo


def encode_image_to_base64(image_np: np.ndarray, is_gray: bool = False) -> str:
    """Mã hóa ma trận ảnh OpenCV thành chuỗi Base64 Data URL để Frontend React render trực tiếp."""
    if is_gray and len(image_np.shape) == 2:
        img_to_encode = image_np
    else:
        img_to_encode = image_np
    success, buffer = cv2.imencode(".jpg", img_to_encode, [cv2.IMWRITE_JPEG_QUALITY, 85])
    if not success:
        return ""
    b64_str = base64.b64encode(buffer).decode("utf-8")
    return f"data:image/jpeg;base64,{b64_str}"


def run_pipeline(file_bytes: bytes, preset_name: str = DEFAULT_PRESET) -> Dict[str, Any]:
    """
    Chạy toàn bộ quy trình xử lý ảnh từ đầu đến cuối.
    
    Args:
        file_bytes: Dữ liệu nhị phân file ảnh upload
        preset_name: Tên preset chuẩn ảnh
        
    Returns:
        dict kết quả chuẩn API theo đúng đặc tả tài liệu kiến trúc
    """
    preset_config = PRESET_CONFIGS.get(preset_name, PRESET_CONFIGS[DEFAULT_PRESET])
    
    # 1. Module 1: Tiền xử lý & Kích thước (Hảo)
    image_bgr, image_gray, preproc_metrics = preprocess_image(file_bytes, preset_config)
    
    # 2. Module 2: Khuôn mặt & Hình học (Quân)
    face_metrics = analyze_face(image_bgr, image_gray, preset_config)
    
    # 3. Module 3: Chất lượng ảnh & Độ mờ (Chương)
    quality_metrics, laplacian_map = analyze_quality(image_bgr, image_gray, preset_config)
    
    # 4. Module 4: Độ đồng nhất nền (Huy)
    bg_metrics, bg_visual_img = analyze_background(image_bgr, image_gray, preset_config)
    
    # 5. Module 5: Động cơ đánh giá tổng hợp & Tính điểm (Hảo)
    eval_result = evaluate_photo(preproc_metrics, face_metrics, quality_metrics, bg_metrics)
    
    # 6. Tạo các ảnh trực quan hóa trung gian phục vụ Visual Step-by-Step Canvas trên React
    # Ảnh vẽ Bounding Box
    bbox_visual_img = image_bgr.copy()
    for bbox in face_metrics.get("bounding_boxes", []):
        bx, by, bw, bh = bbox["x"], bbox["y"], bbox["width"], bbox["height"]
        cv2.rectangle(bbox_visual_img, (bx, by), (bx + bw, by + bh), (0, 255, 0), 2)
        cv2.putText(bbox_visual_img, f"Face: {bw}x{bh}", (bx, max(20, by - 8)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                    
    visual_assets = {
        "original": encode_image_to_base64(image_bgr),
        "grayscale": encode_image_to_base64(image_gray, is_gray=True),
        "laplacian_map": encode_image_to_base64(laplacian_map, is_gray=True),
        "face_bbox": encode_image_to_base64(bbox_visual_img),
        "background_rois": encode_image_to_base64(bg_visual_img),
        "histogram_data": quality_metrics["brightness"]["histogram_data"]
    }
    
    return {
        "status": "success",
        "preset": preset_name,
        "verdict": eval_result["verdict"],
        "overall_score": eval_result["overall_score"],
        "summary": eval_result["summary"],
        "reasons": eval_result["reasons"],
        "recommendations": eval_result["recommendations"],
        "bounding_boxes": face_metrics.get("bounding_boxes", []),
        "checks": eval_result["checks"],
        "visual_assets": visual_assets
    }
