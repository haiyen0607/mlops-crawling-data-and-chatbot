@echo off
chcp 65001

REM Kích hoạt môi trường Conda
call C:\Users\ADMIN\anaconda3\Scripts\activate.bat bigdata-env

REM Chuyển sang thư mục chatbot_rag
cd /d D:\bigdata_test\chatbot_rag

REM Xây lại index với dữ liệu mới nhất
python build_index.py

REM Gửi notify nếu bạn cần đồng bộ UI hoặc frontend (nếu có WebSocket)
curl http://localhost:8000/notify

pause
