@echo off
chcp 65001
REM Kích hoạt môi trường conda và chạy lệnh trong cùng một dòng

call C:\Users\ADMIN\anaconda3\Scripts\activate.bat bigdata-env

cd /d D:\bigdata_test\crawl_vnexpress

python main_vnexpress.py sync --num_links 10000 --max_pagination 100 --force_crawl
REM Gửi notify tới WebSocket server để cập nhật dashboard
curl http://localhost:8000/notify
pause