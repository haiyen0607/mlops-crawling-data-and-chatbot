import streamlit as st
import pandas as pd
import altair as alt
from streamlit.components.v1 import html
import os
from datetime import datetime
import glob
from PIL import Image
import json
import sys

st.set_page_config(layout="wide")

# ---------- WebSocket Client ----------
html("""
<script>
(function() {
  function connectWS() {
    const socket = new WebSocket("ws://127.0.0.1:8000/ws");
    socket.onmessage = function(event) {
      if (event.data.trim() === "data_updated") {
        parent.window.location.reload();
      }
    };
    socket.onopen = function() {
      console.log("✅ WebSocket connected");
    };
    socket.onerror = function(err) {
      console.error("WebSocket error:", err);
    };
    socket.onclose = function() {
      console.warn("WebSocket closed, retrying in 3s...");
      setTimeout(connectWS, 3000);
    };
  }
  window.addEventListener("load", connectWS);
})();
</script>
""", height=0, scrolling=False)

# ---------- Dân Trí Section ----------
st.header("📊 Dashboard bài viết Dân Trí - Tự động cập nhật")
try:
    df_dantri_raw = pd.read_csv("../crawl_dantri/data/data.csv")
except Exception as e:
    st.error(f"Không thể đọc dữ liệu Dân Trí: {e}")
    df_dantri_raw = pd.DataFrame()

if not df_dantri_raw.empty:
    df_dantri = df_dantri_raw.dropna(subset=["title", "url", "content"]).copy()
    df_dantri["topic"] = df_dantri["url"].str.extract(r"dantri.com.vn/([^/]+)/")

    st.metric("Số dòng thực tế đọc được (Dân Trí)", df_dantri_raw.shape[0])
    st.metric("Tổng số bài viết (Dân Trí)", len(df_dantri))

    st.subheader("Một số bài viết đầu tiên")
    st.dataframe(df_dantri[["title", "url"]].head(), use_container_width=True)

    summary_dt = df_dantri['topic'].value_counts().reset_index()
    summary_dt.columns = ['Chuyên mục', 'Số bài']
    summary_dt['Tỉ lệ (%)'] = (summary_dt['Số bài'] / len(df_dantri) * 100).round(2)

    st.subheader("Tỷ lệ chuyên mục (Dân Trí)")
    st.dataframe(summary_dt, use_container_width=True)

    st.altair_chart(alt.Chart(summary_dt).mark_bar().encode(
        x='Số bài:Q', y=alt.Y('Chuyên mục:N', sort='-x'),
        color='Chuyên mục:N', tooltip=['Chuyên mục', 'Số bài', 'Tỉ lệ (%)']
    ).properties(width=700, height=400), use_container_width=True)

    st.altair_chart(alt.Chart(summary_dt.sort_values("Số bài", ascending=False)).mark_line(point=True).encode(
        x=alt.X('Chuyên mục:N', sort=summary_dt.sort_values("Số bài", ascending=False)['Chuyên mục'].tolist(), title='Chuyên mục'),
        y=alt.Y('Tỉ lệ (%):Q', title='Tỉ lệ (%)'),
        tooltip=['Chuyên mục', 'Tỉ lệ (%)']
    ).properties(width=900, height=400), use_container_width=True)

    # Hiển thị lịch sử cập nhật cho Dân Trí
    st.subheader("Lịch sử cập nhật (Dân Trí)")
    log_file_dt = "../crawl_dantri/data/update_log.txt"
    topic_history_file_dt = "../crawl_dantri/data/topic_history.csv"
    now_dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    total_articles_dt = len(df_dantri)

    log_line_dt = f"{now_dt} | Tổng bài viết: {total_articles_dt}"
    os.makedirs(os.path.dirname(log_file_dt), exist_ok=True)
    with open(log_file_dt, mode="a", encoding="utf-8") as f:
        f.write(log_line_dt + "\n")

    summary_dt['timestamp'] = now_dt
    write_header_dt = not os.path.exists(topic_history_file_dt)
    summary_dt[["timestamp", "Chuyên mục", "Tỉ lệ (%)"]].rename(columns={
        "Chuyên mục": "topic",
        "Tỉ lệ (%)": "ratio"
    }).to_csv(topic_history_file_dt, mode='a', index=False, header=write_header_dt, encoding='utf-8')

    try:
        with open(log_file_dt, mode="r", encoding="utf-8") as f:
            logs_dt = [line.strip().split(" | ") for line in f.readlines()][-10:]
            df_logs_dt = pd.DataFrame(logs_dt, columns=["Thời điểm cập nhật", "Tổng bài viết"])
            st.table(df_logs_dt)
    except Exception as e:
        st.warning("Không thể đọc lịch sử cập nhật (Dân Trí).")

# ---------- VnExpress Section ----------
st.header("📊 Dashboard bài viết VnExpress - Tự động cập nhật")
try:
    df_vne_raw = pd.read_csv("../crawl_vnexpress/data_vnexpress/data.csv")
except Exception as e:
    st.error(f"Không thể đọc dữ liệu VnExpress: {e}")
    df_vne_raw = pd.DataFrame()

if not df_vne_raw.empty:
    df_vne = df_vne_raw.dropna(subset=["title", "url", "content", "topic"]).copy()

    st.metric("Số dòng thực tế đọc được (VnExpress)", df_vne_raw.shape[0])
    st.metric("Tổng số bài viết (VnExpress)", len(df_vne))

    st.subheader("Một số bài viết đầu tiên (VnExpress)")
    st.dataframe(df_vne[["title", "url"]].head(), use_container_width=True)

    summary_vne = df_vne['topic'].value_counts().reset_index()
    summary_vne.columns = ['Chuyên mục', 'Số bài']
    summary_vne['Tỉ lệ (%)'] = (summary_vne['Số bài'] / len(df_vne) * 100).round(2)

    st.subheader("Tỷ lệ chuyên mục (VnExpress)")
    st.dataframe(summary_vne, use_container_width=True)

    st.altair_chart(alt.Chart(summary_vne).mark_bar().encode(
        x='Số bài:Q', y=alt.Y('Chuyên mục:N', sort='-x'),
        color='Chuyên mục:N', tooltip=['Chuyên mục', 'Số bài', 'Tỉ lệ (%)']
    ).properties(width=700, height=400), use_container_width=True)

    st.altair_chart(alt.Chart(summary_vne.sort_values("Tỉ lệ (%)", ascending=False)).mark_line(point=True).encode(
        x=alt.X('Chuyên mục:N', sort=summary_vne.sort_values("Tỉ lệ (%)", ascending=False)['Chuyên mục'].tolist(), title='Chuyên mục'),
        y=alt.Y('Tỉ lệ (%):Q', title='Tỉ lệ (%)'),
        tooltip=['Chuyên mục', 'Tỉ lệ (%)']
    ).properties(width=900, height=400), use_container_width=True)

    # Hiển thị lịch sử cập nhật cho VnExpress
    st.subheader("Lịch sử cập nhật (VnExpress)")
    log_file_vne = "../crawl_vnexpress/data_vnexpress/update_log.txt"
    topic_history_file_vne = "../crawl_vnexpress/data_vnexpress/topic_history.csv"
    now_vne = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    total_articles_vne = len(df_vne)

    log_line_vne = f"{now_vne} | Tổng bài viết: {total_articles_vne}"
    os.makedirs(os.path.dirname(log_file_vne), exist_ok=True)
    with open(log_file_vne, mode="a", encoding="utf-8") as f:
        f.write(log_line_vne + "\n")

    summary_vne['timestamp'] = now_vne
    write_header_vne = not os.path.exists(topic_history_file_vne)
    summary_vne[["timestamp", "Chuyên mục", "Tỉ lệ (%)"]].rename(columns={
        "Chuyên mục": "topic",
        "Tỉ lệ (%)": "ratio"
    }).to_csv(topic_history_file_vne, mode='a', index=False, header=write_header_vne, encoding='utf-8')

    try:
        with open(log_file_vne, mode="r", encoding="utf-8") as f:
            logs_vne = [line.strip().split(" | ") for line in f.readlines()][-10:]
            df_logs_vne = pd.DataFrame(logs_vne, columns=["Thời điểm cập nhật", "Tổng bài viết"])
            st.table(df_logs_vne)
    except Exception as e:
        st.warning("Không thể đọc lịch sử cập nhật (VnExpress).")

# ---------- Phân phối cụm từ hot (Dân Trí) ----------
st.header("🔥 Biểu đồ cụm từ hot trong 3 ngày gần nhất")

try:
    # JSON phân phối cụm từ
    with open("../analyze_dantri_trends/data/top_phrases.json", "r", encoding="utf-8") as f:
        top_phrases = json.load(f)
    df_phrases = pd.DataFrame(top_phrases, columns=["Cụm từ", "Số lần xuất hiện"])

    st.dataframe(df_phrases, use_container_width=True)

    st.altair_chart(alt.Chart(df_phrases).mark_bar().encode(
        x=alt.X("Số lần xuất hiện:Q", title="Số lần xuất hiện"),
        y=alt.Y("Cụm từ:N", sort='-x', title="Cụm từ"),
        tooltip=["Cụm từ", "Số lần xuất hiện"]
    ).properties(width=750, height=400), use_container_width=True)

    # Hiển thị ảnh biểu đồ mới nhất
    image_dir = "../analyze_dantri_trends/data/image/"
    image_files = sorted(glob.glob(os.path.join(image_dir, "top_phrases_*.png")), reverse=True)
    if image_files:
        latest_img = image_files[0]
        st.image(Image.open(latest_img), caption=f"Ảnh: {os.path.basename(latest_img)}", use_container_width=True)

except Exception as e:
    st.warning(f"Không thể đọc biểu đồ phân phối cụm từ: {e}")

# ---------- Hiển thị bảng chủ đề hot và bài viết liên quan ----------
st.subheader("🔥 Chủ đề hot nhất gần đây và bài viết liên quan")

try:
    topic_files = sorted(glob.glob("../analyze_dantri_trends/data/hot_topics_*.csv"), reverse=True)
    if topic_files:
        latest_topic_file = topic_files[0]
        df_topic = pd.read_csv(latest_topic_file)
        st.dataframe(df_topic, use_container_width=True)
    else:
        st.info("Không tìm thấy file hot_topics_*.csv")

except Exception as e:
    st.warning(f"Lỗi khi đọc hot_topics.csv: {e}")

# ---------------chatbot----------------
sys.path.append(os.path.abspath("../chatbot_rag"))

from query import run_query_external 

st.header("Chatbot hỏi đáp báo chí")

with st.expander("Hỏi chatbot về dữ liệu báo chí"):
    user_question = st.text_input("Nhập câu hỏi:")

    if user_question:
        with st.spinner("Đang xử lý..."):
            answers = run_query_external(user_question)
            for line in answers:
                st.markdown(f"- {line}")

