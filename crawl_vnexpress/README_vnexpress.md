# 📰 VnExpress News Crawler

**VnExpress News Crawler** là một dự án Python để tự động thu thập tin tức từ trang báo điện tử [VnExpress](https://vnexpress.net). Dự án sử dụng kết hợp kỹ thuật **HTML Parsing**, **Phân trang đệ quy**, và xử lý DOM để thu thập dữ liệu từ nhiều chuyên mục khác nhau.

---

## 📁 Cấu trúc thư mục

```
crawl_vnexpress/
├── data_vnexpress/                  # Thư mục lưu dữ liệu sau khi crawl
├── src/
│   └── crawler_vnexpress/
│       ├── base.py                 # Lớp cơ sở BaseCrawler dùng chung
│       ├── utils.py                # Hàm tiện ích (xử lý chuỗi, log, etc.)
│       ├── config.py               # Cấu hình thời gian chờ, max page, v.v.
│       └── vnexpress/
│           └── vnexpress.py        # Logic chính để crawl từ VnExpress
├── main_vnexpress.py               # Chạy crawl và lưu dữ liệu ra file
├── worker.py                       # (Tùy chọn) quản lý crawl song song hoặc theo queue
├── run_crawler_vnexpress.bat       # File batch để chạy nhanh quá trình crawl
└── requirements.txt                # Danh sách các thư viện cần cài
```

---

## 🚀 Cách sử dụng

### 1. Cài đặt môi trường ảo
#### 1.1. Tạo môi trường chạy ảo (nếu chưa có)
```bash
conda -n create bigdata-env python=3.10
```
#### 1.2. Kích hoạt môi trường ảo
```bash
conda activate bigdata-env
```
### 2. Cài đặt môi trường

```bash
pip install -r requirements.txt
```

### 3. Chạy crawler

```bash
python main_vnexpress.py sync --num_links 100 --max_pagination 5
```

### 4. (Tùy chọn) Chạy bằng batch trên Windows

```bash
run_crawler_vnexpress.bat
```

---

## ⚙️ Kỹ thuật áp dụng

| Kỹ thuật                | Mô tả |
|-------------------------|-------|
| **HTML Parsing**        | Dùng BeautifulSoup để phân tích DOM HTML |
| **Đệ quy phân trang**   | Lặp qua các trang trong mỗi chuyên mục (`p2`, `p3`, ...) |
| **DOM Traversal**       | Truy cập các thẻ `h1`, `span.date`, `article p`, ... để lấy dữ liệu |
| **Lọc trùng lặp URL**   | Dùng `set()` để loại bỏ bài viết đã gặp |
| **Gắn nhãn chủ đề**     | Gán thông tin chuyên mục (`topic`) cho từng bài viết |
| **TQDM**                | Hiển thị tiến trình crawl từng chuyên mục/sub chuyên mục |

---

## 📊 Đầu ra

Dữ liệu sau khi crawl được lưu trong thư mục `data_vnexpress/`, định dạng CSV hoặc JSON tùy theo cấu hình trong `main_vnexpress.py`.

---

## 📌 Tác giả

- 👨‍💻 **Lê Hải Yến**
- 📘 Trường Đại học Phenikaa

---

## ✅ TODO

- [ ] Tự động hóa cập nhật dữ liệu theo lịch trình (cron/Jenkins)
- [ ] Phân tích từ khóa từ nội dung bài viết
- [ ] Hỗ trợ xuất dữ liệu ra định dạng chuẩn (JSONL hoặc SQLite)