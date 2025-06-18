# # import os
# # from dotenv import load_dotenv
# # from datetime import datetime
# # import pandas as pd
# # import google.generativeai as genai

# # from llama_index.core import StorageContext, load_index_from_storage
# # from llama_index.core.settings import Settings
# # from llama_index.embeddings.huggingface import HuggingFaceEmbedding
# # from llama_index.llms.gemini import Gemini

# # # ==== TỪ KHÓA ĐỂ PHÂN BIỆT CÂU HỎI HOT TREND ====
# # TREND_KEYWORDS = [
# #     "chủ đề hot", "chủ đề nóng", "vấn đề nổi cộm",
# #     "xu hướng", "trending", "cụm từ hot", "tin nóng", "vấn đề đáng chú ý"
# # ]

# # def is_trend_question(question: str) -> bool:
# #     q = question.lower()
# #     return any(keyword in q for keyword in TREND_KEYWORDS)


# # # ==== LẤY FILE HOT TOPICS MỚI NHẤT ====
# # def get_latest_hot_topics_file(data_dir="data"):
# #     prefix = "hot_topics_"
# #     suffix = ".csv"

# #     files = [
# #         os.path.join(data_dir, f)
# #         for f in os.listdir(data_dir)
# #         if f.startswith(prefix) and f.endswith(suffix)
# #     ]
# #     if not files:
# #         return None

# #     # Sắp xếp theo thời gian cập nhật gần nhất
# #     files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
# #     return files[0]
# # # ==== IN RA DANH SÁCH HOT TREND ====
# # def show_trending_articles():
# #     file_path = get_latest_hot_topics_file()
# #     if not file_path:
# #         print("Không tìm thấy dữ liệu hot topics.")
# #         return

# #     df = pd.read_csv(file_path)

# #     print("\nChủ đề hot gần đây và bài viết liên quan:")
# #     for _, row in df.iterrows():
# #         print(f"- [{row['topic']}] {row['url']} ({row['created_at']})")


# # # Load API Key
# # os.environ["GOOGLE_API_KEY"] = "AIzaSyD10Ny4Gd9nKBY-irrQ70RNQeiHVuBCkGM"

# # # Load embedding
# # embed_model = HuggingFaceEmbedding(model_name="bkai-foundation-models/vietnamese-bi-encoder")
# # Settings.embed_model = embed_model

# # # Load LLM
# # llm = Gemini(
# #     model_name="models/gemini-1.5-flash",
# #     api_key=os.environ["GOOGLE_API_KEY"]
# # )
# # Settings.llm = llm

# # # Load index từ thư mục đã lưu
# # storage_context = StorageContext.from_defaults(persist_dir="index/storage")
# # index = load_index_from_storage(storage_context)

# # # Tạo Query Engine
# # query_engine = index.as_query_engine(llm=llm, similarity_top_k=10)

# # # ==== VÒNG LẶP CHAT ====
# # while True:
# #     question = input("Nhập câu hỏi (gõ 'exit' để thoát):\n>> ")
# #     if question.lower() in ["exit", "quit"]:
# #         break

# #     if is_trend_question(question):
# #         show_trending_articles()
# #         continue

# #     response = query_engine.query(question)

# #     # Sắp xếp kết quả theo ngày mới nhất
# #     nodes = response.source_nodes
# #     try:
# #         for node in nodes:
# #             if isinstance(node.metadata.get("created_at"), str):
# #                 node.metadata["created_at"] = datetime.strptime(node.metadata["created_at"], "%Y-%m-%d")
# #         sorted_nodes = sorted(nodes, key=lambda x: x.metadata["created_at"], reverse=True)

# #         print("\nCâu trả lời:")
# #         for node in sorted_nodes:
# #             date = node.metadata["created_at"].strftime("%Y-%m-%d")
# #             title = node.metadata.get("title", "Không có tiêu đề")
# #             print(f"{date} - {title}")
# #     except Exception as e:
# #         print("Đã xảy ra lỗi khi sắp xếp theo ngày:", e)
# #         print("\nCâu trả lời thô:\n", response)

# import os
# from datetime import datetime
# from llama_index.core import StorageContext, load_index_from_storage
# from llama_index.core.settings import Settings
# from llama_index.embeddings.huggingface import HuggingFaceEmbedding
# from llama_index.llms.gemini import Gemini

# # Thiết lập API key (hoặc load từ .env nếu cần)
# os.environ["GOOGLE_API_KEY"] = "AIzaSyAm9RzA3ckL-pHO25PgeWihdRvVkPsRaIY"

# # Đường dẫn tuyệt đối đến index
# index_path = os.path.join(os.path.dirname(__file__), "index", "storage")
# storage_context = StorageContext.from_defaults(persist_dir=index_path)

# # Thiết lập mô hình
# embed_model = HuggingFaceEmbedding(model_name="bkai-foundation-models/vietnamese-bi-encoder")
# Settings.embed_model = embed_model

# llm = Gemini(model_name="models/gemini-1.5-flash", api_key=os.environ["GOOGLE_API_KEY"])
# Settings.llm = llm

# # Load index
# storage_context = StorageContext.from_defaults(persist_dir=index_path)
# index = load_index_from_storage(storage_context)
# query_engine = index.as_query_engine(llm=llm, similarity_top_k=30)


# # HÀM CHO STREAMLIT GỌI
# def run_query_external(question: str, top_k: int = 4):
#     try:
#         response = query_engine.query(question)
#         nodes = response.source_nodes

#         for node in nodes:
#             if isinstance(node.metadata.get("created_at"), str):
#                 node.metadata["created_at"] = datetime.strptime(node.metadata["created_at"], "%Y-%m-%d")

#         sorted_nodes = sorted(nodes, key=lambda x: x.metadata["created_at"], reverse=True)
#         seen = set()
#         result = []

#         for node in sorted_nodes:
#             title = node.metadata.get("title", "Không có tiêu đề")
#             url = node.metadata.get("url", "")
#             date = node.metadata["created_at"].strftime("%Y-%m-%d")
#             if title not in seen:
#                 seen.add(title)
#                 result.append(f"{date} - [{title}]({url})")
#             if len(result) >= top_k:
#                 break

#         return result
#     except Exception as e:
#         return [f"Lỗi: {str(e)}"]


# # PHẦN CLI CHỈ CHẠY KHI RUN TRỰC TIẾP
# if __name__ == "__main__":
#     while True:
#         question = input("Nhập câu hỏi (gõ 'exit' để thoát):\n>> ")
#         if question.lower() in ["exit", "quit"]:
#             break

#         results = run_query_external(question)
#         print("\nCác bài viết liên quan:")
#         for line in results:
#             print(f"- {line}")


import os
from datetime import datetime
from llama_index.core import StorageContext, load_index_from_storage
from llama_index.core.settings import Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.gemini import Gemini

# Thiết lập API key
#AIzaSyBpnsFVe2Fn_YiVY67X4dCUIkxj5FuZhjA
os.environ["GOOGLE_API_KEY"] = "AIzaSyDstywi_yI7m8QYHvqLF7SOEVxx_4FmShc"

# Đường dẫn tuyệt đối đến index
index_path = os.path.join(os.path.dirname(__file__), "index", "storage")

# Thiết lập mô hình embedding và LLM
embed_model = HuggingFaceEmbedding(model_name="bkai-foundation-models/vietnamese-bi-encoder")
Settings.embed_model = embed_model

llm = Gemini(model_name="models/gemini-1.5-flash", api_key=os.environ["GOOGLE_API_KEY"])
Settings.llm = llm

# HÀM CHO STREAMLIT GỌI
def run_query_external(question: str, top_k: int = 4):
    try:
        # 🔁 Luôn load lại index mỗi lần gọi
        storage_context = StorageContext.from_defaults(persist_dir=index_path)
        index = load_index_from_storage(storage_context)
        query_engine = index.as_query_engine(llm=llm, similarity_top_k=30)

        response = query_engine.query(question)
        nodes = response.source_nodes

        for node in nodes:
            if isinstance(node.metadata.get("created_at"), str):
                node.metadata["created_at"] = datetime.strptime(node.metadata["created_at"], "%Y-%m-%d")

        sorted_nodes = sorted(nodes, key=lambda x: x.metadata["created_at"], reverse=True)
        seen = set()
        result = []

        for node in sorted_nodes:
            title = node.metadata.get("title", "Không có tiêu đề")
            url = node.metadata.get("url", "")
            date = node.metadata["created_at"].strftime("%Y-%m-%d")
            if title not in seen:
                seen.add(title)
                result.append(f"{date} - [{title}]({url})")
            if len(result) >= top_k:
                break

        return result
    except Exception as e:
        return [f"Lỗi: {str(e)}"]


# PHẦN CLI CHỈ CHẠY KHI RUN TRỰC TIẾP
if __name__ == "__main__":
    while True:
        question = input("Nhập câu hỏi (gõ 'exit' để thoát):\n>> ")
        if question.lower() in ["exit", "quit"]:
            break

        results = run_query_external(question)
        print("\nCác bài viết liên quan:")
        for line in results:
            print(f"- {line}")
