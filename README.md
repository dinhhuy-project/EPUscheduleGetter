# EPUscheduleGetter
This script helps EPU students automatically retrieve their weekly class schedules.

# Các bước sử dụng
Script này thực hiện các bước:

- Lấy cookies từ trình duyệt
- Gửi POST request tới trang `https://thanhtoanhocphi.epu.edu.vn` để lấy thời khóa biểu tuần tới
- Lưu HTML response và chụp ảnh trang
- Tự động upload ảnh lên Google Drive

---

## 🧩 Yêu cầu hệ thống

- Python 3.8 trở lên
- Trình duyệt đã đăng nhập vào [https://thanhtoanhocphi.epu.edu.vn](https://thanhtoanhocphi.epu.edu.vn)
- Có tài khoản Google Drive (và file `credentials.json`)

---

## 🚀 Hướng dẫn cài đặt

### 1. Clone dự án

```bash
git clone https://github.com/dinhhuy-project/EPUscheduleGetter
cd EPUscheduleGetter
```

### 2. Cài dependencies

```bash
pip install -r requirements.txt
playwright install
```

### 3. Chuẩn bị credentials Google Drive

Truy cập: https://console.cloud.google.com

Tạo project và bật API: "Google Drive API"

Tạo OAuth 2.0 credentials (Desktop App)

Tải file credentials.json và đặt vào file credentials.json

📌 File token.pickle sẽ tự động được tạo khi bạn chạy lần đầu.

Lấy id của folder Drive đặt vào file .env

### 4. Cách sử dụng script

```bash
python main.py
```