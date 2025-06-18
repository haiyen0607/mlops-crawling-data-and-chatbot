# 📰 Dantri News Crawler

**Dantri News Crawler** là một dự án Python dùng để tự động thu thập tin tức từ trang báo điện tử [Dân Trí](https://dantri.com.vn). Dự án sử dụng kết hợp giữa kỹ thuật **HTTP Request + HTML Parsing** và **Selenium Headless** để xử lý nội dung động trên trang.

---

## 📦 Cấu trúc thư mục

```
crawl_dantri/
├── data/                    # Lưu dữ liệu sau khi crawl
├── src/
│   └── crawler/
│       ├── base.py          # Lớp crawler cơ sở
│       ├── utils.py         # Hàm tiện ích (log, xử lý chuỗi, etc.)
│       ├── config.py        # Các thông số cấu hình (sleep time, pagination...)
│       └── dantri/
│           └── dantri.py    # Crawler chính cho trang Dân Trí
├── crawl_log.txt            # File ghi log quá trình crawl
├── main.py                  # Chạy crawl và lưu kết quả
├── worker.py                # Quản lý đa luồng hoặc queue
├── eval.ipynb               # Phân tích dữ liệu đã crawl
├── run_crawl.bat            # Batch file để chạy crawler
└── requirements.txt         # Các thư viện cần cài đặt
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
python main.py sync --num_links 100 --max_pagination 5
```

### 4. (Tùy chọn) Chạy bằng batch trên Windows

```bash
run_crawler_vnexpress.bat
```

---

## ⚙️ Các kỹ thuật sử dụng

| Kỹ thuật                  | Mô tả |
|---------------------------|-------|
| **Selenium + Headless**   | Scroll trang `Tin Mới Nhất` để lấy dữ liệu động |
| **BeautifulSoup**         | Phân tích cấu trúc DOM và trích xuất nội dung HTML |
| **Đệ quy phân trang**     | Lặp qua các trang `p1`, `p2`, ... trong mỗi chuyên mục |
| **Slugify**               | Chuyển tên chuyên mục thành dạng slug (để đặt key) |
| **TQDM**                  | Hiển thị tiến trình crawl |
| **Cấu hình động**         | Thông qua `config.py` để thay đổi sleep time, max page, v.v |

---

## 📊 Đầu ra

Dữ liệu sau khi crawl được lưu vào thư mục `data/`, có thể ở dạng `.csv`, `.json`, hoặc đưa vào notebook `eval.ipynb` để trực quan hóa.

---

## 📌 Tác giả

- 👨‍💻 **Lê Hải Yến**
- 📘 Trường Đại học Phenikaa
- 🔍 Liên hệ hỗ trợ: [GitHub](https://github.com/)

---

## 🛠️ TODOs

- [ ] Crawl ảnh đính kèm bài viết
- [ ] Crawl bình luận (nếu có)
- [ ] Hỗ trợ crawl các báo khác (VNExpress, Tuổi Trẻ...)
- [ ] Thêm lịch tự động bằng Jenkins hoặc cronjob

---