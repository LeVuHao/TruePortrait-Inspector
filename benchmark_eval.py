"""
benchmark_eval.py
=================
Script đánh giá thực nghiệm toàn diện hệ thống PhotoCheck trên bộ Dataset có Ground Truth.
Phụ trách bởi: HUY

Mục đích:
    - Chạy tự động toàn bộ pipeline phân tích ảnh (background_analyzer + các module khác)
      lên từng ảnh trong thư mục dataset/.
    - So sánh kết quả PASS/FAIL của hệ thống với nhãn Ground Truth (dataset_annotations.json).
    - Tính toán và xuất báo cáo khoa học đầy đủ:
        * Confusion Matrix
        * Accuracy, Precision, Recall, F1-Score (toàn bộ và từng loại lỗi)
    - Xuất file CSV chi tiết và bảng tổng hợp để đưa vào báo cáo môn học.

Cách chạy:
    cd TruePortrait-Inspector
    python benchmark_eval.py

Đầu ra:
    benchmark_results/
        benchmark_report.txt   -- Báo cáo văn bản đầy đủ
        benchmark_details.csv  -- Chi tiết từng ảnh (Ground Truth vs Prediction)
        confusion_matrix.png   -- Hình ảnh Confusion Matrix
"""

import os
import sys
import json
import csv
import numpy as np
from datetime import datetime

# Thêm backend vào path để import các module
BACKEND_DIR = os.path.join(os.path.dirname(__file__), "backend")
sys.path.insert(0, BACKEND_DIR)

# Import pipeline chính
try:
    from app.core.config import PRESET_CONFIGS, DEFAULT_PRESET
    from app.core.preprocessor import preprocess_image
    from app.core.face_analyzer import analyze_face
    from app.core.quality_analyzer import analyze_quality
    from app.core.background_analyzer import analyze_background
    from app.core.evaluator import evaluate_photo
    PIPELINE_AVAILABLE = True
except ImportError as e:
    print(f"[!] Khong the import pipeline: {e}")
    print("    Dang chay o che do Background-Only (chi danh gia Module 4 cua Huy).")
    PIPELINE_AVAILABLE = False

# Import OpenCV cho background-only mode
import cv2


# ────────────────────────────────────────────────────────────────────────────
# CẤU HÌNH
# ────────────────────────────────────────────────────────────────────────────
DATASET_DIR   = os.path.join(os.path.dirname(__file__), "dataset")
ANNOTATIONS   = os.path.join(DATASET_DIR, "dataset_annotations.json")
OUTPUT_DIR    = os.path.join(os.path.dirname(__file__), "benchmark_results")


# ────────────────────────────────────────────────────────────────────────────
# HÀM ĐỌC ẢNH HỖ TRỢ UNICODE PATH (Windows)
# ────────────────────────────────────────────────────────────────────────────
def imread_unicode(path: str):
    """Đọc ảnh từ đường dẫn có ký tự Unicode trên Windows."""
    try:
        buf = np.fromfile(path, dtype=np.uint8)
        return cv2.imdecode(buf, cv2.IMREAD_COLOR)
    except Exception:
        return None


# ────────────────────────────────────────────────────────────────────────────
# PHÂN TÍCH NỀN ĐỘC LẬP (dùng khi pipeline đầy đủ chưa sẵn sàng)
# ────────────────────────────────────────────────────────────────────────────
def analyze_background_only(img_bgr: np.ndarray) -> str:
    """
    Chạy riêng Module 4 (Background Analyzer) và trả về nhãn PASS/FAIL.
    Dùng khi các module khác chưa được tích hợp.
    """
    from app.core.background_analyzer import analyze_background
    from app.core.config import PRESET_CONFIGS, DEFAULT_PRESET

    img_gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    preset   = PRESET_CONFIGS[DEFAULT_PRESET]
    metrics, _ = analyze_background(img_bgr, img_gray, preset)
    return "PASS" if metrics["passed"] else "FAIL"


# ────────────────────────────────────────────────────────────────────────────
# CHẠY FULL PIPELINE
# ────────────────────────────────────────────────────────────────────────────
def run_full_pipeline(img_path: str) -> str:
    """Chạy toàn bộ pipeline và trả về nhãn PASS/FAIL cuối cùng."""
    with open(img_path, "rb") as f:
        file_bytes = f.read()
    preset_config = PRESET_CONFIGS[DEFAULT_PRESET]

    image_bgr, image_gray, preproc_metrics = preprocess_image(file_bytes, preset_config)
    face_metrics                           = analyze_face(image_bgr, image_gray, preset_config)
    quality_metrics, _                     = analyze_quality(image_bgr, image_gray, preset_config)
    bg_metrics, _                          = analyze_background(image_bgr, image_gray, preset_config)
    eval_result                            = evaluate_photo(preproc_metrics, face_metrics, quality_metrics, bg_metrics)

    return eval_result["verdict"]


# ────────────────────────────────────────────────────────────────────────────
# TÍNH CÁC CHỈ SỐ ĐÁNH GIÁ
# ────────────────────────────────────────────────────────────────────────────
def compute_metrics(tp: int, tn: int, fp: int, fn: int) -> dict:
    """Tính Accuracy, Precision, Recall, F1 từ Confusion Matrix."""
    total     = tp + tn + fp + fn
    accuracy  = (tp + tn) / total if total > 0 else 0.0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall    = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1        = (2 * precision * recall / (precision + recall)
                 if (precision + recall) > 0 else 0.0)
    return {
        "TP": tp, "TN": tn, "FP": fp, "FN": fn,
        "Accuracy":  round(accuracy  * 100, 2),
        "Precision": round(precision * 100, 2),
        "Recall":    round(recall    * 100, 2),
        "F1_Score":  round(f1        * 100, 2),
    }


# ────────────────────────────────────────────────────────────────────────────
# MAIN
# ────────────────────────────────────────────────────────────────────────────
def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # ── 1. Đọc Ground Truth ──────────────────────────────────────────────────
    if not os.path.isfile(ANNOTATIONS):
        print(f"[ERROR] Khong tim thay file Ground Truth: {ANNOTATIONS}")
        print("        Hay chay build_dataset.py truoc.")
        sys.exit(1)

    with open(ANNOTATIONS, "r", encoding="utf-8") as f:
        annotations = json.load(f)

    print("=" * 65)
    print("  BENCHMARK EVALUATION -- PhotoCheck ID Photo Quality Checker")
    print(f"  Thoi gian: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 65)
    print(f"[*] Dataset:    {DATASET_DIR}")
    print(f"[*] Tong mau:   {len(annotations)} anh")
    print(f"[*] Pipeline:   {'DAY DU (tat ca module)' if PIPELINE_AVAILABLE else 'BACKGROUND-ONLY (chi Module 4)'}")
    print()

    # ── 2. Chạy đánh giá từng ảnh ────────────────────────────────────────────
    details = []           # Chi tiết từng ảnh
    tp = tn = fp = fn = 0  # Confusion Matrix toàn bộ

    # Thống kê theo từng loại lỗi
    fail_type_stats = {}

    for i, ann in enumerate(annotations, start=1):
        rel_path = ann["filename"]      # e.g. "pass/id_001.jpg"
        gt_label = ann["label"]         # "PASS" or "FAIL"
        reason   = ann.get("reason", "None")

        img_path = os.path.join(DATASET_DIR, rel_path.replace("/", os.sep))

        if not os.path.isfile(img_path):
            pred_label = "ERROR"
            correct    = False
            print(f"  [{i:03d}] SKIP: {rel_path} -- file khong ton tai")
        else:
            try:
                if PIPELINE_AVAILABLE:
                    pred_label = run_full_pipeline(img_path)
                else:
                    img = imread_unicode(img_path)
                    if img is None:
                        pred_label = "ERROR"
                    else:
                        pred_label = analyze_background_only(img)
            except Exception as e:
                pred_label = "ERROR"

            correct = (pred_label == gt_label)

            # Cập nhật Confusion Matrix
            if gt_label == "PASS" and pred_label == "PASS":
                tp += 1
            elif gt_label == "FAIL" and pred_label == "FAIL":
                tn += 1
            elif gt_label == "FAIL" and pred_label == "PASS":
                fp += 1   # False Positive: hệ thống nói PASS nhưng thực tế FAIL
            elif gt_label == "PASS" and pred_label == "FAIL":
                fn += 1   # False Negative: hệ thống nói FAIL nhưng thực tế PASS

            # Thống kê theo loại lỗi
            if reason != "None":
                if reason not in fail_type_stats:
                    fail_type_stats[reason] = {"total": 0, "correct": 0}
                fail_type_stats[reason]["total"]   += 1
                fail_type_stats[reason]["correct"] += 1 if correct else 0

        details.append({
            "filename":   rel_path,
            "gt_label":   gt_label,
            "pred_label": pred_label,
            "reason":     reason,
            "correct":    correct,
        })

        status = "OK" if correct else "WRONG"
        print(f"  [{i:03d}/{len(annotations)}] {rel_path:<40} GT={gt_label:<4} PRED={pred_label:<5} [{status}]")

    # ── 3. Tính các chỉ số đánh giá ─────────────────────────────────────────
    overall = compute_metrics(tp, tn, fp, fn)

    # ── 4. In báo cáo ra màn hình ────────────────────────────────────────────
    report_lines = []
    def p(line=""):
        print(line)
        report_lines.append(line)

    p()
    p("=" * 65)
    p("  KET QUA TONG HOP -- CONFUSION MATRIX & METRICS")
    p("=" * 65)
    p()
    p("  Confusion Matrix:")
    p(f"  {'':30} | Pred PASS | Pred FAIL")
    p(f"  {'-'*60}")
    p(f"  {'Ground Truth: PASS':30} |  TP={tp:>5}  |  FN={fn:>5}")
    p(f"  {'Ground Truth: FAIL':30} |  FP={fp:>5}  |  TN={tn:>5}")
    p()
    p(f"  Accuracy  : {overall['Accuracy']:.2f}%  ({tp + tn}/{tp + tn + fp + fn} du doan dung)")
    p(f"  Precision : {overall['Precision']:.2f}%  (trong so luong PASS he thong du doan, bao nhieu thuc su la PASS)")
    p(f"  Recall    : {overall['Recall']:.2f}%  (trong so luong PASS thuc su, he thong bat duoc bao nhieu)")
    p(f"  F1-Score  : {overall['F1_Score']:.2f}%")
    p()

    if fail_type_stats:
        p("  Chi tiet theo tung loai loi:")
        p(f"  {'Loai loi':<25} | {'Tong':<6} | {'Dung':<6} | {'Sai':<6} | {'Acc %':<8}")
        p(f"  {'-'*60}")
        for ftype, stat in sorted(fail_type_stats.items()):
            tot   = stat["total"]
            cor   = stat["correct"]
            wrong = tot - cor
            acc   = cor / tot * 100 if tot > 0 else 0
            p(f"  {ftype:<25} | {tot:<6} | {cor:<6} | {wrong:<6} | {acc:.1f}%")
        p()

    p("=" * 65)

    # ── 5. Xuất file báo cáo văn bản ─────────────────────────────────────────
    report_path = os.path.join(OUTPUT_DIR, "benchmark_report.txt")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))
    print(f"\n[+] Bao cao da luu: {report_path}")

    # ── 6. Xuất file CSV chi tiết ─────────────────────────────────────────────
    csv_path = os.path.join(OUTPUT_DIR, "benchmark_details.csv")
    with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=["filename", "gt_label", "pred_label", "reason", "correct"])
        writer.writeheader()
        writer.writerows(details)
    print(f"[+] Chi tiet CSV:   {csv_path}")

    # ── 7. Xuất Confusion Matrix dạng ảnh PNG (dùng OpenCV, không cần matplotlib) ──
    cm_path = os.path.join(OUTPUT_DIR, "confusion_matrix.png")
    _draw_confusion_matrix(tp, tn, fp, fn, overall, cm_path)
    print(f"[+] Confusion Matrix PNG: {cm_path}")
    print()


def _draw_confusion_matrix(tp, tn, fp, fn, metrics, out_path):
    """Vẽ Confusion Matrix bằng OpenCV thuần (không cần matplotlib)."""
    W, H = 520, 440
    img = np.full((H, W, 3), 30, dtype=np.uint8)  # nền tối

    def text(canvas, txt, x, y, scale=0.55, color=(220, 220, 220), bold=False):
        thickness = 2 if bold else 1
        cv2.putText(canvas, txt, (x, y), cv2.FONT_HERSHEY_SIMPLEX,
                    scale, color, thickness, cv2.LINE_AA)

    # Tiêu đề
    text(img, "CONFUSION MATRIX", 130, 35, 0.75, (255, 255, 255), bold=True)
    text(img, "PhotoCheck -- Background Uniformity Module", 55, 60, 0.42, (160, 160, 160))

    # Header cột
    text(img, "Predicted: PASS", 220, 105, 0.5, (100, 255, 100))
    text(img, "Predicted: FAIL", 360, 105, 0.5, (80, 140, 255))

    # Header hàng
    text(img, "GT: PASS", 25, 175, 0.5, (100, 255, 100))
    text(img, "GT: FAIL", 25, 290, 0.5, (80, 140, 255))

    # Ô Confusion Matrix
    cells = [
        (tp, "TP", (40, 120), (0, 200, 80)),    # PASS/PASS
        (fn, "FN", (40, 120), (0, 60, 230)),     # Thực PASS / Pred FAIL
        (fp, "FP", (40, 120), (0, 60, 230)),     # Thực FAIL / Pred PASS
        (tn, "TN", (40, 120), (0, 200, 80)),     # FAIL/FAIL
    ]
    positions = [(205, 140), (345, 140), (205, 255), (345, 255)]
    cell_size = (135, 100)

    for (value, label, _, color), (cx, cy) in zip(cells, positions):
        cv2.rectangle(img, (cx, cy), (cx + cell_size[0], cy + cell_size[1]), color, 2)
        text(img, label, cx + 8, cy + 22, 0.5, color)
        text(img, str(value), cx + 45, cy + 65, 1.6, (255, 255, 255), bold=True)

    # Metrics bên dưới
    y0 = 380
    text(img, f"Accuracy: {metrics['Accuracy']:.2f}%", 30, y0, 0.5, (230, 230, 100))
    text(img, f"Precision: {metrics['Precision']:.2f}%", 170, y0, 0.5, (230, 230, 100))
    text(img, f"Recall: {metrics['Recall']:.2f}%", 320, y0, 0.5, (230, 230, 100))
    text(img, f"F1-Score: {metrics['F1_Score']:.2f}%", 430, y0, 0.5, (230, 230, 100))

    # Ghi file (dùng imencode để hỗ trợ Unicode path)
    ok, buf = cv2.imencode(".png", img)
    if ok:
        buf.tofile(out_path)


if __name__ == "__main__":
    main()
