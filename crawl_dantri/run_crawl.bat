@echo off
chcp 65001

REM Kích hoạt môi trường Conda
call C:\Users\ADMIN\anaconda3\Scripts\activate.bat bigdata-env

REM Chuyển sang thư mục chứa crawler
cd /d D:\bigdata_test\crawl_dantri

REM Chạy crawl dữ liệu
python main.py sync --num_links 10000 --max_pagination 5 --force_crawl

REM Gửi notify tới WebSocket server để cập nhật dashboard
curl http://localhost:8000/notify

pause
