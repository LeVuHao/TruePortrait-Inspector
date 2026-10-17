# KỊCH BẢN LIVE DEMO HỆ THỐNG PHOTOCHECK (3 PHÚT)
## CHUYÊN ĐỀ: ĐẶC TRƯNG TOÀN CỤC (GLOBAL FEATURES)

Tập ảnh mẫu nằm ngay trong thư mục này (`d:\xulyanh\demo_samples\`). 
Khi lên thuyết trình trước Thầy và Hội đồng, Hảo mở trình duyệt Web và lần lượt kéo thả 5 file ảnh theo thứ tự sau:

---

### ẢNH 1: `01_anh_chuan_PASS.jpg` (Ảnh thẻ chuẩn đạt yêu cầu)
* **Thao tác:** Kéo thả ảnh `01_anh_chuan_PASS.jpg` vào vùng upload.
* **Hiện tượng trên Web:**
  * Thẻ kết luận: **ẢNH ĐẠT CHUẨN (PASS)**, Điểm chất lượng cao (> 90/100).
  * Tiêu chí số 5 (Đặc trưng toàn cục): **Đạt chuẩn (Bhattacharyya $d_B = 0.09 < 0.45$)**.
  * Hai ngọn núi Histogram 16 bins đè khít lên nhau giữa ảnh người dùng và Profile mẫu chuẩn.
* **Lời thoại với Thầy:**
  > *"Thưa thầy, đây là một ảnh thẻ chuẩn. Hệ thống trích xuất vector 18 chiều và so sánh với Profile ảnh thẻ chuẩn của nhóm: Khoảng cách Bhattacharyya chỉ 0.09, chứng minh phân bố ánh sáng và phổ màu rất tương đồng với ảnh chuẩn."*

---

### ẢNH 2: `02_anh_thieu_sang_DARK.jpg` (Ảnh chụp thiếu sáng + DEMO CÂN BẰNG SÁNG)
* **Thao tác:** Kéo thả ảnh `02_anh_thieu_sang_DARK.jpg`.
* **Hiện tượng trên Web:**
  * Bắt lỗi ngay: **Thiếu sáng nghiêm trọng** (Mean $\approx 48 < 90$, Skewness dương lệch trái, $d_B = 0.82$).
  * Hai ngọn núi Histogram lệch hẳn nhau (ngọn núi ảnh lệch về vùng tối 0-50).
* **ĐIỂM NHẤN ĂN ĐIỂM (CÚ CHỐT):**
  * Hảo bấm sang tab màu vàng: **"Cân bằng CLAHE"**.
  * Ảnh lập tức sáng bừng, nhìn rõ từng đường nét khuôn mặt nhưng màu da vẫn giữ tự nhiên.
* **Lời thoại với Thầy:**
  > *"Thưa thầy, khi gặp ảnh thiếu sáng, hệ thống không chỉ phát hiện lỗi mà còn áp dụng thuật toán Cân bằng sáng toàn cục CLAHE trên không gian màu CIELAB để tự động cứu ảnh trước và sau như thầy đang thấy ạ!"*

---

### ẢNH 3: `03_anh_chay_sang_OVEREXPOSED.jpg` (Ảnh chụp cháy sáng / đèn rọi)
* **Thao tác:** Kéo thả ảnh `03_anh_chay_sang_OVEREXPOSED.jpg`.
* **Hiện tượng trên Web:**
  * Thẻ kết luận: **KHÔNG ĐẠT (FAIL)**.
  * Bắt lỗi: **Ảnh bị cháy sáng / quá phơi sáng** (Mean Intensity > 215.0).
* **Lời thoại với Thầy:**
  > *"Với các trường hợp chụp đèn flash quá mạnh hoặc đứng dưới nắng gắt, đặc trưng toàn cục phát hiện ngay cường độ trung bình vượt ngưỡng 215."*

---

### ẢNH 4: `04_anh_mo_nhet_BLUR.jpg` (Ảnh bị nhòe tay / out nét)
* **Thao tác:** Kéo thả ảnh `04_anh_mo_nhet_BLUR.jpg`.
* **Hiện tượng trên Web:**
  * Bấm sang tab: **"Viền Laplacian"**.
  * Phương sai ma trận Laplacian $Var(\nabla^2 f) < 75.0$ $\rightarrow$ Bắt lỗi ảnh mờ.
* **Lời thoại với Thầy:**
  > *"Tiêu chuẩn độ nét được đo bằng toán tử đạo hàm bậc hai Laplacian (Slide 5), phát hiện ảnh bị rung tay hoặc camera mất nét."*

---

### ẢNH 5: `05_anh_2_nguoi_FACE_COUNT.jpg` (Ảnh chụp 2 người)
* **Thao tác:** Kéo thả ảnh `05_anh_2_nguoi_FACE_COUNT.jpg`.
* **Hiện tượng trên Web:**
  * Vẽ 2 Bounding Box màu xanh lên mặt 2 người $\rightarrow$ Báo lỗi: Phát hiện 2 khuôn mặt (yêu cầu duy nhất 1).
* **Lời thoại với Thầy:**
  > *"Hệ thống sử dụng bộ lọc đặc trưng cục bộ Haar-like (Slide 6) để đảm bảo tính duy nhất của chủ thể ảnh hồ sơ."*
