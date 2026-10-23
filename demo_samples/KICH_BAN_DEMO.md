# KỊCH BẢN LIVE DEMO HỆ THỐNG PHOTOCHECK (8 TRƯỜNG HỢP)
## CHUYÊN ĐỀ: ĐẶC TRƯNG TOÀN CỤC (GLOBAL FEATURES) & XỬ LÝ ẢNH CHÂN DUNG

Tập ảnh mẫu nằm ngay trong thư mục này (`d:\xulyanh\demo_samples\`). 
Khi quay video demo nộp Thầy, bạn mở trình duyệt Web (`http://localhost:5173/`) và lần lượt kéo thả 8 file ảnh theo thứ tự sau:

---

### ẢNH 1: `01_anh_chuan_PASS.jpg` (Ảnh thẻ chuẩn đạt yêu cầu - ICAO White Background)
* **Thao tác:** Kéo thả ảnh `01_anh_chuan_PASS.jpg` vào vùng upload.
* **Hiện tượng trên Web:**
  * Thẻ kết luận: **ẢNH ĐẠT CHUẨN (PASS)**, Điểm chất lượng cao (> 90/100).
  * Tiêu chí số 5 (Đặc trưng toàn cục): **Đạt chuẩn (Bhattacharyya $d_B = 0.09 < 0.50$)**.
  * Hai ngọn núi Histogram 16 bins đè khít lên nhau giữa ảnh người dùng và Profile mẫu chuẩn.
* **Lời thoại với Thầy:**
  > *"Thưa thầy, đây là một ảnh thẻ chuẩn. Hệ thống trích xuất vector 18 chiều và so sánh với Profile ảnh thẻ chuẩn của nhóm: Khoảng cách Bhattacharyya chỉ 0.09, chứng minh phân bố ánh sáng và phổ màu rất tương đồng với ảnh chuẩn."*

---

### ẢNH 2: `08_anh_chuan_2_PASS.jpg` (Ảnh thẻ chuẩn đạt yêu cầu thứ 2)
* **Thao tác:** Bấm "Tải ảnh khác" rồi kéo thả `08_anh_chuan_2_PASS.jpg`.
* **Hiện tượng trên Web:**
  * Thẻ kết luận: **ẢNH ĐẠT CHUẨN (PASS)**, Điểm chất lượng cao (> 90/100).
  * Cả 6 tiêu chí đều tích xanh.
* **Lời thoại với Thầy:**
  > *"Hệ thống tiếp tục nhận diện chính xác một mẫu ảnh thẻ chuẩn khác với tỷ lệ khuôn mặt đạt 54.2%, chứng minh tính ổn định của pipeline trên nhiều chủ thể khác nhau."*

---

### ẢNH 3: `02_anh_thieu_sang_DARK.jpg` (Ảnh chụp thiếu sáng / phòng tối)
* **Thao tác:** Kéo thả ảnh `02_anh_thieu_sang_DARK.jpg`.
* **Hiện tượng trên Web:**
  * Bắt lỗi: **Thiếu sáng nghiêm trọng** (Mean $\approx 48 < 90$, Skewness dương lệch trái, $d_B = 0.82$).
  * Ngọn núi Histogram lệch hẳn về vùng tối bên trái (0-50).
* **ĐIỂM NHẤN CÔNG NGHỆ:**
  * Bấm sang tab màu tím: **"Chuẩn hóa DIP (3:4)"**.
  * Hệ thống tự động nâng sáng thích nghi bằng hàm Gamma kết hợp căn chỉnh lại khung hình.
* **Lời thoại với Thầy:**
  > *"Khi gặp ảnh thiếu sáng, mô-men Skewness mang giá trị dương lớn chứng minh phổ sáng dồn về tối. Hệ thống tự động áp dụng hàm mũ Gamma nâng sáng tự nhiên mà không làm cháy phông nền."*

---

### ẢNH 4: `03_anh_chay_sang_OVEREXPOSED.jpg` (Ảnh chụp cháy sáng / đèn rọi)
* **Thao tác:** Kéo thả ảnh `03_anh_chay_sang_OVEREXPOSED.jpg`.
* **Hiện tượng trên Web:**
  * Thẻ kết luận: **KHÔNG ĐẠT (FAIL)**.
  * Bắt lỗi: **Ảnh bị cháy sáng / quá phơi sáng** (Mean Intensity > 215.0, Highlight clipping cao).
* **Lời thoại với Thầy:**
  > *"Với các trường hợp chụp đèn flash quá mạnh hoặc đứng dưới nắng gắt, đặc trưng toàn cục phát hiện ngay cường độ trung bình vượt ngưỡng 215 và các điểm ảnh bão hòa sáng kịch trần."*

---

### ẢNH 5: `04_anh_mo_nhet_BLUR.jpg` (Ảnh bị nhòe tay / out nét + DEMO LÀM MỊN & TĂNG NÉT)
* **Thao tác:** Kéo thả ảnh `04_anh_mo_nhet_BLUR.jpg`.
* **Hiện tượng trên Web:**
  * Bắt lỗi tại tiêu chí 4: **Ảnh bị mờ** (Phương sai Laplacian $Var(\nabla^2 f) < 75.0$).
* **ĐIỂM NHẤN ĂN ĐIỂM (CÚ CHỐT):**
  * Bấm sang tab màu xanh ngọc: **"✨ Làm mịn & Tăng nét DIP"**.
  * Ảnh lập tức được làm mịn màng da mặt nhưng viền mắt, chân mày và sợi tóc nét đanh lên rõ rệt.
* **Lời thoại với Thầy:**
  > *"Tiêu chuẩn độ nét đo bằng phương sai đạo hàm bậc hai Laplacian phát hiện ảnh mờ nét. Khi em bấm tab 'Làm mịn & Tăng nét DIP', hệ thống áp dụng bộ lọc song phương Bilateral Filter để làm mịn da bảo toàn cạnh kết hợp Unsharp Masking để phục hồi độ nét chi tiết như app điện thoại ạ!"*

---

### ẢNH 6: `05_anh_2_nguoi_FACE_COUNT.jpg` (Ảnh chụp 2 người)
* **Thao tác:** Kéo thả ảnh `05_anh_2_nguoi_FACE_COUNT.jpg`.
* **Hiện tượng trên Web:**
  * Bấm tab **"Khung mặt"**: Vẽ 2 Bounding Box màu xanh lên mặt 2 người $\rightarrow$ Báo lỗi: Phát hiện 2 khuôn mặt (yêu cầu duy nhất 1).
* **Lời thoại với Thầy:**
  > *"Hệ thống sử dụng bộ lọc đặc trưng cục bộ Haar-like để đảm bảo tính duy nhất của chủ thể hồ sơ."*

---

### ẢNH 7: `06_anh_mat_nho_FACE_SIZE.jpg` (Ảnh chụp đứng quá xa / Mặt quá nhỏ)
* **Thao tác:** Kéo thả ảnh `06_anh_mat_nho_FACE_SIZE.jpg`.
* **Hiện tượng trên Web:**
  * Bắt lỗi tiêu chí 3: Tỷ lệ khuôn mặt chỉ chiếm ~24.4% chiều cao ảnh (yêu cầu 35% - 70%).
* **ĐIỂM NHẤN ĂN ĐIỂM:**
  * Bấm nút **"Tải ảnh đề xuất chuẩn 3:4 (JPG)"**: Hệ thống tự động căn chỉnh và tải ngay file ảnh thẻ đã crop chuẩn 3:4 (600x800px) với tỷ lệ khuôn mặt đạt đúng 54% ICAO về máy tính!
* **Lời thoại với Thầy:**
  > *"Thuật toán biến đổi hình học tự động tính toán lại vùng đệm đỉnh đầu và bờ vai để crop lại ảnh đạt chuẩn 3:4 với tỷ lệ mặt ~54%, người dùng chỉ cần bấm tải ảnh JPG chuẩn về là dán hồ sơ được ngay ạ!"*

---

### ẢNH 8: `07_anh_nen_tap_BACKGROUND.jpg` (Ảnh phông nền phức tạp / nền tạp)
* **Thao tác:** Kéo thả ảnh `07_anh_nen_tap_BACKGROUND.jpg`.
* **Hiện tượng trên Web:**
  * Bắt lỗi tiêu chí 6: **Phông nền không sạch** (Độ loang lổ nền > 15.0).
* **Lời thoại với Thầy:**
  > *"Hệ thống phân tích độ phân tán màu sắc tại vùng biên phông nền. Khi có vật thể hoặc hoa văn, độ lệch chuẩn mẫu màu vọt lên cao chứng minh phông nền bị tạp và không đạt chuẩn."*
