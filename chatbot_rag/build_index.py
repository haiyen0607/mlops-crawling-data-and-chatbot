import os
import requests
from dotenv import load_dotenv
from datetime import datetime, timedelta

from load_data import load_documents_from_csv
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.core.settings import Settings

# Load biến môi trường
load_dotenv()

# Đường dẫn file CSV
csv_path = "D:\\bigdata_test\\crawl_dantri\\data\\data.csv"

# Lọc bài trong 7 ngày gần nhất
from_date = datetime.today() - timedelta(days=7)
documents = load_documents_from_csv(csv_path, from_date=from_date)

# Thiết lập mô hình embedding
embed_model = HuggingFaceEmbedding(model_name="bkai-foundation-models/vietnamese-bi-encoder")
Settings.embed_model = embed_model

# Cắt văn bản - chunk_size
parser = SentenceSplitter(chunk_size=2000, chunk_overlap=0)
nodes = parser.get_nodes_from_documents(documents)

# ⚠️ Không truyền persist_dir khi tạo mới
storage_context = StorageContext.from_defaults()

# Tạo và lưu index
index = VectorStoreIndex(nodes, storage_context=storage_context)
index.storage_context.persist(persist_dir="index/storage")

print("[OK] Da tao va luu index vao: index/storage/")

print("[OK] Da tao va luu index vao: index/storage/")

# Notify WebSocket
try:
    response = requests.get("http://127.0.0.1:8000/notify")
    print(f"[WebSocket Notify] Response status: {response.status_code}")
    print(f"[WebSocket Notify] Response content: {response.text}")
except Exception as e:
    print(f"[WebSocket Notify] Failed to notify clients: {e}")

# Ghi log vào file
with open("last_update.log", "a", encoding="utf-8") as f:
    f.write(f"[{datetime.now().isoformat()}] ✅ Da cap nhat index va notify clients\n")
