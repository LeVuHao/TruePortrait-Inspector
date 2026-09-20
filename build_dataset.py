"""
build_dataset.py
================
Muc dich: Lay UTKFace, loc ra 50 anh chat luong nhat,
          ghep nen trang thanh anh the chuan (600x800),
          sau do sinh 150 anh loi (blur/dark/overexposed)
          va xuat file Ground Truth dataset_annotations.json

Cau truc thu muc dau ra (trong TruePortrait-Inspector):
    dataset/
        pass/         -- 50 anh the chuan (PASS)
        fail_blur/    -- 50 anh bi mo
        fail_dark/    -- 50 anh thieu sang
        fail_overexposed/ -- 50 anh choi sang
        dataset_annotations.json -- nhan ground truth

Chay:
    python build_dataset.py
"""

import os, sys, shutil, json, random
import cv2
import numpy as np

# ---------------------------------------------------------------
# 1. CAU HINH DUONG DAN
# ---------------------------------------------------------------
# Duong dan den thu muc UTKFace (chua toan bo .chip.jpg)
# Tim thay tai: D:\Study\University\Hoc ky 1...\Do an\UTKFace
SRC_DIR = os.path.join(
    "D:\\", "Study", "University",
    "H\u1ecdc k\u1ef3 1- N\u0103m h\u1ecdc 2026 - 2027",
    "X\u1eed L\u00fd \u1ea2nh",
    "\u0110\u1ed3 \u00e1n",
    "UTKFace"
)

# Thu muc output (dat trong TruePortrait-Inspector)
OUT_DIR = os.path.join(os.path.dirname(__file__), "dataset")

PASS_DIR   = os.path.join(OUT_DIR, "pass")
BLUR_DIR   = os.path.join(OUT_DIR, "fail_blur")
DARK_DIR   = os.path.join(OUT_DIR, "fail_dark")
BRIGHT_DIR = os.path.join(OUT_DIR, "fail_overexposed")

# Kich thuoc anh the chuan (ty le 3:4)
TARGET_W, TARGET_H = 600, 800

# So luong anh toc nguon muon loc
NUM_SELECTED = 50

# Nguong chat luong toi thieu de giu lai
MIN_LAPLACIAN_VAR = 5.0    # Phuong sai Laplacian -- loai anh qua mo (anh chip nho nen ha nguong)
MIN_BRIGHTNESS    = 60     # Do sang trung binh toi thieu
MAX_BRIGHTNESS    = 230    # Do sang trung binh toi da (tranh chay sang)
MIN_FILE_SIZE_KB  = 3      # Bo qua anh nho < 3KB (co the hong)


# ---------------------------------------------------------------
# 2. HELPER: DOC ANH HO TRO UNICODE PATH TREN WINDOWS
# ---------------------------------------------------------------
def imread_unicode(path: str):
    """Doc anh tu duong dan co ky tu Unicode (tieng Viet) tren Windows."""
    try:
        buf = np.fromfile(path, dtype=np.uint8)
        img = cv2.imdecode(buf, cv2.IMREAD_COLOR)
        return img
    except Exception:
        return None


def find_utkface_dir():
    """Tim thu muc UTKFace duoi Do an neu SRC_DIR khong hop le."""
    base = os.path.join("D:\\", "Study", "University")
    for root, dirs, _ in os.walk(base):
        if "UTKFace" in dirs:
            return os.path.join(root, "UTKFace")
    return None


# ---------------------------------------------------------------
# 3. TINH CHAT LUONG ANH
# ---------------------------------------------------------------
def imwrite_unicode(path: str, img: np.ndarray) -> bool:
    """Ghi anh ra duong dan co ky tu Unicode (tieng Viet) tren Windows."""
    try:
        ext = os.path.splitext(path)[1]  # e.g. '.jpg'
        ok, buf = cv2.imencode(ext, img)
        if ok:
            buf.tofile(path)
        return ok
    except Exception:
        return False



def quality_score(img_bgr: np.ndarray) -> dict:
    gray       = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    lap_var    = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    brightness = float(gray.mean())
    return {"lap_var": lap_var, "brightness": brightness}


# ---------------------------------------------------------------
# 4. GHEP ANH MAT LEN NEN TRANG (gia lap anh the)
# ---------------------------------------------------------------
def make_id_photo(face_img: np.ndarray) -> np.ndarray:
    """
    Nhan vao anh khuon mat (vuong, bat ky kich thuoc).
    Tra ve anh the 600x800 (BGR):
      - Nen trang sach
      - Khuon mat duoc resize ve ~55% chieu cao, can giua theo chieu ngang,
        dat o vi tri 1/6 chieu cao tu tren xuong (giong anh the chuan).
    """
    canvas = np.full((TARGET_H, TARGET_W, 3), 255, dtype=np.uint8)

    face_h = int(TARGET_H * 0.58)          # ~58% chieu cao anh
    face_w = int(face_h * face_img.shape[1] / face_img.shape[0])

    # Giu ty le khung mat
    face_resized = cv2.resize(face_img, (face_w, face_h))

    # Vi tri dan mat: can giua ngang, padding tren ~12%
    x = (TARGET_W - face_w) // 2
    y = int(TARGET_H * 0.12)

    # Dan mat vao canvas (cat neu vuot bien)
    x2 = min(x + face_w, TARGET_W)
    y2 = min(y + face_h, TARGET_H)
    canvas[y:y2, x:x2] = face_resized[: y2 - y, : x2 - x]

    return canvas


# ---------------------------------------------------------------
# 5. TAO CAC BIEN THE LOI
# ---------------------------------------------------------------
def make_blur(img: np.ndarray) -> np.ndarray:
    """Lam mo manh bang GaussianBlur + Motion Blur nhe."""
    blurred = cv2.GaussianBlur(img, (31, 31), 0)
    # Them motion blur
    kernel = np.zeros((20, 20))
    kernel[10, :] = 1.0 / 20
    blurred = cv2.filter2D(blurred, -1, kernel)
    return blurred


def make_dark(img: np.ndarray) -> np.ndarray:
    """Toi anh xuong ~35% do sang goc."""
    return cv2.convertScaleAbs(img, alpha=0.30, beta=-10)


def make_overexposed(img: np.ndarray) -> np.ndarray:
    """Choi sang len ~170% do sang goc."""
    return cv2.convertScaleAbs(img, alpha=1.70, beta=50)


# ---------------------------------------------------------------
# 6. MAIN
# ---------------------------------------------------------------
def main():
    print("=" * 55)
    print("  BUILD DATASET -- ID Photo Quality Checker")
    print("=" * 55)

    # Tim thu muc UTKFace
    src = SRC_DIR
    if not os.path.isdir(src):
        print(f"[!] Khong tim thay: {src}")
        src = find_utkface_dir()
        if src:
            print(f"[*] Tim thay tai: {src}")
        else:
            print("[ERROR] Khong tim thay thu muc UTKFace!")
            print("        Hay sua SRC_DIR trong file build_dataset.py")
            sys.exit(1)

    # Lay danh sach tat ca anh
    all_files = [
        f for f in os.listdir(src)
        if f.lower().endswith(".jpg")
        and os.path.getsize(os.path.join(src, f)) >= MIN_FILE_SIZE_KB * 1024
    ]
    print(f"[*] Tong so anh trong UTKFace: {len(all_files)}")

    # Xao tron de lay ngau nhien
    random.seed(42)
    random.shuffle(all_files)

    # Loc va chon 50 anh dep nhat
    selected = []
    for fname in all_files:
        if len(selected) >= NUM_SELECTED:
            break
        fpath = os.path.join(src, fname)
        img = imread_unicode(fpath)
        if img is None:
            continue
        # Chi giu anh nguoi truong thanh (tuoi >= 18) -- lay tu ten file
        try:
            age = int(fname.split("_")[0])
            if age < 18:
                continue
        except:
            pass
        # Kiem tra chat luong
        q = quality_score(img)
        if q["lap_var"] < MIN_LAPLACIAN_VAR:
            continue
        if not (MIN_BRIGHTNESS <= q["brightness"] <= MAX_BRIGHTNESS):
            continue
        selected.append((fname, fpath, img))

    print(f"[*] Chon duoc {len(selected)} anh dat chat luong.")
    if len(selected) < NUM_SELECTED:
        print(f"[!] Chi chon duoc {len(selected)} / {NUM_SELECTED}. Tang MIN_FILE_SIZE_KB hoac ha nguong neu can them.")

    # Tao cac thu muc output
    for d in [PASS_DIR, BLUR_DIR, DARK_DIR, BRIGHT_DIR]:
        os.makedirs(d, exist_ok=True)

    annotations = []

    for idx, (fname, fpath, img) in enumerate(selected, start=1):
        out_name = f"id_{idx:03d}.jpg"

        # Ghep len nen trang --> anh the chuan
        id_photo = make_id_photo(img)

        # --- PASS ---
        imwrite_unicode(os.path.join(PASS_DIR, out_name), id_photo)
        annotations.append({
            "filename": f"pass/{out_name}",
            "label": "PASS",
            "reason": "None",
            "source_file": fname
        })

        # --- FAIL_BLUR ---
        imwrite_unicode(os.path.join(BLUR_DIR, out_name), make_blur(id_photo))
        annotations.append({
            "filename": f"fail_blur/{out_name}",
            "label": "FAIL",
            "reason": "FAIL_BLUR",
            "source_file": fname
        })

        # --- FAIL_DARK ---
        imwrite_unicode(os.path.join(DARK_DIR, out_name), make_dark(id_photo))
        annotations.append({
            "filename": f"fail_dark/{out_name}",
            "label": "FAIL",
            "reason": "FAIL_DARK",
            "source_file": fname
        })

        # --- FAIL_OVEREXPOSED ---
        imwrite_unicode(os.path.join(BRIGHT_DIR, out_name), make_overexposed(id_photo))
        annotations.append({
            "filename": f"fail_overexposed/{out_name}",
            "label": "FAIL",
            "reason": "FAIL_OVEREXPOSED",
            "source_file": fname
        })

        print(f"  [{idx:02d}/{len(selected)}] {out_name} OK")

    # Xuat Ground Truth JSON
    ann_path = os.path.join(OUT_DIR, "dataset_annotations.json")
    with open(ann_path, "w", encoding="utf-8") as f:
        json.dump(annotations, f, indent=4, ensure_ascii=False)

    print()
    print("=" * 55)
    print(f"[+] HOAN THANH!")
    print(f"[+] Tong so anh: {len(annotations)}")
    print(f"    - pass/          : {NUM_SELECTED} anh chuan (PASS)")
    print(f"    - fail_blur/     : {NUM_SELECTED} anh bi mo")
    print(f"    - fail_dark/     : {NUM_SELECTED} anh thieu sang")
    print(f"    - fail_overexposed/: {NUM_SELECTED} anh choi sang")
    print(f"[+] Ground Truth: dataset/dataset_annotations.json")
    print(f"[+] Thu muc dataset: {OUT_DIR}")
    print()
    print("[!] Cac anh UTKFace goc trong thu muc nguon van con nguyen.")
    print("    Ban co the xoa thu muc UTKFace thu muc goc neu muon giai phong bo nho.")
    print("=" * 55)


if __name__ == "__main__":
    main()
