import pandas as pd
from llama_index.core.schema import Document
from datetime import datetime, timedelta

def load_documents_from_csv(csv_path: str, from_date: datetime = None):
    df = pd.read_csv(csv_path, encoding="utf-8")
    df['created_at'] = pd.to_datetime(df['created_at'])

    if from_date:
        df = df[df['created_at'] >= from_date]

    documents = []
    for _, row in df.iterrows():
        full_text = (
            f"Tiêu đề: {row['title']}\n"
            f"Tác giả: {row['author']}\n"
            f"Ngày đăng: {row['created_at']}\n"
            f"Nội dung: {row['content']}\n"
            f"URL: {row['url']}"
        )

        doc = Document(
            text=full_text,
            metadata={
                "title": row['title'],
                "author": row['author'],
                "created_at": row['created_at'].strftime("%Y-%m-%d"),
                "url": row['url']
            }
        )
        documents.append(doc)
    return documents
