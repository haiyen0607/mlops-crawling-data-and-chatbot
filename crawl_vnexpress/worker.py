import time
import random
import requests
from queue import Queue
from typing import List
from threading import Thread
from datetime import datetime
import csv
import os

from config import Config
from src.crawler_vnexpress.base import News


class Producer(Thread):
    def __init__(self, queue: Queue, urls: List[str]):
        Thread.__init__(self)
        self.q = queue
        self.urls = urls

    def run(self):
        for url in self.urls:
            self.q.put(url)


class Consumer(Thread):
    def __init__(
        self,
        queue: Queue,
        instance,
        consumer_id: int,
        sleep_time: float = 1.0,
        timeout: int = 60,
        output_file: str = "data_vnexpress/data.csv",
        *args,
        **kwargs,
    ):
        Thread.__init__(self)
        self.q = queue
        self.instance = instance
        self.timeout = timeout
        self.sleep_time = sleep_time
        self.consumer_id = consumer_id
        self.progress_bar = kwargs.get("progress_bar")
        self.output_file = output_file

    def run(self):
        while not self.q.empty():
            try:
                url = self.q.get(timeout=self.timeout)
                print(f"[Consumer-{self.consumer_id}] Fetching: {url}")
                time.sleep(self.sleep_time)
                news = self.instance.scrape_news(url=url)

                if news:
                    self._append_to_csv(news)
                self.q.task_done()

                if self.progress_bar:
                    self.progress_bar.update(1)
            except Exception as e:
                print(f"[Consumer-{self.consumer_id}] Error: {e}")

    def _append_to_csv(self, news: News):
        file_exists = os.path.isfile(self.output_file)
        existing_urls = set()

        if file_exists:
            with open(self.output_file, mode='r', encoding='utf-8') as file:
                for line in file:
                    parts = line.strip().split(',')
                    if len(parts) >= 5:
                        existing_urls.add(parts[4])

        if news.url in existing_urls:
            print(f"[SKIP] Duplicated URL: {news.url}")
            return

        with open(self.output_file, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(['title', 'author', 'created_at', 'content', 'url'])
            writer.writerow([
                news.title,
                news.author,
                news.created_at.isoformat(),
                news.content,
                news.url
            ])
        print(f"[SAVE] {news.title[:60]}... -> {news.url}")
