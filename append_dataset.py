"""
Script to append 3 new failure categories to the existing dataset.
Uses the images in dataset/pass/ as the source.
"""

import os, json, cv2
import numpy as np

OUT_DIR = os.path.join(os.path.dirname(__file__), "dataset")
PASS_DIR = os.path.join(OUT_DIR, "pass")
FACE_COUNT_DIR = os.path.join(OUT_DIR, "fail_face_count")
FACE_SIZE_DIR = os.path.join(OUT_DIR, "fail_face_size")
BG_DIR = os.path.join(OUT_DIR, "fail_background")
JSON_PATH = os.path.join(OUT_DIR, "dataset_annotations.json")

TARGET_W, TARGET_H = 600, 800

for d in [FACE_COUNT_DIR, FACE_SIZE_DIR, BG_DIR]:
    os.makedirs(d, exist_ok=True)

def imread_unicode(path: str):
    try:
        buf = np.fromfile(path, dtype=np.uint8)
        return cv2.imdecode(buf, cv2.IMREAD_COLOR)
    except Exception:
        return None

def imwrite_unicode(path: str, img: np.ndarray) -> bool:
    try:
        ext = os.path.splitext(path)[1]
        ok, buf = cv2.imencode(ext, img)
        if ok:
            buf.tofile(path)
        return ok
    except Exception:
        return False

def make_fail_face_count(pass_img: np.ndarray) -> np.ndarray:
    """Tao loi 2 khuon mat tren cung mot anh."""
    # pass_img la anh 600x800 voi mat o giua.
    # Ta se crop phan mat (va mot chut nen) de tao thanh 2 mat.
    # Khuon mat thuong o vung y: 100-600, x: 100-500
    face_crop = pass_img[96:600, 100:500]
    face_resized = cv2.resize(face_crop, (200, 250))
    
    canvas = np.full((TARGET_H, TARGET_W, 3), 255, dtype=np.uint8)
    
    # Mat 1
    y = 200
    x1 = 50
    canvas[y:y+250, x1:x1+200] = face_resized
    
    # Mat 2
    x2 = 350
    canvas[y:y+250, x2:x2+200] = face_resized
    
    return canvas

def make_fail_face_size(pass_img: np.ndarray) -> np.ndarray:
    """Tao loi khuon mat qua nho (< 45% chieu cao anh)."""
    face_crop = pass_img[96:600, 100:500]
    # Resize mat xuong nho
    face_resized = cv2.resize(face_crop, (150, 180)) # < 200px chieu cao la chac chan fail
    
    canvas = np.full((TARGET_H, TARGET_W, 3), 255, dtype=np.uint8)
    y = 300
    x = (TARGET_W - 150) // 2
    canvas[y:y+180, x:x+150] = face_resized
    return canvas

def make_fail_background(pass_img: np.ndarray) -> np.ndarray:
    """Tao loi nen phia sau khong dong nhat (nen gradient)."""
    face_crop = pass_img[96:600, 100:500]
    
    canvas = np.zeros((TARGET_H, TARGET_W, 3), dtype=np.uint8)
    for y in range(TARGET_H):
        val = int(255 * (y / TARGET_H))
        canvas[y, :] = (val, val, val)
        
    y = 150
    x = (TARGET_W - 400) // 2
    canvas[y:y+504, x:x+400] = face_crop
    
    return canvas

def main():
    if not os.path.exists(JSON_PATH):
        print("JSON file not found!")
        return
        
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        annotations = json.load(f)
        
    # check if already added
    if any(a["reason"] == "FAIL_FACE_COUNT" for a in annotations):
        print("Already appended.")
        return

    pass_files = [f for f in os.listdir(PASS_DIR) if f.endswith(".jpg")]
    
    for fname in pass_files:
        fpath = os.path.join(PASS_DIR, fname)
        img = imread_unicode(fpath)
        if img is None: continue
        
        # FAIL_FACE_COUNT
        out_fc = make_fail_face_count(img)
        imwrite_unicode(os.path.join(FACE_COUNT_DIR, fname), out_fc)
        annotations.append({
            "filename": f"fail_face_count/{fname}",
            "label": "FAIL",
            "reason": "FAIL_FACE_COUNT",
            "source_file": fname
        })
        
        # FAIL_FACE_SIZE
        out_fs = make_fail_face_size(img)
        imwrite_unicode(os.path.join(FACE_SIZE_DIR, fname), out_fs)
        annotations.append({
            "filename": f"fail_face_size/{fname}",
            "label": "FAIL",
            "reason": "FAIL_FACE_SIZE",
            "source_file": fname
        })
        
        # FAIL_BACKGROUND
        out_bg = make_fail_background(img)
        imwrite_unicode(os.path.join(BG_DIR, fname), out_bg)
        annotations.append({
            "filename": f"fail_background/{fname}",
            "label": "FAIL",
            "reason": "FAIL_BACKGROUND",
            "source_file": fname
        })
        
        print(f"Generated 3 fail cases for {fname}")
        
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(annotations, f, indent=4, ensure_ascii=False)
        
    print("Done generating new fail cases.")

if __name__ == "__main__":
    main()
