import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import requests
import os

# === CẤU HÌNH ===
WATCH_DIR = os.path.abspath("../data")
WATCH_FILE = "data.csv"
NOTIFY_URL = "http://localhost:8000/notify"

class DataChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.is_directory:
            return

        if os.path.basename(event.src_path) == WATCH_FILE:
            print(f"[WATCH] Phát hiện thay đổi ở {WATCH_FILE}, gửi notify...")
            try:
                response = requests.get(NOTIFY_URL)
                print(f"[NOTIFY] Đã gửi notify, server trả về {response.status_code}")
            except Exception as e:
                print(f"[ERROR] Lỗi khi gửi notify: {e}")

if __name__ == "__main__":
    print(f"[START] Đang theo dõi: {os.path.join(WATCH_DIR, WATCH_FILE)}")
    event_handler = DataChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, path=WATCH_DIR, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[STOP] Dừng theo dõi.")
        observer.stop()
    observer.join()
