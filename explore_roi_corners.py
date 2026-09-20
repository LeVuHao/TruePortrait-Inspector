"""
explore_roi_corners.py
======================
GIAI ĐOẠN 1 - Ngày 4 đến 7: Script thử nghiệm thăm dò ban đầu
Phụ trách: HUY

Mục đích (theo timeline):
    - Viết script cắt 4 góc ảnh (Corner ROIs)
    - Tính độ lệch chuẩn màu (Std Dev) trên 15 ảnh nền mẫu từ dataset
    - Quan sát phân bố Std Dev để xác định khoảng ngưỡng thô ban đầu
      cho cấu hình Background Uniformity trong config.py

Cách chạy:
    python explore_roi_corners.py

Đầu ra:
    - In bảng Std Dev cho từng ảnh PASS và từng ảnh FAIL lên màn hình
    - Gợi ý ngưỡng max_color_std ban đầu
    - Lưu ảnh visualization có vẽ 4 góc ROI vào thư mục explore_output/
"""

import os
import sys
import cv2
import numpy as np

# Thêm backend vào path
BACKEND_DIR = os.path.join(os.path.dirname(__file__), "backend")
sys.path.insert(0, BACKEND_DIR)

from app.core.config import PRESET_CONFIGS, DEFAULT_PRESET
from app.core.background_analyzer import analyze_background

DATASET_DIR  = os.path.join(os.path.dirname(__file__), "dataset")
OUTPUT_DIR   = os.path.join(os.path.dirname(__file__), "explore_output")
NUM_SAMPLES  = 15   # Theo timeline: thử nghiệm trên 15 ảnh mẫu


def imread_unicode(path: str):
    buf = np.fromfile(path, dtype=np.uint8)
    return cv2.imdecode(buf, cv2.IMREAD_COLOR)


def imwrite_unicode(path: str, img: np.ndarray):
    ok, buf = cv2.imencode(".jpg", img)
    if ok:
        buf.tofile(path)


def explore_folder(folder_name: str, label: str, preset_config: dict):
    """Phân tích 15 ảnh đầu tiên trong một thư mục và in bảng kết quả."""
    folder = os.path.join(DATASET_DIR, folder_name)
    files  = sorted(os.listdir(folder))[:NUM_SAMPLES]

    stds = []
    print(f"\n{'─'*60}")
    print(f"  [{label}] Thư mục: {folder_name}/ ({len(files)} ảnh mẫu)")
    print(f"{'─'*60}")
    print(f"  {'Ảnh':<20} {'GrayStd':>9} {'ColorStd':>9} {'Combined':>9}")
    print(f"  {'─'*50}")

    out_folder = os.path.join(OUTPUT_DIR, folder_name)
    os.makedirs(out_folder, exist_ok=True)

    for fname in files:
        fpath = os.path.join(folder, fname)
        img   = imread_unicode(fpath)
        if img is None:
            continue

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        metrics, vis_img = analyze_background(img, gray, preset_config)

        combined  = metrics["avg_std_dev"]
        gray_std  = metrics["avg_gray_std"]
        color_std = metrics["avg_color_std"]
        stds.append(combined)

        print(f"  {fname:<20} {gray_std:>9.2f} {color_std:>9.2f} {combined:>9.2f}")

        # Lưu ảnh visualization
        out_path = os.path.join(out_folder, fname)
        imwrite_unicode(out_path, vis_img)

    if stds:
        print(f"  {'─'*50}")
        print(f"  {'Min':>29} {min(stds):>9.2f}")
        print(f"  {'Max':>29} {max(stds):>9.2f}")
        print(f"  {'Mean':>29} {np.mean(stds):>9.2f}")
        print(f"  {'Median':>29} {np.median(stds):>9.2f}")

    return stds


def suggest_threshold(pass_stds, fail_stds):
    """Gợi ý ngưỡng max_color_std dựa trên phân bố thực nghiệm."""
    if not pass_stds or not fail_stds:
        return

    print(f"\n{'='*60}")
    print("  GỢI Ý NGƯỠNG BAN ĐẦU (Data-driven Threshold)")
    print(f"{'='*60}")
    print(f"  Std tổng hợp nhóm PASS: min={min(pass_stds):.2f}  max={max(pass_stds):.2f}  mean={np.mean(pass_stds):.2f}")
    print(f"  Std tổng hợp nhóm FAIL: min={min(fail_stds):.2f}  max={max(fail_stds):.2f}  mean={np.mean(fail_stds):.2f}")

    # Ngưỡng gợi ý: percentile 95 của nhóm PASS (ảnh chuẩn)
    suggested = float(np.percentile(pass_stds, 95))
    print(f"\n  --> Gợi ý max_color_std = {suggested:.1f}")
    print(f"      (Percentile 95 của nhóm PASS = {suggested:.2f})")
    print(f"      Cập nhật giá trị này vào backend/app/core/config.py")
    print(f"      Sau đó chạy benchmark_eval.py để đo lại F1-Score.")
    print(f"{'='*60}")


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    preset = PRESET_CONFIGS[DEFAULT_PRESET]

    print("=" * 60)
    print("  THĂM DÒ ROI CORNERS -- Giai đoạn 1, Ngày 4-7")
    print("  Phụ trách: HUY")
    print("=" * 60)
    print(f"  Dataset: {DATASET_DIR}")
    print(f"  Mẫu phân tích mỗi nhóm: {NUM_SAMPLES} ảnh")
    print(f"  Ngưỡng hiện tại trong config: max_color_std = "
          f"{preset['background_uniformity']['max_color_std']}")

    pass_stds = explore_folder("pass",          "PASS - Ảnh thẻ chuẩn", preset)
    blur_stds = explore_folder("fail_blur",      "FAIL - Ảnh mờ",        preset)
    dark_stds = explore_folder("fail_dark",      "FAIL - Ảnh tối",       preset)
    exp_stds  = explore_folder("fail_overexposed","FAIL - Ảnh chói",     preset)

    all_fail_stds = blur_stds + dark_stds + exp_stds
    suggest_threshold(pass_stds, all_fail_stds)

    print(f"\n  Ảnh visualization đã lưu tại: {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
