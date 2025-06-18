import os
import json
import time
import argparse
import csv
import sys
import io
from queue import Queue
from tqdm import tqdm

from config import Config
from src.crawler_vnexpress.vnexpress import VnExpress
from src.crawler_vnexpress.base import News
from worker import Producer, Consumer

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def get_existing_urls(file_path='data_vnexpress/data.csv'):
    existing_urls = set()
    if os.path.exists(file_path):
        with open(file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                existing_urls.add(row['url'])
    return existing_urls

def append_news_to_csv(news: News, topic: str, file_path='data_vnexpress/data.csv', existing_urls=None):
    if existing_urls is None:
        existing_urls = get_existing_urls(file_path)

    if news.url in existing_urls:
        print(f"[SKIP] Already saved: {news.url}")
        return

    file_exists = os.path.isfile(file_path)
    with open(file_path, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, quoting=csv.QUOTE_ALL)
        if not file_exists or os.stat(file_path).st_size == 0:
            writer.writerow(['title', 'author', 'created_at', 'content', 'url', 'topic'])
        writer.writerow([
            news.title.strip(),
            news.author.strip(),
            news.created_at.isoformat(),
            news.content.replace('\n', ' ').replace('\r', ' ').strip(),
            news.url,
            topic
        ])
    print(f"[SAVE] {news.title[:60]}... -> {news.url}")

def filter_existing_links(links, existing_urls):
    filtered = [item for item in links if item['url'] not in existing_urls]
    print(f"[FILTER] Skipped {len(links) - len(filtered)} already in data.csv")
    return filtered

# -------------------- MAIN --------------------
if __name__ == "__main__":
    os.makedirs("data_vnexpress", exist_ok=True)

    parser = argparse.ArgumentParser(description="Crawl news from VnExpress.")
    parser.add_argument("method", type=str, choices=["sync", "thread", "async"], default="sync",
                        help="Method to run: sync, thread, async")
    parser.add_argument("--max_pagination", type=int, default=2, help="Max paginations per topic")
    parser.add_argument("--num_workers", type=int, default=4, help="Threads for 'thread' method")
    parser.add_argument("--num_links", type=int, default=1000, help="Max number of links to crawl")
    parser.add_argument("--force_crawl", action="store_true", help="Force re-crawling and merge new links")

    args = parser.parse_args()

    q = Queue()
    vnexpress = VnExpress()
    urls_file = "data_vnexpress/urls.json"
    csv_file = "data_vnexpress/data.csv"

    if args.force_crawl:
        print(f"[CRAWL] Crawling fresh links from VnExpress (max_pagination={args.max_pagination}) ...")
        new_links = vnexpress.crawl(max_pagination=args.max_pagination, link_only=True)
        if os.path.exists(urls_file):
            with open(urls_file, "r", encoding="utf-8") as f:
                old_links = json.load(f)
        else:
            old_links = []

        old_urls = {item['url'] for item in old_links}
        combined_links = old_links + [item for item in new_links if item['url'] not in old_urls]

        with open(urls_file, "w", encoding="utf-8") as f:
            json.dump(combined_links, f, ensure_ascii=False, indent=4)
        print(f"[SAVE] Merged and saved {len(combined_links)} links to {urls_file}")

    if os.path.exists(urls_file):
        with open(urls_file, "r", encoding="utf-8") as f:
            links = json.load(f)
        print(f"[LOAD] Loaded {len(links)} links from {urls_file}")
    else:
        print("[ERROR] urls.json not found. Use --force_crawl first.")
        exit(1)

    existing_urls = get_existing_urls(file_path=csv_file)
    links = filter_existing_links(links, existing_urls)
    links = links[:args.num_links]

    start_time = time.time()

    if args.method == "sync":
        print("-------------------- Synchronous --------------------")
        scrape_news = vnexpress.scrape_news()
        for i, item in enumerate(tqdm(links), 1):
            print(f"[{i}/{len(links)}] Fetching: {item['url']}")
            time.sleep(Config.SLEEP_TIME)
            result = scrape_news(url=item['url'])
            if result:
                append_news_to_csv(result, topic=item['topic'], file_path=csv_file, existing_urls=existing_urls)
                existing_urls.add(result.url)
        
        print(f"[FINISH] Sync mode finished in {round(time.time() - start_time, 2)} seconds")

        # Gửi notify sau khi crawl xong toàn bộ
        try:
            import requests
            response = requests.get("http://localhost:8000/notify", timeout=2)
            print(f"[NOTIFY] Sent final notify after crawl completed. Status: {response.status_code}")
        except Exception as e:
            print(f"[WARN] Failed to send notify: {e}")

