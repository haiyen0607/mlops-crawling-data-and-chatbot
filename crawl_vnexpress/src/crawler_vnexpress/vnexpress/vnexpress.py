import time
from bs4 import Tag
from tqdm import tqdm
from typing import List
from datetime import datetime
from urllib.parse import urljoin
from slugify import slugify

from src.crawler_vnexpress.base import BaseCrawler, News
from config import Config


class VnExpress(BaseCrawler):
    TOPIC_LINKS = {
        "thoi-su": "https://vnexpress.net/thoi-su",
        "the-gioi": "https://vnexpress.net/the-gioi",
        "kinh-doanh": "https://vnexpress.net/kinh-doanh",
        "giai-tri": "https://vnexpress.net/giai-tri",
        "the-thao": "https://vnexpress.net/the-thao",
        "phap-luat": "https://vnexpress.net/phap-luat",
        "giao-duc": "https://vnexpress.net/giao-duc",
        "suc-khoe": "https://vnexpress.net/suc-khoe",
        "doi-song": "https://vnexpress.net/doi-song",
        "du-lich": "https://vnexpress.net/du-lich",
        "so-hoa": "https://vnexpress.net/so-hoa",
        "oto-xe-may": "https://vnexpress.net/oto-xe-may"
    }

    def __init__(self, *args, **kwargs):
        super().__init__(parent_url="https://vnexpress.net/", *args, **kwargs)

    #Phân tích DOM để lấy chuyên mục phụ
    def _get_subtopics(self, url: str) -> List[str]:
        soup = self._fetch(url)
        sub_links = set()
        base_path = url.strip("/").split("/")[-1]  # ví dụ: "thoi-su"

        for a in soup.find_all("a", href=True):
            href = a["href"]
            if (
                href.startswith(f"https://vnexpress.net/{base_path}/")
                and len(href.split("/")) > 4
                and href != url
            ):
                sub_links.add(href)

        return list(sub_links)

    #Trích xuất nội dung bài viết
    def _scrape_news(self, url: str, *args, **kwargs):
        soup = self._fetch(url, *args, **kwargs)
        if not soup or not soup.text.strip():
            print(f"[WARN] Empty or invalid soup for: {url}")
            return None

        title = soup.find("h1", class_="title-detail")
        time_tag = soup.find("span", class_="date")
        content_tags = soup.select("article.fck_detail p")

        # ==== Tìm tên tác giả ====
        author = "Không rõ"
        author_tag = soup.find("p", class_="author_mail")
        if author_tag:
            author = author_tag.get_text(strip=True)
        else:
            author_paras = soup.select("article.fck_detail p.Normal[style*='text-align:right']")
            for p in reversed(author_paras):
                strong = p.find("strong")
                if strong and strong.text.strip():
                    author = strong.text.strip()
                    break

        created_at = datetime.now()
        if time_tag:
            try:
                created_at = datetime.strptime(
                    time_tag.text.strip(), "%A, %d/%m/%Y, %H:%M (GMT+7)"
                )
            except:
                pass

        content = "\n".join([p.get_text(strip=True) for p in content_tags if p.get_text(strip=True)])

        if title and content:
            return News(
                title=title.get_text(strip=True),
                author=author,
                created_at=created_at,
                content=content,
                url=url,
            )
        return None

    #Đệ quy phân trang
    def _scrape_topic(self, url: str, n_th_page: int = 1, *args, **kwargs):
        time.sleep(Config.SLEEP_TIME)

        if n_th_page > kwargs.get("max_pagination", Config.MAX_PAGINATION):
            return []

        soup = self._fetch(url, *args, **kwargs)
        article_tags = soup.select("article.item-news a[href^='https://vnexpress.net/']")
        raw_links = {a["href"] for a in article_tags if isinstance(a, Tag) and a.get("href")}

        # Lọc link chỉ lấy link hợp lệ: kết thúc bằng .html và không có #
        news_links = [
            link.split("#")[0]  # Bỏ phần fragment nếu có
            for link in raw_links
            if link.endswith(".html")
        ]

        next_tag = soup.select_one("a.next-page")
        if isinstance(next_tag, Tag) and next_tag.get("href"):
            next_page_url = urljoin(self.parent_url, next_tag.get("href"))
            news_links += self._scrape_topic(next_page_url, n_th_page + 1, *args, **kwargs)

        return news_links

    #Tổng hợp crawl toàn bộ chuyên mục chính + phụ
    def crawl(self, max_pagination: int = 5, link_only: bool = False, *args, **kwargs) -> List[News] | List[dict]:
        print(f"[INFO] Crawling topics and subtopics...")
        news_links = []

        for topic, url in (pbar := tqdm(self.TOPIC_LINKS.items())):
            pbar.set_description(f"Crawling {topic}")

            sub_urls = [url] + self._get_subtopics(url)
            for sub_url in sub_urls:
                pbar.set_postfix(sub=sub_url.replace(self.parent_url, ""))
                links = self._scrape_topic(sub_url, max_pagination=max_pagination, pbar=pbar)

                for link in links:
                    news_links.append({"url": link, "topic": topic})

                time.sleep(Config.SLEEP_TIME)

        # Xoá trùng link theo URL
        seen = set()
        unique_links = []
        for item in news_links:
            if item["url"] not in seen:
                seen.add(item["url"])
                unique_links.append(item)

        if link_only:
            return unique_links

        print("[INFO] Scraping article content...")
        news = []
        for item in tqdm(unique_links):
            time.sleep(Config.SLEEP_TIME)
            article = self._scrape_news(item["url"])
            if article:
                news.append(article)

        return news



    def scrape_news(self):
        return self._scrape_news
